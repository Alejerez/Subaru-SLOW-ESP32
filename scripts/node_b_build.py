"""Node B build figures: hole-by-hole placement and solder-side jumper routing.

Imported by generate_diagrams.py. Node B is TWO boards:

  B-GAUGE  the board in the OEM clock bay: ESP32, the OLED/RTC/button connectors,
           the ADC clamps and filters.  11 x 27 holes (3 x 7 cm).
  B-PWR    a board at the i59 adapter carrying everything that touches 12 V:
           the protection chain, the Recom buck, the ILL divider and the L9637D.
           A second 3 x 7 cm board; it uses fewer than half its holes.

The split exists because the gauge board is provably full -- see budget().

Columns are lettered A..L with I omitted so it cannot be read as 1; rows are
numbered from the USB end on B-GAUGE and from the K-line end on B-PWR.

NOTE ON NAMES: a hole is a column letter plus a row number (C13, K21). A
reference designator is a letter plus a sequence number (C6, R4). They look
alike and are not related: hole C13 has nothing to do with capacitor C13.
"""
import math
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))

from diagram_lib import (  # noqa: E402
    Svg, BG, PANEL, PANEL_2, EDGE, FG, FG_DIM, FG_FAINT,
    V12, V5, V33, GND, SIG, NODE_A, NODE_B, NODE_C, WARN,
)

import board_lib as BL                                              # noqa: E402
from board_lib import (  # noqa: E402
    COLS, ci, ri, ESP_L, ESP_R, body_box, check_bodies,
)

PAD = "#7a5334"               # copper ring
PAD_IN = "#1c1008"

# --- the six wire colours on the bench, and what each carries -----------------
WIRE = {
    "AMARILLO": (V12,  "12 V, and VBAT after D1"),
    "ROJO":     (V33,  "+3.3 V"),
    "NEGRO":    (GND,  "GND"),
    "AZUL":     (SIG,  "logic: SPI, I2C, UART, ADC nodes"),
    "BLANCO":   (FG,   "bezel buttons, sensor input"),
}

# --- nets: key -> (label, wire colour) ---------------------------------------
NETS = {
    "V12":  ("+12 V IG (pre-D1)",      "AMARILLO"),
    "VBAT": ("VBAT (post-D1)",         "AMARILLO"),
    "ILLR": ("ILL raw, i59 pin 1",     "AMARILLO"),
    "V33":  ("+3.3 V",                 "ROJO"),
    "GND":  ("GND",                    "NEGRO"),
    "ILL":  ("ILL divided -> GPIO35",  "AZUL"),
    "AN":   ("sensor divided -> GPIO34", "AZUL"),
    "KRX":  ("K-line RX -> GPIO16",    "AZUL"),
    "KTX":  ("K-line TX <- GPIO17",    "AZUL"),
    "K":    ("K-line bus (OBD pin 7)", "AZUL"),
    "MOSI": ("OLED MOSI <- GPIO23",    "AZUL"),
    "SCLK": ("OLED SCLK <- GPIO18",    "AZUL"),
    "CS":   ("OLED CS <- GPIO5",       "AZUL"),
    "DC":   ("OLED DC <- GPIO19",      "AZUL"),
    "RST":  ("OLED RST <- GPIO4",      "AZUL"),
    "SDA":  ("RTC SDA <-> GPIO21",     "AZUL"),
    "SCL":  ("RTC SCL -> GPIO22",      "AZUL"),
    "ANR":  ("sensor raw 0-5 V",       "BLANCO"),
    "BDISP": ("button DISP -> GPIO32", "BLANCO"),
    "BSET":  ("button SET -> GPIO33",  "BLANCO"),
    "BPLUS": ("button [+] -> GPIO25",  "BLANCO"),
    "BMINUS": ("button [-] -> GPIO26", "BLANCO"),
    "NC":   ("not connected (spare)",  "BLANCO"),
}


def colour(net):
    return WIRE[NETS[net][1]][0]


# =============================================================================
# B-GAUGE  --  the board in the clock bay.  11 x 27 holes.
# =============================================================================
GAUGE = dict(
    key="b-gauge",
    title="B-GAUGE",
    nrow=27,
    esp=True,
    esp_used={
        "A2": "GND",
        "A7": "BMINUS", "A8": "BPLUS", "A9": "BSET", "A10": "BDISP",
        "A11": "ILL", "A12": "AN",
        "L1": "V33", "L2": "GND", "L5": "RST", "L6": "KRX", "L7": "KTX",
        "L8": "CS", "L9": "SCLK", "L10": "DC", "L11": "SDA",
        "L14": "SCL", "L15": "MOSI",
    },
    components=[
        ("J1", "umbilical to B-PWR · 5p", "hdr90",
         [("A27", "1 +3V3", "V33"), ("B27", "2 GND", "GND"), ("C27", "3 ILL", "ILL"),
          ("D27", "4 K-RX", "KRX"), ("E27", "5 K-TX", "KTX")]),
        ("J4", "RTC DS3231 · 4p", "hdr90",
         [("H27", "VCC", "V33"), ("J27", "GND", "GND"),
          ("K27", "SDA", "SDA"), ("L27", "SCL", "SCL")]),
        ("J2", "OLED SSD1322 · 7p", "hdr",
         [("E24", "VCC", "V33"), ("F24", "GND", "GND"), ("G24", "SCLK", "SCLK"),
          ("H24", "MOSI", "MOSI"), ("J24", "CS", "CS"), ("K24", "DC", "DC"),
          ("L24", "RST", "RST")]),
        ("J5", "sensor 0-5 V · 2p", "hdr",
         [("E21", "SIG", "ANR"), ("F21", "GND", "GND")]),
        ("J3", "OEM buttons · 5p", "hdr",
         [("G21", "DISP", "BDISP"), ("H21", "SET", "BSET"), ("J21", "[+]", "BPLUS"),
          ("K21", "[-]", "BMINUS"), ("L21", "GND", "GND")]),
        ("C3", "100u 16V 105C", "rad", [("A23", "+", "V33"), ("C23", "-", "GND")]),
        ("C11", "10u X7R", "ax2f", [("K1", "a", "V33"), ("K3", "b", "GND")]),
        ("R5", "20k 1%", "ax3f", [("A19", "in", "ANR"), ("D19", "node", "AN")]),
        ("C13", "100n X7R", "ax3f", [("B5", "a", "BDISP"), ("E5", "b", "GND")]),
        ("C14", "100n X7R", "ax3f", [("B7", "a", "BSET"), ("E7", "b", "GND")]),
        ("C15", "100n X7R", "ax3f", [("G5", "a", "BPLUS"), ("K5", "b", "GND")]),
        ("C16", "100n X7R", "ax3f", [("G7", "a", "BMINUS"), ("K7", "b", "GND")]),
        ("D4", "BAT85", "ax2f", [("B9", "A", "ILL"), ("D9", "K", "V33")]),
        ("D5", "BAT85", "ax2f", [("G9", "A", "AN"), ("J9", "K", "V33")]),
        ("C6", "1u X7R", "ax2f", [("B11", "a", "ILL"), ("D11", "b", "GND")]),
        ("R6", "10k 1%", "ax2f", [("G11", "node", "AN"), ("J11", "GND-side", "GND")]),
        ("C7", "100n X7R", "ax2f", [("G13", "a", "AN"), ("J13", "b", "GND")]),
    ],
    heights={"C11": 4.0, "R5": 3.2, "C13": 3.2, "C14": 3.2, "C15": 3.2,
             "C16": 3.2, "D4": 3.6, "D5": 3.6, "C6": 3.2, "R6": 3.2,
             "C7": 3.2, "C3": 11.0},
    body_override={"C3": (6.3, 6.3, "round")},
    tie_points={},
    unconnected=set(),
    runs=[
        ("R1", "V33", ["A27", "A23"],            "J1 +3V3 -> C3 +"),
        ("R2", "V33", ["A23", "K1", "L1"],       "-> C11 -> ESP32 3V3 pin"),
        ("R3", "V33", ["A27", "H27"],            "-> RTC VCC"),
        ("R4", "V33", ["H27", "E24"],            "-> OLED VCC"),
        ("R5w", "V33", ["L1", "J9"],             "-> D5 cathode"),
        ("R6w", "V33", ["J9", "D9"],             "-> D4 cathode"),
        ("N1", "GND", ["B27", "C23"],            "J1 GND -> C3 -"),
        ("N2", "GND", ["C23", "K3", "L2"],       "-> C11 -> ESP32 GND"),
        ("N3", "GND", ["B27", "F24", "F21"],     "-> OLED, sensor"),
        ("N4", "GND", ["B27", "L21"],            "-> buttons common"),
        ("N5", "GND", ["L2", "J27"],             "-> RTC GND"),
        ("N6", "GND", ["B27", "A2"],             "-> ESP32 GND, left row"),
        ("N7", "GND", ["A2", "D11", "E7", "E5"], "-> C6, C14, C13"),
        ("N8", "GND", ["A2", "J11", "J13"],      "-> R6, C7"),
        ("N9", "GND", ["K3", "K5", "K7"],        "-> C15, C16"),
        ("BL1", "ILL", ["C27", "B9"],            "umbilical ILL -> D4 anode"),
        ("BL2", "ILL", ["B9", "B11"],            "-> C6"),
        ("BL3", "ILL", ["B11", "A11"],           "-> GPIO35"),
        ("W1", "ANR", ["E21", "A19"],            "J5 -> R5"),
        ("BL4", "AN", ["D19", "G11"],            "R5 -> R6"),
        ("BL5", "AN", ["G11", "G9"],             "-> D5 anode"),
        ("BL6", "AN", ["G11", "G13"],            "-> C7"),
        ("BL7", "AN", ["G13", "A12"],            "-> GPIO34"),
        ("BL8", "KRX", ["D27", "L6"],            "umbilical -> RX2"),
        ("BL9", "KTX", ["E27", "L7"],            "umbilical -> TX2"),
        ("BL10", "SCLK", ["G24", "L9"],          "OLED -> GPIO18"),
        ("BL11", "MOSI", ["H24", "L15"],         "OLED -> GPIO23"),
        ("BL12", "CS", ["J24", "L8"],            "OLED -> GPIO5"),
        ("BL13", "DC", ["K24", "L10"],           "OLED -> GPIO19"),
        ("BL14", "RST", ["L24", "L5"],           "OLED -> GPIO4"),
        ("BL15", "SDA", ["K27", "L11"],          "RTC -> GPIO21"),
        ("BL16", "SCL", ["L27", "L14"],          "RTC -> GPIO22"),
        ("W2", "BDISP", ["G21", "B5", "A10"],    "DISP -> C13 -> GPIO32"),
        ("W3", "BSET", ["H21", "B7", "A9"],      "SET -> C14 -> GPIO33"),
        ("W4", "BPLUS", ["J21", "G5", "A8"],     "[+] -> C15 -> GPIO25"),
        ("W5", "BMINUS", ["K21", "G7", "A7"],    "[-] -> C16 -> GPIO26"),
    ],
    route_via={},
)


