#!/usr/bin/env python3
"""
Source of truth for every figure in docs/01-hardware/diagrams/.

The figures are *drawn here*, not extracted from anywhere: run this script and the
PNGs are rebuilt. Only the PNGs are committed -- this file is the editable source.

    python3 scripts/generate_diagrams.py

Requires playwright (chromium) for the SVG -> PNG step.
"""
import pathlib
import shutil
import subprocess
import tempfile
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from diagram_lib import (  # noqa: E402
    Svg, tw, marker_for,
    BG, PANEL, PANEL_2, EDGE, GRID, FG, FG_DIM, FG_FAINT,
    V12, V5, V33, GND, SIG, RADIO, NODE_A, NODE_B, NODE_C, WARN,
)

from node_a_build import (  # noqa: E402
    fig12_node_a_placement, fig13_node_a_solder_side, fig14_node_a_technique,
)
from node_b_build import (  # noqa: E402
    fig04_node_b_spatial, fig05_node_b_grid,
    fig15_b_split, fig16_b_gauge_placement, fig17_b_gauge_solder,
    fig18_b_pwr_placement, fig19_b_pwr_solder, fig20_b_technique,
)

OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "01-hardware" / "diagrams"
SCALE = 2  # device pixel ratio for the PNG render


# ---------------------------------------------------------------------------
# Fig. 1 -- system architecture
# ---------------------------------------------------------------------------
def fig01_system_architecture():
    s = Svg(1240, 580)
    s.text(40, 44, "SYSTEM ARCHITECTURE", size=15, fill=FG, weight=700)
    s.text(40, 64, "a star: Node B is the hub. The nodes share no wiring at all.",
           size=12, fill=FG_FAINT)
    s.text(40, 100, "ESP-NOW  ·  2.4 GHz  ·  fixed channel", size=12, fill=RADIO, weight=700)

    ax, bx, cx, w = 40, 440, 840, 360
    acx, bcx, ccx = ax + w / 2, bx + w / 2, cx + w / 2

    # --- radio links, one per row so no two share a line
    s.text(430, 124, "speed  ·  every 100-200 ms", size=11, fill=FG_DIM, anchor="middle")
    s.line(bcx, 138, acx, 138, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")

    s.text(430, 160, "lock mode  ·  on button press", size=11, fill=FG_DIM, anchor="middle")
    s.line(acx, 174, bcx, 174, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")

    s.text(830, 196, "sensor channels  ·  about 1 Hz  ·  v0.3", size=11, fill=FG_DIM,
           anchor="middle")
    s.line(ccx, 210, bcx, 210, stroke=NODE_C, sw=1.6, dash="4 6", marker="arw_c")

    s.line(acx, 174, acx, 234, stroke=RADIO, sw=1.4, dash="5 5")
    s.line(bcx, 210, bcx, 234, stroke=RADIO, sw=1.4, dash="5 5")
    s.line(ccx, 210, ccx, 234, stroke=NODE_C, sw=1.4, dash="4 6")

    # --- the nodes
    _, ny, _, nh = s.card(ax, 240, w, "NODE A  ·  CENTRAL LOCKING",
                          ["ESP32 · next to the BIU (A-pillar)",
                           "pulses the lock and unlock lines",
                           "v0.1 · in the first build"], accent=NODE_A)
    s.card(bx, 240, w, "NODE B  ·  GAUGE  ·  HUB",
           ["ESP32 · centre console, clock bay",
            "reads the ECU over SSM2, drives the OLED",
            "v0.1 · in the first build"], accent=NODE_B)
    s.card(cx, 240, w, "NODE C  ·  ANALOGUE FRONT END",
           ["ESP32 · cabin, at the firewall",
            "reads sensor channels, sends them to B",
            "v0.3 · designed, NOT built"], accent=NODE_C)

    # --- wired interfaces
    y2 = ny + nh + 40
    for cxx in (acx, bcx, ccx):
        s.line(cxx, ny + nh, cxx, y2 - 6, stroke=EDGE, marker="arw")

    s.card(ax, y2, w, "WIRED INTERFACE",
           ["OUT  relay CH1 -> BIU pin 15  (lock)",
            "OUT  relay CH2 -> BIU pin 29  (unlock)",
            "IN   IG 12 V  (supply + ign. sense)",
            "IN   OEM ON/OFF switch -> GPIO27",
            "OUT  OEM tell-tale LED -> GPIO33"], accent=EDGE, title_size=12,
           title_color=FG_DIM)
    s.card(bx, y2, w, "WIRED INTERFACE",
           ["i59 connector: IG · GND · ILL",
            "K-line -> OBD pin 7  (SSM2, 4800 bd)",
            "OLED SSD1322 SPI · RTC DS3231 I2C",
            "4 OEM buttons -> GPIO 32/33/25/26",
            ""], accent=EDGE, title_size=12, title_color=FG_DIM)
    s.card(cx, y2, w, "WIRED INTERFACE",
           ["sealed bulkhead connector at the firewall",
            "ADS1115 channel bank on I2C",
            "0-5 V analogue · NTC/RTD · digital in",
            "engine-bay sensors on 2.5-3 m runs",
            ""], accent=EDGE, title_size=12, title_color=FG_DIM)

    s.caption(s.h - 18, "No cable runs between the nodes. Speed is measured by Node B and sent "
                        "to Node A; the lock mode travels back; Node C reports to Node B only.")
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
    s.text(40, 44, "NODE B  ·  B-PWR POWER STAGE  (IG 12 V -> 3.3 V)", size=15, fill=FG, weight=700)
    s.text(40, 64, "Node A's stage is the same shape but ends at 5 V, for the relay coil",
           size=12, fill=FG_FAINT)

    # --- 12 V rail
    yr = 150
    s.card(40, 112, 160, "i59 pin 8", ["IG 12 V, switched"], accent=V12, title_size=13, line_size=11)
    s.line(200, yr, 940, yr, stroke=V12, sw=2.0)
    s.label_box(265, yr - 16, "F1 · fuse 1 A T", anchor="center")
    s.label_box(400, yr - 16, "D1 · SB1100", anchor="center")
    s.text(455, yr - 24, "VBAT", size=10.5, fill=FG_FAINT)

    ygnd = 268
    for x, lbl in ((545, "D2 · P6KE20A"), (700, "C1 · 100 µF / 35 V"), (850, "C2 · 100 nF")):
        s.dot(x, yr, 3.6, V12)
        s.line(x, yr, x, yr + 22, stroke=V12, sw=1.6)
        s.label_box(x, yr + 22, lbl, anchor="center")
        s.line(x, yr + 54, x, ygnd, stroke=GND, sw=1.6)
    s.line(520, ygnd, 880, ygnd, stroke=GND, sw=2.0)
    _gnd_symbol(s, 880, ygnd)
    s.text(508, ygnd + 4, "GND", size=11, fill=GND, anchor="end")

    s.card(940, 112, 160, "U1", ["R-78E3.3-1.0", "12 V -> 3.3 V / 1 A"],
           accent=V33, title_size=13, line_size=11)

    # --- 5 V rail
    y5 = 372
    s.poly([(1020, 194), (1020, y5), (250, y5)], stroke=V33, sw=2.0, marker="arw_v33")
    s.text(1032, 250, "+3.3 V", size=11, fill=V33)
    s.card(40, y5 - 38, 200, "-> ESP32", ["3V3 pin · U2 VCC", "· up the umbilical"],
           accent=V33, title_size=13, line_size=11)

    y5g = 470
    for x, lbl in ((640, "C4 · 100 nF"), (880, "C3 · 100 µF / 16 V")):
        s.dot(x, y5, 3.6, V33)
        s.line(x, y5, x, y5 + 22, stroke=V33, sw=1.6)
        s.label_box(x, y5 + 22, lbl, anchor="center")
        s.line(x, y5 + 54, x, y5g, stroke=GND, sw=1.6)
    s.line(600, y5g, 880, y5g, stroke=GND, sw=2.0)
    _gnd_symbol(s, 880, y5g)
    s.text(588, y5g + 4, "GND", size=11, fill=GND, anchor="end")

    s.text(40, y5g + 4, "C4 is on B-PWR; C3 is on B-GAUGE, at the", size=11, fill=FG_FAINT)
    s.text(40, y5g + 22, "far end of the umbilical. The whole rail", size=11, fill=FG_FAINT)
    s.text(40, y5g + 40, "stays under the Recom's 220 µF limit.", size=11, fill=FG_FAINT)

    for i, (col, lbl) in enumerate(((V12, "+12 V"), (V33, "+3.3 V"), (GND, "GND"))):
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
    s.text(40, 64, "all of this lives on B-PWR except the two connectors, which are on "
                   "B-GAUGE (Fig. 15)", size=12, fill=FG_FAINT)

    cx, cy, cw, ch = 430, 130, 280, 120
    s.rect(cx, cy, cw, ch, fill=PANEL, stroke=SIG, sw=1.8, r=10)
    s.text(cx + cw / 2, cy + 42, "U2 · L9637D", size=15, fill=SIG, anchor="middle", weight=700)
    s.text(cx + cw / 2, cy + 66, "K-line transceiver", size=11.5, fill=FG_DIM, anchor="middle")
    s.text(cx + cw / 2, cy + 86, "ISO 9141-2 · SOIC-DIP adapter", size=11.5, fill=FG_DIM, anchor="middle")

    for yy, lbl, col in ((cy + 28, "VS · +12 V (IG)", V12),
                         (cy + 60, "VCC · +3.3 V, local", V33),
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
    s.text(570, cy + ch + 84, "UART2 @ 4800 baud 8N1  ·  across the umbilical",
           size=11, fill=FG_FAINT, anchor="middle")

    s.card(60, 400, 490, "J2 · OLED connector  (7-pin, latching)",
           ["SSD1322 256×64 mono · 4-wire SPI",
            "+3.3 V · GND",
            "SCLK GPIO18 · MOSI GPIO23 · CS GPIO5",
            "DC GPIO19 · RST GPIO4"], accent=NODE_B, title_size=13)
    s.card(590, 400, 490, "J4 · RTC connector  (4-pin, latching)",
           ["DS3231 + CR2032 cell · I²C",
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
    s.caption(s.h - 20, "Row 27 carries every off-board connector; rows 16-18 stay empty "
                        "under the module body and the PCB antenna.")
    return name, s


def fig09_node_a_grid():
    return _grid_plan(
        "NODE A  ·  PERFBOARD GRID PLAN",
        "zones only — the hole-by-hole layout is Fig. 12",
        [(1, 15, "ESP32 DevKit V1 — socketed", "pins in col A and col L", NODE_A),
         (16, 18, "empty — module body and antenna overhang", None, EDGE),
         (19, 21, "D1 SB1100 · U1 R-78E5.0-1.0 · C2", None, V5),
         (22, 24, "D2 P6KE20A · the TVS clamp", None, V12),
         (25, 26, "C1 · C3, 100 µF each · C4", "rows 19-26 keep 73 of 88 holes free", EDGE),
         (27, 27, "90° headers: IG 2p · relay 5p · switch 2p", None, EDGE)],
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
    s.text(276, ay + ah + 26, "SW1 GPIO27 · LED1 GPIO33 (i78)", size=11.5, fill=FG)
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

    s.card(40, 292, 320, "OEM switch  ·  i78",
           ["SW1 pins 1-2 · to GND · INPUT_PULLUP",
            "LED1 pins 8-9 · lit while DISABLED"],
           accent=WARN, title_size=13, line_size=11)
    s.line(360, 326, ex - 6, 326, stroke=WARN, sw=1.8, marker="arw")
    s.text(366, 316, "SW1 -> 27", size=10.5, fill=WARN)
    s.line(ex - 6, 352, 360, 352, stroke=WARN, sw=1.8, marker="arw")
    s.text(366, 370, "LED1 <- 33", size=10.5, fill=WARN)

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
    _zone(s, zx, by + 170, zw, 40, "buck R-78E5.0-1.0 · 100 µF ×2 · SB1100 · P6KE20A",
          color=V5)
    _zone(s, zx, by + 220, zw, 84, "free — 73 holes of headroom for later I/O",
          color=EDGE, size=11)
    _zone(s, zx, by + 312, zw, 50, "connector edge: relay 5p · IG · GND · SW1 · LED1",
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
                                    ("<-  SW1 -> GPIO27 · LED1 <- GPIO33", WARN))):
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
    s = Svg(1140, 480)
    s.text(40, 44, "CARRIER BOARD CONCEPT", size=15, fill=FG, weight=700)
    s.text(40, 64, "layout, not a schematic — three boards, all the same 3 × 7 cm part",
           size=12, fill=FG_FAINT)

    boards = [("NODE A  ·  at the BIU", NODE_A,
               ["ESP32 DevKit V1 — socketed",
                "passives soldered flat",
                "-> relay module (latch)",
                "-> IG 12 V · OEM switch (latch)"]),
              ("B-GAUGE  ·  clock bay", NODE_B,
               ["ESP32 DevKit V1 — socketed",
                "ten flat parts under it",
                "-> OLED · buttons (latch)",
                "-> RTC, in its own case (latch)"]),
              ("B-PWR  ·  at the i59", V12,
               ["L9637D — socketed on its adapter",
                "buck, diodes, ILL divider",
                "-> i59 12 V · K-line (latch)",
                "-> umbilical to B-GAUGE (latch)"])]
    bw, gap = 340, 26
    for i, (title, col, lines) in enumerate(boards):
        bx = 60 + i * (bw + gap)
        s.rect(bx, 100, bw, 250, fill="none", stroke=col, sw=1.8, r=12)
        s.text(bx + 16, 130, title, size=12.5, fill=col, weight=700)
        s.text(bx + 16, 150, "11 × 27 holes", size=10.5, fill=FG_FAINT)
        for j, ln in enumerate(lines):
            s.text(bx + 16, 182 + j * 30, ln, size=11.5, fill=FG_DIM)

    s.caption(s.h - 98, "Modules = socket + removable retainer   ·   outputs to the car = "
                        "latching connectors   ·   no Dupont anywhere.")
    s.caption(s.h - 66, "Nothing expensive is soldered down: the ESP32s and the L9637D plug "
                        "into sockets and can be pulled out with the board in place.")
    s.caption(s.h - 34, "One printed tray design fits all three, because all three are the "
                        "same board.")
    return "10-carrier-concept", s



# ---------------------------------------------------------------------------
# Fig. 11 -- Node C channel architecture
# ---------------------------------------------------------------------------
def fig11_node_c_channels():
    s = Svg(1240, 700)
    s.text(40, 44, "NODE C  ·  ANALOGUE FRONT END", size=15, fill=FG, weight=700)
    s.text(40, 64, "v0.3, designed and NOT built: no channel has its conditioning "
                   "arithmetic yet — see the open questions in the Node C page",
           size=12, fill=FG_FAINT)

    # --- the two environments, split by the firewall
    s.rect(40, 96, 470, 520, fill="none", stroke=WARN, sw=1.5, r=12, dash="7 6")
    s.text(56, 124, "ENGINE BAY — sealed side", size=12, fill=WARN, weight=700)
    s.text(56, 144, "sensors, environmental connectors", size=10.5, fill=FG_FAINT)

    s.rect(660, 96, 540, 520, fill="none", stroke=NODE_C, sw=1.5, r=12)
    s.text(676, 124, "CABIN — standard side", size=12, fill=NODE_C, weight=700)
    s.text(676, 144, "project-standard connectors, no sealing needed", size=10.5, fill=FG_FAINT)

    # --- bulkhead connector, the boundary
    s.rect(540, 250, 80, 220, fill=PANEL_2, stroke=SIG, sw=1.8, r=8, dash="6 5")
    for row in range(5):
        s.line(552, 282 + row * 38, 608, 282 + row * 38, stroke=EDGE, sw=1.4)
    s.text(580, 240, "BULKHEAD", size=11, fill=SIG, anchor="middle", weight=700)
    s.text(580, 492, "pin count is OC-11:", size=10.5, fill=WARN, anchor="middle")
    s.text(580, 508, "not drawn, not settled", size=10.5, fill=FG_FAINT, anchor="middle")

    # --- sensors on the engine-bay side
    sensors = [
        ("Coolant level", "float sender · catch tank", V5),
        ("Caliper temp  ×2", "PT1000 surface, ~3 m", V33),
        ("Radiator dT", "in / out, surface", SIG),
        ("Ambient air", "NTC", SIG),
        ("Battery voltage", "divider — still OC-12", V12),
        ("Boost", "provision only — 0-5 V", FG_FAINT),
    ]
    for i, (name, note, col) in enumerate(sensors):
        y = 168 + i * 74
        s.rect(60, y, 430, 58, fill=PANEL, stroke=col, sw=1.4, r=8)
        s.text(76, y + 24, name, size=12, fill=FG)
        s.text(76, y + 44, note, size=10.5, fill=FG_FAINT)
        s.line(492, y + 29, 534, y + 29, stroke=col, sw=1.6, marker=marker_for(col))

    # --- channel bank
    s.card(680, 168, 500, "CHANNEL BANK  ·  ADS1115 ×n on I²C",
           ["0-5 V analogue    · single-ended or differential",
            "resistive NTC / RTD · 3-wire",
            "digital in         · float switches, states",
            "16-bit, programmable gain, 4 addresses on one bus"],
           accent=SIG, title_size=13, line_size=11)
    s.text(680, 322, "differential rejects the noise a 3 m run picks up", size=10.5, fill=FG_FAINT)

    s.line(1120, 300, 1120, 348, stroke=SIG, sw=1.8, marker="arw_sig")
    s.text(1108, 330, "I²C", size=11, fill=SIG, anchor="end")

    s.card(680, 356, 500, "ESP32  ·  Node C",
           ["scales, filters and validates each channel",
            "flags every reading valid / invalid",
            "no display, no actuators"], accent=NODE_C, title_size=13, line_size=11)

    s.label_box(930, 500, "ESP-NOW  ->  Node B   ·   ~1 Hz", size=12, fill=PANEL,
                stroke=RADIO, color=RADIO, anchor="center")
    s.line(930, 468, 930, 496, stroke=RADIO, sw=1.6, dash="5 5", marker="arw_radio")
    s.text(930, 560, "temperatures and levels are slow:", size=10.5, fill=FG_FAINT, anchor="middle")
    s.text(930, 578, "1 Hz is generous, and the locking link is untouched", size=10.5,
           fill=FG_FAINT, anchor="middle")

    s.caption(s.h - 22, "The node lives in the cabin. Only the bulkhead connector has to survive "
                        "the engine bay — not the electronics.")
    return "11-node-c-channels", s


# ---------------------------------------------------------------------------
FIGURES = [fig01_system_architecture, fig02_node_b_power, fig03_node_b_signal,
           fig04_node_b_spatial, fig05_node_b_grid, fig06_node_a_state_machine,
           fig07_node_a_interface, fig08_node_a_spatial, fig09_node_a_grid, fig10_carrier,
           fig11_node_c_channels, fig12_node_a_placement,
           fig13_node_a_solder_side, fig14_node_a_technique,
           fig15_b_split, fig16_b_gauge_placement, fig17_b_gauge_solder,
           fig18_b_pwr_placement, fig19_b_pwr_solder, fig20_b_technique]


def main():
    import check_figure_text
    if check_figure_text.main():
        raise SystemExit("figure text does not match the layout — fix it before drawing")
    OUT.mkdir(parents=True, exist_ok=True)
    # A temp directory from the platform, not a hard-coded "/tmp": this script has
    # to run on Windows too, where /tmp does not exist.
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="diagram-svg-"))
    try:
        names = []
        for fn in FIGURES:
            name, svg = fn()
            (tmp / f"{name}.svg").write_text(svg.render(), encoding="utf-8")
            names.append(name)
            print(f"  drew {name}  ({svg.w}×{svg.h})")
        subprocess.run([sys.executable,
                        str(pathlib.Path(__file__).resolve().parent / "svg_to_png.py"),
                        str(tmp), str(OUT), str(SCALE)], check=True)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"\n{len(names)} figures written to {OUT}")


if __name__ == "__main__":
    main()
