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

COLS = "ABCDEFGHJKL"          # 11 columns, I omitted on purpose
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
    "IGN":  ("node_IGN",          "AZUL",     SIG),
    "IN1":  ("IN1 -> relay CH1",  "AZUL",     SIG),
    "IN2":  ("IN2 -> relay CH2",  "AZUL",     SIG),
    "SW1":  ("SW1 (OEM switch)",  "BLANCO",   FG),
    "LED1": ("LED1 (tell-tale)",  "BLANCO",   FG),
}

# --- ESP32 header, physical order, row 1 = USB end ----------------------------
ESP_L = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32",
         "D35", "D34", "VN", "VP", "EN"]
ESP_R = ["D23", "D22", "TX0", "RX0", "D21", "D19", "D18", "D5", "TX2", "RX2",
         "D4", "D2", "D15", "GND", "3V3"]
ESP_USED = {"A1": "V5", "A2": "GND", "A6": "SW1", "A7": "IN2", "A8": "IN1",
            "A9": "LED1", "A12": "IGN", "L15": "V33"}

# --- discrete components: ref, part, shape, [(hole, pin, net)] ----------------
COMPONENTS = [
    ("J1", "IG in · 2p",      "hdr",  [("A27", "1 +12V", "V12"), ("B27", "2 GND", "GND")]),
    ("J2", "relay · 5p",      "hdr",  [("D27", "JD-VCC", "V5"), ("E27", "GND", "GND"),
                                       ("F27", "IN1", "IN1"), ("G27", "IN2", "IN2"),
                                       ("H27", "VCC", "V33")]),
    ("J3", "OEM switch · 2p", "hdr",  [("K27", "SW1", "SW1"), ("L27", "LED1", "LED1")]),
    ("D1", "SS34",            "vert", [("A26", "A", "V12"), ("A25", "K", "VBAT")]),
    ("D2", "SMAJ18A",         "ax2",  [("A24", "K", "VBAT"), ("C24", "A", "GND")]),
    ("C1", "470u 35V",        "rad",  [("A23", "+", "VBAT"), ("C23", "-", "GND")]),
    ("U1", "R-78E5.0-1.0",    "sip3", [("B21", "1 +Vin", "VBAT"), ("C21", "2 GND", "GND"),
                                       ("D21", "3 +Vout", "V5")]),
    ("C3", "470u 16V",        "rad",  [("B19", "-", "GND"), ("D19", "+", "V5")]),
    ("R1", "10k",             "vert", [("G23", "1", "VBAT"), ("G22", "2", "IGN")]),
    ("R2", "3k3",             "vert", [("H22", "1", "IGN"), ("H21", "2", "GND")]),
    ("D3", "BAT85",           "ax1",  [("J23", "A", "IGN"), ("K23", "K", "V33")]),
    ("C5", "100n",            "ax1",  [("J22", "1", "IGN"), ("K22", "2", "GND")]),
]

# --- bare pads used only as junctions (no component lead) ---------------------
TIE_POINTS = {"C27": "GND"}   # ground spine junction, keeps three leads off D2's pad

# --- solder-side runs: (id, net, [holes in soldering order], note) ------------
RUNS = [
    ("Y1", "V12",  ["A27", "A26"],                       "J1 -> D1 anode"),
    ("Y2", "VBAT", ["A25", "A24", "A23", "B21"],         "D1 K -> D2 -> C1+ -> U1 +Vin"),
    ("Y3", "VBAT", ["A23", "G23"],                       "VBAT -> R1 (divider top)"),
    ("N1", "GND",  ["E27", "C27", "C24", "C23", "C21"],  "relay GND -> spine -> D2, C1-, U1"),
    ("N2", "GND",  ["B27", "C27"],                       "J1 GND -> spine"),
    ("N3", "GND",  ["C21", "B19"],                       "spine -> C3 -"),
    ("N4", "GND",  ["C21", "A2"],                        "spine -> ESP32 GND"),
    ("N5", "GND",  ["K22", "H21", "C21"],                "C5 -, R2 bottom -> spine"),
    ("G1", "V5",   ["D19", "D21", "D27"],                "C3+ -> U1 out -> relay JD-VCC"),
    ("G2", "V5",   ["D21", "A1"],                        "U1 out -> ESP32 VIN"),
    ("R1w", "V33", ["L15", "K23"],                       "ESP32 3V3 -> D3 cathode"),
    ("R2w", "V33", ["K23", "H27"],                       "3V3 -> relay VCC"),
    ("B1", "IGN",  ["G22", "H22", "J22", "J23"],         "divider node: R1-R2-C5-D3"),
    ("B2", "IGN",  ["G22", "A12"],                       "node_IGN -> GPIO34"),
    ("B3", "IN1",  ["A8", "F27"],                        "GPIO25 -> relay IN1"),
    ("B4", "IN2",  ["A7", "G27"],                        "GPIO26 -> relay IN2"),
    ("W1", "SW1",  ["A6", "K27"],                        "GPIO27 -> SW1"),
    ("W2", "LED1", ["A9", "L27"],                        "GPIO33 -> LED1"),
]