PWR = dict(
    key="b-pwr",
    title="B-PWR",
    nrow=27,
    esp=False,
    esp_used={},
    components=[
        ("J6", "car in (i59) · 3p", "hdr90L",
         [("A5", "1 +12V IG", "V12"), ("A6", "2 GND", "GND"), ("A7", "3 ILL", "ILLR")]),
        ("J7", "K-line to OBD p7 · 2p", "hdr90T",
         [("K1", "1 K", "K"), ("L1", "2 n/c", "NC")]),
        ("J8", "umbilical to B-GAUGE · 5p", "hdr90R",
         [("L20", "1 +3V3", "V33"), ("L21", "2 GND", "GND"), ("L22", "3 ILL", "ILL"),
          ("L23", "4 K-RX", "KRX"), ("L24", "5 K-TX", "KTX")]),
        ("D1", "SB1100", "ax2f", [("C5", "A", "V12"), ("E5", "K", "VBAT")]),
        ("D2", "P6KE20A", "ax3f", [("B9", "K", "VBAT"), ("E9", "A", "GND")]),
        ("C1", "100u 35V 105C", "rad", [("B13", "+", "VBAT"), ("D13", "-", "GND")]),
        ("C9", "100n X7R", "ax2f", [("F13", "a", "V33"), ("F15", "b", "GND")]),
        ("C10", "100n X7R 50V", "ax2f", [("G3", "a", "VBAT"), ("G5", "b", "GND")]),
        ("R3", "20k", "ax2f", [("J4", "in", "ILLR"), ("L4", "node", "ILL")]),
        ("R4", "3.3k", "ax2f", [("H7", "node", "ILL"), ("K7", "GND-side", "GND")]),
        ("U2", "L9637D on SOIC-DIP", "dip8",
         [("H12", "1 RX", "KRX"), ("H13", "2 LO", "NC"), ("H14", "3 VCC", "V33"),
          ("H15", "4 TX", "KTX"), ("L15", "5 GND", "GND"), ("L14", "6 K", "K"),
          ("L13", "7 VS", "VBAT"), ("L12", "8 LI", "VBAT")]),
        ("R7", "510R 1/2W", "ax3f", [("G17", "VS", "VBAT"), ("K17", "K", "K")]),
        ("C8", "1n C0G", "ax2f", [("H10", "a", "K"), ("K10", "b", "GND")]),
        ("C2", "100n X7R 50V", "ax2f", [("B18", "a", "VBAT"), ("D18", "b", "GND")]),
        ("U1", "R-78E3.3-1.0", "sip3",
         [("B22", "1 +Vin", "VBAT"), ("C22", "2 GND", "GND"), ("D22", "3 +Vout", "V33")]),
        ("C4", "100n X7R", "ax2f", [("B26", "a", "V33"), ("D26", "b", "GND")]),
    ],
    heights={},
    body_override={"C1": (6.3, 6.3, "round")},
    tie_points={},
    unconnected={"H13", "L1"},
    runs=[
        ("Y1", "V12",  ["A5", "C5"],                     "J6 +12 V -> D1 anode"),
        ("Y2", "VBAT", ["E5", "B9", "B13", "B22"],       "D1 K -> D2 -> C1+ -> U1 +Vin"),
        ("Y3", "VBAT", ["B22", "B18"],                   "-> C2"),
        ("Y4", "VBAT", ["B13", "G3"],                    "-> C10"),
        ("Y5", "VBAT", ["G3", "G17"],                    "-> R7"),
        ("Y6", "VBAT", ["G17", "L13"],                   "-> U2 VS"),
        ("Y7", "VBAT", ["L13", "L12"],                   "VS -> LI (see the note on LI)"),
        ("Y8", "ILLR", ["A7", "J4"],                     "J6 ILL -> R3"),
        ("N1", "GND",  ["A6", "E9", "D13", "C22"],       "J6 GND -> D2 -> C1- -> U1 GND"),
        ("N2", "GND",  ["C22", "D18"],                   "-> C2"),
        ("N3", "GND",  ["C22", "D26"],                   "-> C4"),
        ("N4", "GND",  ["C22", "L21"],                   "-> umbilical GND"),
        ("N5", "GND",  ["E9", "F15"],                    "-> C9"),
        ("N6", "GND",  ["F15", "G5"],                    "-> C10"),
        ("N7", "GND",  ["G5", "L15"],                    "-> U2 GND"),
        ("N8", "GND",  ["L15", "K10"],                   "-> C8"),
        ("N9", "GND",  ["K10", "K7"],                    "-> R4 lower leg"),
        ("G1", "V33",  ["D22", "B26"],                   "U1 out -> C4"),
        ("G2", "V33",  ["D22", "L20"],                   "-> umbilical"),
        ("R1", "V33",  ["L20", "H14"],                   "-> U2 VCC"),
        ("R2", "V33",  ["H14", "F13"],                   "-> C9"),
        ("BL1", "ILL", ["L4", "H7"],                     "R3 out -> R4 in"),
        ("BL2", "ILL", ["L4", "L22"],                    "-> umbilical"),
        ("BL3", "K",   ["L14", "K17"],                   "U2 K -> R7 pull-up"),
        ("BL4", "K",   ["K17", "H10"],                   "-> C8"),
        ("BL5", "K",   ["L14", "K1"],                    "-> J7, to OBD pin 7"),
        ("BL6", "KRX", ["H12", "L23"],                   "U2 RX -> umbilical"),
        ("BL7", "KTX", ["H15", "L24"],                   "U2 TX <- umbilical"),
    ],
    route_via={},
)


BOARDS = {b["key"]: b for b in (GAUGE, PWR)}


# --- helpers ------------------------------------------------------------------
# shapes that are flat enough to live under the ESP32 module (8.5 mm of clearance)
LOW_PROFILE = {"ax1f", "ax2f", "ax3f"}
MOUNT = {"hdr": "vertical header", "hdr90": "90° header, edge",
         "hdr90L": "90° header, left edge", "hdr90R": "90° header, right edge",
         "hdr90T": "90° header, top edge", "vert": "standing, 1 pitch",
         "ax2f": "axial, flat, 2 pitches", "ax1f": "axial, flat, 1 pitch",
         "ax3f": "axial, flat, 3 pitches",
         "rad": "radial, 2 pitches", "sip3": "SIP3, three in a row",
         "dip8": "DIP-8 adapter, 2 × 4"}


