"""delivery_check.py: the plugin's Stop hook (Claude Code only). When one of this plugin's skills ran its claim ledger
(scripts/claim_ledger.py) in the current turn, it checks, before Claude stops, that the reply Claude is about to send is exactly the text the
ledger last checked, and sends Claude back with the reason when it is not:
  1. the last claim_ledger.py run of the turn is a passing --final run (its first line: "claim_ledger --final: PASS, reply digest <d>");
  2. no tool that can change a file ran after it (Write, Edit, MultiEdit, NotebookEdit, or a shell command that is not a plain read);
  3. the reply's digest (the ledger's digest rule: line ends and trailing spaces ignored) is that digest. The reply is all the text Claude
     wrote after that run, joined, so a line before the checked text counts too.
Only a python run of a claim_ledger.py with --user, whose output carries this ledger's summary line or whose path names one of this plugin's skills, starts the check; a turn without one
is left alone, so the hook does nothing in any other conversation. It sends Claude back at most twice per turn, then lets the reply through.
What it guarantees: the final reply of the turn (the result of `claude -p`, and the last message in interactive use) and the saved files
the --final run checked. In interactive use the screen also shows any text written earlier in the turn; the skills write none.

What it reads: the Stop hook input (on standard input) and the session transcript file it names, both on this computer. What it writes: one
small counter file per session in a folder next to that transcript (b2b-sales-enablement-claim-ledger/), so it never sends Claude back more than twice.
Run 36P loop 1: it also sends Claude back when a file saved in the turn was not checked by the --final run, and, in a conversation where a
skill of this plugin was loaded, when a turn saves a deliverable or writes more than a short line without running the ledger.
Loop 2: a file saved in the turn is also found by its change time in the working folder (names only, three levels down; it opens none).
It sends nothing anywhere, makes no network call and reads no environment variable. Standard library only. It always exits 0; on any error it
lets the reply through. (Run 36P: the run 35C hook of b2b-icp-and-customer-insight, with this plugin's name and skills.)
"""
import hashlib, json, os, re, sys

MARK = "[b2b-sales-enablement claim ledger delivery check]"
MAX_SEND_BACKS = 2
READ_ONLY = re.compile(r"^\s*(cat|type|ls|dir|head|tail|wc|sha256sum|md5sum|echo|pwd|cut|sort|grep|Get-Content|gc)\b(?![^>|;&]*\s-o\b)[^>|;&]*$")
DELIVERABLE = re.compile(r"[\w./\\:~-]*[\w-]\.(?:md|txt|csv|tsv|json|html|docx|pptx|xlsx)\b", re.I)
WORKING = re.compile(r"ledger-check|(^|[/\\])(user|reply|page-\d+|search-\d+|script-\d+)\.(md|txt)$", re.I)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # this plugin's folder: a skill loaded from it names this path
LONG_REPLY = 50   # loop 2 (gate audit r02 major 5): in a conversation using these skills, any reply past a short line goes through the ledger
CHANGERS = ("Write", "Edit", "MultiEdit", "NotebookEdit")
SHELLS = ("Bash", "PowerShell")
SKILLS = ('competitive-intelligence', 'meeting-prep-debrief', 'sales-proposal-builder')
RUN = re.compile(r"\b(?:python[0-9.]*(\.exe)?|py(?:\.exe)?(?:\s+-3(?:\.\d+)?)?)\b[^|;&\n]*?(?<![\w-])claim_ledger\.py\b[^|;&\n]*--user\b")


def digest(text):
    t = "\n".join(l.rstrip() for l in (text or "").replace("\r\n", "\n").strip().splitlines())
    return hashlib.sha256(t.encode("utf-8")).hexdigest()[:16]


def body(c):
    b = c.get("content")
    b = "\n".join(y.get("text", "") for y in b if isinstance(y, dict)) if isinstance(b, list) else (b or "")
    return b.replace("\r\n", "\n")


def is_prompt(m):
    """A message the person typed (not a tool result, a compaction summary or any hook's feedback)."""
    if m.get("type") != "user" or m.get("isMeta") or m.get("isCompactSummary") or m.get("isVisibleInTranscriptOnly"):
        return False
    c = (m.get("message") or {}).get("content")
    if isinstance(c, list):
        if any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c):
            return False
        c = " ".join(x.get("text", "") for x in c if isinstance(x, dict))
    return isinstance(c, str) and MARK not in c and not c.lstrip().startswith(("Stop hook feedback", "This session is being continued"))


def turn(path):
    """The messages of the current turn: everything after the last message the person typed."""
    msgs, prompts = [], 0
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if isinstance(m, dict):
                if is_prompt(m):
                    msgs, prompts = [], prompts + 1
                else:
                    msgs.append(m)
    return msgs, prompts


def read_only(cmd):
    parts = [x for x in re.split(r"\n|\|", str(cmd)) if x.strip()]
    return bool(parts) and all(READ_ONLY.match(x) for x in parts)


