"""Extract brand styling from uploaded PPTX or DOCX files.

Discovers colors, fonts, layout patterns, logo positions, and slide/page structures
by reading the Office XML parts (theme, slide masters, and content) directly from
the zip archive. Nothing is extracted to disk.

The uploaded file is treated as untrusted, because it is often a third-party file.
The script therefore:
    - rejects archives with more than MAX_ARCHIVE_MEMBERS entries,
    - reads only the specific XML parts it needs, straight from the ZipFile,
    - rejects any of those parts that is larger than MAX_MEMBER_BYTES once
      uncompressed, or that has an extreme compression ratio (zip bomb),
    - caps the total amount of XML it decompresses, and
    - parses XML with defusedxml when it is installed.

Usage:
    python extract_brand_style.py <office_file> <output_json>

Examples:
    python extract_brand_style.py client-deck.pptx brand_style.json
    python extract_brand_style.py client-proposal.docx brand_style.json

Output:
    JSON file with discovered brand tokens that can be used to replicate the style.
"""

import argparse
import fnmatch
import json
import os
import re
import sys
import zipfile
import zlib
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET

try:
    # defusedxml blocks entity-expansion ("billion laughs") and external-entity
    # attacks hidden in the XML of an uploaded, possibly third-party file.
    from defusedxml import DefusedXmlException as _DefusedXmlError
    from defusedxml.ElementTree import fromstring as _xml_fromstring
except ImportError:
    # Fallback, used only when defusedxml is not installed: the standard library
    # parser. It does not fetch external entities, and the size and ratio limits
    # below still apply, but it is less strict than defusedxml. Install defusedxml
    # ("pip install defusedxml") for full protection.
    from xml.etree.ElementTree import fromstring as _xml_fromstring

    class _DefusedXmlError(Exception):
        """Stand-in so the except clauses below work without defusedxml."""


# XML errors that mean "this part could not be parsed safely": the part is skipped.
_XML_ERRORS = (ET.ParseError, _DefusedXmlError)

# Safety limits for untrusted uploads. Real decks and documents sit far below them.
MAX_ARCHIVE_MEMBERS = 2000             # entries in the zip archive
MAX_MEMBER_BYTES = 20 * 1024 * 1024    # uncompressed size of any one part we read
MAX_TOTAL_BYTES = 200 * 1024 * 1024    # all parts we read, combined
MAX_COMPRESSION_RATIO = 200            # uncompressed size / compressed size
RATIO_CHECK_MIN_BYTES = 1024 * 1024    # parts smaller than this skip the ratio check


class UnsafeArchiveError(Exception):
    """Raised when an uploaded file breaks one of the safety limits above."""


