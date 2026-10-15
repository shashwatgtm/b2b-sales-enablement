"""Tests for delivery_check.py, the plugin's Stop hook (run 35C tests, adapted in run 36P: this plugin's hook path, marker and skill names).
Kept outside the shipped plugin folder. Run from the repository root: python3 tests/test_delivery_check.py (or python where python3 is not found).
Each test writes a small session transcript (one JSON object per line, as Claude Code stores it), feeds the hook its Stop input and reads
its answer: nothing printed lets Claude stop; a JSON "block" decision sends Claude back with the reason."""
import hashlib, json, pathlib, subprocess, sys, tempfile, unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOK = sorted(ROOT.glob("plugins/*/hooks/delivery_check.py"))[0]
SKILL0 = sorted(p.name for p in HOOK.parent.parent.glob("skills/*"))[0]


def dg(t):
    t = "\n".join(l.rstrip() for l in t.replace("\r\n", "\n").strip().splitlines())
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


REPLY = "Plan: synthesis of five interviews.\n\n| Pain | Interviews |\n|---|---|\n| Late close | 3 of 5 |\n\nWhich round comes next?"
LEDGER = f'python3 "/x/skills/{SKILL0}/scripts/claim_ledger.py" --final --user /s/user.txt /s/reply.md'


def final_out(text=REPLY, needs=0):
    d = dg(text)
    head = f"== /s/reply.md\nlabels in /s/reply.md: none\ndigest /s/reply.md: {d}\nclaim_ledger: {needs} lines NEEDS a source, a label or a rewrite; 0 label drops; digests reply.md={d}\n"
    if needs:
        return head + "NOT DELIVERABLE: fix every NEEDS line and run --final again."
    return head + f"DELIVER: send as your whole chat reply exactly the text between the two marker lines.\n=== BEGIN CHECKED REPLY {d} ===\n{text}\n=== END CHECKED REPLY {d} ==="


