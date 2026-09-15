"""Node A build figures: hole-by-hole placement and solder-side jumper routing.

Imported by generate_diagrams.py. The board is 11 x 27 holes (3 x 7 cm, 2.54 mm
pitch). Columns are lettered A..L with I omitted so it cannot be read as 1; rows
are numbered 1..27 with row 1 at the USB end.
"""
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from diagram_lib import (  # noqa: E402
    Svg, tw, BG, PANEL, PANEL_2, EDGE, FG, FG_DIM, FG_FAINT,
    V12, V5, V33, GND, SIG, RADIO, NODE_A, NODE_B, NODE_C, WARN,
)

import board_lib as BL                                              # noqa: E402
from board_lib import COLS, ci, ri, ESP_L, ESP_R, body_box, check_bodies  # noqa: E402

NROW = 27
PAD = "#7a5334"               # copper ring
PAD_IN = "#1c1008"

# --- nets: key -> (label, physical wire colour, figure colour) -----------------
NETS = {
    "V12":  ("+12 V IG (pre-D1)", "AMARILLO", V12),
    "VBAT": ("VBAT (post-D1)",    "AMARILLO", V12),
    "GND":  ("GND",               "NEGRO",    GND),
    "V5":   ("+5 V",              "VERDE",    NODE_A),
    "V33":  ("+3.3 V",            "ROJO",     V33),
    "IN1":  ("IN1 -> relay CH1",  "AZUL",     SIG),
    "IN2":  ("IN2 -> relay CH2",  "AZUL",     SIG),
    "SW1":  ("SW1, raw from i78", "BLANCO",   FG),
    "SW1D": ("SW1 at GPIO27",     "BLANCO",   FG),
    "LED1": ("LED1, out to i78",  "BLANCO",   FG),
    "LED1D": ("LED1 at GPIO33",   "BLANCO",   FG),
}

ESP_USED = {"A1": "V5", "A2": "GND", "A6": "SW1D", "A7": "IN2", "A8": "IN1",
            "A9": "LED1D", "L1": "V33"}

# --- discrete components: ref, part, shape, [(hole, pin, net)] ----------------
COMPONENTS = [
    ("J1", "IG in · 2p",      "hdr90", [("A27", "1 +12V", "V12"), ("B27", "2 GND", "GND")]),
    ("J2", "relay · 5p",      "hdr90", [("D27", "JD-VCC", "V5"), ("E27", "GND", "GND"),
                                        ("F27", "IN1", "IN1"), ("G27", "IN2", "IN2"),
                                        ("H27", "VCC", "V33")]),
    ("J3", "OEM switch · 2p", "hdr90", [("K27", "SW1", "SW1"), ("L27", "LED1", "LED1")]),
    ("D1", "SB1100",      "ax2f", [("A21", "A", "V12"), ("C21", "K", "VBAT")]),
    ("D2", "P6KE20A",     "ax3f", [("A23", "K", "VBAT"), ("D23", "A", "GND")]),
    ("U1", "R-78E5.0-1.0", "sip3", [("G21", "1 +Vin", "VBAT"), ("H21", "2 GND", "GND"),
                                    ("J21", "3 +Vout", "V5")]),
    ("C2", "100n X7R 50V", "ax2f", [("A19", "a", "VBAT"), ("C19", "b", "GND")]),
    ("C1", "100u 35V 105C", "rad", [("F25", "+", "VBAT"), ("H25", "-", "GND")]),
    ("C3", "100u 16V 105C", "rad", [("J25", "+", "V5"), ("L25", "-", "GND")]),
    ("C4", "100n X7R", "ax2f", [("A25", "a", "V5"), ("C25", "b", "GND")]),
    ("C11", "100n X7R", "ax2f", [("B1", "a", "V5"), ("B3", "b", "GND")]),
    ("R9", "1k", "ax2f", [("C6", "in", "SW1"), ("E6", "out", "SW1D")]),
    ("C12", "100n X7R", "ax2f", [("E8", "a", "SW1D"), ("G8", "b", "GND")]),
    ("R8", "0R link", "ax2f", [("C10", "GPIO side", "LED1D"), ("E10", "out", "LED1")]),
]

