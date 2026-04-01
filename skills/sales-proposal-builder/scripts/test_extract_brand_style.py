"""Unit tests for extract_brand_style.py

Coverage target: 100% of all functions and branches.
"""

import json
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch
from xml.etree.ElementTree import Element, SubElement

# Add script directory to path
sys.path.insert(0, os.path.dirname(__file__))
from extract_brand_style import (
    extract_brand_style,
    _hex_from_rgb,
    _parse_color,
    _extract_theme_colors,
    _build_design_tokens,
)


class TestHexFromRgb(unittest.TestCase):
    """Tests for _hex_from_rgb helper."""

    def test_black(self):
        self.assertEqual(_hex_from_rgb(0, 0, 0), "#000000")

    def test_white(self):
        self.assertEqual(_hex_from_rgb(255, 255, 255), "#FFFFFF")

    def test_red(self):
        self.assertEqual(_hex_from_rgb(255, 0, 0), "#FF0000")

    def test_arbitrary_color(self):
        self.assertEqual(_hex_from_rgb(17, 21, 40), "#111528")


class TestParseColor(unittest.TestCase):
    """Tests for _parse_color helper."""

    def test_none_input(self):
        self.assertIsNone(_parse_color(None))

    def test_srgb_color(self):
        ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
        el = Element("test")
        srgb = SubElement(el, f"{{{ns}}}srgbClr")
        srgb.set("val", "C9A962")
        self.assertEqual(_parse_color(el), "#C9A962")

    def test_sys_color(self):
        ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
        el = Element("test")
        sys_clr = SubElement(el, f"{{{ns}}}sysClr")
        sys_clr.set("lastClr", "1A1F36")
        self.assertEqual(_parse_color(el), "#1A1F36")

    def test_invalid_color_length(self):
        ns = "http://schemas.openxmlformats.org/drawingml/2006/main"
        el = Element("test")
        srgb = SubElement(el, f"{{{ns}}}srgbClr")
        srgb.set("val", "FFF")  # Too short
        self.assertIsNone(_parse_color(el))

    def test_empty_element(self):
        el = Element("test")
        self.assertIsNone(_parse_color(el))


class TestBuildDesignTokens(unittest.TestCase):
    """Tests for _build_design_tokens helper."""

    def test_empty_style(self):
        style = {}
        tokens = _build_design_tokens(style)
        self.assertIsNone(tokens["primary_color"])
        self.assertIsNone(tokens["heading_font"])

    def test_theme_colors_populate_tokens(self):
        style = {
            "theme_colors": {
                "dk1": "#000000",
                "lt1": "#FFFFFF",
                "accent1": "#C9A962",
                "accent2": "#1A1F36",
                "accent3": "#2563EB",
            },
            "fonts": {"headings": ["Georgia"], "body": ["Calibri"]},
            "text_sizes": {
                "headings": {"avg": 24.0},
                "body": {"avg": 11.0},
            },
        }
        tokens = _build_design_tokens(style)
        self.assertEqual(tokens["primary_color"], "#C9A962")
        self.assertEqual(tokens["secondary_color"], "#1A1F36")
        self.assertEqual(tokens["accent_color"], "#2563EB")
        self.assertEqual(tokens["text_color"], "#000000")
        self.assertEqual(tokens["background_color"], "#FFFFFF")
        self.assertEqual(tokens["heading_font"], "Georgia")
        self.assertEqual(tokens["body_font"], "Calibri")
        self.assertEqual(tokens["heading_size_pt"], 24.0)
        self.assertEqual(tokens["body_size_pt"], 11.0)

    def test_used_colors_fallback(self):
        style = {
            "theme_colors": {},
            "used_colors": [
                {"color": "#FF0000", "frequency": 10},
                {"color": "#00FF00", "frequency": 5},
            ],
            "fonts": {"headings": [], "body": []},
            "text_sizes": {},
        }
        tokens = _build_design_tokens(style)
        self.assertEqual(tokens["primary_color"], "#FF0000")
        self.assertEqual(tokens["secondary_color"], "#00FF00")

    def test_no_fonts_returns_none(self):
        style = {"theme_colors": {}, "fonts": {"headings": [], "body": []}, "text_sizes": {}}
        tokens = _build_design_tokens(style)
        self.assertIsNone(tokens["heading_font"])
        self.assertIsNone(tokens["body_font"])