# --- helpers ------------------------------------------------------------------
def ci(hole):
    return COLS.index(hole[0])


def ri(hole):
    return int(hole[1:])


def check():
    """Fail loudly on a placement that cannot be built."""
    used = {}
    for ref, _p, _s, pins in COMPONENTS:
        for h, pin, net in pins:
            assert h[0] in COLS and 1 <= ri(h) <= NROW, f"{ref}: hole {h} off the board"
            assert h not in used, f"{ref} and {used[h]} both claim hole {h}"
            used[h] = ref
    for h in list(ESP_USED) + [f"A{r}" for r in range(1, 16)] + [f"L{r}" for r in range(1, 16)]:
        if h in used:
            raise AssertionError(f"{used[h]} sits on ESP32 header hole {h}")
    # every run hole must be a real pad of something, and share the run's net
    netof = {h: n for _r, _p, _s, pins in COMPONENTS for h, _pin, n in pins}
    netof.update(ESP_USED)
    netof.update(TIE_POINTS)
    for rid, net, holes, _note in RUNS:
        for h in holes:
            assert h in netof, f"run {rid}: {h} is not a component pad"
            a, b = netof[h], net
            ok = a == b or {a, b} <= {"V12", "VBAT"}
            assert ok, f"run {rid} ({net}) lands on {h} which is net {netof[h]}"
    # every component pad must be reachable
    reached = {h for _i, _n, hs, _x in RUNS for h in hs}
    for h, n in netof.items():
        if h.startswith(("A", "L")) and ri(h) <= 15 and h not in ESP_USED:
            continue
        if h in TIE_POINTS:
            continue
        assert h in reached, f"pad {h} ({n}) is not connected by any run"
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


LABEL_POS = {"J1": "N", "J2": "N", "J3": "N", "D1": "E", "D2": "E", "C1": "E",
             "U1": "E", "C3": "E", "R1": "W", "R2": "N", "D3": "E", "C5": "E"}


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
        xs = [_xy(x0, y0, hh)[0] for hh, _p, _n in pins]
        ys = [_xy(x0, y0, hh)[1] for hh, _p, _n in pins]
        pad = 11
        bx, by = min(xs) - pad, min(ys) - pad
        bw, bh = max(xs) - min(xs) + 2 * pad, max(ys) - min(ys) + 2 * pad
        col = V12 if ref in ("D1", "D2", "C1", "U1", "C3") else (
            FG_DIM if shape == "hdr" else SIG)
        s.rect(bx, by, bw, bh, fill=PANEL_2, stroke=col, sw=1.7, r=5)
        for hh, pl, nn in pins:
            s.dot(*_xy(x0, y0, hh), PR - 2.2, NETS[nn][2])
        pos = LABEL_POS[ref]
        if pos == "E":
            s.text(bx + bw + 7, by + bh / 2 + 4, ref, size=11, fill=col, weight=700)
        elif pos == "W":
            s.text(bx - 7, by + bh / 2 + 4, ref, size=11, fill=col, weight=700,
                   anchor="right")
        else:
            s.text(bx + bw / 2, by - 7, ref, size=11, fill=col, weight=700, anchor="middle")

    # right-hand panel: the parts list
    px = 700
    s.text(px, 210, "WHAT GOES WHERE", size=13, fill=FG, weight=700)
    s.text(px, 232, "hole = column letter + row number, e.g. A27", size=10.5, fill=FG_FAINT)
    rows = [("ref", "part", "holes", "mounting")]
    mount = {"hdr": "90° header", "vert": "standing", "ax2": "axial, 2 pitches",
             "ax1": "axial, 1 pitch", "rad": "radial, 2 pitches", "sip3": "SIP3, in a row"}
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
            "which is why rows 16-18 carry no parts. All 9 holes between the rows",
            "stay free, and that is where the solder-side wiring runs."]):
        s.text(px, yy + 26 + i * 20, ln, size=11.5, fill=FG_DIM)

    yy += 26 + 5 * 20 + 26
    s.text(px, yy, "BEFORE YOU SOLDER ANYTHING", size=13, fill=WARN, weight=700)
    for i, ln in enumerate([
            "Check your module's silkscreen against the pin names drawn here.",
            "DevKit V1 clones exist with a different order. The eight that",
            "matter are VIN, GND, D34, D33, D25, D26, D27 and 3V3 — find each",
            "one on your own board and confirm it sits in the row shown."]):
        s.text(px, yy + 26 + i * 20, ln, size=11.5, fill=FG_DIM)

    s.caption(s.h - 20, "Parts on this side, wires on the other. Nothing is soldered to the "
                        "board except the sockets, the connectors and these passives.")
    return "12-node-a-placement", s