def written(name, ti):
    """Deliverable files a tool call writes: Write, Edit or MultiEdit file paths; files a shell command names that is not a plain read."""
    if name in CHANGERS:
        f = str(ti.get("file_path") or ti.get("notebook_path") or "")
        return [f] if f and DELIVERABLE.fullmatch(f.strip()) and not WORKING.search(f) and not os.path.abspath(f).startswith(ROOT) else []
    if name in SHELLS:
        cmd = str(ti.get("command", ""))
        if read_only(cmd) or RUN.search(cmd):
            return []
        # loop 3: a shell command saves a file only through a redirect, tee or an output option; a file a script saves is found by the folder
        # scan; the plugin's own files (its references) are never deliverables
        targets = re.findall(r"(?:>>?|\btee(?:\s+-a)?|(?:^|\s)(?:-o|--output|--out)(?:=|\s+))\s*['\"]?([^\s'\";|&>]+)", cmd)
        return [f for f in targets if DELIVERABLE.fullmatch(f) and not WORKING.search(f) and not os.path.abspath(f).startswith(ROOT)]
    return []


def turn_start(path):
    """Seconds since the epoch when the person's last message was written (its transcript timestamp), or an hour ago when there is none."""
    import datetime, time
    last = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                m = json.loads(line)
            except ValueError:
                continue
            if isinstance(m, dict) and is_prompt(m) and m.get("timestamp"):
                last = m["timestamp"]
    if last:
        try:
            return datetime.datetime.fromisoformat(str(last).replace("Z", "+00:00")).timestamp() - 2
        except ValueError:
            pass
    return time.time() - 3600


def saved_in_folder(cwd, since):
    """Deliverable files (Word, PowerPoint, Excel, Markdown, text, CSV, HTML) in the working folder, three levels down, changed since the turn
    began: a file a build script saved is seen even when its name is on no command line (loop 2, gate audit r02 major 4)."""
    out, seen = [], 0
    if not cwd or not os.path.isdir(cwd) or os.path.abspath(cwd).startswith(ROOT):
        return out
    base = os.path.abspath(cwd)
    for d, dirs, files in os.walk(base):
        dirs[:] = [x for x in dirs if not x.startswith((".", "node_modules", "__pycache__", "ledger-check")) and d.count(os.sep) - base.count(os.sep) < 3]
        for fn in files:
            seen += 1
            if seen > 3000:
                return out
            p = os.path.join(d, fn)
            if DELIVERABLE.fullmatch(fn) and not WORKING.search(p):
                try:
                    if os.path.getmtime(p) >= since:
                        out.append(p)
                except OSError:
                    pass
    return out


def skill_loaded(path):
    """True when a skill of this plugin was loaded in this session (its folder named in the transcript, or a Skill call with its name)."""
    plug = os.path.basename(ROOT)
    marks = (os.path.join(ROOT, "skills"), ROOT.replace("\\", "/") + "/skills")
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            if any(m in line for m in marks) or f'"skill": "{plug}:' in line or f'"skill":"{plug}:' in line:
                return True
    return False