# body heights in mm, for the parts that sit under the socketed module
HEIGHTS = {"C11": 3.2, "R9": 3.2, "C12": 3.2, "R8": 3.2, "C2": 3.2,
           "D1": 2.6, "D2": 3.6, "C4": 3.2, "C1": 11.0, "C3": 11.0, "U1": 10.4}
BODY_OVERRIDE = {"C1": (6.3, 6.3, "round"), "C3": (6.3, 6.3, "round")}

TIE_POINTS = {"C27": "GND"}   # ground spine junction, keeps three leads off D2's pad

RUNS = [
    ("Y1", "V12",  ["A27", "A21"],                 "J1 -> D1 anode"),
    ("Y2", "VBAT", ["C21", "A23", "A19"],          "D1 K -> D2 K -> C2"),
    ("Y3", "VBAT", ["A23", "G21", "F25"],          "-> U1 +Vin -> C1 +"),
    ("N1", "GND",  ["B27", "C27", "D23", "C19"],   "J1 GND -> spine -> D2 A -> C2"),
    ("N2", "GND",  ["C27", "E27"],                 "spine -> relay GND"),
    ("N3", "GND",  ["C19", "H21"],                 "-> U1 GND"),
    ("N4", "GND",  ["H21", "H25", "L25"],          "-> C1 -, C3 -"),
    ("N5", "GND",  ["H21", "C25"],                 "-> C4"),
    ("N6", "GND",  ["H21", "A2", "B3"],            "-> ESP32 GND, C11"),
    ("N7", "GND",  ["A2", "G8"],                   "-> C12"),
    ("G1", "V5",   ["J21", "J25"],                 "U1 out -> C3 +"),
    ("G2", "V5",   ["J21", "A25"],                 "-> C4"),
    ("G3", "V5",   ["J21", "D27"],                 "-> relay JD-VCC"),
    ("G4", "V5",   ["J21", "B1", "A1"],            "-> C11 -> ESP32 VIN"),
    ("R1w", "V33", ["L1", "H27"],                  "ESP32 3V3 -> relay VCC"),
    ("BL1", "IN1", ["A8", "F27"],                  "GPIO25 -> relay IN1"),
    ("BL2", "IN2", ["A7", "G27"],                  "GPIO26 -> relay IN2"),
    ("W1", "SW1",  ["K27", "C6"],                  "i78 pin 1 -> R9"),
    ("W2", "SW1D", ["E6", "E8"],                   "R9 -> C12"),
    ("W3", "SW1D", ["E8", "A6"],                   "-> GPIO27"),
    ("W4", "LED1D", ["A9", "C10"],                 "GPIO33 -> R8"),
    ("W5", "LED1", ["E10", "L27"],                "R8 -> i78 pin 8"),
]


# --- helpers ------------------------------------------------------------------
BOARD = {"key": "node-a", "esp": True, "nrow": NROW}
LOW_PROFILE = {"ax1f", "ax2f", "ax3f"}
MOUNT = {"hdr90": "90° header, edge", "vert": "standing, 1 pitch",
         "ax2f": "axial, flat, 2 pitches", "ax3f": "axial, flat, 3 pitches",
         "rad": "radial, 2 pitches", "sip3": "SIP3, three in a row"}


def bodies():
    return {ref: body_box(ref, sh, pins, BODY_OVERRIDE.get(ref))
            for ref, _p, sh, pins in COMPONENTS}


