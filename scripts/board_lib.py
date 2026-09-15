"""Shared board geometry, the DevKit pin order, and the structural checks.

Both node build scripts import this. The ESP32 header order lives here and
nowhere else: it was duplicated in two files and wrong in both until v0.1.8,
which is exactly the failure mode one copy prevents.

    Column letters skip I so it cannot be read as a 1.
    A hole is a letter plus a row number (C13). It is not a reference designator.
"""
import math

COLS = "ABCDEFGHJKL"
PITCH = 2.54                      # mm
BOARD_W = len(COLS) * PITCH       # 27.94 mm, an 11-column 3 x 7 cm board

# --- DOIT ESP32 DevKit V1, 30 pins, ROW 1 = THE MICRO-USB END ----------------
# Verified against four machine-readable sources (KiCad symbol + footprint with
# a USB silk marker, a Fritzing part, and Wokwi's board geometry): VIN faces
# 3V3 at the USB end, EN faces D23 at the antenna end. Reading a pinout image
# from the wrong end reverses the right-hand column and nothing else, which is
# how this was wrong from v0.1.0 to v0.1.7.
ESP_L = ["VIN", "GND", "D13", "D12", "D14", "D27", "D26", "D25", "D33", "D32",
         "D35", "D34", "VN", "VP", "EN"]
ESP_R = ["3V3", "GND", "D15", "D2", "D4", "RX2", "TX2", "D5", "D18", "D19",
         "D21", "RX0", "TX0", "D22", "D23"]

GPIO_AT = {}                      # "L6" -> "RX2", "A9" -> "D33"
for _r, (_l, _rr) in enumerate(zip(ESP_L, ESP_R), start=1):
    GPIO_AT[f"A{_r}"] = _l
    GPIO_AT[f"L{_r}"] = _rr

MODULE_ROWS = 15                  # pin rows the module occupies
MODULE_BODY_ROW = 18              # its body and PCB antenna reach this far
MODULE_CLEAR_MM = 8.5             # clearance under a socketed module


def ci(hole):
    return COLS.index(hole[0])


def ri(hole):
    return int(hole[1:])


def xy_mm(hole):
    """Centre of a hole in mm, measured from column A / row 1."""
    return ci(hole) * PITCH, (ri(hole) - 1) * PITCH


# --- component body model ----------------------------------------------------
# Only real dimensions go here. Anything absent falls back to a lead-span box,
# which is why every part that is bigger than its leads must be listed.
SHAPE_BODY = {                    # shape -> (across columns, across rows) in mm
    "sip3": (11.6, 8.5),          # Recom R-78E, datasheet L x W
    "dip8": (9.0, 10.5),          # SOIC-8 on a DIP-8 adapter, in its socket
}
LEAD_PAD = 3.0                    # a flat axial part is ~3 mm wider than its holes
AXIAL_DIA = {                     # body diameter of the through-hole parts used
    "DO-41": 2.6, "DO-15": 3.6, "ceramic": 3.2,
}
HDR_SHELL = 5.8                   # JST-XH housing, across the pin axis
HDR_BODY90 = 2.5                  # a 90-degree header's body; the pins bend off the edge


def body_box(ref, shape, pins, override=None):
    """(cx, cy, w, h, kind) in mm. The body, not the lead span."""
    cs = [ci(h) for h, *_ in pins]
    rs = [ri(h) for h, *_ in pins]
    cx = (min(cs) + max(cs)) / 2 * PITCH
    cy = ((min(rs) + max(rs)) / 2 - 1) * PITCH
    span_c = (max(cs) - min(cs)) * PITCH
    span_r = (max(rs) - min(rs)) * PITCH
    if override:
        return (cx, cy) + tuple(override)
    if shape in SHAPE_BODY:
        w, h = SHAPE_BODY[shape]
        return cx, cy, w, h, "rect"
    if shape.startswith("hdr"):
        w = HDR_BODY90 if "90" in shape else HDR_SHELL
        if span_c >= span_r:
            return cx, cy, span_c + 2.0, w, "rect"
        return cx, cy, w, span_r + 2.0, "rect"
    if shape == "vert":
        return cx, cy, 3.0, span_r + 3.0, "rect"
    if span_c >= span_r:
        return cx, cy, span_c + LEAD_PAD, AXIAL_DIA["ceramic"], "rect"
    return cx, cy, AXIAL_DIA["ceramic"], span_r + LEAD_PAD, "rect"


def _extent(b):
    cx, cy, w, h, _k = b
    return cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2


def overlap(a, b, slack=0.0):
    """Do two body boxes intersect, allowing `slack` mm of tolerance?"""
    ax0, ax1, ay0, ay1 = _extent(a)
    bx0, bx1, by0, by1 = _extent(b)
    return (ax0 < bx1 - slack and bx0 < ax1 - slack and
            ay0 < by1 - slack and by0 < ay1 - slack)


def check_bodies(board, bodies, heights, min_gap=0.4):
    """No two parts may occupy the same space, and nothing may foul the module.

    `check()` only ever tested hole occupancy, so five parts on Node A shared
    the same cubic centimetre from v0.1.6 until this check existed. `heights`
    is ref -> body height in mm; a part whose body reaches into the module's
    footprint must be shorter than the clearance underneath it.
    """
    bad = []
    items = list(bodies.items())
    for i, (ref_a, a) in enumerate(items):
        for ref_b, b in items[i + 1:]:
            if overlap(a, b, -min_gap):
                bad.append(f"{ref_a} and {ref_b} bodies overlap or sit closer "
                           f"than {min_gap} mm")
    for ref, b in bodies.items():
        x0, x1, _y0, _y1 = _extent(b)
        if not (x0 > -2.6 and x1 < BOARD_W + 0.1):
            bad.append(f"{ref} hangs more than a hole off the board edge")
    assert not bad, f"{board['key']}: " + "; ".join(bad)
    if not board["esp"]:
        return
    mod_far = (MODULE_BODY_ROW - 1) * PITCH
    for ref, b in bodies.items():
        _x0, _x1, y0, _y1 = _extent(b)
        if y0 < mod_far + min_gap:
            h = heights.get(ref)
            assert h is not None and h <= MODULE_CLEAR_MM, (
                f"{board['key']}: {ref}'s body reaches row "
                f"{y0 / PITCH + 1:.2f}, inside the module's footprint, and it "
                f"is {h if h else 'un-declared'} mm tall against "
                f"{MODULE_CLEAR_MM} mm of clearance")