def fig13_node_a_solder_side():
    s = Svg(1560, 1070)
    s.text(40, 44, "NODE A  ·  SOLDER SIDE  —  the 18 jumpers, and where each one runs",
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
    s.text(px, yy, "Three colours carry more than one net. They are never joined:",
           size=10.5, fill=WARN)
    s.text(px, yy + 18, "amarillo Y1 ≠ Y2/Y3 · azul B1/B2 ≠ B3 ≠ B4 · blanco W1 ≠ W2",
           size=10.5, fill=FG_DIM)
    yy += 44
    s.dot(px + 22, yy, 5.2, FG_DIM)
    s.text(px + 56, yy + 4, "dot", size=11, fill=FG, weight=700)
    s.text(px + 150, yy + 4, "solder here — the wire is joined to this pad",
           size=11, fill=FG_DIM)
    yy += 26
    s.line(px, yy, px + 44, yy, stroke=FG_DIM, sw=3.0, cap="round")
    s.text(px + 56, yy + 4, "line", size=11, fill=FG, weight=700)
    s.text(px + 150, yy + 4, "insulated wire lying on the board — crossings are fine",
           size=11, fill=FG_DIM)

    yy += 42
    s.text(px, yy, "CUT LIST  ·  18 jumpers, 790 mm of wire", size=13, fill=FG, weight=700)
    yy += 26
    hdr = ("id", "colour", "solder at", "cut")
    colx = [px, px + 52, px + 152, px + 566]
    for cx, cell in zip(colx, hdr):
        s.text(cx, yy, cell, size=10.5, fill=FG_DIM, weight=700)
    s.line(px, yy + 7, px + 640, yy + 7, stroke=EDGE, sw=1.2)
    for i, (rid, net, holes, _note) in enumerate(RUNS):
        ry = yy + 24 + i * 22
        colr = NETS[net][2]
        for cx, cell in zip(colx, (rid, NETS[net][1], "  ".join(holes),
                                   f"{run_length(holes):.0f} mm")):
            s.text(cx, ry, cell, size=11, fill=colr if cx == colx[1] else FG)

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


def fig14_node_a_technique():
    s = Svg(1520, 840)
    s.text(40, 44, "NODE A  ·  HOW TO MOUNT AND SOLDER IT", size=15, fill=FG, weight=700)
    s.text(40, 64, "the six things that decide whether a perfboard build works first time",
           size=12, fill=FG_FAINT)

    W, H, GX, GY = 460, 330, 20, 20
    X0, Y0 = 40, 100

    # 1 -- standing axial
    px, py = _panel(s, X0, Y0, W, H, "1 · STANDING AXIAL  —  D1, R1, R2", [
        "Used where the part must fit one pitch: D1, R1, R2.",
        "Bend one lead 180° down the side of the body.",
        "Both leads end up 2.54 mm apart — two touching holes."], SIG)
    _pads(s, px + 60, py + 170, 4)
    s.line(px + 60, py + 170, px + 60, py + 60, stroke=FG_DIM, sw=2)
    s.rect(px + 46, py + 40, 28, 62, fill=PANEL_2, stroke=SIG, sw=1.6, r=4)
    s.line(px + 86, py + 170, px + 86, py + 50, stroke=FG_DIM, sw=2)
    s.line(px + 60, py + 46, px + 86, py + 46, stroke=FG_DIM, sw=2)
    s.text(px + 112, py + 96, "body stands up", size=10.5, fill=FG_FAINT)
    s.text(px + 112, py + 114, "one lead folded over", size=10.5, fill=FG_FAINT)
    s.text(px + 52, py + 196, "1 pitch", size=10, fill=SIG)

    # 2 -- flat axial
    px, py = _panel(s, X0 + W + GX, Y0, W, H, "2 · FLAT AXIAL  —  D2, D3, C5", [
        "D2 spans 2 pitches (A24 to C24). D3 and C5 span 1.",
        "Bend both leads square, close to the body, and lay it down.",
        "Flat parts are easier to inspect and harder to short."], SIG)
    _pads(s, px + 60, py + 120, 4)
    s.line(px + 60, py + 120, px + 60, py + 92, stroke=FG_DIM, sw=2)
    s.line(px + 112, py + 120, px + 112, py + 92, stroke=FG_DIM, sw=2)
    s.line(px + 60, py + 92, px + 112, py + 92, stroke=FG_DIM, sw=2)
    s.rect(px + 66, py + 80, 40, 24, fill=PANEL_2, stroke=SIG, sw=1.6, r=4)
    s.rect(px + 66, py + 80, 8, 24, fill=SIG, stroke=SIG, sw=1)
    s.text(px + 132, py + 90, "band = cathode (K)", size=10.5, fill=FG_FAINT)
    s.text(px + 132, py + 108, "D2: band to the A column", size=10.5, fill=WARN)
    s.text(px + 62, py + 146, "2 pitches", size=10, fill=SIG)

    # 3 -- polarity
    px, py = _panel(s, X0 + 2 * (W + GX), Y0, W, H, "3 · POLARITY  —  get these five right", [
        "A reversed electrolytic vents. A reversed diode kills the stage.",
        "Check every one against Fig. 12 before the iron is hot."], WARN)
    rows = [("D1 SS34", "band -> A25 (cathode, toward the buck)"),
            ("D2 SMAJ18A", "band = cathode -> A24 (VBAT), NOT ground"),
            ("D3 BAT85", "band -> K23 (the +3.3 V side)"),
            ("C1 470u/35V", "stripe = minus -> C23"),
            ("C3 470u/16V", "stripe = minus -> B19")]
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