def check():
    """Fail loudly on a placement that cannot be built."""
    used = {}
    for ref, _p, shape, pins in COMPONENTS:
        for h, _pin, net in pins:
            assert h[0] in COLS and 1 <= ri(h) <= NROW, f"{ref}: hole {h} off the board"
            assert h not in used, f"{ref} and {used[h]} both claim hole {h}"
            assert net in NETS, f"{ref}: unknown net {net}"
            used[h] = ref
        if any(ri(h) <= 18 for h, *_ in pins):
            assert shape in LOW_PROFILE, (
                f"{ref} sits under the ESP32 (rows 1-18) but is {shape}, not flat")
        for h, *_ in pins:
            assert not (16 <= ri(h) <= 18), f"{ref}: {h} is in the antenna rows 16-18"
    for h in [f"A{r}" for r in range(1, 16)] + [f"L{r}" for r in range(1, 16)]:
        if h in used:
            raise AssertionError(f"{used[h]} sits on ESP32 header hole {h}")
    netof = {h: n for _r, _p, _s, pins in COMPONENTS for h, _pin, n in pins}
    netof.update(ESP_USED)
    netof.update(TIE_POINTS)
    for rid, net, holes, _note in RUNS:
        for h in holes:
            assert h in netof, f"run {rid}: {h} is not a component pad"
            # No V12/VBAT exemption: a run that bridges D1 would defeat the
            # reverse-polarity protection silently, and used to pass.
            assert netof[h] == net, (
                f"run {rid} ({net}) lands on {h}, which is net {netof[h]}")
    reached = {h for _i, _n, hs, _x in RUNS for h in hs}
    for h, n in netof.items():
        if h[0] in "AL" and ri(h) <= 15 and h not in ESP_USED:
            continue
        if h in TIE_POINTS:
            continue
        assert h in reached, f"pad {h} ({n}) is not connected by any run"
    check_bodies(BOARD, bodies(), HEIGHTS)
    return used


def run_length(holes):
    """Manhattan length in mm plus 12 mm of slack for stripping and bends."""
    mm = 0.0
    for a, b in zip(holes, holes[1:]):
        mm += (abs(ci(a) - ci(b)) + abs(ri(a) - ri(b))) * 2.54
    return mm + 12


# --- routing ------------------------------------------------------------------
def _used_pads():
    u = set()
    for _r, _p, _s, pins in COMPONENTS:
        u |= {h for h, _pin, _n in pins}
    u |= set(TIE_POINTS)
    u |= {f"A{r}" for r in range(1, 16)} | {f"L{r}" for r in range(1, 16)}
    return u


def _path_cost(path, used):
    """How many occupied pads a candidate path runs over, excluding its ends."""
    return sum(1 for h in path[1:-1] if h in used)


def _leg(a, b, used):
    """One orthogonal L between two holes, choosing the corner that crosses least."""
    ca, ra, cb, rb = ci(a), ri(a), ci(b), ri(b)
    if ca == cb or ra == rb:
        return [a, b]
    v_first = [a, f"{COLS[ca]}{rb}", b]        # down/up the source column, then across
    h_first = [a, f"{COLS[cb]}{ra}", b]        # across the source row, then down/up
    def cells(p):
        out = []
        for x, y in zip(p, p[1:]):
            cx, rx, cy, ry = ci(x), ri(x), ci(y), ri(y)
            if cx == cy:
                out += [f"{COLS[cx]}{r}" for r in range(min(rx, ry), max(rx, ry) + 1)]
            else:
                out += [f"{COLS[c]}{rx}" for c in range(min(cx, cy), max(cx, cy) + 1)]
        return out
    cv, ch = _path_cost(cells(v_first), used), _path_cost(cells(h_first), used)
    return v_first if cv <= ch else h_first


def route(holes):
    used = _used_pads()
    pts = [holes[0]]
    for a, b in zip(holes, holes[1:]):
        pts += _leg(a, b, used)[1:]
    return pts


ROUTE_VIA = {"W2": ["B9", "B18", "L18"]}   # keeps LED1 clear of the right-hand header


def route_pts(rid, holes):
    via = ROUTE_VIA.get(rid)
    seq = [holes[0]] + via + holes[1:] if via else holes
    return route(seq)


# --- drawing ------------------------------------------------------------------
P = 28
PR, PRI = 8.0, 3.0


def _xy(x0, y0, hole, mirror=False):
    c, r = ci(hole), ri(hole)
    if mirror:
        c = len(COLS) - 1 - c
    return x0 + c * P, y0 + (r - 1) * P


