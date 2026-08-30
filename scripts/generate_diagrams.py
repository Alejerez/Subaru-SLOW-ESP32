#!/usr/bin/env python3
"""
Source of truth for every figure in docs/01-hardware/diagrams/.

The figures are *drawn here*, not extracted from anywhere: run this script and the
PNGs are rebuilt. Only the PNGs are committed -- this file is the editable source.

    python3 scripts/generate_diagrams.py

Requires playwright (chromium) for the SVG -> PNG step.
"""
import pathlib
import subprocess
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from diagram_lib import (  # noqa: E402
    Svg, tw, marker_for,
    BG, PANEL, PANEL_2, EDGE, GRID, FG, FG_DIM, FG_FAINT,
    V12, V5, V33, GND, SIG, RADIO, NODE_A, NODE_B, WARN,
)

OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "01-hardware" / "diagrams"
SCALE = 2  # device pixel ratio for the PNG render


# ---------------------------------------------------------------------------
# Fig. 1 -- system architecture
# ---------------------------------------------------------------------------
def fig01_system_architecture():
    s = Svg(1140, 400)
    s.text(40, 44, "SYSTEM ARCHITECTURE", size=15, fill=FG, weight=700)
    s.text(40, 64, "two independent ESP32 nodes, linked only by radio", size=12, fill=FG_FAINT)

    ax, bx, w = 40, 710, 390
    _, ay, _, ah = s.card(ax, 96, w, "NODE A  ·  CENTRAL LOCKING",
                          ["ESP32 · next to the BIU (A-pillar)",
                           "acts on the lock/unlock lines"], accent=NODE_A)
    s.card(bx, 96, w, "NODE B  ·  GAUGE",
           ["ESP32 · centre console (clock bay)",
            "reads the ECU over SSM2"], accent=NODE_B)

    # radio link, both directions
    mid = (ax + w + bx) / 2
    s.text(mid, 118, "ESP-NOW · 2.4 GHz", size=12, fill=RADIO, anchor="middle", weight=700)
    s.line(bx - 10, 140, ax + w + 10, 140, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")
    s.text(mid, 158, "speed · every 100-200 ms", size=10.5, fill=FG_FAINT, anchor="middle")
    s.line(ax + w + 10, 176, bx - 10, 176, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")
    s.text(mid, 194, "lock mode · on button press", size=10.5, fill=FG_FAINT, anchor="middle")

    y2 = ay + ah + 34
    s.line(ax + w / 2, ay + ah, ax + w / 2, y2 - 6, stroke=EDGE, marker="arw")
    s.line(bx + w / 2, ay + ah, bx + w / 2, y2 - 6, stroke=EDGE, marker="arw")
    s.card(ax, y2, w, "WIRED INTERFACE",
           ["OUT  relay CH1 -> BIU pin 15  (lock)",
            "OUT  relay CH2 -> BIU pin 29  (unlock)",
            "IN   IG 12 V  (supply + ign. sense)",
            "IN   OEM ON/OFF switch -> GPIO27"], accent=EDGE, title_size=12,
           title_color=FG_DIM)
    s.card(bx, y2, w, "WIRED INTERFACE",
           ["i59 connector: IG · GND · ILL",
            "K-line -> OBD pin 7  (SSM2, 10400 bd)",
            "OLED SSD1322 SPI · RTC DS3231 I2C",
            "4 OEM buttons -> GPIO 32/33/25/26"], accent=EDGE, title_size=12,
           title_color=FG_DIM)

    s.caption(s.h - 18, "No cable runs between the two nodes. Speed is measured by Node B and "
                        "sent over the air; the lock mode travels back the same way.")
    return "01-system-architecture", s


# ---------------------------------------------------------------------------
# Fig. 2 -- Node B power stage
# ---------------------------------------------------------------------------
def _gnd_symbol(s, x, y, color=GND):
    s.line(x, y, x, y + 10, stroke=color, sw=1.6)
    s.line(x - 13, y + 10, x + 13, y + 10, stroke=color, sw=2.0)
    s.line(x - 8, y + 15, x + 8, y + 15, stroke=color, sw=2.0)
    s.line(x - 3.5, y + 20, x + 3.5, y + 20, stroke=color, sw=2.0)


def fig02_node_b_power():
    s = Svg(1140, 520)
    s.text(40, 44, "NODE B  ·  POWER STAGE  (IG 12 V -> 5 V)", size=15, fill=FG, weight=700)
    s.text(40, 64, "same stage is used on Node A", size=12, fill=FG_FAINT)

    # --- 12 V rail
    yr = 150
    s.card(40, 112, 160, "i59 pin 8", ["IG 12 V, switched"], accent=V12, title_size=13, line_size=11)
    s.line(200, yr, 940, yr, stroke=V12, sw=2.0)
    s.label_box(265, yr - 16, "F1 · fuse 2 A", anchor="center")
    s.label_box(400, yr - 16, "D1 · SS34", anchor="center")
    s.text(455, yr - 24, "VBAT", size=10.5, fill=FG_FAINT)

    ygnd = 268
    for x, lbl in ((545, "D2 · SMAJ18A"), (700, "C1 · 470 µF / 35 V"), (850, "C2 · 100 nF")):
        s.dot(x, yr, 3.6, V12)
        s.line(x, yr, x, yr + 22, stroke=V12, sw=1.6)
        s.label_box(x, yr + 22, lbl, anchor="center")
        s.line(x, yr + 54, x, ygnd, stroke=GND, sw=1.6)
    s.line(520, ygnd, 880, ygnd, stroke=GND, sw=2.0)
    _gnd_symbol(s, 880, ygnd)
    s.text(508, ygnd + 4, "GND", size=11, fill=GND, anchor="end")

    s.card(940, 112, 160, "U1", ["R-78E5.0-1.0", "12 V -> 5.0 V / 1 A"],
           accent=V5, title_size=13, line_size=11)

    # --- 5 V rail
    y5 = 372
    s.poly([(1020, 194), (1020, y5), (250, y5)], stroke=V5, sw=2.0, marker="arw_v5")
    s.text(1032, 250, "+5 V", size=11, fill=V5)
    s.card(40, y5 - 38, 200, "-> ESP32", ["5V pin (on-board", "LDO makes 3.3 V)"],
           accent=V5, title_size=13, line_size=11)

    y5g = 470
    for x, lbl in ((700, "C4 · 100 nF"), (850, "C3 · 470 µF / 16 V")):
        s.dot(x, y5, 3.6, V5)
        s.line(x, y5, x, y5 + 22, stroke=V5, sw=1.6)
        s.label_box(x, y5 + 22, lbl, anchor="center")
        s.line(x, y5 + 54, x, y5g, stroke=GND, sw=1.6)
    s.line(660, y5g, 880, y5g, stroke=GND, sw=2.0)
    _gnd_symbol(s, 880, y5g)
    s.text(648, y5g + 4, "GND", size=11, fill=GND, anchor="end")

    s.text(40, y5g + 4, "C3 sits closest to the ESP32:", size=11, fill=FG_FAINT)
    s.text(40, y5g + 22, "it is the local charge reserve", size=11, fill=FG_FAINT)
    s.text(40, y5g + 40, "for the Wi-Fi/ESP-NOW bursts.", size=11, fill=FG_FAINT)

    for i, (col, lbl) in enumerate(((V12, "+12 V"), (V5, "+5 V"), (GND, "GND"))):
        ly = 38 + i * 20
        s.line(986, ly, 1016, ly, stroke=col, sw=2.4)
        s.text(1026, ly + 4, lbl, size=11, fill=col)
    return "02-node-b-power-stage", s


# ---------------------------------------------------------------------------
# Fig. 3 -- Node B signal interface
# ---------------------------------------------------------------------------
def fig03_node_b_signal():
    s = Svg(1140, 600)
    s.text(40, 44, "NODE B  ·  SIGNAL INTERFACE", size=15, fill=FG, weight=700)
    s.text(40, 64, "no signal connector ever touches 12 V — only VS of the L9637D and the "
                   "510 Ω pull-up do", size=12, fill=FG_FAINT)

    cx, cy, cw, ch = 430, 130, 280, 120
    s.rect(cx, cy, cw, ch, fill=PANEL, stroke=SIG, sw=1.8, r=10)
    s.text(cx + cw / 2, cy + 42, "U2 · L9637D", size=15, fill=SIG, anchor="middle", weight=700)
    s.text(cx + cw / 2, cy + 66, "K-line transceiver", size=11.5, fill=FG_DIM, anchor="middle")
    s.text(cx + cw / 2, cy + 86, "ISO 9141-2 · on breakout", size=11.5, fill=FG_DIM, anchor="middle")

    for yy, lbl, col in ((cy + 28, "VS · +12 V (IG)", V12),
                         (cy + 60, "VCC · +3.3 V", V33),
                         (cy + 92, "GND", GND)):
        s.text(cx - 46, yy + 4, lbl, size=11.5, fill=col, anchor="end")
        s.line(cx - 38, yy, cx - 4, yy, stroke=col, sw=1.8, marker=marker_for(col))

    # K-line bus network
    yk = cy + 30
    s.line(cx + cw, yk, 990, yk, stroke=SIG, sw=2.0)
    s.text(1000, yk + 4, "K  ->  OBD pin 7", size=12, fill=SIG)

    s.dot(790, yk, 3.6, SIG)
    s.line(790, yk, 790, yk - 34, stroke=V12, sw=1.6)
    s.label_box(790, yk - 66, "R7 · 510 Ω", anchor="center")
    s.line(790, yk - 66, 790, yk - 86, stroke=V12, sw=1.6, marker="arw_v12")
    s.text(790, yk - 94, "+12 V", size=11, fill=V12, anchor="middle")

    s.dot(890, yk, 3.6, SIG)
    s.line(890, yk, 890, yk + 40, stroke=SIG, sw=1.6)
    s.label_box(890, yk + 40, "C8 · 1 nF", anchor="center")
    s.line(890, yk + 72, 890, yk + 92, stroke=GND, sw=1.6)
    _gnd_symbol(s, 890, yk + 92)
    s.text(940, yk + 60, "≤ 1.3 nF per datasheet", size=10.5, fill=FG_FAINT)

    for xx, lbl in ((500, "RX  ·  GPIO16"), (640, "TX  ·  GPIO17")):
        s.line(xx, cy + ch, xx, cy + ch + 40, stroke=SIG, sw=1.8, marker="arw_sig")
        s.text(xx, cy + ch + 60, lbl, size=12, fill=SIG, anchor="middle")
    s.text(570, cy + ch + 84, "UART2 @ 10400 baud", size=11, fill=FG_FAINT, anchor="middle")

    s.card(60, 400, 490, "J3 · OLED connector  (7-pin, latching)",
           ["SSD1322 256×64 mono · 4-wire SPI",
            "+3.3 V · GND",
            "SCLK GPIO18 · MOSI GPIO23 · CS GPIO5",
            "DC GPIO19 · RST GPIO4"], accent=NODE_B, title_size=13)
    s.card(590, 400, 490, "J4 · RTC connector  (4-pin, latching)",
           ["DS3231 + LIR2032 cell · I²C",
            "+3.3 V · GND",
            "SDA GPIO21 · SCL GPIO22",
            "module carries its own I²C pull-ups"], accent=NODE_B, title_size=13)
    return "03-node-b-signal-interface", s


# ---------------------------------------------------------------------------
# Fig. 4 -- Node B spatial layout
# ---------------------------------------------------------------------------
def _zone(s, x, y, w, h, label, note=None, color=SIG, size=12):
    s.rect(x, y, w, h, fill=PANEL_2, stroke=color, sw=1.3, r=7, op=0.9)
    if note:
        s.text(x + 12, y + h / 2 - 3, label, size=size, fill=FG)
        s.text(x + 12, y + h / 2 + 15, note, size=10.5, fill=FG_FAINT)
    else:
        s.text(x + 12, y + h / 2 + size * 0.36, label, size=size, fill=FG)


def fig04_node_b_spatial():
    s = Svg(1140, 700)
    s.text(40, 44, "NODE B  ·  SPATIAL LAYOUT", size=15, fill=FG, weight=700)
    s.text(40, 64, "solid border = on the board   ·   dashed = off the board, reached by cable",
           size=12, fill=FG_FAINT)

    bx, by, bw, bh = 60, 96, 520, 564
    s.rect(bx, by, bw, bh, fill="none", stroke=NODE_B, sw=1.8, r=12)
    s.text(bx + 16, by + 28, "CARRIER PERFBOARD — inside the clock housing",
           size=12.5, fill=NODE_B, weight=700)
    s.text(bx + 16, by + 48, "11 × 27 holes ≈ 3 × 7 cm at 2.54 mm pitch", size=10.5, fill=FG_FAINT)

    zx, zw = bx + 16, bw - 32
    _zone(s, zx, by + 64, zw, 118, "ESP32 DevKit V1 — socketed",
          "header pins in col 1 and col 11 · passives sit UNDERNEATH", color=NODE_B)
    _zone(s, zx, by + 192, zw, 40, "ignition divider  10 kΩ / 3.3 kΩ", color=SIG)
    _zone(s, zx, by + 240, zw, 40, "ILL divider  10 kΩ / 3.3 kΩ + 1 µF", color=SIG)
    _zone(s, zx, by + 288, zw, 40, "analog divider  10 kΩ / 20 kΩ", color=SIG)
    _zone(s, zx, by + 336, zw, 34, "100 nF decoupling", color=SIG)
    _zone(s, zx, by + 378, zw, 40, "buck R-78E5.0-1.0 · 470 µF ×2 · SS34 · TVS", color=V5)
    _zone(s, zx, by + 426, zw, 40, "L9637D breakout + 510 Ω + 1 nF", color=V12)
    _zone(s, zx, by + 472, zw, 34, "row 25 — vertical headers: RTC 4p · K-line 2p", color=EDGE, size=11)
    _zone(s, zx, by + 514, zw, 34, "row 27 — 90° headers: OLED 7p · i59 3p", color=EDGE, size=11)

    px, py, pw, ph = 640, 140, 440, 250
    s.rect(px, py, pw, ph, fill="none", stroke=EDGE, sw=1.5, r=12, dash="7 6")
    s.text(px + 16, py + 26, "OFF THE BOARD — CABLE ONLY", size=12, fill=FG_DIM, weight=700)
    s.card(px + 16, py + 44, pw - 32, "RTC DS3231",
           ["own LIR2032 cell, mounted separately"], accent=EDGE, title_size=13,
           line_size=11, title_color=FG)
    s.card(px + 16, py + 140, pw - 32, "OLED SSD1322",
           ["anchored to the original clock PCB",
            "retained by the 3D-printed bezel"], accent=EDGE, title_size=13,
           line_size=11, title_color=FG)

    s.poly([(bx + bw, by + 489), (610, by + 489), (610, py + 125), (px - 8, py + 125)],
           stroke=EDGE, sw=1.4, dash="4 4", marker="arw")

    for i, (lbl, col) in enumerate((("->  i59 connector (to the car harness)", V12),
                                    ("->  OBD pin 7  (K-line, 1.2-1.5 m)", SIG))):
        yy = 450 + i * 42
        s.line(px, yy, px + 40, yy, stroke=col, sw=1.8, marker=marker_for(col))
        s.text(px + 50, yy + 4, lbl, size=12, fill=col)
    s.text(px, 546, "Both leave the housing through a grommet,", size=10.5, fill=FG_FAINT)
    s.text(px, 564, "with strain relief on the inside.", size=10.5, fill=FG_FAINT)
    return "04-node-b-spatial-layout", s


# ---------------------------------------------------------------------------
# Fig. 5 / 9 -- perfboard grid plans
# ---------------------------------------------------------------------------
def _grid_plan(title, subtitle, zones, name, accent):
    cols, rows, pitch = 11, 27, 20
    x0, y0 = 96, 108
    gw, gh = (cols - 1) * pitch, (rows - 1) * pitch
    s = Svg(880, y0 + gh + 78)
    s.text(40, 44, title, size=15, fill=FG, weight=700)
    s.text(40, 64, subtitle, size=12, fill=FG_FAINT)

    s.rect(x0 - 14, y0 - 14, gw + 28, gh + 28, fill=PANEL, stroke=accent, sw=1.6, r=8)
    for c in range(cols):
        for r in range(rows):
            s.dot(x0 + c * pitch, y0 + r * pitch, 1.6, GRID)
    for c in (1, 6, 11):
        s.text(x0 + (c - 1) * pitch, y0 - 24, str(c), size=10, fill=FG_FAINT, anchor="middle")
    for r in (1, 10, 20, 25, 27):
        s.text(x0 - 26, y0 + (r - 1) * pitch + 4, str(r), size=10, fill=FG_FAINT, anchor="end")

    lx = x0 + gw + 40
    for (r1, r2, label, note, color) in zones:
        zy = y0 + (r1 - 1) * pitch - 8
        zh = (r2 - r1) * pitch + 16
        s.rect(x0 - 8, zy, gw + 16, zh, fill=color, stroke=color, sw=1.2, r=6, op=0.14)
        cyy = zy + zh / 2
        s.line(x0 + gw + 10, cyy, lx - 8, cyy, stroke=color, sw=1.2)
        if note:
            s.text(lx, cyy - 2, label, size=11.5, fill=FG)
            s.text(lx, cyy + 16, note, size=10.5, fill=FG_FAINT)
        else:
            s.text(lx, cyy + 4, label, size=11.5, fill=FG)
    s.caption(s.h - 20, "Rows 25 and 27 carry the headers; row 26 is deliberately left empty "
                        "so the two header rows cannot short.")
    return name, s


def fig05_node_b_grid():
    return _grid_plan(
        "NODE B  ·  PERFBOARD GRID PLAN",
        "11 × 27 holes ≈ 3 × 7 cm at 2.54 mm pitch",
        [(1, 14, "ESP32 DevKit V1 — socketed", "pins in col 1 and col 11; passives underneath", NODE_B),
         (15, 16, "ignition divider 10k / 3.3k", None, SIG),
         (17, 18, "ILL divider 10k / 3.3k + 1 µF", None, SIG),
         (19, 20, "analog divider 10k / 20k", None, SIG),
         (21, 21, "100 nF decoupling", None, SIG),
         (22, 23, "buck R-78 · 470 µF ×2 · SS34 · TVS", None, V5),
         (24, 24, "L9637D breakout · 510 Ω · 1 nF", None, V12),
         (25, 25, "vertical headers: RTC 4p · K-line 2p", None, EDGE),
         (27, 27, "90° headers: OLED 7p · i59 3p", None, EDGE)],
        "05-node-b-grid-plan", NODE_B)


def fig09_node_a_grid():
    return _grid_plan(
        "NODE A  ·  PERFBOARD GRID PLAN",
        "same 11 × 27 board, far emptier — the relay module lives off the board",
        [(1, 14, "ESP32 DevKit V1 — socketed", "pins in col 1 and col 11", NODE_A),
         (15, 16, "ignition divider 10k / 3.3k", None, SIG),
         (17, 21, "free", "spare area for later nodes / sensors", EDGE),
         (22, 24, "buck R-78 · 470 µF ×2 · SS34 · TVS", None, V5),
         (25, 25, "vertical headers: relay 5p (IN1·IN2·VCC·JD·GND)", None, EDGE),
         (27, 27, "90° headers: IG · GND · SW1 ON/OFF", None, EDGE)],
        "09-node-a-grid-plan", NODE_A)


# ---------------------------------------------------------------------------
# Fig. 6 -- Node A state machine
# ---------------------------------------------------------------------------
def fig06_node_a_state_machine():
    s = Svg(1060, 430)
    s.text(40, 44, "NODE A  ·  STATE MACHINE", size=15, fill=FG, weight=700)
    s.text(40, 64, "state is not persisted — every IG-on starts ARMED", size=12, fill=FG_FAINT)

    _, ay, _, ah = s.card(60, 100, 320, "ARMED",
                          ["default at every ignition-on", "auto lock/unlock active"],
                          accent=NODE_A)
    dy = ay + ah + 76
    s.card(60, dy, 320, "DISABLED",
           ["no automatic lock or unlock", "this ignition cycle only"], accent=GND)

    s.line(220, ay + ah + 8, 220, dy - 8, stroke=FG_DIM, sw=1.6, marker="arw")
    s.line(252, dy - 8, 252, ay + ah + 8, stroke=FG_DIM, sw=1.6, marker="arw")
    s.text(276, ay + ah + 26, "SW1 · OEM button on GPIO27", size=11.5, fill=FG)
    s.text(276, ay + ah + 44, "toggles on every press", size=10.5, fill=FG_FAINT)

    for i, (title, lines, yy) in enumerate((
            ("v  ≥  20 km/h", ["relay CH1 pulse ≈ 0.4 s", "BIU pin 15  ->  LOCK"], 92),
            ("v  =  0 km/h", ["relay CH2 pulse ≈ 0.4 s", "BIU pin 29  ->  UNLOCK"], 232))):
        s.card(600, yy, 420, title, lines, accent=SIG)
        s.poly([(380, ay + 40 + i * 34), (500, ay + 40 + i * 34), (500, yy + 40), (590, yy + 40)],
               stroke=SIG, sw=1.6, marker="arw_sig")

    s.caption(s.h - 20, "Re-locking falls out of the cycle: stop -> unlock, pass 20 km/h again -> "
                        "lock. No door-ajar signal is read.")
    return "06-node-a-state-machine", s


# ---------------------------------------------------------------------------
# Fig. 7 -- Node A interface
# ---------------------------------------------------------------------------
def fig07_node_a_interface():
    s = Svg(1140, 500)
    s.text(40, 44, "NODE A  ·  INTERFACE", size=15, fill=FG, weight=700)
    s.text(40, 64, "the ON/OFF button is wired straight to this node — it does not travel over "
                   "the radio", size=12, fill=FG_FAINT)

    s.label_box(570, 92, "ESP-NOW  <->  Node B", size=12, fill=PANEL, stroke=RADIO,
                color=RADIO, anchor="center")
    ex, ey, ew, eh = 430, 210, 280, 120
    s.rect(ex, ey, ew, eh, fill=PANEL, stroke=NODE_A, sw=1.8, r=10)
    s.text(ex + ew / 2, ey + 46, "ESP32", size=15, fill=NODE_A, anchor="middle", weight=700)
    s.text(ex + ew / 2, ey + 70, "Node A", size=11.5, fill=FG_DIM, anchor="middle")
    s.text(ex + ew / 2, ey + 92, "3.3 V logic", size=11.5, fill=FG_DIM, anchor="middle")

    s.line(548, 126, 548, ey - 6, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")
    s.line(576, ey - 6, 576, 126, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")
    s.text(600, 156, "speed  in    (B -> A)", size=11, fill=RADIO)
    s.text(600, 180, "mode   out   (A -> B)", size=11, fill=RADIO)

    s.card(40, 150, 320, "Ignition divider",
           ["R1 10 kΩ / R2 3.3 kΩ", "D3 BAT85 clamp · C5 100 nF"],
           accent=SIG, title_size=13, line_size=11)
    s.line(360, 190, ex - 6, 190, stroke=SIG, sw=1.8, marker="arw_sig")
    s.text(372, 180, "IG 12 V  ->  GPIO34", size=11, fill=SIG)

    s.card(40, 292, 320, "SW1 · OEM switch",
           ["unused wiper de-icer button", "switch to GND · INPUT_PULLUP"],
           accent=WARN, title_size=13, line_size=11)
    s.line(360, 332, ex - 6, 332, stroke=WARN, sw=1.8, marker="arw")
    s.text(372, 322, "GPIO27", size=11, fill=WARN)

    s.card(790, 130, 310, "K1 · 2-ch relay module",
           ["external, screw terminals",
            "VCC     -> +3.3 V  (logic)",
            "JD-VCC  -> +5 V  (coil, jumper off)",
            "IN1     <- GPIO25",
            "IN2     <- GPIO26",
            "CH1 COM -> BIU p15 · NO -> GND",
            "CH2 COM -> BIU p29 · NO -> GND"], accent=NODE_A, title_size=13, line_size=11)
    s.line(ex + ew + 6, 258, 784, 258, stroke=SIG, sw=1.8, marker="arw_sig")
    s.text(750, 246, "GPIO 25/26", size=10.5, fill=SIG, anchor="middle")

    s.caption(s.h - 20, "Each relay is driven with a short pulse (≈ 0.4 s), never held. "
                        "COM to the BIU wire, NO to ground = negative pulse.")
    return "07-node-a-interface", s


# ---------------------------------------------------------------------------
# Fig. 8 -- Node A spatial layout
# ---------------------------------------------------------------------------
def fig08_node_a_spatial():
    s = Svg(1140, 620)
    s.text(40, 44, "NODE A  ·  SPATIAL LAYOUT", size=15, fill=FG, weight=700)
    s.text(40, 64, "solid border = on the board   ·   dashed = off the board, reached by cable",
           size=12, fill=FG_FAINT)

    bx, by, bw, bh = 60, 160, 500, 380
    s.label_box(300, 92, "ESP-NOW  <-  Node B  (speed)", size=11, fill=PANEL,
                stroke=RADIO, color=RADIO, anchor="center")
    s.line(300, 124, 300, by - 6, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")

    s.rect(bx, by, bw, bh, fill="none", stroke=NODE_A, sw=1.8, r=12)
    s.text(bx + 16, by + 28, "CARRIER PERFBOARD — next to the BIU (A-pillar)",
           size=12.5, fill=NODE_A, weight=700)
    s.text(bx + 16, by + 48, "11 × 27 holes ≈ 3 × 7 cm at 2.54 mm pitch", size=10.5, fill=FG_FAINT)

    zx, zw = bx + 16, bw - 32
    _zone(s, zx, by + 64, zw, 96, "ESP32 DevKit V1 — socketed",
          "header pins in col 1 and col 11", color=NODE_A)
    _zone(s, zx, by + 170, zw, 40, "ignition divider  10 kΩ / 3.3 kΩ", color=SIG)
    _zone(s, zx, by + 220, zw, 40, "buck R-78E5.0-1.0 · 470 µF ×2 · SS34 · TVS", color=V5)
    _zone(s, zx, by + 270, zw, 34, "free — room for later I/O", color=EDGE, size=11)
    _zone(s, zx, by + 312, zw, 50, "connector edge: relay 5p · IG · GND · SW1 ON/OFF",
          color=EDGE, size=11)

    px, py, pw, ph = 640, 200, 440, 190
    s.rect(px, py, pw, ph, fill="none", stroke=EDGE, sw=1.5, r=12, dash="7 6")
    s.text(px + 16, py + 26, "OFF THE BOARD — CABLE ONLY", size=12, fill=FG_DIM, weight=700)
    s.card(px + 16, py + 44, pw - 32, "K1 · 2-ch relay module",
           ["screw terminals, opto-isolated",
            "CH1 -> BIU pin 15  (lock)",
            "CH2 -> BIU pin 29  (unlock)"], accent=EDGE, title_size=13, line_size=11,
           title_color=FG)
    s.poly([(bx + bw, by + 336), (600, by + 336), (600, py + 118), (px - 8, py + 118)],
           stroke=EDGE, sw=1.4, dash="4 4", marker="arw")

    for i, (lbl, col) in enumerate((("<-  IG 12 V, taken at the A-pillar", V12),
                                    ("<-  SW1, OEM ON/OFF switch -> GPIO27", WARN))):
        yy = 448 + i * 40
        s.line(px + 40, yy, px, yy, stroke=col, sw=1.8, marker=marker_for(col))
        s.text(px + 50, yy + 4, lbl, size=12, fill=col)
    s.text(px, 550, "Everything hangs off latching connectors: unplug them and the car is stock.",
           size=10.5, fill=FG_FAINT)
    return "08-node-a-spatial-layout", s


# ---------------------------------------------------------------------------
# Fig. 10 -- carrier concept
# ---------------------------------------------------------------------------
def fig10_carrier():
    s = Svg(1140, 420)
    s.text(40, 44, "CARRIER BOARD CONCEPT", size=15, fill=FG, weight=700)
    s.text(40, 64, "layout, not a schematic — boxes that do not touch, no crossing lines",
           size=12, fill=FG_FAINT)

    bx, by, bw, bh = 60, 100, 1020, 210
    s.rect(bx, by, bw, bh, fill="none", stroke=EDGE, sw=1.8, r=12)
    s.text(bx + 16, by + 28, "CARRIER (double-sided perfboard) — sockets soldered, modules "
                             "plugged in", size=12.5, fill=FG, weight=700)

    mods = [("ESP32", "socketed"), ("OLED", "latching conn."),
            ("L9637D", "socketed"), ("RTC / buck", "socketed")]
    mw, gap = 228, 24
    for i, (t, sub) in enumerate(mods):
        mx = bx + 20 + i * (mw + gap)
        s.rect(mx, by + 48, mw, 76, fill=PANEL_2, stroke=NODE_B, sw=1.4, r=8)
        s.text(mx + mw / 2, by + 78, t, size=13.5, fill=FG, anchor="middle", weight=700)
        s.text(mx + mw / 2, by + 100, sub, size=11, fill=FG_DIM, anchor="middle")

    s.rect(bx + 20, by + 140, bw - 40, 46, fill=PANEL_2, stroke=EDGE, sw=1.3, r=8)
    s.text(bx + bw / 2, by + 168, "passives (dividers, K-line R/C) — soldered straight to the "
                                  "carrier", size=11.5, fill=FG_DIM, anchor="middle")

    for i, lbl in enumerate(("->  i59  (latch)", "->  K-line  (latch)", "->  12 V / BIU  (latch)")):
        xx = bx + 180 + i * 330
        s.line(xx, by + bh, xx, by + bh + 26, stroke=EDGE, sw=1.6, marker="arw")
        s.label_box(xx, by + bh + 30, lbl, size=11.5, anchor="center")

    s.caption(s.h - 24, "Modules = socket + removable retainer   ·   outputs to the car = latching "
                        "connectors   ·   no Dupont anywhere.")
    return "10-carrier-concept", s


# ---------------------------------------------------------------------------
FIGURES = [fig01_system_architecture, fig02_node_b_power, fig03_node_b_signal,
           fig04_node_b_spatial, fig05_node_b_grid, fig06_node_a_state_machine,
           fig07_node_a_interface, fig08_node_a_spatial, fig09_node_a_grid, fig10_carrier]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    tmp = pathlib.Path("/tmp/diagram_svg")
    tmp.mkdir(exist_ok=True)
    names = []
    for fn in FIGURES:
        name, svg = fn()
        (tmp / f"{name}.svg").write_text(svg.render(), encoding="utf-8")
        names.append(name)
        print(f"  drew {name}  ({svg.w}×{svg.h})")
    subprocess.run([sys.executable, str(pathlib.Path(__file__).parent / "svg_to_png.py"),
                    str(tmp), str(OUT), str(SCALE)], check=True)
    print(f"\n{len(names)} figures written to {OUT}")


if __name__ == "__main__":
    main()
