#!/usr/bin/env python3
"""Run the checklist in skills/prompt-clarifier/SKILL.md on three prompts.

This does not call a model and it does not use the network. It only applies
the skill's own rule: no target means ask, a vague change means wait, a
request that already names the file, the change, and done means stay quiet.
"""
import re
import sys
import textwrap

TARGET_RE = re.compile(
    r"`([^`]+)`|(?<!\w)([A-Za-z0-9_\-./]+\.(?:js|jsx|ts|tsx|py|go|rs|css|html|md))\b"
)
SUCCESS_RE = re.compile(r"\b(done when|hotovo|tests pass|neselže)\b", re.I)
DROP = {
    "a", "an", "the", "this", "it", "to", "in", "on", "of", "and", "or",
    "fix", "make", "made", "add", "improve", "clean", "up", "faster",
    "better", "login", "please", "just", "look", "at",
}
SYMPTOM_RE = re.compile(r"\b(bug|error|401|form|query|redirect|race|password)\b", re.I)


def assess(text):
    targets = [a or b for a, b in TARGET_RE.findall(text)]
    success = SUCCESS_RE.search(text) is not None
    rest = TARGET_RE.sub(" ", text).lower()
    rest = re.sub(r"[^a-z0-9 ]+", " ", rest)
    content = [w for w in rest.split() if w not in DROP]
    change = bool(SYMPTOM_RE.search(text)) or len(content) >= 4
    if not targets:
        action = "ASK"
    elif not change or not success:
        action = "WAIT"
    else:
        action = "QUIET"
    return targets, change, success, action


CASES = [
    "fix this",
    "make auth.js faster",
    "Fix the bug in `auth.js` where login with a correct password sometimes returns 401 — looks like a race condition in token verification. Done when existing login tests pass and 10 consecutive logins don't fail once.",
]


def main():
    lines = [
        "prompt-clarifier checklist",
        "source: skills/prompt-clarifier/SKILL.md",
        "model: none    network: none",
        "",
    ]
    failed = False
    for i, prompt in enumerate(CASES, 1):
        targets, change, success, action = assess(prompt)
        shown = textwrap.wrap(prompt, width=72) or [""]
        lines.append(f"{i}  {shown[0]}")
        for extra in shown[1:]:
            lines.append(f"   {extra}")
        lines.append("   target   " + (", ".join(targets) if targets else "missing"))
        lines.append("   change   " + ("present" if change else "missing"))
        lines.append("   success  " + ("present" if success else "missing"))
        lines.append(f"   action   {action}")
        if action == "ASK":
            reply = "Which file do you mean? I get that you want it fixed — just need to know where."
            lines.append(f"   reply    {reply}")
            invented = TARGET_RE.search(reply) is not None
            lines.append("   invented " + ("yes" if invented else "no"))
            if invented or targets:
                failed = True
        elif action == "WAIT":
            lines.append("   note     target is known, the change is not. It does not start.")
            if not targets or change:
                failed = True
        else:
            if not targets or not change or not success:
                failed = True
        lines.append("")
    lines.append("result  vague prompt did not invent a file; the specific one stayed quiet")
    text = "\n".join(lines).rstrip() + "\n"
    sys.stdout.write(text)
    if failed or "action   ASK" not in text or "action   WAIT" not in text or "action   QUIET" not in text:
        return 1
    if "invented no" not in text:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