def _board(s, x0, y0, mirror, title, num_off=30):
    w, h = (len(COLS) - 1) * P, (NROW - 1) * P
    s.rect(x0 - 14, y0 - 14, w + 28, h + 28, fill=PANEL, stroke=EDGE, sw=1.6, r=6)
    order = list(reversed(COLS)) if mirror else list(COLS)
    for i, L in enumerate(order):
        for t in (y0 - 26, y0 + h + 34):
            s.text(x0 + i * P, t, L, size=11.5, fill=FG_DIM, anchor="middle", weight=700)
    for r in range(1, NROW + 1):
        for t, an in ((x0 - num_off, "right"), (x0 + w + num_off, "start")):
            s.text(t, y0 + (r - 1) * P + 4, str(r), size=10.5, fill=FG_FAINT, anchor=an)
    for i in range(len(COLS)):
        for r in range(1, NROW + 1):
            cx, cy = x0 + i * P, y0 + (r - 1) * P
            s.dot(cx, cy, PR, PAD)
            s.dot(cx, cy, PRI, PAD_IN)
    s.text(x0 - 14, y0 - 48, title, size=13, fill=FG, weight=700)
    return w, h


MM = P / 2.54          # px per mm


def fig12_node_a_placement():
    s = Svg(1460, 1070)
    s.text(40, 44, "NODE A  ·  COMPONENT SIDE  —  where each part goes", size=15, fill=FG,
           weight=700)
    s.text(40, 64, "11 × 27 holes at 2.54 mm · looking down from above · this is the side the "
                   "parts sit on", size=12, fill=FG_FAINT)

    x0, y0 = 250, 230
    w, h = _board(s, x0, y0, False, "TOP VIEW  ·  column A on the LEFT", num_off=78)

    mx0, mx1 = x0 - 14, x0 + w + 14
    my0, my1 = y0 - 3.1 * P, y0 + 17.1 * P
    s.rect(mx0, my0, mx1 - mx0, my1 - my0, fill=NODE_B, stroke=NODE_B, sw=1.6, r=8, op=0.10)
    s.rect(mx0, my0, mx1 - mx0, my1 - my0, fill="none", stroke=NODE_B, sw=1.6, r=8, dash="6 5")
    s.text((mx0 + mx1) / 2, my0 - 14, "ESP32 DevKit V1 — USB overhangs this edge",
           size=11, fill=NODE_B, anchor="middle", weight=700)
    s.rect(mx0 + 6, y0 + 15.5 * P, mx1 - mx0 - 12, 2.2 * P, fill=NODE_B, stroke="none",
           r=5, op=0.12)
    ty = y0 + 16.6 * P
    s.rect((mx0 + mx1) / 2 - 118, ty - 13, 236, 20, fill=BG, stroke="none", r=4, op=0.82)
    s.text((mx0 + mx1) / 2, ty + 2, "antenna end — keep rows 16-18 empty",
           size=10.5, fill=NODE_B, anchor="middle", weight=700)

    for r, (nl, nr) in enumerate(zip(ESP_L, ESP_R), start=1):
        for col, name, an, tx in ((0, nl, "right", x0 - 30), (10, nr, "start", x0 + w + 30)):
            hy = y0 + (r - 1) * P
            net = ESP_USED.get(f"{COLS[col]}{r}")
            s.dot(x0 + col * P, hy, PR - 1.4, NETS[net][2] if net else NODE_B)
            s.text(tx, hy + 4, name, size=10.5,
                   fill=NETS[net][2] if net else FG_FAINT, anchor=an,
                   weight=700 if net else 400)

    for ref, part, shape, pins in COMPONENTS:
        cx, cy, bw, bh, kind = body_box(ref, shape, pins, BODY_OVERRIDE.get(ref))
        px_, py_ = x0 + cx * MM, y0 + cy * MM
        col = V12 if ref in ("D1", "D2", "C1", "C2", "U1") else (
            NODE_A if ref in ("C3", "C4", "C11") else
            FG_DIM if shape.startswith("hdr") else SIG)
        if kind == "round":
            s.add(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="{bw * MM / 2:.1f}" '
                  f'fill="{PANEL_2}" stroke="{col}" stroke-width="1.7"/>')
        else:
            s.rect(px_ - bw * MM / 2, py_ - bh * MM / 2, bw * MM, bh * MM,
                   fill=PANEL_2, stroke=col, sw=1.7, r=4)
        for hh, _pl, nn in pins:
            s.dot(*_xy(x0, y0, hh), PR - 2.2, NETS[nn][2])
        if bw >= bh or shape.startswith("hdr") or shape in ("sip3", "rad"):
            s.text(px_, py_ - bh * MM / 2 - 8, ref, size=11, fill=col,
                   weight=700, anchor="middle")
        else:
            s.text(px_ + bw * MM / 2 + 7, py_ + 4, ref, size=11, fill=col, weight=700)

    # right-hand panel: the parts list
    px = 700
    s.text(px, 210, "WHAT GOES WHERE", size=13, fill=FG, weight=700)
    s.text(px, 232, "hole = column letter + row number, e.g. A27", size=10.5, fill=FG_FAINT)
    rows = [("ref", "part", "holes", "mounting")]
    mount = MOUNT
    for ref, part, shape, pins in COMPONENTS:
        rows.append((ref, part, " ".join(f"{h}={p}" for h, p, _n in pins), mount[shape]))
    colx = [px, px + 58, px + 200, px + 590]
    for i, rw in enumerate(rows):
        yy = 264 + i * 26
        if i == 0:
            s.line(px, yy + 7, px + 720, yy + 7, stroke=EDGE, sw=1.2)
        for cx, cell in zip(colx, rw):
            s.text(cx, yy, cell, size=11 if i else 10.5,
                   fill=FG if i else FG_DIM, weight=400 if i else 700)

    yy = 264 + len(rows) * 26 + 26
    s.text(px, yy, "WHY THE ESP32 FILLS THE WIDTH", size=13, fill=FG, weight=700)
    for i, ln in enumerate([
            "The DevKit V1's two pin rows are 25.4 mm apart — exactly 10 pitches —",
            "so they land in column A and column L and nothing else fits beside them.",
            "Rows 1-15 are the pins; the module body reaches about 3 rows further,",
            "which is why rows 16-18 carry no parts. Columns B-K underneath keep",
            "8.5 mm of clearance, which is where the flat parts and the wiring go."]):
        s.text(px, yy + 26 + i * 20, ln, size=11.5, fill=FG_DIM)

    yy += 26 + 5 * 20 + 26
    s.text(px, yy, "BEFORE YOU SOLDER ANYTHING", size=13, fill=WARN, weight=700)
    for i, ln in enumerate([
            "Check BOTH pin rows against the names drawn here. 3V3 sits beside",
            "VIN at the USB end, not at the antenna end: reading a pinout image",
            "from the wrong end reverses the right-hand column and nothing else,",
            "which is how this repository had it wrong from v0.1.0 to v0.1.7."]):
        s.text(px, yy + 26 + i * 20, ln, size=11.5, fill=FG_DIM)

    s.caption(s.h - 20, "Parts on this side, wires on the other. Nothing is soldered to the "
                        "board except the sockets, the connectors and these passives.")
    return "12-node-a-placement", s


