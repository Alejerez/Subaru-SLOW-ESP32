#!/usr/bin/env python3
"""Check every relative link and heading anchor in the Markdown.

A `](../foo.md#some-heading)` that points at a heading which has been renamed
still renders as a link on GitHub; it just lands at the top of the page. Nothing
warns you. This walks every `.md` file in the repository, reproduces GitHub's
heading-slug rules (lower-case, punctuation dropped, spaces to hyphens, a `-1`,
`-2`, ... suffix on repeats) and reports:

  * links to files that do not exist,
  * links to anchors that do not exist in the target file,
  * images whose file is missing.

Exits non-zero if anything is broken, so it can gate a commit.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\]\(([^)\s]+)\)")
HEAD = re.compile(r"^(#{1,6})\s+(.*)")


def slug(heading):
    h = heading.strip().lower()
    h = re.sub(r"`([^`]*)`", r"\1", h)                  # code spans
    h = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", h)      # links in headings
    h = re.sub(r"[*_]", "", h)                          # emphasis
    h = "".join(c for c in h if c.isalnum() or c in " -_")
    return h.replace(" ", "-")


def anchors(path):
    seen, out = {}, set()
    for line in path.read_text(encoding="utf-8").splitlines():
        m = HEAD.match(line)
        if not m:
            continue
        s = slug(m.group(2))
        n = seen.get(s, 0)
        seen[s] = n + 1
        out.add(s if n == 0 else f"{s}-{n}")
    return out


def main():
    files = [f for f in ROOT.rglob("*.md") if ".git" not in f.parts]
    heads = {f.resolve(): anchors(f) for f in files}
    bad = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        for m in LINK.finditer(text):
            target = m.group(1)
            if target.startswith(("http", "mailto:", "#!")):
                continue
            path, _, frag = target.partition("#")
            tf = (f.parent / path).resolve() if path else f.resolve()
            rel = f.relative_to(ROOT)
            if path and not tf.exists():
                bad.append(f"{rel}: missing file -> {target}")
                continue
            if not frag or tf.suffix != ".md":
                continue
            if frag not in heads.get(tf, set()):
                bad.append(f"{rel}: missing anchor -> {target}")
    for b in sorted(set(bad)):
        print("  -", b)
    n = len(set(bad))
    print(f"{n} broken link{'' if n == 1 else 's'}" if n
          else "links: every relative path and every anchor resolves")
    return 1 if n else 0


if __name__ == "__main__":
    raise SystemExit(main())