class _OfficeArchive:
    """Read-only view of an open Office zip archive.

    Parts are read straight from the ZipFile into memory, only when needed and
    only after the size and ratio checks. Nothing is written to disk, so member
    names such as "../../evil" cannot escape a folder. Part names are matched
    without regard to case, as the Office (OPC) format specifies.
    """

    def __init__(self, zf: zipfile.ZipFile):
        infos = zf.infolist()
        if len(infos) > MAX_ARCHIVE_MEMBERS:
            raise UnsafeArchiveError(
                f"archive has {len(infos)} entries (limit {MAX_ARCHIVE_MEMBERS})"
            )
        self._zf = zf
        self._bytes_read = 0
        self._keys = set()   # lower-case names of every entry, folders included
        self._files = {}     # lower-case name -> (name, ZipInfo) for file entries
        for info in infos:
            name = info.filename.replace("\\", "/")
            key = name.lower()
            self._keys.add(key)
            if not name.endswith("/"):
                # A later entry with the same name wins, as it would on extraction.
                self._files[key] = (name, info)

    def has_file(self, name: str) -> bool:
        return name.lower() in self._files

    def has_dir(self, folder: str) -> bool:
        prefix = folder.lower().rstrip("/") + "/"
        return any(key.startswith(prefix) for key in self._keys)

    def list_dir(self, folder: str, pattern: str) -> list:
        """Files directly inside folder whose own name matches pattern, sorted."""
        prefix = folder.lower().rstrip("/") + "/"
        found = []
        for key, (name, _info) in self._files.items():
            rest = key[len(prefix):]
            if key.startswith(prefix) and "/" not in rest and fnmatch.fnmatchcase(rest, pattern.lower()):
                found.append(name)
        return sorted(found, key=str.lower)

    def find_first(self, pattern: str):
        """First file anywhere whose own name matches pattern, or None.

        Shallower folders come first, then alphabetical order, so the choice is
        stable. For a standard file this is the main theme (theme1.xml).
        """
        matches = [
            name for key, (name, _info) in self._files.items()
            if fnmatch.fnmatchcase(key.rsplit("/", 1)[-1], pattern.lower())
        ]
        if not matches:
            return None
        return min(matches, key=lambda n: (n.count("/"), n.lower()))

    def read(self, name: str) -> bytes:
        """Return the uncompressed bytes of one part, after the safety checks."""
        part_name, info = self._files[name.lower()]
        size = info.file_size
        if size > MAX_MEMBER_BYTES:
            raise UnsafeArchiveError(
                f"part {part_name} is {size} bytes uncompressed (limit {MAX_MEMBER_BYTES})"
            )
        if size > RATIO_CHECK_MIN_BYTES and size > MAX_COMPRESSION_RATIO * max(info.compress_size, 1):
            raise UnsafeArchiveError(
                f"part {part_name} has an extreme compression ratio (limit {MAX_COMPRESSION_RATIO}:1)"
            )
        if self._bytes_read + size > MAX_TOTAL_BYTES:
            raise UnsafeArchiveError(
                f"parts read exceed the total limit of {MAX_TOTAL_BYTES} bytes"
            )
        try:
            with self._zf.open(info) as fh:
                # Read at most one byte past the cap, so a false size in the zip
                # header cannot make us decompress more than the limit.
                data = fh.read(MAX_MEMBER_BYTES + 1)
        except (zlib.error, EOFError, NotImplementedError, RuntimeError) as exc:
            raise zipfile.BadZipFile(str(exc)) from exc
        if len(data) > MAX_MEMBER_BYTES:
            raise UnsafeArchiveError(
                f"part {part_name} is larger than {MAX_MEMBER_BYTES} bytes uncompressed"
            )
        self._bytes_read += len(data)
        return data

    def parse_xml(self, name: str):
        """Parse one XML part and return its root element."""
        return _xml_fromstring(self.read(name))


# XML Namespaces
NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main",
    "wp": "http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing",
    "mc": "http://schemas.openxmlformats.org/markup-compatibility/2006",
    "ct": "http://schemas.openxmlformats.org/package/2006/content-types",
}


def extract_brand_style(input_file: str) -> dict:
    """Main extraction function. Returns a brand style dictionary."""
    input_path = Path(input_file)
    suffix = input_path.suffix.lower()

    if suffix not in (".pptx", ".docx"):
        return {"error": f"Unsupported file type: {suffix}. Use .pptx or .docx"}

    # Read the needed parts straight from the archive; never extract it to disk.
    try:
        with zipfile.ZipFile(input_path, "r") as zf:
            archive = _OfficeArchive(zf)
            if suffix == ".pptx":
                return _extract_pptx_style(archive, input_file)
            else:
                return _extract_docx_style(archive, input_file)
    except zipfile.BadZipFile:
        return {"error": f"Invalid Office file: {input_file}"}
    except UnsafeArchiveError as exc:
        return {"error": f"Unsafe Office file rejected: {input_file} ({exc})"}


def _hex_from_rgb(r: int, g: int, b: int) -> str:
    """Convert RGB to hex string."""
    return f"#{r:02X}{g:02X}{b:02X}"