def fig13_node_a_solder_side():
    s = Svg(1760, 1120)
    n_runs = len(RUNS)
    total_mm = sum(run_length(h) for _i, _n, h, _x in RUNS)
    s.text(40, 44, f"NODE A  ·  SOLDER SIDE  —  the {n_runs} jumpers, and where each one runs",
           size=15, fill=FG, weight=700)
    s.text(40, 64, "THE BOARD IS FLIPPED OVER: column A is now on the RIGHT. "
                   "Every wire below is on this face.", size=12, fill=WARN, weight=700)

    x0, y0 = 300, 230
    w, h = _board(s, x0, y0, True, "BOTTOM VIEW  ·  mirrored  ·  column A on the RIGHT",
                  num_off=42)

    s.rect(x0 - 14, y0 - 3.1 * P, w + 28, 20.2 * P, fill="none", stroke=NODE_B, sw=1.4,
           r=8, dash="6 5", op=0.5)
    s.text(x0 + w / 2, y0 - 3.1 * P - 12, "ESP32 module is on the other side",
           size=10.5, fill=NODE_B, anchor="middle")

    # ghost the parts that sit on the other face, so a gap in a run is readable
    for ref, _part, shape, pins in COMPONENTS:
        xs = [_xy(x0, y0, hh, True)[0] for hh, _p, _n in pins]
        ys = [_xy(x0, y0, hh, True)[1] for hh, _p, _n in pins]
        s.rect(min(xs) - 11, min(ys) - 11, max(xs) - min(xs) + 22, max(ys) - min(ys) + 22,
               fill="none", stroke=FG_FAINT, sw=1.3, r=5, dash="3 3", op=0.55)
        s.text(min(xs) - 14, min(ys) - 14, ref, size=9, fill=FG_FAINT, anchor="right")

    solder = {h for _i, _n, hs, _x in RUNS for h in hs}
    for rid, net, holes, _note in RUNS:
        colr = NETS[net][2]
        pts = [_xy(x0, y0, hh, True) for hh in route_pts(rid, holes)]
        for a, b in zip(pts, pts[1:]):                      # halo first, then the wire
            s.line(a[0], a[1], b[0], b[1], stroke=BG, sw=7.0, cap="round")
        for a, b in zip(pts, pts[1:]):
            s.line(a[0], a[1], b[0], b[1], stroke=colr, sw=3.0, cap="round")
        for hh in holes:
            s.dot(*_xy(x0, y0, hh, True), 5.2, colr)

    for hh in solder:
        s.dot(*_xy(x0, y0, hh, True), 2.0, BG)

    px = 830
    s.text(px, 184, "SYMBOLOGY", size=13, fill=FG, weight=700)
    for i, (key, (lbl, wire, colr)) in enumerate(NETS.items()):
        yy = 212 + i * 24
        s.line(px, yy - 4, px + 44, yy - 4, stroke=colr, sw=3.4, cap="round")
        s.dot(px + 22, yy - 4, 5.2, colr)
        s.text(px + 56, yy, wire, size=11, fill=colr, weight=700)
        s.text(px + 148, yy, lbl, size=11, fill=FG_DIM)
    yy = 212 + len(NETS) * 24 + 6
    # one wire colour, more than one NET -- not merely more than one run
    by_colour = {}
    for rid, net, _h, _x in RUNS:
        by_colour.setdefault(NETS[net][1], {}).setdefault(net, []).append(rid)
    dup = {c: nets for c, nets in by_colour.items() if len(nets) > 1}
    s.text(px, yy, "Several colours carry more than one net,",
           size=10.5, fill=WARN)
    s.text(px, yy + 18, "and they are never joined. Go by the cut list.",
           size=10.5, fill=WARN)
    for i, (c, nets) in enumerate(dup.items()):
        s.text(px, yy + 40 + i * 17,
               f"{c.lower()}: " + "  ≠  ".join("/".join(ids)
                                               for ids in nets.values()),
               size=10, fill=FG_DIM)
    yy += len(dup) * 17 + 22
    yy += 44
    s.dot(px + 22, yy, 5.2, FG_DIM)
    s.text(px + 56, yy + 4, "dot", size=11, fill=FG, weight=700)
    s.text(px + 150, yy + 4, "the wire is soldered to this pad",
           size=11, fill=FG_DIM)
    yy += 26
    s.line(px, yy, px + 44, yy, stroke=FG_DIM, sw=3.0, cap="round")
    s.text(px + 56, yy + 4, "line", size=11, fill=FG, weight=700)
    s.text(px + 150, yy + 4, "insulated wire; crossings are fine",
           size=11, fill=FG_DIM)

    px, yy = 1250, 184
    s.text(px, yy, f"CUT LIST  ·  {n_runs} jumpers, {total_mm:.0f} mm of wire",
           size=13, fill=FG, weight=700)
    yy += 26
    hdr = ("id", "net", "colour", "solder at", "cut")
    colx = [px, px + 44, px + 100, px + 178, px + 412]
    for cx, cell in zip(colx, hdr):
        s.text(cx, yy, cell, size=10.5, fill=FG_DIM, weight=700)
    s.line(px, yy + 7, px + 470, yy + 7, stroke=EDGE, sw=1.2)
    for i, (rid, net, holes, _note) in enumerate(RUNS):
        ry = yy + 24 + i * 21
        colr = NETS[net][2]
        for cx, cell in zip(colx, (rid, net, NETS[net][1].lower(),
                                   "  ".join(holes), f"{run_length(holes):.0f} mm")):
            s.text(cx, ry, cell, size=10.5, fill=colr if cx in colx[1:3] else FG)

    s.caption(s.h - 20, "Strip 3 mm, tin both ends, lay the wire flat and solder it to every "
                        "pad the cut list names for it. Longest first, shortest last.")
    return "13-node-a-solder-side", s