def netmap(b):
    m = {h: n for _r, _p, _s, pins in b["components"] for h, _pin, n in pins}
    m.update(b["esp_used"])
    m.update(b["tie_points"])
    return m


def check(b):
    """Fail loudly on a placement that cannot be built."""
    used = {}
    for ref, _p, shape, pins in b["components"]:
        for h, pin, net in pins:
            assert h[0] in COLS and 1 <= ri(h) <= b["nrow"], f"{ref}: {h} off the board"
            assert h not in used, f"{ref} and {used[h]} both claim hole {h}"
            assert net in NETS, f"{ref}: unknown net {net}"
            used[h] = ref
        if b["esp"] and any(ri(h) <= 18 for h, _p, _n in pins):
            assert shape in LOW_PROFILE, (
                f"{ref} sits under the ESP32 (rows 1-18) but is {shape}, not flat")
    if b["esp"]:
        hdr = [f"A{r}" for r in range(1, 16)] + [f"L{r}" for r in range(1, 16)]
        for h in hdr:
            if h in used:
                raise AssertionError(f"{used[h]} sits on ESP32 header hole {h}")
        for ref, _p, _s, pins in b["components"]:
            for h, _pin, _n in pins:
                assert not (16 <= ri(h) <= 18), f"{ref}: {h} is in the antenna rows 16-18"
    nm = netmap(b)
    for rid, net, holes, _note in b["runs"]:
        for h in holes:
            assert h in nm, f"run {rid}: {h} is not a pad or a tie point"
            assert nm[h] == net, f"run {rid} ({net}) lands on {h}, which is net {nm[h]}"
    reached = {h for _i, _n, hs, _x in b["runs"] for h in hs}
    for h, n in nm.items():
        if h in b["unconnected"]:
            continue
        if b["esp"] and h[0] in "AL" and ri(h) <= 15 and h not in b["esp_used"]:
            continue
        assert h in reached, f"pad {h} ({n}) is not connected by any run"
    for h in b["unconnected"]:
        assert h not in reached, f"{h} is listed as unconnected but a run lands on it"
    check_bodies(b, bodies(b), b["heights"])
    return used


def check_umbilical():
    """The two boards' only electrical interface: the five wires must agree.

    check() takes one board at a time, so it cannot see this -- and a swap here
    is not a wiring mistake that shows up as "it does not work", it is +3.3 V
    landed on GND through 20 cm of wire the moment the boards are joined.
    """
    def pins(board, ref):
        for r, _p, _s, ps in board["components"]:
            if r == ref:
                return ps
        raise AssertionError(f"{ref} not found on {board['key']}")
    a, b = pins(GAUGE, "J1"), pins(PWR, "J8")
    assert len(a) == len(b) == 5, "the umbilical is five wires"
    for i, (pa, pb) in enumerate(zip(a, b), start=1):
        assert pa[2] == pb[2], (
            f"umbilical pin {i}: B-GAUGE J1 has {pa[2]}, B-PWR J8 has {pb[2]}")
    return [p[2] for p in a]


def run_length(holes):
    """Manhattan length in mm plus 12 mm of slack for stripping and bends."""
    mm = 0.0
    for a, bb in zip(holes, holes[1:]):
        mm += (abs(ci(a) - ci(bb)) + abs(ri(a) - ri(bb))) * 2.54
    return mm + 12


# --- routing ------------------------------------------------------------------
def _used_pads(b):
    u = {h for _r, _p, _s, pins in b["components"] for h, _pin, _n in pins}
    u |= set(b["tie_points"])
    if b["esp"]:
        u |= {f"A{r}" for r in range(1, 16)} | {f"L{r}" for r in range(1, 16)}
    return u


def _leg(a, bb, used):
    """One orthogonal L between two holes, choosing the corner that crosses least."""
    ca, ra, cb, rb = ci(a), ri(a), ci(bb), ri(bb)
    if ca == cb or ra == rb:
        return [a, bb]
    v_first = [a, f"{COLS[ca]}{rb}", bb]
    h_first = [a, f"{COLS[cb]}{ra}", bb]

    def cells(p):
        out = []
        for x, y in zip(p, p[1:]):
            cx, rx, cy, ry = ci(x), ri(x), ci(y), ri(y)
            if cx == cy:
                out += [f"{COLS[cx]}{r}" for r in range(min(rx, ry), max(rx, ry) + 1)]
            else:
                out += [f"{COLS[c]}{rx}" for c in range(min(cx, cy), max(cx, cy) + 1)]
        return out

    cost = lambda p: sum(1 for h in cells(p)[1:-1] if h in used)  # noqa: E731
    return v_first if cost(v_first) <= cost(h_first) else h_first


def route_pts(b, rid, holes):
    used = _used_pads(b)
    via = b["route_via"].get(rid)
    seq = [holes[0]] + via + holes[1:] if via else holes
    pts = [seq[0]]
    for a, bb in zip(seq, seq[1:]):
        pts += _leg(a, bb, used)[1:]
    return pts


# --- drawing ------------------------------------------------------------------
P = 28                       # px per 2.54 mm pitch
MM = P / 2.54                # px per mm
PR, PRI = 8.0, 3.0

def bodies(b):
    return {ref: body_box(ref, sh, pins, b["body_override"].get(ref))
            for ref, _p, sh, pins in b["components"]}


def _xy(x0, y0, hole, b, mirror=False):
    c, r = ci(hole), ri(hole)
    if mirror:
        c = len(COLS) - 1 - c
    return x0 + c * P, y0 + (r - 1) * P


def _grid(s, x0, y0, b, mirror, title, num_off=30, letters=True):
    w, h = (len(COLS) - 1) * P, (b["nrow"] - 1) * P
    s.rect(x0 - 14, y0 - 14, w + 28, h + 28, fill=PANEL, stroke=EDGE, sw=1.6, r=6)
    order = list(reversed(COLS)) if mirror else list(COLS)
    if letters:
        for i, L in enumerate(order):
            for t in (y0 - 26, y0 + h + 34):
                s.text(x0 + i * P, t, L, size=11.5, fill=FG_DIM, anchor="middle",
                       weight=700)
    for r in range(1, b["nrow"] + 1):
        for t, an in ((x0 - num_off, "right"), (x0 + w + num_off, "start")):
            s.text(t, y0 + (r - 1) * P + 4, str(r), size=10.5, fill=FG_FAINT, anchor=an)
    for i in range(len(COLS)):
        for r in range(1, b["nrow"] + 1):
            cx, cy = x0 + i * P, y0 + (r - 1) * P
            s.dot(cx, cy, PR, PAD)
            s.dot(cx, cy, PRI, PAD_IN)
    s.text(x0 - 14, y0 - 48, title, size=13, fill=FG, weight=700)
    return w, h


def _draw_esp(s, x0, y0, b, w):
    mx0, mx1 = x0 - 14, x0 + w + 14
    my0, my1 = y0 - 3.1 * P, y0 + 17.1 * P
    s.rect(mx0, my0, mx1 - mx0, my1 - my0, fill=NODE_B, stroke=NODE_B, sw=1.6, r=8, op=0.10)
    s.rect(mx0, my0, mx1 - mx0, my1 - my0, fill="none", stroke=NODE_B, sw=1.6, r=8, dash="6 5")
    s.text((mx0 + mx1) / 2, my0 - 14, "ESP32 DevKit V1 — USB overhangs this edge",
           size=11, fill=NODE_B, anchor="middle", weight=700)
    s.rect(mx0 + 6, y0 + 15.5 * P, mx1 - mx0 - 12, 2.2 * P, fill=NODE_B, stroke="none",
           r=5, op=0.12)
    ty = y0 + 16.6 * P
    s.rect((mx0 + mx1) / 2 - 126, ty - 13, 252, 20, fill=BG, stroke="none", r=4, op=0.82)
    s.text((mx0 + mx1) / 2, ty + 2, "antenna end — rows 16-18 carry no parts",
           size=10.5, fill=NODE_B, anchor="middle", weight=700)
    for r, (nl, nr) in enumerate(zip(ESP_L, ESP_R), start=1):
        for col, name, an, tx in ((0, nl, "right", x0 - 30), (10, nr, "start", x0 + w + 30)):
            hy = y0 + (r - 1) * P
            net = b["esp_used"].get(f"{COLS[col]}{r}")
            s.dot(x0 + col * P, hy, PR - 1.4, colour(net) if net else NODE_B)
            s.text(tx, hy + 4, name, size=10.5, fill=colour(net) if net else FG_FAINT,
                   anchor=an, weight=700 if net else 400)