class TestExtractBrandStyleUnsupported(unittest.TestCase):
    """Tests for unsupported file types."""

    def test_unsupported_file_type(self):
        with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as f:
            f.write(b"fake")
            f.flush()
            result = extract_brand_style(f.name)
            self.assertIn("error", result)
            self.assertIn("Unsupported", result["error"])
            os.unlink(f.name)

    def test_invalid_zip(self):
        with tempfile.NamedTemporaryFile(suffix=".pptx", delete=False) as f:
            f.write(b"not a zip file at all")
            f.flush()
            result = extract_brand_style(f.name)
            self.assertIn("error", result)
            os.unlink(f.name)


class TestExtractPptxStyle(unittest.TestCase):
    """Tests for PPTX extraction."""

    def _create_minimal_pptx(self, tmp_dir, theme_xml=None, slide_xml=None, pres_xml=None):
        """Create a minimal valid PPTX zip."""
        pptx_path = os.path.join(tmp_dir, "test.pptx")
        with zipfile.ZipFile(pptx_path, "w") as zf:
            # Content types
            zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')

            if pres_xml:
                zf.writestr("ppt/presentation.xml", pres_xml)
            else:
                zf.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')

            if theme_xml:
                zf.writestr("ppt/theme/theme1.xml", theme_xml)

            if slide_xml:
                zf.writestr("ppt/slides/slide1.xml", slide_xml)

        return pptx_path

    def test_minimal_pptx(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_pptx(tmp)
            result = extract_brand_style(path)
            self.assertEqual(result["file_type"], "pptx")
            self.assertIn("design_tokens", result)
            self.assertIn("slide_dimensions", result)

    def test_pptx_dimensions_16_9(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_pptx(tmp)
            result = extract_brand_style(path)
            self.assertEqual(result["slide_dimensions"]["aspect_ratio"], "16:9")

    def test_pptx_dimensions_4_3(self):
        pres_xml = '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="9144000" cy="6858000"/></p:presentation>'
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_pptx(tmp, pres_xml=pres_xml)
            result = extract_brand_style(path)
            self.assertEqual(result["slide_dimensions"]["aspect_ratio"], "4:3")

    def test_pptx_with_theme(self):
        theme_xml = '''<?xml version="1.0"?>
        <a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main">
          <a:themeElements>
            <a:clrScheme name="Test">
              <a:dk1><a:srgbClr val="111528"/></a:dk1>
              <a:lt1><a:srgbClr val="F4F3EF"/></a:lt1>
              <a:accent1><a:srgbClr val="C9A962"/></a:accent1>
            </a:clrScheme>
            <a:fontScheme name="Test">
              <a:majorFont><a:latin typeface="Georgia"/></a:majorFont>
              <a:minorFont><a:latin typeface="Calibri"/></a:minorFont>
            </a:fontScheme>
          </a:themeElements>
        </a:theme>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_pptx(tmp, theme_xml=theme_xml)
            result = extract_brand_style(path)
            self.assertEqual(result["theme_colors"]["dk1"], "#111528")
            self.assertEqual(result["theme_colors"]["lt1"], "#F4F3EF")
            self.assertEqual(result["theme_colors"]["accent1"], "#C9A962")
            self.assertIn("Georgia", result["fonts"]["headings"])
            self.assertIn("Calibri", result["fonts"]["body"])

    def test_pptx_slide_count(self):
        with tempfile.TemporaryDirectory() as tmp:
            slide_xml = '<?xml version="1.0"?><p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"></p:sld>'
            path = self._create_minimal_pptx(tmp, slide_xml=slide_xml)
            result = extract_brand_style(path)
            self.assertEqual(result["slide_count"], 1)


class TestExtractDocxStyle(unittest.TestCase):
    """Tests for DOCX extraction."""

    def _create_minimal_docx(self, tmp_dir, doc_xml=None, styles_xml=None, theme_xml=None):
        """Create a minimal valid DOCX zip."""
        docx_path = os.path.join(tmp_dir, "test.docx")
        with zipfile.ZipFile(docx_path, "w") as zf:
            zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')

            if doc_xml:
                zf.writestr("word/document.xml", doc_xml)
            else:
                zf.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>')

            if styles_xml:
                zf.writestr("word/styles.xml", styles_xml)

            if theme_xml:
                zf.writestr("word/theme/theme1.xml", theme_xml)

        return docx_path

    def test_minimal_docx(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_docx(tmp)
            result = extract_brand_style(path)
            self.assertEqual(result["file_type"], "docx")
            self.assertIn("design_tokens", result)

    def test_docx_a4_detection(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_docx(tmp)
            result = extract_brand_style(path)
            self.assertEqual(result["page_dimensions"]["size"], "A4")

    def test_docx_letter_detection(self):
        doc_xml = '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:sectPr><w:pgSz w:w="12240" w:h="15840"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>'
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_docx(tmp, doc_xml=doc_xml)
            result = extract_brand_style(path)
            self.assertEqual(result["page_dimensions"]["size"], "Letter")

    def test_docx_margins(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_docx(tmp)
            result = extract_brand_style(path)
            self.assertEqual(result["margins"]["top"]["twips"], 1440)
            self.assertEqual(result["margins"]["top"]["inches"], 1.0)

    def test_docx_with_styles(self):
        styles_xml = '''<?xml version="1.0"?>
        <w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
          <w:style w:type="paragraph" w:styleId="Heading1">
            <w:name w:val="heading 1"/>
          </w:style>
          <w:style w:type="paragraph" w:styleId="Normal">
            <w:name w:val="Normal"/>
          </w:style>
        </w:styles>'''
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_minimal_docx(tmp, styles_xml=styles_xml)
            result = extract_brand_style(path)
            style_ids = [s["id"] for s in result["paragraph_styles"]]
            self.assertIn("Heading1", style_ids)
            self.assertIn("Normal", style_ids)


class TestCLIInterface(unittest.TestCase):
    """Tests for CLI argument parsing and file output."""

    def test_cli_output_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            # Create a minimal PPTX
            pptx_path = os.path.join(tmp, "test.pptx")
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')

            output_path = os.path.join(tmp, "output.json")

            # Run as CLI
            import subprocess
            result = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "extract_brand_style.py"), pptx_path, output_path],
                capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(output_path))

            with open(output_path) as f:
                data = json.load(f)
            self.assertEqual(data["file_type"], "pptx")
            self.assertIn("design_tokens", data)


if __name__ == "__main__":
    unittest.main(verbosity=2)


class TestPptxSlideContent(unittest.TestCase):
    """Tests for PPTX slide text/color/font extraction - covers lines 204-283."""

    def _create_pptx_with_text(self, tmp_dir):
        """Create PPTX with actual text content in slides."""
        ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
        ns_p = "http://schemas.openxmlformats.org/presentationml/2006/main"

        slide_xml = f'''<?xml version="1.0"?>
        <p:sld xmlns:p="{ns_p}" xmlns:a="{ns_a}">
          <p:cSld>
            <p:bg>
              <p:bgPr>
                <a:solidFill><a:srgbClr val="111528"/></a:solidFill>
              </p:bgPr>
            </p:bg>
            <p:spTree>
              <p:sp>
                <p:txBody>
                  <a:p>
                    <a:r>
                      <a:rPr sz="2400" b="1">
                        <a:latin typeface="Georgia"/>
                        <a:solidFill><a:srgbClr val="C9A962"/></a:solidFill>
                      </a:rPr>
                      <a:t>Heading Text</a:t>
                    </a:r>
                  </a:p>
                  <a:p>
                    <a:r>
                      <a:rPr sz="1100">
                        <a:latin typeface="Calibri"/>
                        <a:solidFill><a:srgbClr val="3A3F52"/></a:solidFill>
                      </a:rPr>
                      <a:t>Body text content</a:t>
                    </a:r>
                  </a:p>
                </p:txBody>
                <p:spPr>
                  <a:solidFill><a:srgbClr val="F4F3EF"/></a:solidFill>
                </p:spPr>
              </p:sp>
            </p:spTree>
          </p:cSld>
        </p:sld>'''

        pptx_path = os.path.join(tmp_dir, "text_test.pptx")
        with zipfile.ZipFile(pptx_path, "w") as zf:
            zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
            zf.writestr("ppt/presentation.xml", f'<?xml version="1.0"?><p:presentation xmlns:p="{ns_p}"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
            zf.writestr("ppt/slides/slide1.xml", slide_xml)
        return pptx_path

    def test_extracts_text_colors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_pptx_with_text(tmp)
            result = extract_brand_style(path)
            colors = [c["color"] for c in result["used_colors"]]
            self.assertIn("#C9A962", colors)
            self.assertIn("#3A3F52", colors)

    def test_extracts_background_color(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_pptx_with_text(tmp)
            result = extract_brand_style(path)
            self.assertIn("#111528", result["background_colors"])

    def test_extracts_heading_font(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_pptx_with_text(tmp)
            result = extract_brand_style(path)
            self.assertIn("Georgia", result["fonts"]["headings"])

    def test_extracts_body_font(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_pptx_with_text(tmp)
            result = extract_brand_style(path)
            self.assertIn("Calibri", result["fonts"]["body"])

    def test_extracts_heading_sizes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_pptx_with_text(tmp)
            result = extract_brand_style(path)
            self.assertIsInstance(result["text_sizes"]["headings"], dict)
            self.assertIn("avg", result["text_sizes"]["headings"])

    def test_extracts_body_sizes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_pptx_with_text(tmp)
            result = extract_brand_style(path)
            self.assertIsInstance(result["text_sizes"]["body"], dict)

    def test_extracts_shape_fill_colors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_pptx_with_text(tmp)
            result = extract_brand_style(path)
            colors = [c["color"] for c in result["used_colors"]]
            self.assertIn("#F4F3EF", colors)


class TestDocxTextContent(unittest.TestCase):
    """Tests for DOCX text extraction - covers lines 356-398."""

    def _create_docx_with_text(self, tmp_dir):
        """Create DOCX with styled text content."""
        ns_w = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
        doc_xml = f'''<?xml version="1.0"?>
        <w:document xmlns:w="{ns_w}">
          <w:body>
            <w:p>
              <w:pPr>
                <w:pStyle w:val="Heading1"/>
              </w:pPr>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Georgia" w:hAnsi="Georgia"/>
                  <w:sz w:val="48"/>
                  <w:color w:val="1A1F36"/>
                </w:rPr>
                <w:t>Heading Text</w:t>
              </w:r>
            </w:p>
            <w:p>
              <w:r>
                <w:rPr>
                  <w:rFonts w:ascii="Calibri" w:hAnsi="Calibri"/>
                  <w:sz w:val="22"/>
                  <w:color w:val="3A3F52"/>
                </w:rPr>
                <w:t>Body paragraph text</w:t>
              </w:r>
            </w:p>
            <w:sectPr>
              <w:pgSz w:w="11906" w:h="16838"/>
              <w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/>
            </w:sectPr>
          </w:body>
        </w:document>'''

        docx_path = os.path.join(tmp_dir, "text_test.docx")
        with zipfile.ZipFile(docx_path, "w") as zf:
            zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
            zf.writestr("word/document.xml", doc_xml)
        return docx_path

    def test_extracts_heading_font(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_docx_with_text(tmp)
            result = extract_brand_style(path)
            self.assertIn("Georgia", result["fonts"]["headings"])

    def test_extracts_body_font(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_docx_with_text(tmp)
            result = extract_brand_style(path)
            self.assertIn("Calibri", result["fonts"]["body"])

    def test_extracts_text_colors(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_docx_with_text(tmp)
            result = extract_brand_style(path)
            colors = [c["color"] for c in result["used_colors"]]
            self.assertIn("#1A1F36", colors)
            self.assertIn("#3A3F52", colors)

    def test_extracts_heading_sizes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_docx_with_text(tmp)
            result = extract_brand_style(path)
            # 48 half-points = 24pt
            self.assertIsInstance(result["text_sizes"]["headings"], dict)
            self.assertEqual(result["text_sizes"]["headings"]["avg"], 24.0)

    def test_extracts_body_sizes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = self._create_docx_with_text(tmp)
            result = extract_brand_style(path)
            # 22 half-points = 11pt
            self.assertIsInstance(result["text_sizes"]["body"], dict)
            self.assertEqual(result["text_sizes"]["body"]["avg"], 11.0)


class TestPptxMediaDetection(unittest.TestCase):
    """Tests for logo/image detection in PPTX - covers lines 313-315."""

    def test_detects_media_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = os.path.join(tmp, "media_test.pptx")
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
                zf.writestr("ppt/media/image1.png", b"fake png")
                zf.writestr("ppt/media/image2.jpg", b"fake jpg")

            result = extract_brand_style(pptx_path)
            self.assertEqual(result["logo_info"]["image_count"], 2)
            self.assertIn("image1.png", result["logo_info"]["image_files"])


class TestDocxMediaDetection(unittest.TestCase):
    """Tests for image detection in DOCX - covers lines 444-445."""

    def test_detects_media_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            docx_path = os.path.join(tmp, "media_test.docx")
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>')
                zf.writestr("word/media/image1.png", b"fake logo")

            result = extract_brand_style(docx_path)
            self.assertEqual(result["logo_info"]["image_count"], 1)


class TestCLIErrorPath(unittest.TestCase):
    """Test CLI error handling - covers lines 524-529."""

    def test_cli_error_on_invalid_file(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            bad_path = os.path.join(tmp, "bad.pptx")
            with open(bad_path, "w") as f:
                f.write("not a zip")
            out_path = os.path.join(tmp, "out.json")

            result = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "extract_brand_style.py"), bad_path, out_path],
                capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("Error", result.stdout)


class TestThemeParseError(unittest.TestCase):
    """Test theme XML parse error handling - covers line 133-134."""

    def test_corrupt_theme_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = os.path.join(tmp, "corrupt_theme.pptx")
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
                zf.writestr("ppt/theme/theme1.xml", "<<<NOT VALID XML>>>")

            result = extract_brand_style(pptx_path)
            # Should not crash, just return empty theme colors
            self.assertEqual(result["file_type"], "pptx")
            self.assertEqual(result["theme_colors"], {})


class TestCorruptSlideXml(unittest.TestCase):
    """Test slide XML parse error handling."""

    def test_corrupt_slide_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = os.path.join(tmp, "corrupt_slide.pptx")
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
                zf.writestr("ppt/slides/slide1.xml", "<<<BAD XML>>>")

            result = extract_brand_style(pptx_path)
            self.assertEqual(result["file_type"], "pptx")
            self.assertEqual(result["slide_count"], 1)


class TestCorruptDocxXml(unittest.TestCase):
    """Test DOCX XML parse error handling - covers line 398."""

    def test_corrupt_document_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            docx_path = os.path.join(tmp, "corrupt_doc.docx")
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("word/document.xml", "<<<BAD XML>>>")

            result = extract_brand_style(docx_path)
            self.assertEqual(result["file_type"], "docx")


class TestPptxSkipsThemeFonts(unittest.TestCase):
    """Test that +mj-lt and +mn-lt theme font references are skipped."""

    def test_skips_theme_font_refs(self):
        ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
        ns_p = "http://schemas.openxmlformats.org/presentationml/2006/main"

        slide_xml = f'''<?xml version="1.0"?>
        <p:sld xmlns:p="{ns_p}" xmlns:a="{ns_a}">
          <p:cSld>
            <p:spTree>
              <p:sp>
                <p:txBody>
                  <a:p>
                    <a:r>
                      <a:rPr sz="1200">
                        <a:latin typeface="+mj-lt"/>
                      </a:rPr>
                      <a:t>Theme ref</a:t>
                    </a:r>
                  </a:p>
                </p:txBody>
              </p:sp>
            </p:spTree>
          </p:cSld>
        </p:sld>'''

        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = os.path.join(tmp, "themefont.pptx")
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", f'<?xml version="1.0"?><p:presentation xmlns:p="{ns_p}"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
                zf.writestr("ppt/slides/slide1.xml", slide_xml)

            result = extract_brand_style(pptx_path)
            # +mj-lt should NOT appear in fonts
            all_fonts = result["fonts"]["headings"] + result["fonts"]["body"]
            self.assertNotIn("+mj-lt", all_fonts)
            self.assertNotIn("+mn-lt", all_fonts)




class TestPptxPresentationParseError(unittest.TestCase):
    """Test corrupt presentation.xml - covers lines 180-181."""

    def test_corrupt_presentation_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = os.path.join(tmp, "corrupt_pres.pptx")
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", "<<<BAD XML>>>")

            result = extract_brand_style(pptx_path)
            self.assertEqual(result["file_type"], "pptx")
            # Dimensions should be empty since presentation.xml failed to parse
            self.assertEqual(result["slide_dimensions"], {})


class TestDocxStylesParseError(unittest.TestCase):
    """Test corrupt styles.xml - covers lines 420-421."""

    def test_corrupt_styles_xml(self):
        with tempfile.TemporaryDirectory() as tmp:
            docx_path = os.path.join(tmp, "corrupt_styles.docx")
            with zipfile.ZipFile(docx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("word/document.xml", '<?xml version="1.0"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:sectPr><w:pgSz w:w="11906" w:h="16838"/><w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440"/></w:sectPr></w:body></w:document>')
                zf.writestr("word/styles.xml", "<<<BAD XML>>>")

            result = extract_brand_style(docx_path)
            self.assertEqual(result["file_type"], "docx")
            # Styles should be empty since styles.xml failed to parse
            self.assertEqual(result["paragraph_styles"], [])


class TestPptxLogoInfoNote(unittest.TestCase):
    """Test logo info note field - covers lines 313, 315."""

    def test_logo_info_has_note(self):
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = os.path.join(tmp, "logo_note.pptx")
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
                zf.writestr("ppt/media/image1.png", b"fake")

            result = extract_brand_style(pptx_path)
            self.assertIn("note", result["logo_info"])
            self.assertIn("logo", result["logo_info"]["note"].lower())


class TestCLIMainBlock(unittest.TestCase):
    """Integration tests for CLI main block - covers lines 510-531."""

    def test_cli_success_output(self):
        import subprocess
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = os.path.join(tmp, "cli_test.pptx")
            ns_a = "http://schemas.openxmlformats.org/drawingml/2006/main"
            with zipfile.ZipFile(pptx_path, "w") as zf:
                zf.writestr("[Content_Types].xml", '<?xml version="1.0"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
                zf.writestr("ppt/presentation.xml", '<?xml version="1.0"?><p:presentation xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"><p:sldSz cx="12192000" cy="6858000"/></p:presentation>')
                theme_xml = f'''<?xml version="1.0"?>
                <a:theme xmlns:a="{ns_a}">
                  <a:themeElements>
                    <a:clrScheme name="T"><a:accent1><a:srgbClr val="FF0000"/></a:accent1></a:clrScheme>
                    <a:fontScheme name="T">
                      <a:majorFont><a:latin typeface="Arial"/></a:majorFont>
                      <a:minorFont><a:latin typeface="Verdana"/></a:minorFont>
                    </a:fontScheme>
                  </a:themeElements>
                </a:theme>'''
                zf.writestr("ppt/theme/theme1.xml", theme_xml)

            out_path = os.path.join(tmp, "output.json")
            result = subprocess.run(
                [sys.executable, os.path.join(os.path.dirname(__file__), "extract_brand_style.py"), pptx_path, out_path],
                capture_output=True, text=True
            )
            self.assertEqual(result.returncode, 0)
            self.assertIn("Primary color", result.stdout)
            self.assertIn("Heading font", result.stdout)
            self.assertIn("Body font", result.stdout)
            self.assertIn("Saved to", result.stdout)


