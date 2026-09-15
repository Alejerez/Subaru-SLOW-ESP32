#!/usr/bin/env python3
"""Check that the text drawn inside the figures still matches the layout data.

The figures are drawn by hand-written code, so their labels can drift away from
the component tables the boards are actually built from.  That is exactly what
happened between v0.1.5 and v0.1.8: the layout moved to SB1100, P6KE20A, 100 uF
reservoirs and a 3.3 V Node B, while ten figures went on naming SS34, SMAJ18A,
470 uF and a 5 V rail.  Prose is reviewed; figure strings are not.

Two checks:

  1. retired tokens - a part or a number the project has superseded must not
     appear in any figure label at all.
  2. reference/value agreement - where a label names a component reference
     together with a value, that value must match the layout's part string for
     that reference on that node.

Run directly, or let generate_diagrams.py run it.
"""
import ast
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent
FILES = ("generate_diagrams.py", "node_a_build.py", "node_b_build.py")

# 1 -- tokens the project has retired.  Anything here is a defect wherever it is
# drawn; the prose may still discuss them (README lists SS34 as the SMD
# alternative), but a *label* naming one is out of date.
RETIRED = {
    "SS34": "superseded by SB1100 (DO-41, 100 V, 0.8 mm leads)",
    "SMAJ18A": "superseded by P6KE20A (DO-15, clamps at 27.7 V)",
    "470 µF": "exceeds the Recom's 220 µF maximum capacitive load",
    "470u": "exceeds the Recom's 220 µF maximum capacitive load",
    "umbilical 6p": "the umbilical is five wires",
    "six-wire umbilical": "the umbilical is five wires",
    "R-78E5.0": None,        # allowed on Node A only -- handled below
}
NODE_A_ONLY = {"R-78E5.0"}

# 2 -- a reference followed by a value, e.g. "C1 · 100 µF / 35 V" or "D2 P6KE20A"
REF_VALUE = re.compile(
    r"\b([CDRUJ]\d{1,2})\b[\s·:]*"
    r"((?:\d+(?:\.\d+)?\s*(?:[munpk]?[FΩR]|µF|nF|uF|kΩ|k\b))"
    r"|(?:SB\d{4}|P6KE\d+A|SMAJ\d+A|SS\d{2}|BAT\d{2}|L9637D|R-78E\d\.\d))")

UNIT = {"µf": "u", "uf": "u", "nf": "n", "pf": "p", "ω": "r", "r": "r", "k": "k", "f": ""}


def norm(value):
    """'100 µF' -> '100u', '20 kΩ' -> '20k', 'SB1100' -> 'sb1100'."""
    v = value.strip().lower().replace(" ", "")
    m = re.fullmatch(r"(\d+(?:\.\d+)?)(µf|uf|nf|pf|kω|k|ω|r|f)", v)
    if m:
        num = m.group(1)
        if num.endswith(".0"):
            num = num[:-2]
        return num + UNIT.get(m.group(2), m.group(2))
    return v


def layout_parts():
    """ref -> {normalised value strings} per node, straight from the build data."""
    sys.path.insert(0, str(ROOT))
    import node_a_build as na
    import node_b_build as nb
    out = {"a": {}, "b": {}}
    def add(bucket, ref, part):
        toks = {norm(t) for t in re.split(r"[ /]", part) if t}
        toks.add(norm(part.split()[0]))
        out[bucket].setdefault(ref, set()).update(toks)
    for ref, part, _shape, _pins in na.COMPONENTS:
        add("a", ref, part)
    for board in nb.BOARDS.values():
        for ref, part, _shape, _pins in board["components"]:
            add("b", ref, part)
    return out


def figure_strings():
    """(file, function, string) for every literal inside a figure function."""
    for fname in FILES:
        tree = ast.parse((ROOT / fname).read_text())
        for node in ast.walk(tree):
            if not isinstance(node, ast.FunctionDef):
                continue
            if not (node.name.startswith("fig") or node.name in ("_grid_plan", "budget")):
                continue
            for n in ast.walk(node):
                if isinstance(n, ast.Constant) and isinstance(n.value, str):
                    yield fname, node.name, n.value


def _is_history(text):
    """A label may name a retired part to explain why it was retired."""
    return any(m in text.lower() for m in
               ("the limit", "twice the", "not 470", "was 470", "superseded",
                "would only ever", "instead of"))


def node_of(fname, func):
    if fname == "node_a_build.py":
        return "a"
    if fname == "node_b_build.py":
        return "b"
    return "a" if "node_a" in func else "b" if "node_b" in func else None


def main():
    parts = layout_parts()
    bad = []
    for fname, func, text in figure_strings():
        node = node_of(fname, func)
        for token, why in RETIRED.items():
            if token in text and not _is_history(text):
                if token in NODE_A_ONLY and node == "a":
                    continue
                bad.append(f"{func}: retired token {token!r} in {text[:60]!r}"
                           + (f" — {why}" if why else " — Node A only"))
        if node is None:
            continue
        for ref, value in REF_VALUE.findall(text):
            known = parts[node].get(ref)
            if known is None:
                continue
            nv = norm(value)
            if nv not in known and not any(k.startswith(nv) for k in known):
                bad.append(f"{func}: {ref} is drawn as {value!r} but the "
                           f"{node.upper()} layout says {sorted(known)}")
    if bad:
        print("FIGURE TEXT DOES NOT MATCH THE LAYOUT:")
        for b in sorted(set(bad)):
            print("  -", b)
        return 1
    print("figure text: no retired parts, and every labelled value matches the layout")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