def _wrap(items, width):
    """Greedy wrap of short tokens into lines of at most `width` characters."""
    lines, cur = [], ""
    for it in items:
        if cur and len(cur) + 1 + len(it) > width:
            lines.append(cur)
            cur = it
        else:
            cur = f"{cur} {it}".strip()
    if cur:
        lines.append(cur)
    return lines


def draw_placement(b, w_px, h_px, x0, y0, panel_x, notes):
    s = Svg(w_px, h_px)
    s.text(40, 44, f"NODE B · {b['title']} · COMPONENT SIDE — where each part goes",
           size=15, fill=FG, weight=700)
    s.text(40, 64, f"11 × {b['nrow']} holes at 2.54 mm · looking down from above · "
                   "outlines are the real body sizes, to scale", size=12, fill=FG_FAINT)

    w, h = _grid(s, x0, y0, b, False, "TOP VIEW  ·  column A on the LEFT",
                 num_off=78, letters=False)
    if b["esp"]:
        _draw_esp(s, x0, y0, b, w)

    for ref, part, shape, pins in b["components"]:
        cx, cy, bw, bh, kind = body_box(ref, shape, pins,
                                        b["body_override"].get(ref))
        px_, py_ = x0 + cx * MM, y0 + cy * MM
        col = V12 if ref in ("D1", "D2", "C1", "C2", "U1", "R3") else (
            FG_DIM if shape.startswith("hdr") else SIG)
        if kind == "round":
            s.add(f'<circle cx="{px_:.1f}" cy="{py_:.1f}" r="{bw * MM / 2:.1f}" '
                  f'fill="{PANEL_2}" stroke="{col}" stroke-width="1.7"/>')
        else:
            s.rect(px_ - bw * MM / 2, py_ - bh * MM / 2, bw * MM, bh * MM,
                   fill=PANEL_2, stroke=col, sw=1.7, r=4)
        for hh, _pl, nn in pins:
            s.dot(*_xy(x0, y0, hh, b), PR - 2.2, colour(nn))
        wide = bw >= bh      # a part lying along a row: label it above, not beside
        if shape in ("dip8", "sip3", "rad") or (shape.startswith("ax") and wide):
            ly = py_ - bh * MM / 2 - 8
            s.text(px_, ly, ref, size=11, fill=col, weight=700, anchor="middle")
        elif shape.startswith("hdr"):
            if shape in ("hdr90L", "hdr90R", "hdr90T"):
                lx = px_ + (bw * MM / 2 + 7 if shape == "hdr90L" else -bw * MM / 2 - 7)
                s.text(lx, py_ + 4, ref, size=11, fill=col, weight=700,
                       anchor="start" if shape == "hdr90L" else "right")
            else:
                ly = py_ - bh * MM / 2 - 8
                s.rect(px_ - 15, ly - 12, 30, 17, fill=BG, stroke="none", r=3, op=0.85)
                s.text(px_, ly, ref, size=11, fill=col, weight=700, anchor="middle")
        else:
            lx, ly = px_ + bw * MM / 2 + 7, py_ + 4
            if lx > x0 + w - 6:
                s.text(px_ - bw * MM / 2 - 7, ly, ref, size=11, fill=col, weight=700,
                       anchor="right")
            else:
                s.text(lx, ly, ref, size=11, fill=col, weight=700)

    for i, L in enumerate(COLS):            # letters last, clear of the 90° bodies
        for ty in (y0 - 26, y0 + h + 56):
            s.text(x0 + i * P, ty, L, size=11.5, fill=FG_DIM, anchor="middle", weight=700)

    # -- parts list
    s.text(panel_x, 210, "WHAT GOES WHERE", size=13, fill=FG, weight=700)
    s.text(panel_x, 231, "a hole is a column letter + a row number (H27). "
                         "It is not a reference: hole C6 is not capacitor C6.",
           size=10.5, fill=FG_FAINT)
    yy = 262
    colx = [panel_x, panel_x + 44, panel_x + 236, panel_x + 432]
    for cxx, cell in zip(colx, ("ref", "part", "mounting", "holes")):
        s.text(cxx, yy, cell, size=10.5, fill=FG_DIM, weight=700)
    s.line(panel_x, yy + 7, panel_x + 740, yy + 7, stroke=EDGE, sw=1.2)
    yy += 24
    for ref, part, shape, pins in b["components"]:
        toks = [f"{h}={p}" for h, p, _n in pins]
        lines = _wrap(toks, 46)
        col = V12 if ref in ("D1", "D2", "C1", "C2", "U1", "R3") else FG
        s.text(colx[0], yy, ref, size=11, fill=col, weight=700)
        s.text(colx[1], yy, part, size=10.5, fill=FG)
        s.text(colx[2], yy, MOUNT[shape], size=10.5, fill=FG_DIM)
        for i, ln in enumerate(lines):
            s.text(colx[3], yy + i * 18, ln, size=10.5, fill=FG_DIM)
        yy += max(22, len(lines) * 18 + 4)

    yy += 18
    for title, lines, accent in notes:
        s.text(panel_x, yy, title, size=13, fill=accent, weight=700)
        for i, ln in enumerate(lines):
            s.text(panel_x, yy + 24 + i * 19, ln, size=11.5, fill=FG_DIM)
        yy += 24 + len(lines) * 19 + 22
    return s


def draw_solder(b, w_px, h_px, x0, y0, panel_x, cut_x=None):
    s = Svg(w_px, h_px)
    n = len(b["runs"])
    total = sum(run_length(hs) for _i, _x, hs, _y in b["runs"])
    s.text(40, 44, f"NODE B · {b['title']} · SOLDER SIDE — the {n} jumpers, "
                   "and where each one runs", size=15, fill=FG, weight=700)
    s.text(40, 64, "THE BOARD IS FLIPPED OVER: column A is now on the RIGHT. "
                   "Every wire below is on this face.", size=12, fill=WARN, weight=700)

    w, h = _grid(s, x0, y0, b, True, "BOTTOM VIEW  ·  mirrored  ·  column A on the RIGHT",
                 num_off=42)
    if b["esp"]:
        s.rect(x0 - 14, y0 - 3.1 * P, w + 28, 20.2 * P, fill="none", stroke=NODE_B,
               sw=1.4, r=8, dash="6 5", op=0.5)
        s.text(x0 + w / 2, y0 - 3.1 * P - 12, "ESP32 module is on the other side",
               size=10.5, fill=NODE_B, anchor="middle")

    for ref, _part, shape, pins in b["components"]:
        xs = [_xy(x0, y0, hh, b, True)[0] for hh, _p, _n in pins]
        ys = [_xy(x0, y0, hh, b, True)[1] for hh, _p, _n in pins]
        s.rect(min(xs) - 11, min(ys) - 11, max(xs) - min(xs) + 22, max(ys) - min(ys) + 22,
               fill="none", stroke=FG_FAINT, sw=1.3, r=5, dash="3 3", op=0.55)
        s.text(min(xs) - 14, min(ys) - 14, ref, size=9, fill=FG_FAINT, anchor="right")

    for rid, net, holes, _note in b["runs"]:
        colr = colour(net)
        pts = [_xy(x0, y0, hh, b, True) for hh in route_pts(b, rid, holes)]
        for a, bb in zip(pts, pts[1:]):
            s.line(a[0], a[1], bb[0], bb[1], stroke=BG, sw=7.0, cap="round")
        for a, bb in zip(pts, pts[1:]):
            s.line(a[0], a[1], bb[0], bb[1], stroke=colr, sw=3.0, cap="round")
        for hh in holes:
            s.dot(*_xy(x0, y0, hh, b, True), 5.2, colr)
    for hh in {h for _i, _n, hs, _x in b["runs"] for h in hs}:
        s.dot(*_xy(x0, y0, hh, b, True), 2.0, BG)

    # -- symbology, by wire colour
    used_c = {NETS[net][1] for _i, net, _h, _x in b["runs"]}
    s.text(panel_x, 170, f"SYMBOLOGY  ·  {len(used_c)} wire colours on this board",
           size=13, fill=FG, weight=700)
    yy = 198
    for name, (colr, what) in ((k, v) for k, v in WIRE.items() if k in used_c):
        s.line(panel_x, yy - 4, panel_x + 44, yy - 4, stroke=colr, sw=3.4, cap="round")
        s.dot(panel_x + 22, yy - 4, 5.2, colr)
        s.text(panel_x + 56, yy, name.lower(), size=11, fill=colr, weight=700)
        s.text(panel_x + 156, yy, what, size=11, fill=FG_DIM)
        yy += 23
    yy += 4
    s.dot(panel_x + 22, yy, 5.2, FG_DIM)
    s.text(panel_x + 56, yy + 4, "dot", size=11, fill=FG, weight=700)
    s.text(panel_x + 156, yy + 4, "the wire is soldered to this pad",
           size=11, fill=FG_DIM)
    yy += 24
    s.line(panel_x, yy, panel_x + 44, yy, stroke=FG_DIM, sw=3.0, cap="round")
    s.text(panel_x + 56, yy + 4, "line", size=11, fill=FG, weight=700)
    s.text(panel_x + 156, yy + 4, "insulated wire; crossings are fine",
           size=11, fill=FG_DIM)
    yy += 22
    s.text(panel_x, yy + 20, "One colour carries several nets. They are never joined —",
           size=10.5, fill=WARN)
    s.text(panel_x, yy + 37, "the cut list is what says which pads belong to which wire.",
           size=10.5, fill=WARN)

    # -- cut list
    cx0 = cut_x if cut_x else panel_x
    cy0 = yy + 74 if cut_x is None else 170
    s.text(cx0, cy0, f"CUT LIST  ·  {n} jumpers, {total:.0f} mm of wire",
           size=13, fill=FG, weight=700)
    cy0 += 26
    colx = [cx0, cx0 + 52, cx0 + 116, cx0 + 232, cx0 + 470]
    for cxx, cell in zip(colx, ("id", "net", "colour", "solder at", "cut")):
        s.text(cxx, cy0, cell, size=10.5, fill=FG_DIM, weight=700)
    s.line(cx0, cy0 + 7, cx0 + 540, cy0 + 7, stroke=EDGE, sw=1.2)
    for i, (rid, net, holes, _note) in enumerate(b["runs"]):
        ry = cy0 + 24 + i * 21
        colr = colour(net)
        for cxx, cell in zip(colx, (rid, net, NETS[net][1].lower(), "  ".join(holes),
                                    f"{run_length(holes):.0f} mm")):
            s.text(cxx, ry, cell, size=10.5, fill=colr if cxx in colx[1:3] else FG)
    return s