class T:
    """A transcript builder."""
    def __init__(self):
        self.lines, self.n = [], 0

    def user(self, text):
        self.lines.append({"type": "user", "message": {"role": "user", "content": text}}); return self

    def tool(self, name, inp, result):
        self.n += 1
        tid = f"toolu_{self.n}"
        self.lines.append({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "tool_use", "id": tid, "name": name, "input": inp}]}})
        self.lines.append({"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tid, "content": result}]}})
        return self

    def bash(self, cmd, result):
        return self.tool("Bash", {"command": cmd}, result)

    def say(self, text):
        self.lines.append({"type": "assistant", "message": {"role": "assistant", "content": [{"type": "text", "text": text}]}}); return self

    def hook(self, last=None, active=False, session="s1", raw=None, cwd=None):
        d = pathlib.Path(tempfile.mkdtemp())
        p = d / "t.jsonl"
        p.write_text("\n".join(json.dumps(x) for x in self.lines) + "\n", encoding="utf-8")
        inp = raw if raw is not None else json.dumps({"session_id": session + d.name, "transcript_path": str(p), "hook_event_name": "Stop",
                                                      "stop_hook_active": active, **({"last_assistant_message": last} if last is not None else {}),
                                                      **({"cwd": cwd} if cwd else {})})
        r = subprocess.run([sys.executable, str(HOOK)], input=inp, capture_output=True, text=True, env={"TMPDIR": str(d), "PATH": "/usr/bin:/bin"})
        self.code = r.returncode
        out = r.stdout.strip()
        return json.loads(out) if out else None


class Allows(unittest.TestCase):
    def test_a_turn_without_the_ledger_is_left_alone(self):
        t = T().user("hello").bash("ls", "a b").say("Hi.")
        self.assertIsNone(t.hook("Hi."))
        self.assertEqual(t.code, 0)

    def test_reply_equal_to_the_checked_text_passes(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say(REPLY)
        self.assertIsNone(t.hook(REPLY))

    def test_trailing_spaces_and_end_newlines_do_not_count(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say(REPLY)
        self.assertIsNone(t.hook("\n" + REPLY.replace("\n", "  \n") + "\n\n"))

    def test_last_message_read_from_the_transcript_when_not_given(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say(REPLY)
        self.assertIsNone(t.hook(None))

    def test_a_read_after_the_final_run_is_fine(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).bash("cat /s/reply.md", REPLY).tool("Read", {"file_path": "/s/reply.md"}, REPLY).say(REPLY)
        self.assertIsNone(t.hook(REPLY))

    def test_ledger_in_an_earlier_turn_only(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say(REPLY).user("Thanks. What is a hypothesis tally?").say("It counts ...")
        self.assertIsNone(t.hook("It counts ..."))

    def test_bad_input_never_blocks(self):
        for raw in ["", "not json", json.dumps({"transcript_path": "/nowhere/t.jsonl", "last_assistant_message": "x"})]:
            t = T()
            self.assertIsNone(t.hook(raw=raw))
            self.assertEqual(t.code, 0)

    def test_tool_result_as_a_list_of_blocks(self):
        t = T().user("notes ...").bash(LEDGER, [{"type": "text", "text": final_out()}]).say(REPLY)
        self.assertIsNone(t.hook(REPLY))


class Blocks(unittest.TestCase):
    def test_reworded_reply_is_sent_back(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say("I've synthesised the five interviews. " + REPLY)
        r = t.hook("I've synthesised the five interviews. " + REPLY)
        self.assertEqual(r["decision"], "block")
        self.assertIn(dg(REPLY), r["reason"])
        self.assertIn("BEGIN CHECKED REPLY", r["reason"])

    def test_ledger_ran_but_never_passed_final(self):
        t = T().user("notes ...").bash(LEDGER.replace(" --final", ""), "claim_ledger: 3 lines NEEDS a source, a label or a rewrite; 0 label drops").say(REPLY)
        r = t.hook(REPLY)
        self.assertEqual(r["decision"], "block")
        self.assertIn("--final", r["reason"])

    def test_final_run_with_needs_lines(self):
        t = T().user("notes ...").bash(LEDGER, final_out(needs=2)).say(REPLY)
        self.assertEqual(t.hook(REPLY)["decision"], "block")

    def test_a_change_after_the_final_run(self):
        for tool, inp in (("Write", {"file_path": "/s/reply.md", "content": "x"}), ("Edit", {"file_path": "/s/guide.md", "old_string": "a", "new_string": "b"}),
                          ("Bash", {"command": "cp /s/reply.md /w/guide.md"}), ("Bash", {"command": "cat > /s/reply.md <<'EOF'\nx\nEOF"})):
            t = T().user("notes ...").bash(LEDGER, final_out()).tool(tool, inp, "ok").say(REPLY)
            r = t.hook(REPLY)
            self.assertEqual((r or {}).get("decision"), "block", tool + str(inp))

    def test_earlier_final_then_a_later_ordinary_run(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).bash(LEDGER.replace(" --final", ""), "claim_ledger: 0 lines NEEDS ...").say(REPLY)
        self.assertEqual(t.hook(REPLY)["decision"], "block")

    def test_hook_feedback_does_not_start_a_new_turn(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say("Summary first. " + REPLY)
        r = t.hook("Summary first. " + REPLY)
        t.user("Stop hook feedback:\n" + r["reason"]).say("Summary again. " + REPLY)
        self.assertEqual(t.hook("Summary again. " + REPLY, active=True)["decision"], "block")

    def test_at_most_two_sends_back_per_turn(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say("x " + REPLY)
        d = pathlib.Path(tempfile.mkdtemp())
        p = d / "t.jsonl"
        p.write_text("\n".join(json.dumps(x) for x in t.lines) + "\n", encoding="utf-8")
        inp = json.dumps({"session_id": "cap-" + d.name, "transcript_path": str(p), "stop_hook_active": False, "last_assistant_message": "x " + REPLY})
        got = []
        for _ in range(3):
            r = subprocess.run([sys.executable, str(HOOK)], input=inp, capture_output=True, text=True, env={"TMPDIR": str(d), "PATH": "/usr/bin:/bin"})
            got.append(json.loads(r.stdout)["decision"] if r.stdout.strip() else None)
        self.assertEqual(got, ["block", "block", None])


class AuditR01(unittest.TestCase):
    """Run 35C gate audit r01 (N1, N2, N4 to N8)."""
    def test_text_before_the_final_run_does_not_count_but_text_after_it_does(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say("Here it is.").say(REPLY)
        self.assertEqual(t.hook(None)["decision"], "block")   # N1: a preamble block after --final is part of the reply

    def test_utf8_stdin_bytes(self):   # N2: the hook reads stdin as UTF-8 bytes whatever the console code page
        text = REPLY + " \u2019quoted\u2019 \u201cok\u201d"
        t = T().user("notes ...").bash(LEDGER, final_out(text)).say(text)
        d = pathlib.Path(tempfile.mkdtemp()); p = d / "t.jsonl"
        p.write_text("\n".join(json.dumps(x) for x in t.lines) + "\n", encoding="utf-8")
        inp = json.dumps({"session_id": "u8" + d.name, "transcript_path": str(p), "last_assistant_message": text}, ensure_ascii=False).encode("utf-8")
        r = subprocess.run([sys.executable, str(HOOK)], input=inp, capture_output=True, env={"TMPDIR": str(d), "PATH": "/usr/bin:/bin", "PYTHONIOENCODING": "cp1252"})
        self.assertEqual(r.stdout.strip(), b"")
        bad = json.dumps({"session_id": "u9" + d.name, "transcript_path": str(p), "last_assistant_message": "\u201cReworded\u201d " + text}, ensure_ascii=False).encode("utf-8")
        r = subprocess.run([sys.executable, str(HOOK)], input=bad, capture_output=True, env={"TMPDIR": str(d), "PATH": "/usr/bin:/bin", "PYTHONIOENCODING": "cp1252"})
        self.assertIn(b"block", r.stdout)

    def test_tools_that_change_no_file_after_the_final_run(self):   # N4
        for name, inp in (("TodoWrite", {"todos": []}), ("WebSearch", {"query": "x"}), ("WebFetch", {"url": "page"}), ("Skill", {"skill": "x"}), ("TaskUpdate", {"id": "1"})):
            t = T().user("notes ...").bash(LEDGER, final_out()).tool(name, inp, "ok").say(REPLY)
            self.assertIsNone(t.hook(REPLY), name)

    def test_only_a_run_of_this_plugins_ledger_starts_the_check(self):   # N5
        for cmd, out in (("python3 /x/skills/pmf-check/scripts/test_claim_ledger.py", "Ran 76 tests\nOK"), ("cat /x/skills/pmf-check/scripts/claim_ledger.py", '"""claim_ledger.py: the claim ledger.'),
                         ("grep -n final /x/scripts/claim_ledger.py", "12: --final"), ("python3 /other/plugin/claim_ledger.py --user u.txt r.md", "3 problems found")):
            t = T().user("question").bash(cmd, out).say("An answer.")
            self.assertIsNone(t.hook("An answer."), cmd)

    def test_oversize_output_keeps_the_verdict_line(self):   # N6: the first line of --final carries the verdict and digest
        head = f"claim_ledger --final: PASS, reply digest {dg(REPLY)}\n"
        t = T().user("notes ...").bash(LEDGER, head + "Output too large (90KB). Full output saved to: /tmp/x.txt\n\nPreview (first 2KB):\n== /s/reply.md").say(REPLY)
        self.assertIsNone(t.hook(REPLY))

    def test_compaction_and_other_feedback_do_not_start_a_turn(self):   # N7
        for msg in ({"type": "user", "isCompactSummary": True, "message": {"role": "user", "content": "This session is being continued ..."}},
                    {"type": "user", "message": {"role": "user", "content": "Stop hook feedback:\nanother plugin says hi"}}):
            t = T().user("notes ...").bash(LEDGER, final_out())
            t.lines.append(msg)
            t.say("Reworded. " + REPLY)
            self.assertEqual(t.hook("Reworded. " + REPLY)["decision"], "block")

    def test_powershell_ledger_run_is_seen(self):   # N8
        t = T().user("notes ...").tool("PowerShell", {"command": LEDGER}, final_out()).say("x " + REPLY)
        self.assertEqual(t.hook("x " + REPLY)["decision"], "block")


class AuditR02(unittest.TestCase):
    """Run 35C gate audit r02: M2 (the reply window), M4 (CRLF output), M6 (a read only pipe)."""
    def test_send_back_then_the_exact_reply_is_allowed(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say("Reworded. " + REPLY)
        r = t.hook("Reworded. " + REPLY)
        self.assertEqual(r["decision"], "block")
        t.user("Stop hook feedback:\n" + r["reason"]).say(REPLY)
        self.assertIsNone(t.hook(REPLY, active=True))

    def test_reworded_again_after_send_back_is_blocked(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).say("Reworded. " + REPLY)
        r = t.hook("Reworded. " + REPLY)
        t.user("Stop hook feedback:\n" + r["reason"]).say("Still reworded. " + REPLY)
        self.assertEqual(t.hook("Still reworded. " + REPLY, active=True)["decision"], "block")

    def test_crlf_output(self):
        t = T().user("notes ...").bash(LEDGER, final_out().replace("\n", "\r\n")).say(REPLY)
        self.assertIsNone(t.hook(REPLY))

    def test_read_only_pipe_after_final(self):
        t = T().user("notes ...").bash(LEDGER, final_out()).bash("sha256sum /s/reply.md | cut -c1-16", "abc").say(REPLY)
        self.assertIsNone(t.hook(REPLY))



SKILLTURN = "I'm a CSM at Acme Lending (hypothetical). The new CFO said another provider offered a lower price per verification."
ROOTP = HOOK.parent.parent
LOADED = f"Base directory for this skill: {ROOTP}/skills/{SKILL0}\n\n# Skill text"


class Loop1Hook(unittest.TestCase):
    """Run 36P gate audit r01: majors 7 and 8, minors 11, 15 and 17, as tests."""
    def test_r01_7_saved_file_not_passed_to_final_is_sent_back(self):
        d = pathlib.Path(tempfile.mkdtemp())
        t = T().user("notes ...").user(LOADED).bash(f"cd {d} && python3 build.py  # writes save-plan.docx", "ok").tool("Write", {"file_path": "/w/ledger-check/reply.md", "content": REPLY}, "ok")
        (d / "save-plan.docx").write_bytes(b"PK")
        t.bash(LEDGER, final_out()).say(REPLY)
        self.assertEqual(t.hook(REPLY, cwd=str(d))["decision"], "block")
        t = T().user("notes ...").tool("Write", {"file_path": "/w/brief.md", "content": "x"}, "ok").bash(LEDGER, final_out()).say(REPLY)
        self.assertEqual(t.hook(REPLY)["decision"], "block")

    def test_r01_7_saved_file_passed_to_final_is_fine(self):
        t = T().user("notes ...").tool("Write", {"file_path": "/w/brief.md", "content": "x"}, "ok").tool("Write", {"file_path": "/w/ledger-check/user.txt", "content": "x"}, "ok")
        t.bash(LEDGER + " /w/brief.md", final_out()).say(REPLY)
        self.assertIsNone(t.hook(REPLY))

    def test_r01_8_follow_up_turn_without_the_ledger(self):
        t = T().user(SKILLTURN).user(LOADED).bash(LEDGER, final_out()).say(REPLY)
        t.user("Make it punchier and save it as plan.docx").bash("python3 make.py plan.docx", "ok").say("Done. The CFO is the blocker and will sign only after a price cut.")
        self.assertEqual(t.hook("Done. The CFO is the blocker and will sign only after a price cut.")["decision"], "block")

    def test_r01_8_skill_ran_but_the_ledger_was_skipped(self):
        long = "The new CFO is weighing the lower price per verification from another provider. " * 12
        t = T().user(SKILLTURN).user(LOADED).say(long)
        self.assertEqual(t.hook(long)["decision"], "block")

    def test_r01_8_short_chat_after_the_skill_is_left_alone(self):
        t = T().user("notes ...").user(LOADED).bash(LEDGER, final_out()).say(REPLY)
        t.user("thanks!").say("You're welcome.")
        self.assertIsNone(t.hook("You're welcome."))

    def test_r01_8_other_plugins_turns_are_left_alone(self):
        long = "Some long answer. " * 60
        t = T().user("notes ...").user("Base directory for this skill: /elsewhere/plugins/other/skills/x").say(long)
        self.assertIsNone(t.hook(long))

    def test_r01_15_multi_line_or_sort_o_after_final_is_a_change(self):
        for cmd in ["cat /s/reply.md\npython3 build.py", "sort -o /out/plan.md /out/plan.md"]:
            t = T().user("notes ...").bash(LEDGER, final_out()).bash(cmd, "").say(REPLY)
            self.assertEqual(t.hook(REPLY)["decision"], "block", cmd)

    def test_r01_17_py_launcher_run_is_seen(self):
        t = T().user("notes ...").bash(LEDGER.replace("python3 ", "py -3 "), final_out()).say("x " + REPLY)
        self.assertEqual(t.hook("x " + REPLY)["decision"], "block")
        hj = json.loads((HOOK.parent / "hooks.json").read_text(encoding="utf-8"))
        self.assertIn("py -3", hj["hooks"]["Stop"][0]["hooks"][0]["command"])

    def test_r01_11_no_environment_variable_read(self):
        src = HOOK.read_text(encoding="utf-8")
        import re
        self.assertIsNone(re.search(r"os\.environ|\bgetenv\b|gettempdir|import tempfile|, tempfile\b", src))



class Loop2Hook(unittest.TestCase):
    """Run 36P gate audit r02 majors 4 and 5, minor 8, as tests."""
    def test_r02_4_file_saved_by_a_build_script(self):
        d = pathlib.Path(tempfile.mkdtemp())
        t = T().user("notes ...").user(LOADED).tool("Write", {"file_path": str(d / "build.py"), "content": "doc.save('save-plan.docx')"}, "ok").bash(f"cd {d} && python3 build.py", "ok")
        (d / "save-plan.docx").write_bytes(b"PK")
        t.bash(LEDGER, final_out()).say(REPLY)
        self.assertEqual(t.hook(REPLY, cwd=str(d))["decision"], "block")

    def test_r02_4_old_files_in_the_folder_are_not_required(self):
        d = pathlib.Path(tempfile.mkdtemp())
        old = d / "last-week.docx"; old.write_bytes(b"PK")
        import os
        os.utime(old, (1, 1))
        t = T().user("notes ...").bash(LEDGER, final_out()).say(REPLY)
        self.assertIsNone(t.hook(REPLY, cwd=str(d)))

    def test_r02_5_short_follow_ups_with_a_claim(self):
        for reply in ["Yes. The CFO is the blocker and will sign only after a 20% price cut.", "Your new CFO has lost confidence in the verification fix and wants out."]:
            t = T().user(SKILLTURN).user(LOADED).bash(LEDGER, final_out()).say(REPLY).user("Is the CFO the blocker?").say(reply)
            self.assertEqual(t.hook(reply)["decision"], "block", reply)

    def test_r02_5_tiny_replies_pass(self):
        t = T().user("notes ...").user(LOADED).bash(LEDGER, final_out()).say(REPLY).user("thanks").say("You're welcome.")
        self.assertIsNone(t.hook("You're welcome."))

    def test_r02_m8_basename_must_match_whole(self):
        t = T().user("notes ...").tool("Write", {"file_path": "/out/plan.md", "content": "x"}, "ok").bash(LEDGER + " /out/old-plan.md", final_out()).say(REPLY)
        self.assertEqual(t.hook(REPLY)["decision"], "block")



class Loop3Hook(unittest.TestCase):
    """Run 36P round 2 CAH1 and CQB3: reading the skill's reference files was taken for saving them, so the hook asked for them in --final."""
    def test_reading_reference_files_is_not_saving(self):
        cmd = f"cd {ROOTP}/skills/{SKILL0}; ls -R; cat references/input-rules.md; cat references/health-scoring-model.md"
        t = T().user("notes ...").user(LOADED).bash(cmd, "text").bash(LEDGER, final_out()).say(REPLY)
        self.assertIsNone(t.hook(REPLY))

    def test_a_redirect_is_saving(self):
        t = T().user("notes ...").bash("echo hi > /w/plan.md", "").bash(LEDGER, final_out()).say(REPLY)
        self.assertEqual(t.hook(REPLY)["decision"], "block")
        t = T().user("notes ...").bash("python3 make.py | tee /w/brief.md", "").bash(LEDGER, final_out()).say(REPLY)
        self.assertEqual(t.hook(REPLY)["decision"], "block")



class Loop5Hook(unittest.TestCase):
    """Run 36P gate audit r03 major 6: a later turn about something else is not this plugin's to check."""
    SKILLTURN = "I'm a CSM at Acme Lending (hypothetical). The new CFO said another provider offered a lower price per verification."

    def test_r03_6_unrelated_later_turns_are_left_alone(self):
        t = T().user(self.SKILLTURN).user(LOADED).bash(LEDGER, final_out()).say(REPLY)
        t.user("What time zone is Dubai in?").say("Dubai uses Gulf Standard Time, UTC plus 4, with no daylight saving.")
        self.assertIsNone(t.hook("Dubai uses Gulf Standard Time, UTC plus 4, with no daylight saving."))
        t = T().user(self.SKILLTURN).user(LOADED).bash(LEDGER, final_out()).say(REPLY)
        t.user("rename foo to bar in app.py and fix the README").tool("Edit", {"file_path": "/w/app.py", "old_string": "foo", "new_string": "bar"}, "ok").say("Renamed foo to bar in app.py; the README needed no change.")
        self.assertIsNone(t.hook("Renamed foo to bar in app.py; the README needed no change."))

    def test_r03_6_related_follow_ups_are_still_checked(self):
        reply = "Yes. The new CFO is the blocker and will sign only after a 20% price cut per verification."
        t = T().user(self.SKILLTURN).user(LOADED).bash(LEDGER, final_out()).say(REPLY).user("Is the CFO the blocker?").say(reply)
        self.assertEqual(t.hook(reply)["decision"], "block")



class Loop6Hook(unittest.TestCase):
    """Run 36P re-check R4: real follow-ups after the skill turn are checked again."""
    CRS = ("I manage key accounts at Acme Lending (hypothetical, for a test). Account (hypothetical): a consumer lending app in the UAE using us for "
           "account verification and payouts, contract renews in 75 days. The CFO who signed us left in August.")

    def test_recheck_R4_follow_up_claim(self):
        reply = "The new CFO will renew if we match the lower price per verification."
        t = T().user(self.CRS).user(LOADED).bash(LEDGER, final_out()).say(REPLY).user("What will the CFO do?").say(reply)
        self.assertEqual(t.hook(reply)["decision"], "block")

    def test_recheck_R4_skill_asked_then_answered_next_turn(self):
        long = "Here is your save plan. Week 1: meet the new CFO and walk through July. " * 6
        t = T().user(self.CRS).user(LOADED).say("Which provider made the other offer?").user("Not sure, go ahead.").say(long)
        self.assertEqual(t.hook(long)["decision"], "block")

    def test_recheck_R4_hyphenated_file_name(self):
        d = pathlib.Path(tempfile.mkdtemp())
        t = T().user(self.CRS).user(LOADED).bash(LEDGER, final_out()).say(REPLY).user("save it as a doc").bash(f"cd {d} && python3 make.py", "ok")
        (d / "renewal-save-plan.docx").write_bytes(b"PK")
        t.say("Saved.")
        self.assertEqual(t.hook("Saved.", cwd=str(d))["decision"], "block")


if __name__ == "__main__":
    unittest.main(verbosity=2)