def _parse_color(color_el) -> str | None:
    """Extract hex color from a DrawingML color element."""
    if color_el is None:
        return None

    # srgbClr - direct hex
    srgb = color_el.find(".//a:srgbClr", NS)
    if srgb is not None:
        val = srgb.get("val", "")
        if len(val) == 6:
            return f"#{val.upper()}"

    # sysClr - system color
    sys_clr = color_el.find(".//a:sysClr", NS)
    if sys_clr is not None:
        last_clr = sys_clr.get("lastClr", "")
        if len(last_clr) == 6:
            return f"#{last_clr.upper()}"

    return None


def _extract_theme_colors(archive: _OfficeArchive) -> dict:
    """Extract color scheme from theme XML."""
    theme_file = archive.find_first("theme*.xml")
    if theme_file is None:
        return {}

    colors = {}
    try:
        root = archive.parse_xml(theme_file)

        # Color scheme
        clr_scheme = root.find(".//a:clrScheme", NS)
        if clr_scheme is not None:
            color_names = [
                "dk1", "dk2", "lt1", "lt2",
                "accent1", "accent2", "accent3", "accent4",
                "accent5", "accent6", "hlink", "folHlink"
            ]
            for name in color_names:
                el = clr_scheme.find(f"a:{name}", NS)
                if el is not None:
                    c = _parse_color(el)
                    if c:
                        colors[name] = c

        # Font scheme
        font_scheme = root.find(".//a:fontScheme", NS)
        if font_scheme is not None:
            major = font_scheme.find(".//a:majorFont/a:latin", NS)
            minor = font_scheme.find(".//a:minorFont/a:latin", NS)
            if major is not None:
                colors["heading_font"] = major.get("typeface", "")
            if minor is not None:
                colors["body_font"] = minor.get("typeface", "")

    except _XML_ERRORS:
        pass

    return colors