# --- figure entry points ------------------------------------------------------
def fig16_b_gauge_placement():
    check_umbilical()
    check(GAUGE)
    notes = [
        ("WHY THE PASSIVES SIT UNDER THE MODULE", [
            "A socketed DevKit leaves 8.5 mm of clear space beneath it. Columns B-K,",
            "rows 1-15 are nine columns of fifteen holes — 135 — and ten flat parts",
            "go there: C11 at the 3V3 pin, the clamps D4 and D5, the filters C6 and",
            "C7, R6, and the four button capacitors C13-C16. R5 sits at row 19 so the",
            "raw sensor line meets a resistor before it travels. Rows 16-18 stay",
            "empty — the PCB antenna is over them. C3 is the one part too tall."], NODE_B),
        ("WHY C3 IS 100 µF AND NOT 470", [
            "The Recom's maximum capacitive load is 220 µF, and that is the whole",
            "3.3 V rail: C3 plus C11 plus whatever the DevKit carries on its own",
            "3V3 pin. 470 µF is twice the limit, and the module hiccups into it at",
            "start-up — worst at the low input voltage of a cold crank. 100 µF in a",
            "Ø6.3 can leaves room, clears the connector shells, and still covers a",
            "transmit burst; C11 covers the fast edges at the pin."], WARN),
        ("BEFORE YOU SOLDER ANYTHING", [
            "Check BOTH pin rows on your module against the names drawn here.",
            "DevKit V1 clones exist with a different order, and this layout uses",
            "19 of the 30 pins — including the whole right-hand row for the OLED",
            "and the RTC, which is exactly where a clone is most likely to differ."],
         WARN),
    ]
    s = draw_placement(GAUGE, 1560, 1180, 250, 230, 700, notes)
    s.caption(s.h - 20, "Parts on this side, wires on the other. Only the sockets, the "
                        "connectors and the passives are soldered to the board.")
    return "16-node-b-gauge-placement", s


def fig17_b_gauge_solder():
    check(GAUGE)
    s = draw_solder(GAUGE, 1720, 1180, 300, 230, 720, cut_x=1130)
    s.caption(s.h - 20, "Strip 3 mm, tin both ends, lay the wire flat and solder it to every "
                        "pad the cut list names for it. Longest first, shortest last.")
    return "17-node-b-gauge-solder-side", s


def fig18_b_pwr_placement():
    check_umbilical()
    check(PWR)
    notes = [
        ("NO 12 V LEAVES THIS BOARD", [
            "D1, D2, C1 and the buck are here, the fuse inline in the cable; so is",
            "the L9637D, whose VS pin and 510 Ω pull-up are 12 V parts. The ILL",
            "divider is here too, so the cable carries the divided node, not the",
            "dash rheostat's 12 V. The umbilical is 3.3 V, GND, ILL, RX, TX."], V12),
        ("THIS BOARD MAKES THE ONLY 3.3 V IN NODE B", [
            "U1 is the 3.3 V version of the Recom, not the 5 V one. It feeds the",
            "L9637D's VCC locally and the gauge board up the umbilical, and the",
            "DevKit is fed on its 3V3 pin so its own regulator never carries the",
            "OLED. Nothing on Node B runs at 5 V, and B-PWR can be bench-tested",
            "on its own with nothing but 12 V."], V33),
        ("VERIFY THE L9637D PINOUT YOURSELF", [
            "Pin 1 is RX and pin 8 is LI, per Figure 2 of ST's datasheet (Doc ID 1765).",
            "Confirm it on the datasheet before you solder the SOIC-8 to the adapter:",
            "getting RX and LI the wrong way round puts the bus-side comparator on a",
            "logic pin. LO (pin 2) is left open on purpose — it has an internal",
            "pull-up and the L line is not used."], WARN),
    ]
    s = draw_placement(PWR, 1560, 1180, 250, 230, 700, notes)
    s.caption(s.h - 20, "A second 3 × 7 cm board, same part as the other two. Three cables, "
                        "three different edges.")
    return "18-node-b-pwr-placement", s


def fig19_b_pwr_solder():
    check(PWR)
    s = draw_solder(PWR, 1720, 1180, 300, 230, 720, cut_x=1130)
    s.caption(s.h - 20, "Same technique as Node A. The 12 V runs (yellow) are the ones to "
                        "inspect twice — a short there blows the fuse.")
    return "19-node-b-pwr-solder-side", s


def budget():
    """The gauge board's space budget, computed rather than typed.

    Area alone understates the problem: what is left after the connector rails is
    not one block but strips a few millimetres deep, and the three parts that had
    to fit are 8.5-10.5 mm deep. So this returns the strips as well as the totals.
    """
    W = len(COLS) * 2.54                      # 27.94 mm, the board's width
    region = 9 * 2.54                         # rows 19-27
    rail_w = 7 * 2.54                         # rows 21 and 24 carry connectors in E-L
    shell, body90 = 5.8, 4.2                  # vertical shell; 90-degree body on-board
    rails = 2 * shell * rail_w + body90 * W
    # the one free block: columns A-D, from above row 19 to the 90-degree bodies
    block_w = 4 * 2.54
    block_h = 8 * 2.54 - body90 / 2 + 1.27
    c3 = math.pi * 3.15 ** 2                  # O6.3 can, 100 uF/16 V
    # free row-bands outside that block, measured from row 19's centre
    bands = [("rows 19-20", 2.18 + 1.27),
             ("rows 22-23", 12.7 - shell / 2 - (5.08 + shell / 2)),
             ("rows 25-26", 20.32 - body90 / 2 - (12.7 + shell / 2))]
    power = {"C1 100 uF/35 V, O6.3 mm": (math.pi * 3.15 ** 2, 11.0),
             "U1 Recom R-78E3.3, 11.6 x 8.5": (98.6, 10.4),
             "U2 L9637D on a DIP-8 adapter": (94.5, 10.5),
             "D1, D2, C2, C4": (40.0, 3.2)}
    return dict(area=W * region, rails=rails, free=W * region - rails, c3=c3,
                block=block_w * block_h, block_w=block_w,
                block_left=block_w * block_h - c3,
                bands=bands, widest=max(b[1] for b in bands),
                power=power, power_sum=sum(v[0] for v in power.values()),
                tall=[v[1] for v in power.values() if v[1] > 5],
                tall_sum=sum(v[0] for k, v in power.items() if v[1] > 5))