def decide(inp):
    msgs, prompts = turn(inp["transcript_path"])
    inp["_turn"] = prompts
    calls, results, order, texts, feedback = {}, {}, [], [], -1
    for m in msgs:
        c = (m.get("message") or {}).get("content")
        if m.get("type") == "user" and not (isinstance(c, list) and any(isinstance(x, dict) and x.get("type") == "tool_result" for x in c)):
            feedback = len(order)   # hook feedback or any other message in the turn: the reply starts after it
            texts = [(n, s) for n, s in texts if n > feedback]
            if isinstance(c, list):
                continue
        if not isinstance(c, list):
            continue
        for x in c:
            if not isinstance(x, dict):
                continue
            if x.get("type") == "tool_use":
                calls[x.get("id")] = (x.get("name"), x.get("input") or {})
                order.append(x.get("id"))
            elif x.get("type") == "tool_result" and x.get("tool_use_id") in calls:
                results[x.get("tool_use_id")] = body(x)
            elif x.get("type") == "text" and m.get("type") == "assistant":
                texts.append((len(order), x.get("text", "")))
    led = [i for i in order if calls[i][0] in SHELLS and RUN.search(str(calls[i][1].get("command", "")))
           and (re.search(r"^claim_ledger(?: --final)?: ", results.get(i, ""), re.M) or any(s in str(calls[i][1].get("command", "")) for s in SKILLS))]
    if not led:
        # run 36P loop 1 (gate audit r01 major 8): a turn of a conversation where this plugin's skill was loaded, that writes a deliverable
        # or a long reply, must end on the ledger too (a follow-up such as "make it punchier and save it as a .docx")
        files = [f for i in order for f in written(*calls[i])] + saved_in_folder(inp.get("cwd"), turn_start(inp["transcript_path"]))
        reply = "\n\n".join(x for _, x in texts) or (inp.get("last_assistant_message") or "")
        claimy = len(reply) >= LONG_REPLY or (len(reply) >= 40 and re.search(r"\d", reply))
        if (files or claimy) and skill_loaded(inp["transcript_path"]):
            return ("A skill of this plugin is in use in this conversation, and this answer " + ("saves " + ", ".join(sorted(set(files))[:4]) if files else "is long")
                    + " without the claim ledger. Run the skill's last step (\"Claim ledger and delivery\"): save user.txt, the pages and searches, "
                    "write reply.md, run claim_ledger.py on reply.md and every saved file until it exits 0, then run it with --final as your last "
                    "tool call and send exactly the text it prints.")
        return None   # this plugin's ledger did not run in this turn: not ours to check
    last = led[-1]
    out = results.get(last, "")
    begin = re.search(r"^claim_ledger --final: PASS, reply digest ([0-9a-f]{16})$", out, re.M) or re.search(r"^=== BEGIN CHECKED REPLY ([0-9a-f]{16}) ===$", out, re.M)
    if "--final" not in str(calls[last][1].get("command", "")) or not begin:
        return ("The claim ledger ran in this turn, but its last run was not a passing --final run. Fix every NEEDS line, then run "
                "claim_ledger.py --final with the same files as your last tool call (no pipe, no grep), and send as your whole reply exactly "
                "the text between its BEGIN CHECKED REPLY and END CHECKED REPLY lines.")
    for i in order[order.index(last) + 1:]:
        name, ti = calls[i]
        if not (name in CHANGERS or (name in SHELLS and not read_only(ti.get("command", "")))):
            continue
        return (f"A tool that can change a file ({name}) ran after the last claim_ledger.py --final run, so the checked text may not be what "
                "you deliver. Run claim_ledger.py --final again on the reply file and every saved file as your last tool call, and send exactly "
                "the text between its BEGIN CHECKED REPLY and END CHECKED REPLY lines.")
    final_cmd = str(calls[last][1].get("command", ""))
    checked = {os.path.basename(x.strip("'\"").replace("\\", "/")) for x in re.split(r"\s+", final_cmd)}   # whole file names (r02 minor 8)
    saved = [f for i in order[:order.index(last)] for f in written(*calls[i])] + saved_in_folder(inp.get("cwd"), turn_start(inp["transcript_path"]))
    missing = sorted({f for f in saved if os.path.basename(f.replace("\\", "/")) not in checked})
    if missing:   # run 36P loop 1 (gate audit r01 major 7): every file saved in this turn is checked by the --final run
        return ("This turn saved " + ", ".join(missing[:4]) + ", but the last claim_ledger.py --final run did not check it. Run --final again "
                "with the reply file and every saved file (Word, PowerPoint and Excel files included) as your last tool call, and send exactly "
                "the text between its BEGIN CHECKED REPLY and END CHECKED REPLY lines.")
    want = begin.group(1)
    k = order.index(last) + 1
    after = [x for n, x in texts if n >= k]   # texts written before the last feedback message were dropped above
    reply = "\n\n".join(after) if after else (inp.get("last_assistant_message") or "")
    if len(after) == 1 and inp.get("last_assistant_message") is not None:
        reply = inp["last_assistant_message"]
    if digest(reply) == want:
        return None
    return (f"Your reply is not the text the claim ledger checked (digest {want}). Send as your whole reply exactly the text between "
            f"=== BEGIN CHECKED REPLY {want} === and === END CHECKED REPLY {want} === in the last claim_ledger.py --final output: nothing "
            "before it (no summary, no 'here it is'), nothing after it, no word or line changed. To say anything else, put it in the reply "
            "file and run --final again.")


def main():
    try:
        raw = sys.stdin.buffer.read() if hasattr(sys.stdin, "buffer") else sys.stdin.read().encode("utf-8")
        inp = json.loads(raw.decode("utf-8", errors="replace") or "{}")
        if not isinstance(inp, dict) or not inp.get("transcript_path"):
            return 0
        reason = decide(inp)
        # the counter lives next to the session transcript, in Claude Code's own folder for this project (no environment variable read)
        d = os.path.join(os.path.dirname(os.path.abspath(inp["transcript_path"])), "b2b-sales-enablement-claim-ledger")
        sid = re.sub(r"[^A-Za-z0-9_-]", "_", str(inp.get("session_id") or "nosession"))[:80]
        p = os.path.join(d, sid + ".json")
        if reason is None:
            if os.path.exists(p):
                os.remove(p)   # the turn ends cleanly: the next turn starts a new count
            return 0
        os.makedirs(d, mode=0o700, exist_ok=True)
        if os.path.islink(d) or os.path.islink(p):
            return 0
        try:
            with open(p, encoding="utf-8") as f:
                st = json.load(f)
            n = int(st.get("n", 0)) if st.get("turn") == inp["_turn"] else 0
        except (OSError, ValueError, AttributeError, TypeError):
            n = 0
        if n >= MAX_SEND_BACKS:
            return 0
        fd = os.open(p, os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump({"turn": inp["_turn"], "n": n + 1}, f)
        print(json.dumps({"decision": "block", "reason": f"{MARK} {reason}"}))
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