def _panel(s, x, y, w, h, title, lines, accent):
    s.rect(x, y, w, h, fill=PANEL, stroke=accent, sw=1.6, r=10)
    s.text(x + 16, y + 26, title, size=12.5, fill=accent, weight=700)
    for i, ln in enumerate(lines):
        s.text(x + 16, y + h - 14 - (len(lines) - 1 - i) * 17, ln, size=10.5, fill=FG_DIM)
    return x + 16, y + 40


def _pads(s, x, y, n, pitch=26, r=7.5):
    for i in range(n):
        s.dot(x + i * pitch, y, r, PAD)
        s.dot(x + i * pitch, y, 2.8, PAD_IN)



def polarity_rows():
    """The polarity panel is derived from COMPONENTS, never typed by hand.

    Every part with a cathode pin or a marked negative pin appears here with the
    hole the layout actually puts it in, so the drawing cannot drift from the
    board the way it did between v0.1.5 and v0.1.8.
    """
    rows = []
    for ref, part, _shape, pins in COMPONENTS:
        holes = {lbl: h for h, lbl, _ in pins}
        if "K" in holes:
            tail = (" (VBAT), NOT ground" if holes["K"] == "A23"
                    else ", toward the buck")
            rows.append((f"{ref} {part}", f"band = cathode -> {holes['K']}{tail}"))
        elif "-" in holes:
            value = "/".join(part.split()[:2])
            rows.append((f"{ref} {value}", f"stripe = minus -> {holes['-']}"))
    assert rows, "no polarised part found — the layout data changed shape"
    return rows