def fig15_b_split():
    check_umbilical()
    """Why Node B is two boards: the space budget, drawn to scale."""
    s = Svg(1500, 860)
    s.text(40, 44, "NODE B  ·  WHY IT IS TWO BOARDS", size=15, fill=FG, weight=700)
    s.text(40, 64, "the gauge board measured 3 × 7 cm; this is what actually fits on it",
           size=12, fill=FG_FAINT)

    # --- left: the gauge board to scale (1 mm = SC px)
    SC = 7.2
    bx, by = 70, 130
    BW, BH = 27.94 * SC, 68.58 * SC
    s.rect(bx, by, BW, BH, fill=PANEL, stroke=EDGE, sw=1.6, r=4)
    s.text(bx, by - 14, "B-GAUGE, 27.9 × 68.6 mm, to scale", size=11, fill=FG, weight=700)

    def band(y_mm, h_mm, col, lab, op=0.16, sub=None):
        yy = by + y_mm * SC
        s.rect(bx + 2, yy, BW - 4, h_mm * SC, fill=col, stroke=col, sw=1.3, r=3, op=op)
        s.text(bx + BW + 14, yy + h_mm * SC / 2 + 4, lab, size=10.5, fill=col,
               weight=700)
        if sub:
            s.text(bx + BW + 14, yy + h_mm * SC / 2 + 19, sub, size=9.5, fill=FG_FAINT)

    band(0.0, 38.1, NODE_B, "ESP32, rows 1-15", 0.16,
         "8.5 mm under it: flat parts only")
    band(38.1, 7.6, WARN, "rows 16-18", 0.13, "antenna — kept empty")
    band(45.7, 22.9, NODE_A, "rows 19-27", 0.13, "the only full-height space")
    for y_mm, hh, lab in ((45.7 + 2.18, 5.8, "J3 · J5"), (45.7 + 9.8, 5.8, "J2 OLED"),
                          (45.7 + 17.4, 4.2, "J1 · J4")):
        yy = by + y_mm * SC
        s.rect(bx + 2 + BW * 0.36, yy, BW * 0.62, hh * SC, fill=FG_DIM, stroke=FG_DIM,
               sw=1.2, r=2, op=0.30)
        s.text(bx + 2 + BW * 0.67, yy + hh * SC / 2 + 4, lab, size=9.5, fill=FG,
               anchor="middle", weight=700)
    cy = by + (45.7 + 7.62) * SC
    s.add(f'<circle cx="{bx + 2 + BW * 0.16:.1f}" cy="{cy:.1f}" r="{3.15 * SC:.1f}" '
          f'fill="{PANEL_2}" stroke="{SIG}" stroke-width="1.7"/>')
    s.text(bx + 2 + BW * 0.16, cy + 4, "C3", size=10, fill=SIG, anchor="middle", weight=700)

    # --- middle: the arithmetic
    ax = 430
    s.text(ax, 150, "THE ARITHMETIC", size=13, fill=FG, weight=700)
    bg = budget()
    rows = [
        ("clear of the module", "rows 19-27", f"{bg['area']:.0f} mm²"),
        ("three connector rails", "shells at rows 21, 24, 27", f"-{bg['rails']:.0f} mm²"),
        ("one usable block", "cols A-D, rows 19-26", f"{bg['block']:.0f} mm²"),
        ("C3, the 3.3 V reservoir", "Ø6.3 mm can", f"-{bg['c3']:.0f} mm²"),
        ("left in that block", f"{bg['block_w']:.0f} mm wide", f"{bg['block_left']:.0f} mm²"),
    ]
    for i, (a, bb, c) in enumerate(rows):
        yy = 180 + i * 24
        col = WARN if i == 4 else FG
        s.text(ax, yy, a, size=11, fill=col if i in (2, 4) else FG_DIM,
               weight=700 if i in (2, 4) else 400)
        s.text(ax + 172, yy, bb, size=10.5, fill=FG_FAINT)
        s.text(ax + 420, yy, c, size=11, fill=col, anchor="right", weight=700)
    s.line(ax, 180 + 3 * 24 + 8, ax + 420, 180 + 3 * 24 + 8, stroke=EDGE, sw=1.2)

    lines = [f"{k:<32}{v[0]:5.0f} mm²   {v[1]:>4.1f} mm deep"
             for k, v in bg["power"].items()] + [
        "",
        f"{bg['power_sum']:.0f} mm² against {bg['block_left']:.0f} mm², and the block is only",
        f"{bg['block_w']:.0f} mm wide. Everywhere else the free strips are",
        f"at most {bg['widest']:.1f} mm deep, and {len(bg['tall'])} of these parts",
        f"are {min(bg['tall']):.1f}-{max(bg['tall']):.1f} mm deep. Shape, not just area."]
    s.card(ax, 316, 440, "WHAT WILL NOT FIT, AND WHY",
           lines, accent=WARN, title_size=12, line_size=11)

    s.card(ax, 570, 420, "WHAT WAS SETTLED INSTEAD",
           ["The 12 V half moves to its own board at the i59.",
            "The gauge board keeps the ESP32, the connectors,",
            "C3, and ten flat parts under the module.",
            "23 off-board wires on three rails of 11; C3 shadows",
            "the left end of two of them."],
           accent=NODE_A, title_size=12, line_size=11)

    # --- right: the two boards and the umbilical
    rx = 880
    s.text(rx, 150, "THE RESULT", size=13, fill=FG, weight=700)
    s.card(rx, 176, 260, "B-PWR  ·  at the i59",
           ["D1 D2 C1 C2 U1 C4 — 12 V to 3.3 V", "R3 R4 — the ILL divider",
            "U2 L9637D + R7 C8 C9 C10", "11 × 27 holes"],
           accent=V12, title_size=12, line_size=11)
    s.card(rx + 330, 176, 260, "B-GAUGE  ·  in the clock bay",
           ["ESP32 DevKit V1, fed on its 3V3 pin", "C3 C11 D4 C6 R5 R6 C7 D5",
            "C13-C16 at the buttons", "J1 J2 J3 J4 J5 · 11 × 27 holes"],
           accent=NODE_B, title_size=12, line_size=11)
    uy = 330
    s.text(rx + 295, uy - 10, "umbilical", size=11, fill=FG, anchor="middle", weight=700)
    for i, (lab, net) in enumerate((("+3.3 V", "V33"), ("GND", "GND"),
                                    ("ILL divided", "ILL"), ("K-RX", "KRX"),
                                    ("K-TX", "KTX"))):
        yy = uy + 14 + i * 22
        s.line(rx + 190, yy, rx + 400, yy, stroke=colour(net), sw=2.4)
        s.text(rx + 295, yy - 6, lab, size=10.5, fill=colour(net), anchor="middle",
               weight=700)
    s.text(rx + 295, uy + 14 + 5 * 22 + 12, "One rail. The DevKit is fed on its 3V3 pin,",
           size=10.5, fill=FG_FAINT, anchor="middle")
    s.text(rx + 295, uy + 14 + 5 * 22 + 29, "so its own regulator is out of the circuit.",
           size=10.5, fill=FG_FAINT, anchor="middle")

    s.card(rx, 540, 590, "WHAT THE SPLIT BUYS, BEYOND SPACE",
           ["No 12 V reaches the clock bay — the gauge board's highest net is 3.3 V.",
            "The K-line transceiver sits where the K wire arrives, at the i59.",
            "The dash rheostat's 12 V is divided at the source, so the cable in the",
            "console carries a 2 V signal instead of a 12 V one.",
            "Each board can be bench-tested on its own before they are joined."],
           accent=NODE_A, title_size=12, line_size=11)

    s.caption(s.h - 20, "The 3 × 7 cm board was measured, not assumed. Everything above "
                        "follows from that measurement.")
    return "15-node-b-two-boards", s


def _panel(s, x, y, w, h, title, lines, accent):
    s.rect(x, y, w, h, fill=PANEL, stroke=accent, sw=1.6, r=10)
    s.text(x + 16, y + 26, title, size=12.5, fill=accent, weight=700)
    for i, ln in enumerate(lines):
        s.text(x + 16, y + h - 14 - (len(lines) - 1 - i) * 17, ln, size=10.5, fill=FG_DIM)
    return x + 16, y + 44