def _extract_pptx_style(archive: _OfficeArchive, source_file: str) -> dict:
    """Extract brand style from PPTX."""
    style = {
        "source_file": os.path.basename(source_file),
        "file_type": "pptx",
        "theme_colors": {},
        "used_colors": [],
        "fonts": {"headings": [], "body": []},
        "slide_dimensions": {},
        "logo_info": {},
        "layout_patterns": [],
        "background_colors": [],
        "text_sizes": {"headings": [], "body": []},
        "slide_count": 0,
    }

    # Theme colors
    style["theme_colors"] = _extract_theme_colors(archive)
    if "heading_font" in style["theme_colors"]:
        style["fonts"]["headings"].append(style["theme_colors"].pop("heading_font"))
    if "body_font" in style["theme_colors"]:
        style["fonts"]["body"].append(style["theme_colors"].pop("body_font"))

    # Slide dimensions from presentation.xml
    pres_xml = "ppt/presentation.xml"
    if archive.has_file(pres_xml):
        try:
            root = archive.parse_xml(pres_xml)
            slide_size = root.find(".//p:sldSz", NS)
            if slide_size is not None:
                cx = int(slide_size.get("cx", "0"))
                cy = int(slide_size.get("cy", "0"))
                # EMU to inches
                style["slide_dimensions"] = {
                    "width_emu": cx,
                    "height_emu": cy,
                    "width_inches": round(cx / 914400, 2),
                    "height_inches": round(cy / 914400, 2),
                    "aspect_ratio": "16:9" if abs(cx / cy - 16 / 9) < 0.1 else "4:3" if abs(cx / cy - 4 / 3) < 0.1 else "custom",
                }
        except _XML_ERRORS:
            pass

    # Analyze slide content
    slide_dir = "ppt/slides"
    color_counter = Counter()
    font_counter_heading = Counter()
    font_counter_body = Counter()
    size_heading = []
    size_body = []
    bg_colors = []

    if archive.has_dir(slide_dir):
        slide_files = archive.list_dir(slide_dir, "slide*.xml")
        style["slide_count"] = len(slide_files)

        for slide_file in slide_files:
            try:
                root = archive.parse_xml(slide_file)

                # Background colors
                bg = root.find(".//p:bg", NS)
                if bg is not None:
                    c = _parse_color(bg)
                    if c:
                        bg_colors.append(c)

                # Text analysis
                for sp in root.findall(".//p:sp", NS):
                    for paragraph in sp.findall(".//a:p", NS):
                        runs = paragraph.findall(".//a:r", NS)
                        for run in runs:
                            rpr = run.find("a:rPr", NS)
                            text = run.find("a:t", NS)
                            if rpr is not None:
                                # Font
                                latin = rpr.find("a:latin", NS)
                                if latin is not None:
                                    font_name = latin.get("typeface", "")
                                    if font_name and font_name not in ("+mj-lt", "+mn-lt"):
                                        sz = rpr.get("sz", "0")
                                        sz_pt = int(sz) / 100 if sz.isdigit() else 0
                                        if sz_pt >= 20:
                                            font_counter_heading[font_name] += 1
                                            size_heading.append(sz_pt)
                                        else:
                                            font_counter_body[font_name] += 1
                                            size_body.append(sz_pt)

                                # Colors
                                solid_fill = rpr.find("a:solidFill", NS)
                                if solid_fill is not None:
                                    c = _parse_color(solid_fill)
                                    if c:
                                        color_counter[c] += 1

                                # Bold for heading detection
                                if rpr.get("b") == "1":
                                    sz = rpr.get("sz", "0")
                                    sz_pt = int(sz) / 100 if sz.isdigit() else 0
                                    if sz_pt > 0:
                                        size_heading.append(sz_pt)

                # Shape fill colors
                for sp in root.findall(".//p:sp", NS):
                    sp_pr = sp.find(".//p:spPr", NS) or sp.find(".//a:spPr", NS)
                    if sp_pr is not None:
                        solid = sp_pr.find("a:solidFill", NS)
                        if solid is not None:
                            c = _parse_color(solid)
                            if c:
                                color_counter[c] += 1

            except _XML_ERRORS:
                continue

    # Aggregate results
    style["used_colors"] = [{"color": c, "frequency": f} for c, f in color_counter.most_common(10)]
    style["background_colors"] = list(set(bg_colors))

    if font_counter_heading:
        style["fonts"]["headings"] = [f for f, _ in font_counter_heading.most_common(3)]
    if font_counter_body:
        style["fonts"]["body"] = [f for f, _ in font_counter_body.most_common(3)]

    if size_heading:
        style["text_sizes"]["headings"] = {
            "min": round(min(size_heading), 1),
            "max": round(max(size_heading), 1),
            "avg": round(sum(size_heading) / len(size_heading), 1),
        }
    if size_body:
        style["text_sizes"]["body"] = {
            "min": round(min(size_body), 1),
            "max": round(max(size_body), 1),
            "avg": round(sum(size_body) / len(size_body), 1),
        }

    # Check for logo images (typically on slide master or first slide)
    media_dir = "ppt/media"
    if archive.has_dir(media_dir):
        images = archive.list_dir(media_dir, "image*")
        style["logo_info"] = {
            "image_count": len(images),
            "image_files": [img.rsplit("/", 1)[-1] for img in images[:5]],
            "note": "First image in slide master is typically the logo"
        }

    # Build the design token summary
    style["design_tokens"] = _build_design_tokens(style)

    return style