def fig14_node_a_technique():
    s = Svg(1520, 840)
    s.text(40, 44, "NODE A  ·  HOW TO MOUNT AND SOLDER IT", size=15, fill=FG, weight=700)
    s.text(40, 64, "the six things that decide whether a perfboard build works first time",
           size=12, fill=FG_FAINT)

    W, H, GX, GY = 460, 330, 20, 20
    X0, Y0 = 40, 100

    # 1 -- flat axial, 2 pitches
    px, py = _panel(s, X0, Y0, W, H, "1 · FLAT AXIAL, 2 PITCHES  —  D1 and the small parts", [
        "D1 (DO-41, body 4.1 mm) and every ceramic and resistor here.",
        "Bend both leads square, close to the body, and lay it down.",
        "Nothing on this board stands up: flat parts are easier to inspect."], SIG)
    _pads(s, px + 60, py + 120, 4)
    s.line(px + 60, py + 120, px + 60, py + 92, stroke=FG_DIM, sw=2)
    s.line(px + 112, py + 120, px + 112, py + 92, stroke=FG_DIM, sw=2)
    s.line(px + 60, py + 92, px + 112, py + 92, stroke=FG_DIM, sw=2)
    s.rect(px + 70, py + 80, 32, 24, fill=PANEL_2, stroke=SIG, sw=1.6, r=4)
    s.rect(px + 94, py + 80, 8, 24, fill=SIG, stroke=SIG, sw=1)
    s.text(px + 132, py + 90, "band = cathode (K)", size=10.5, fill=FG_FAINT)
    s.text(px + 132, py + 108, "D1: band to C21, toward the buck", size=10.5, fill=WARN)
    s.text(px + 62, py + 146, "2 pitches · A21 to C21", size=10, fill=SIG)

    # 2 -- flat axial, 3 pitches
    px, py = _panel(s, X0 + W + GX, Y0, W, H, "2 · FLAT AXIAL, 3 PITCHES  —  D2", [
        "D2 is a P6KE20A in DO-15: the body is 6.6 mm, wider than one pitch,",
        "so it spans three holes, A23 to D23, and not two.",
        "A ¼ W resistor (6.3 mm body) needs the same three-hole span."], SIG)
    _pads(s, px + 60, py + 120, 4)
    s.line(px + 60, py + 120, px + 60, py + 92, stroke=FG_DIM, sw=2)
    s.line(px + 138, py + 120, px + 138, py + 92, stroke=FG_DIM, sw=2)
    s.line(px + 60, py + 92, px + 138, py + 92, stroke=FG_DIM, sw=2)
    s.rect(px + 70, py + 78, 58, 28, fill=PANEL_2, stroke=SIG, sw=1.6, r=4)
    s.rect(px + 70, py + 78, 9, 28, fill=SIG, stroke=SIG, sw=1)
    s.text(px + 158, py + 90, "band = cathode (K)", size=10.5, fill=FG_FAINT)
    s.text(px + 158, py + 108, "D2: band to A23 (VBAT)", size=10.5, fill=WARN)
    s.text(px + 62, py + 146, "3 pitches · A23 to D23", size=10, fill=SIG)

    # 3 -- polarity
    rows = polarity_rows()
    px, py = _panel(s, X0 + 2 * (W + GX), Y0, W, H,
                    f"3 · POLARITY  —  get these {len(rows)} right", [
        "A reversed electrolytic vents. A reversed TVS shorts 12 V to ground",
        "and blows the fuse. Check every one against Fig. 12 before the iron is hot."],
                    WARN)
    for i, (a, b) in enumerate(rows):
        s.text(px, py + 24 + i * 26, a, size=11, fill=WARN, weight=700)
        s.text(px + 132, py + 24 + i * 26, b, size=10.5, fill=FG_DIM)

    # 4 -- sockets
    px, py = _panel(s, X0, Y0 + H + GY, W, H, "4 · SOCKETS  —  never solder the ESP32 down", [
        "Solder two 15-way female headers into column A and column L.",
        "Tack ONE pin of each, plug the module in, check it sits flat,",
        "then solder the rest. That is what keeps the rows parallel."], NODE_A)
    _pads(s, px + 40, py + 150, 9, pitch=34)
    s.rect(px + 30, py + 116, 22, 68, fill=PANEL_2, stroke=NODE_A, sw=1.6, r=3)
    s.rect(px + 302, py + 116, 22, 68, fill=PANEL_2, stroke=NODE_A, sw=1.6, r=3)
    s.rect(px + 30, py + 84, 294, 34, fill=NODE_B, stroke=NODE_B, sw=1.4, r=5, op=0.22)
    s.text(px + 177, py + 106, "ESP32 module", size=11, fill=NODE_B, anchor="middle")
    s.text(px + 30, py + 204, "female header", size=10, fill=NODE_A)
    s.text(px + 262, py + 204, "female header", size=10, fill=NODE_A)

    # 5 -- making a jumper
    px, py = _panel(s, X0 + W + GX, Y0 + H + GY, W, H, "5 · MAKING ONE JUMPER", [
        "Do the long runs first — they need the clearest board.",
        "Reheat a cold joint; do not pile more solder onto it.",
        "Insulated wire may cross anything. Bare lead may cross nothing."], V5)
    steps = ["cut to the length in the cut list", "strip 3 mm and tin both ends",
             "lay it flat against the board", "solder every pad the list names",
             "tug it — a joint that moves is cold"]
    for i, ln in enumerate(steps):
        s.dot(px + 8, py + 22 + i * 26, 9, PANEL_2)
        s.text(px + 8, py + 26 + i * 26, str(i + 1), size=10.5, fill=V5,
               anchor="middle", weight=700)
        s.text(px + 26, py + 26 + i * 26, ln, size=11, fill=FG_DIM)

    # 6 -- the mirror rule
    px, py = _panel(s, X0 + 2 * (W + GX), Y0 + H + GY, W, H, "6 · THE MIRROR  —  read this twice",
                    ["Fig. 12 is the top. Fig. 13 is the bottom, already mirrored.",
                     "Work from Fig. 13 with the board actually flipped in front of you,",
                     "and the letters will match. Do not mirror it again in your head."], WARN)
    for k, (lbl, order, col) in enumerate((("TOP", "A B C D E", NODE_A),
                                           ("BOTTOM", "E D C B A", WARN))):
        yy = py + 36 + k * 92
        s.text(px, yy, lbl, size=11, fill=col, weight=700)
        for i, ch in enumerate(order.split()):
            s.dot(px + 92 + i * 40, yy + 22, 12, PANEL_2)
            s.text(px + 92 + i * 40, yy + 26, ch, size=11.5, fill=col, anchor="middle",
                   weight=700)
        s.text(px, yy + 26, "row 1 ->", size=10, fill=FG_FAINT)

    s.caption(s.h - 18, "Sockets, connectors and passives are the only things soldered to this "
                        "board. Everything expensive plugs in.")
    return "14-node-a-technique", s