def fig20_b_technique():
    """The six things Node B needs that Node A did not."""
    s = Svg(1520, 880)
    s.text(40, 44, "NODE B  ·  THE SIX THINGS NODE A DID NOT NEED", size=15, fill=FG,
           weight=700)
    s.text(40, 64, "mounting and soldering technique is unchanged — see Fig. 14",
           size=12, fill=FG_FAINT)

    W, H, GX, GY = 460, 350, 20, 20
    X0, Y0 = 40, 100

    # 1 -- the SOIC-8 on its adapter
    px, py = _panel(s, X0, Y0, W, H, "1 · SOIC-8 ONTO THE ADAPTER", [
        "Flux, then drag one bead of solder along each row of four.",
        "Wick the bridges away; do not try to place solder per pin.",
        "Then solder 2 × 4 male pins into the DIP side, pointing down."], SIG)
    ax, ay = px + 40, py + 60
    s.rect(ax, ay, 150, 96, fill=PANEL_2, stroke=SIG, sw=1.6, r=4)
    s.text(ax + 75, ay - 8, "adapter, DIP side up", size=10, fill=FG_FAINT, anchor="middle")
    for i in range(4):
        s.dot(ax + 22, ay + 18 + i * 22, 6, PAD)
        s.dot(ax + 128, ay + 18 + i * 22, 6, PAD)
    s.dot(ax + 22, ay + 18, 9, "none")
    s.add(f'<circle cx="{ax + 22}" cy="{ay + 18}" r="11" fill="none" stroke="{WARN}" '
          f'stroke-width="1.6"/>')
    s.text(ax + 168, ay + 22, "pin 1 — the dot on the", size=10.5, fill=WARN)
    s.text(ax + 168, ay + 38, "chip and the square pad", size=10.5, fill=WARN)
    s.text(ax + 168, ay + 54, "on the adapter must agree", size=10.5, fill=WARN)
    for i, (n, lab) in enumerate((("1", "RX"), ("2", "LO"), ("3", "VCC"), ("4", "TX"))):
        s.text(ax + 40, ay + 22 + i * 22, f"{n} {lab}", size=10, fill=FG)
    for i, (n, lab) in enumerate((("8", "LI"), ("7", "VS"), ("6", "K"), ("5", "GND"))):
        s.text(ax + 116, ay + 22 + i * 22, f"{lab} {n}", size=10, fill=FG, anchor="right")

    # 2 -- verify the pinout
    px, py = _panel(s, X0 + W + GX, Y0, W, H, "2 · VERIFY THE PINOUT BEFORE THE IRON", [
        "ST's datasheet is Doc ID 1765. Open Figure 2 and read the pin",
        "names off it yourself. Swapping RX and LI puts a bus comparator",
        "on a logic pin — it will not blow up, and it will never work."], WARN)
    rows = [("VS  pin 7", "12 V, from VBAT on this board"),
            ("VCC pin 3", "3.3 V, from U1 on this board"),
            ("K   pin 6", "to OBD pin 7, 510 Ω up to VS"),
            ("RX  pin 1", "output to the ESP32's RX2 (GPIO16)"),
            ("TX  pin 4", "input from the ESP32's TX2 (GPIO17)"),
            ("LI  pin 8", "tied to VS — idle, LO stays off"),
            ("LO  pin 2", "left open — internal pull-up to VCC")]
    for i, (a, bb) in enumerate(rows):
        s.text(px, py + 14 + i * 24, a, size=11, fill=WARN, weight=700)
        s.text(px + 96, py + 14 + i * 24, bb, size=10.5, fill=FG_DIM)

    # 3 -- the bench test that proves it
    px, py = _panel(s, X0 + 2 * (W + GX), Y0, W, H, "3 · THE TEST THAT PROVES IT", [
        "Do this on the bench, with the K wire going nowhere,",
        "before B-PWR is ever plugged into the car."], NODE_A)
    steps = ["12 V on J6 pin 1, GND on J6 pin 2 — nothing else",
             "J8 pin 1 reads 3.30 V ±0.07 — the buck is alive",
             "U2 pin 3 reads 3.3 V, U2 pin 7 reads ~11.7 V",
             "TX left open: K idles at ~11.6 V through R7",
             "and RX sits high, 3.0-3.3 V",
             "pull TX to ground: K falls below 1 V, RX follows",
             "let TX go: both return high",
             "any step that fails is a wiring fault, not the chip"]
    for i, ln in enumerate(steps):
        s.dot(px + 8, py + 8 + i * 24, 9, PANEL_2)
        s.text(px + 8, py + 12 + i * 24, str(i + 1), size=10, fill=NODE_A,
               anchor="middle", weight=700)
        s.text(px + 26, py + 12 + i * 24, ln, size=10.5, fill=FG_DIM)

    # 4 -- C3 and the shells
    px, py = _panel(s, X0, Y0 + H + GY, W, H, "4 · C3 AND THE CONNECTOR SHELLS", [
        "C3 is the only tall part on the gauge board and it lives in the",
        "one column band — A to D — where rows 21 and 24 carry no",
        "connector. Dry-fit every shell before C3 goes in."], WARN)
    gx, gy, sc = px + 30, py + 20, 7.0
    s.rect(gx, gy, 27.94 * sc, 22.9 * sc, fill=PANEL_2, stroke=EDGE, sw=1.4, r=3)
    for y_mm, hh, lab in ((2.18, 5.8, "J3 · J5"), (9.8, 5.8, "J2"), (17.4, 4.2, "J1 · J4")):
        s.rect(gx + 27.94 * sc * 0.38, gy + y_mm * sc, 27.94 * sc * 0.60, hh * sc,
               fill=FG_DIM, stroke=FG_DIM, sw=1.1, r=2, op=0.30)
        s.text(gx + 27.94 * sc * 0.68, gy + (y_mm + hh / 2) * sc + 4, lab, size=9.5,
               fill=FG, anchor="middle", weight=700)
    s.add(f'<circle cx="{gx + 3.81 * sc:.1f}" cy="{gy + 7.62 * sc:.1f}" '
          f'r="{4 * sc:.1f}" fill="none" stroke="{SIG}" stroke-width="1.7"/>')
    s.text(gx + 3.81 * sc, gy + 7.62 * sc + 4, "C3", size=10, fill=SIG, anchor="middle",
           weight=700)
    s.text(gx + 27.94 * sc + 14, gy + 30, "rows 19-27, to scale", size=10, fill=FG_FAINT)
    s.text(gx + 27.94 * sc + 14, gy + 48, "if C3 fouls a shell,", size=10.5, fill=WARN)
    s.text(gx + 27.94 * sc + 14, gy + 64, "fit 47 µF/16 V, Ø5", size=10.5, fill=WARN)

    # 5 -- the DS3231 outside
    px, py = _panel(s, X0 + W + GX, Y0 + H + GY, W, H, "5 · THE DS3231 LIVES OUTSIDE", [
        "Four wires on J4 and a 3D-printed case of its own. It is a bare",
        "board with a coin cell: loose in a console it shorts against trim",
        "clips, and its cell has to stay reachable."], NODE_C)
    for i, ln in enumerate([
            "print a closed case: cell hatch on one face,",
            "strain relief for the cable on the other",
            "",
            "fit a CR2032 and disable the module's charger:",
            "at 3.3 V its diode never conducts, so an LIR2032",
            "would only ever discharge — and only to +60 °C",
            "",
            "mount it away from heat, and keep the cable",
            "to 20 cm — I2C with the module's own pull-ups"]):
        s.text(px, py + 12 + i * 22, ln, size=10.5, fill=FG_DIM)

    # 6 -- the umbilical
    px, py = _panel(s, X0 + 2 * (W + GX), Y0 + H + GY, W, H, "6 · THE UMBILICAL", [
        "Five wires, 15-20 cm, one latching connector at each end.",
        "Make it before either board is mounted, and ring it out",
        "pin to pin: a swap here reaches both boards at once."], V5)
    for i, (lab, net, note) in enumerate((
            ("1", "V33", "+3.3 V      B-PWR  ->  gauge"),
            ("2", "GND", "GND         common"),
            ("3", "ILL", "ILL node    B-PWR  ->  gauge"),
            ("4", "KRX", "K-RX        B-PWR  ->  gauge"),
            ("5", "KTX", "K-TX        gauge  ->  B-PWR"))):
        yy = py + 24 + i * 30
        s.line(px, yy, px + 40, yy, stroke=colour(net), sw=3.2, cap="round")
        s.text(px + 52, yy + 4, lab, size=11, fill=colour(net), weight=700)
        s.text(px + 72, yy + 4, note, size=10.5, fill=FG_DIM)
    s.text(px, py + 24 + 5 * 30 + 14, "Every wire runs one way, B-PWR to gauge, except",
           size=10.5, fill=WARN)
    s.text(px, py + 24 + 5 * 30 + 30, "K-TX. There is no 5 V anywhere on Node B.",
           size=10.5, fill=WARN)

    s.caption(s.h - 18, "Everything else — sockets, retainers, the mirror rule, making a "
                        "jumper — is the same as Node A.")
    return "20-node-b-technique", s