def _extract_docx_style(archive: _OfficeArchive, source_file: str) -> dict:
    """Extract brand style from DOCX."""
    style = {
        "source_file": os.path.basename(source_file),
        "file_type": "docx",
        "theme_colors": {},
        "used_colors": [],
        "fonts": {"headings": [], "body": []},
        "page_dimensions": {},
        "margins": {},
        "header_footer": {},
        "text_sizes": {"headings": [], "body": []},
        "paragraph_styles": [],
    }

    # Theme colors
    style["theme_colors"] = _extract_theme_colors(archive)
    if "heading_font" in style["theme_colors"]:
        style["fonts"]["headings"].append(style["theme_colors"].pop("heading_font"))
    if "body_font" in style["theme_colors"]:
        style["fonts"]["body"].append(style["theme_colors"].pop("body_font"))

    # Analyze text styles - declare counters outside try block
    color_counter = Counter()
    font_counter_heading = Counter()
    font_counter_body = Counter()
    size_heading = []
    size_body = []

    # Document properties from document.xml
    doc_xml = "word/document.xml"
    if archive.has_file(doc_xml):
        try:
            root = archive.parse_xml(doc_xml)

            # Page size and margins from sectPr
            sect_pr = root.find(".//w:sectPr", NS)
            if sect_pr is not None:
                pg_sz = sect_pr.find("w:pgSz", NS)
                if pg_sz is not None:
                    w = int(pg_sz.get(f"{{{NS['w']}}}w", "0") or pg_sz.get("w", "0"))
                    h = int(pg_sz.get(f"{{{NS['w']}}}h", "0") or pg_sz.get("h", "0"))
                    style["page_dimensions"] = {
                        "width_twips": w,
                        "height_twips": h,
                        "width_inches": round(w / 1440, 2) if w > 0 else 0,
                        "height_inches": round(h / 1440, 2) if h > 0 else 0,
                        "size": "A4" if abs(w - 11906) < 100 else "Letter" if abs(w - 12240) < 100 else "custom",
                    }

                pg_mar = sect_pr.find("w:pgMar", NS)
                if pg_mar is not None:
                    for attr in ["top", "right", "bottom", "left"]:
                        val = pg_mar.get(f"{{{NS['w']}}}{attr}", "0") or pg_mar.get(attr, "0")
                        style["margins"][attr] = {
                            "twips": int(val),
                            "inches": round(int(val) / 1440, 2),
                        }

            # Analyze text styles within document

            for para in root.findall(".//w:p", NS):
                p_pr = para.find("w:pPr", NS)
                is_heading = False
                if p_pr is not None:
                    p_style = p_pr.find("w:pStyle", NS)
                    if p_style is not None:
                        style_val = p_style.get(f"{{{NS['w']}}}val", "") or p_style.get("val", "")
                        if "heading" in style_val.lower() or "title" in style_val.lower():
                            is_heading = True

                for run in para.findall(".//w:r", NS):
                    r_pr = run.find("w:rPr", NS)
                    if r_pr is not None:
                        # Font
                        r_fonts = r_pr.find("w:rFonts", NS)
                        if r_fonts is not None:
                            for attr in ["ascii", "hAnsi", "cs"]:
                                font_name = r_fonts.get(f"{{{NS['w']}}}{attr}", "") or r_fonts.get(attr, "")
                                if font_name and not font_name.startswith("+"):
                                    if is_heading:
                                        font_counter_heading[font_name] += 1
                                    else:
                                        font_counter_body[font_name] += 1

                        # Size
                        sz = r_pr.find("w:sz", NS)
                        if sz is not None:
                            val = sz.get(f"{{{NS['w']}}}val", "") or sz.get("val", "")
                            if val.isdigit():
                                pt = int(val) / 2  # half-points to points
                                if is_heading:
                                    size_heading.append(pt)
                                else:
                                    size_body.append(pt)

                        # Color
                        color = r_pr.find("w:color", NS)
                        if color is not None:
                            val = color.get(f"{{{NS['w']}}}val", "") or color.get("val", "")
                            if len(val) == 6:
                                color_counter[f"#{val.upper()}"] += 1

        except _XML_ERRORS:
            pass

    # Styles from styles.xml
    styles_xml = "word/styles.xml"
    if archive.has_file(styles_xml):
        try:
            root = archive.parse_xml(styles_xml)
            for st in root.findall(".//w:style", NS):
                style_type = st.get(f"{{{NS['w']}}}type", "") or st.get("type", "")
                style_id = st.get(f"{{{NS['w']}}}styleId", "") or st.get("styleId", "")
                name_el = st.find("w:name", NS)
                name = (name_el.get(f"{{{NS['w']}}}val", "") or name_el.get("val", "")) if name_el is not None else style_id

                if style_type == "paragraph" and ("heading" in name.lower() or "title" in name.lower() or "normal" in name.lower()):
                    style["paragraph_styles"].append({
                        "id": style_id,
                        "name": name,
                        "type": style_type,
                    })
        except _XML_ERRORS:
            pass

    # Aggregate
    style["used_colors"] = [{"color": c, "frequency": f} for c, f in color_counter.most_common(10)]
    if font_counter_heading:
        style["fonts"]["headings"] = [f for f, _ in font_counter_heading.most_common(3)]
    if font_counter_body:
        style["fonts"]["body"] = [f for f, _ in font_counter_body.most_common(3)]

    if size_heading:
        style["text_sizes"]["headings"] = {
            "min": round(min(size_heading), 1),
            "max": round(max(size_heading), 1),
            "avg": round(sum(size_heading) / len(size_heading), 1),
        }
    if size_body:
        style["text_sizes"]["body"] = {
            "min": round(min(size_body), 1),
            "max": round(max(size_body), 1),
            "avg": round(sum(size_body) / len(size_body), 1),
        }

    # Check for images (logo candidates)
    media_dir = "word/media"
    if archive.has_dir(media_dir):
        images = archive.list_dir(media_dir, "image*")
        style["logo_info"] = {
            "image_count": len(images),
            "image_files": [img.rsplit("/", 1)[-1] for img in images[:5]],
        }

    # Build design tokens
    style["design_tokens"] = _build_design_tokens(style)

    return style