# --- Figs 4 and 5: the coarse views, redrawn for two boards --------------------
def fig04_node_b_spatial():
    s = Svg(1360, 700)
    s.text(40, 44, "NODE B  ·  SPATIAL LAYOUT", size=15, fill=FG, weight=700)
    s.text(40, 64, "solid border = on a board   ·   dashed = off the boards, reached by "
                   "cable   ·   why it is split: Fig. 15", size=12, fill=FG_FAINT)

    def board(x, y, w, h, title, sub, accent, zones):
        s.rect(x, y, w, h, fill="none", stroke=accent, sw=1.8, r=12)
        s.text(x + 16, y + 28, title, size=12.5, fill=accent, weight=700)
        s.text(x + 16, y + 48, sub, size=10.5, fill=FG_FAINT)
        zy = y + 64
        for lbl, note, col in zones:
            hh = 40 if note else 32
            s.rect(x + 16, zy, w - 32, hh, fill=col, stroke=col, sw=1.2, r=6, op=0.14)
            s.text(x + 28, zy + (18 if note else 20), lbl, size=11.5, fill=FG)
            if note:
                s.text(x + 28, zy + 33, note, size=10, fill=FG_FAINT)
            zy += hh + 8
        return zy

    board(40, 96, 400, 500, "B-PWR — at the i59 adapter",
          "11 × 27 holes; everything that touches 12 V", V12,
          [("D1 SB1100 · D2 P6KE20A · C1 100 µF/35 V", "reverse polarity, transients, reserve", V12),
           ("U1 Recom R-78E3.3-1.0 · C2 · C4", "12 V → 3.3 V, the only rail", NODE_A),
           ("R3 20k / R4 3.3k", "ILL divider, at the source", SIG),
           ("U2 L9637D on a SOIC-DIP adapter", "R7 510 Ω · C8 1 nF · C9 · C10", V12),
           ("J6 car  ·  J7 K-line  ·  J8 umbilical", None, EDGE)])

    board(470, 96, 400, 500, "B-GAUGE — in the OEM clock bay",
          "11 × 27 holes; nothing above 3.3 V", NODE_B,
          [("ESP32 DevKit V1 — socketed", "cols A and L, rows 1-15; passives underneath", NODE_B),
           ("C3 100 µF/16 V · C11 10 µF X7R", "3.3 V reservoir and decoupling at the pin", NODE_A),
           ("D4 BAT85 · C6 1 µF", "ILL clamp and filter, at GPIO35", SIG),
           ("R5 · R6 · D5 · C7", "sensor divider, clamp and filter, at GPIO34", SIG),
           ("J1 umbilical · J2 OLED · J3 buttons", "J4 RTC · J5 sensor", EDGE)])

    uy = 300
    s.line(440, uy, 470, uy, stroke=V5, sw=2.2)
    s.text(455, uy - 10, "6", size=11, fill=V5, anchor="middle", weight=700)

    px, py, pw, ph = 900, 140, 420, 300
    s.rect(px, py, pw, ph, fill="none", stroke=EDGE, sw=1.5, r=12, dash="7 6")
    s.text(px + 16, py + 26, "OFF THE BOARDS — CABLE ONLY", size=12, fill=FG_DIM, weight=700)
    s.card(px + 16, py + 44, pw - 32, "OLED SSD1322",
           ["in the bezel, retained by its screws"], accent=EDGE, title_size=13,
           line_size=11, title_color=FG)
    s.card(px + 16, py + 122, pw - 32, "DS3231 RTC",
           ["in a 3D-printed case of its own,", "CR2032 cell, away from heat"],
           accent=NODE_C, title_size=13, line_size=11, title_color=FG)
    s.card(px + 16, py + 216, pw - 32, "OEM buttons",
           ["contact pads on the bezel carrier"], accent=EDGE, title_size=13,
           line_size=11, title_color=FG)

    for i, (lbl, col) in enumerate((("->  i59 connector (IG, GND, ILL)", V12),
                                    ("->  OBD pin 7  (K-line, 1.2-1.5 m)", SIG),
                                    ("->  B-GAUGE, five-wire umbilical", V5))):
        yy = 480 + i * 34
        s.line(px, yy, px + 40, yy, stroke=col, sw=1.8)
        s.text(px + 50, yy + 4, lbl, size=12, fill=col)
    s.text(px, 596, "The 12 V cables stop at B-PWR. Only the umbilical reaches",
           size=10.5, fill=FG_FAINT)
    s.text(px, 614, "the clock bay, and its highest voltage is 3.3 V.", size=10.5, fill=FG_FAINT)
    return "04-node-b-spatial-layout", s


def fig05_node_b_grid():
    pitch, cols = 18, 11
    x0, y0 = 110, 140
    gw, gh = (cols - 1) * pitch, 26 * pitch
    s = Svg(1180, y0 + gh + 90)
    s.text(40, 44, "NODE B  ·  PERFBOARD GRID PLAN, BOTH BOARDS", size=15, fill=FG,
           weight=700)
    s.text(40, 64, "zones only — the hole-by-hole layouts are Figs. 16 and 18",
           size=12, fill=FG_FAINT)

    def plan(gx, title, accent, zones, rows_used):
        s.rect(gx - 14, y0 - 14, gw + 28, gh + 28, fill=PANEL, stroke=accent, sw=1.6, r=8)
        s.text(gx - 14, y0 - 26, title, size=12.5, fill=accent, weight=700)
        for c in range(cols):
            for r in range(27):
                s.dot(gx + c * pitch, y0 + r * pitch, 1.6, EDGE)
        for r in (1, 10, 19, 27):
            s.text(gx - 26, y0 + (r - 1) * pitch + 4, str(r), size=10, fill=FG_FAINT,
                   anchor="end")
        for r1, r2, label, note, color in zones:
            zy = y0 + (r1 - 1) * pitch - 7
            zh = (r2 - r1) * pitch + 14
            s.rect(gx - 8, zy, gw + 16, zh, fill=color, stroke=color, sw=1.2, r=6, op=0.14)
            cyy = zy + zh / 2
            s.line(gx + gw + 10, cyy, gx + gw + 34, cyy, stroke=color, sw=1.2)
            s.text(gx + gw + 42, cyy + (-2 if note else 4), label, size=11, fill=FG)
            if note:
                s.text(gx + gw + 42, cyy + 14, note, size=10, fill=FG_FAINT)
        s.text(gx - 14, y0 + gh + 40, rows_used, size=10.5, fill=FG_FAINT)

    plan(x0, "B-GAUGE", NODE_B,
         [(1, 15, "ESP32 DevKit V1 — socketed", "cols A and L; flat parts underneath", NODE_B),
          (16, 18, "empty", "module body and PCB antenna", EDGE),
          (19, 19, "R5, sensor upper leg", None, SIG),
          (20, 22, "J3 buttons 5p · J5 sensor 2p, on row 21",
           "C3 100 µF/16 V at A23-C23", NODE_A),
          (24, 24, "J2 OLED 7p, cols E-L", None, EDGE),
          (27, 27, "90° headers: J1 umbilical 5p · J4 RTC 4p", None, EDGE)],
         "47 of 297 holes used · 10 of 33 rail positions spare")

    plan(x0 + 560, "B-PWR", V12,
         [(1, 1, "90° header: J7 K-line 2p (top edge)", None, EDGE),
          (3, 8, "U2 L9637D on its adapter · C9",
           "J6 car in 3p on the left edge, rows 5-7", V12),
          (9, 16, "D1 · D2 · C1 · C10 · R7 · C8", None, V12),
          (18, 19, "C2 · R3 20k", None, SIG),
          (20, 26, "U1 Recom R-78E3.3-1.0 · R4 · C4",
           "J8 umbilical 5p on the right edge, rows 20-24", NODE_A)],
         "43 of 297 holes used · snap it shorter if the console demands it")

    s.caption(s.h - 20, "Both boards are the same 3 × 7 cm part. B-GAUGE's rails are rows "
                        "21, 24 and 27; B-PWR uses three different edges.")
    return "05-node-b-grid-plan", s