def _build_design_tokens(style: dict) -> dict:
    """Build a clean design token summary from extracted data."""
    tokens = {
        "primary_color": None,
        "secondary_color": None,
        "accent_color": None,
        "background_color": None,
        "text_color": None,
        "heading_font": None,
        "body_font": None,
        "heading_size_pt": None,
        "body_size_pt": None,
    }

    # Colors from theme first, then from usage
    tc = style.get("theme_colors", {})
    if tc.get("dk1"):
        tokens["text_color"] = tc["dk1"]
    if tc.get("lt1"):
        tokens["background_color"] = tc["lt1"]
    if tc.get("accent1"):
        tokens["primary_color"] = tc["accent1"]
    if tc.get("accent2"):
        tokens["secondary_color"] = tc["accent2"]
    if tc.get("accent3"):
        tokens["accent_color"] = tc["accent3"]

    # Override with most-used colors if theme is generic
    used = style.get("used_colors", [])
    if used and not tokens["primary_color"]:
        tokens["primary_color"] = used[0]["color"]
    if len(used) > 1 and not tokens["secondary_color"]:
        tokens["secondary_color"] = used[1]["color"]

    # Fonts
    fonts = style.get("fonts", {})
    if fonts.get("headings"):
        tokens["heading_font"] = fonts["headings"][0]
    if fonts.get("body"):
        tokens["body_font"] = fonts["body"][0]

    # Sizes
    sizes = style.get("text_sizes", {})
    if isinstance(sizes.get("headings"), dict):
        tokens["heading_size_pt"] = sizes["headings"].get("avg")
    if isinstance(sizes.get("body"), dict):
        tokens["body_size_pt"] = sizes["body"].get("avg")

    return tokens


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extract brand styling from PPTX or DOCX files"
    )
    parser.add_argument("input_file", help="PPTX or DOCX file to analyze")
    parser.add_argument("output_json", help="Output JSON file for brand tokens")
    args = parser.parse_args()

    result = extract_brand_style(args.input_file)

    with open(args.output_json, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    if "error" in result:
        print(f"Error: {result['error']}")
        sys.exit(1)
    else:
        tokens = result.get("design_tokens", {})
        print(f"Brand style extracted from {args.input_file}")
        print(f"  Primary color: {tokens.get('primary_color', 'N/A')}")
        print(f"  Heading font:  {tokens.get('heading_font', 'N/A')}")
        print(f"  Body font:     {tokens.get('body_font', 'N/A')}")
        print(f"  Saved to: {args.output_json}")
