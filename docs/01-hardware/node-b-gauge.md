# Node B — Gauge

ESP32 in the centre console, in the OEM clock bay. Reads the ECU over **SSM2** on
the K-line and drives the OLED. It is the **hub of the ESP-NOW star**: it sends
speed to Node A, receives the lock mode back, and from v0.3 receives sensor
channels from Node C ([`docs/02-firmware/`](../02-firmware/README.md#link-topology)).

`Ref` codes below index the [component catalogue](README.md#component-catalogue)
and [BOM](README.md#bom-with-indicative-prices). The hole-by-hole build is
[`node-b-build.md`](node-b-build.md).

## Node B is built as two boards

The gauge board is 3 × 7 cm, measured. Once the DevKit is socketed, the power
stage and the K-line transceiver do not fit on it — the arithmetic is
[Fig. 15](node-b-build.md#node-b-is-two-boards). So the node is split by voltage
domain:

| Board | Where | Stages it carries |
| --- | --- | --- |
| **B-PWR** | at the i59 adapter | 1 (12 V → 3.3 V), 2's divider, 4 (K-line) |
| **B-GAUGE** | in the OEM clock bay | 1b (local decoupling), 2's clamp and filter, 3, 5 |

A **five-wire umbilical** joins them: +3.3 V, GND, the divided ILL node, K-RX and
K-TX. **No 12 V reaches the clock bay, and nothing in Node B runs at 5 V.**

> **Node B has one rail, and it is made on B-PWR.** U1 is the 3.3 V version of the
> Recom, the DevKit is fed on its **3V3 pin** with VIN unconnected, and the
> module's own AMS1117 is out of the circuit entirely. The reason is the display:
> a 3.12" 256×64 SSD1322 module draws **310 mA typical, 340 mA maximum** at 3.3 V
> (Newhaven NHD-3.12-25664UCY2, the reference design these modules clone). With
> the ESP32's 240–350 mA transmit peak on top, the DevKit's AMS1117 would dissipate
> **(5 − 3.3) × 0.6 ≈ 1.0 W** in a SOT-223 on a clone board with no copper pour.
> That is a 120–160 °C rise — thermal shutdown on the bench, never mind in a
> closed console. Feeding 3.3 V directly is not an optimisation; it is the only
> arrangement that works. [ADR 0008](../decisions/0008-node-b-runs-on-one-33-v-rail.md).

## Stages and exact values

### Stage 1 · Power (IG to 3.3 V) — on B-PWR

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| F1 | Fuse + holder | **1 A slow-blow** | inline in +12 V (IG), before J6 | opens on a short |
| D1 | Schottky diode | **SB1100** (1 A, 100 V, DO-41) | +12 V → VBAT (series) | reverse polarity, 100 V reverse rating |
| D2 | Unidirectional TVS | **P6KE20A** (DO-15) | VBAT → GND | transients; clamps at ~27.7 V |
| C1 | Electrolytic | **100 µF / 35 V, 105 °C** | VBAT → GND | input reserve |
| C2 | Ceramic | 100 nF **X7R, 50 V** | VBAT → GND | HF filter at the buck input |
| U1 | Switching regulator | **Recom R-78E3.3-1.0** | VBAT → 3.3 V | **input 7–28 V**, 3.3 V / 1 A, 330 kHz |
| C4 | Ceramic | 100 nF X7R | 3.3 V → GND | HF filter at the buck output |

> **The node resets while cranking, and that is accepted.** D1 costs ~0.4 V, so
> the buck browns out below about 8.4 V at J6, and an EZ30 pulls IG-switched
> supplies to 8–10 V for a few hundred milliseconds at start. C1 holds 470 µF from
> 11.6 V to 8 V — about 16 mJ, roughly 11 ms at this node's load, so it does not
> bridge the crank. Node A behaves the same way and its
> [start-up gap](../04-integration/README.md#field-notes) is already documented.
>
> **At the other end, D2 clamps above the buck's input maximum.** An SMAJ18A's
> clamping voltage at its rated 13.7 A peak is 29.2 V, and the Recom's maximum
> input is 28 V. The TVS protects against the fast transients it is there for and
> does **not** guarantee the buck against a sustained overvoltage such as a
> jump-start on a 24 V system. Recorded, not designed around: the part is already
> bought and Node A uses the same one.

### Stage 1b · Local decoupling — on B-GAUGE

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| C3 | Electrolytic | **100 µF / 16 V, 105 °C, Ø6.3** | 3.3 V → GND | radio bursts |
| C11 | Ceramic | **10 µF X7R** | 3.3 V → GND, at the DevKit's 3V3/GND pins | low-ESR decoupling where the current is drawn |

> **C3 is 100 µF, not 470.** The Recom's maximum capacitive load is **220 µF**,
> and that figure covers the whole rail — C3, C11, and whatever the DevKit carries
> on its own 3V3 pin. 470 µF is twice the limit; the module current-limits into it
> at start-up and hiccups instead of coming up, worst at the low input voltage of a
> cold crank. At 100 µF the rail totals about 115 µF.
>
> **If the Ø6.3 can fouls a connector shell**, fit **47 µF / 16 V in a Ø5 can**
> rather than a physically smaller 220 µF part: 220 µF is the ceiling for the
> whole rail, not a target for one capacitor. Dry-fit every shell before C3 goes
> in ([Fig. 20](node-b-build.md#what-node-b-needs-that-node-a-did-not),
> panel 4).
>
> C3 sits 22 pitches — **56 mm** — from the module's 3V3 pin, because it is the one
> part too tall for the 8.5 mm of clearance. That distance is irrelevant for a
> reservoir, which supplies a millisecond-scale transmit burst through a few tens
> of nanohenries without noticing. **C11 is what matters at the pin**, and it is
> 10 µF X7R rather than 100 nF precisely because the DevKit is now fed on 3V3: this
> is where the ESP32's and the display's current is actually drawn, with no
> regulator in between to hold the rail up.

### Stage 2 · Illumination (ILL) sensing

One divider bringing the dash rheostat's 12 V line down to a safe level, with a
capacitor to average it if the illumination is PWM-dimmed. **The divider is on
B-PWR; the clamp and the filter are on B-GAUGE, at the ADC pin.**

| Ref | Component | Value | Board | Connection | Function |
| --- | --- | --- | --- | --- | --- |
| R3 | Resistor | **20 kΩ** | B-PWR | ILL → node_ILL | upper leg |
| R4 | Resistor | 3.3 kΩ | B-PWR | node_ILL → GND | lower leg |
| D4 | Schottky clamp | BAT85 | B-GAUGE | node_ILL → 3.3 V | clips |
| C6 | Ceramic | 1 µF | B-GAUGE | node_ILL → GND | averages PWM → ADC |

> **R3 was 10 kΩ and that was wrong.** With 10 k / 3.3 k, and the ILL line fed
> straight from i59 pin 1 with no series diode, the node reaches **3.57 V at a
> 14.4 V charging voltage** — above the 3.3 V rail and 0.03 V under the ESP32's
> 3.6 V absolute maximum — and **3.97 V at 16 V**. D4 would have been holding the
> pin at its limit as a matter of routine rather than as a fault case.
>
> With **20 k / 3.3 k** the node reads 1.70 V at 12 V, 2.04 V at 14.4 V and 2.27 V
> at 16 V: inside ADC1's suggested 150–2450 mV window at 11 dB attenuation, below
> the rail at every voltage the car produces, and D4 becomes what it was supposed
> to be — a second line of defence. Source impedance is 2.8 kΩ, and C6 at the pin
> is what the ADC actually charges from.
>
> This is the same defect as the ignition divider removed in v0.1.7, in the divider
> that survived it. The ratio was inherited, not checked.
>
> **D4 puts a path from the ILL line into a dead 3.3 V rail.** i59 pin 1 is fed
> from the tail and illumination relay, which is worked by the light switch, not by
> the ignition — so park lights on with the key out very likely means 12 V on ILL
> while the node is dead. The divider then drives the node to ~1.7 V, D4 conducts
> into an unpowered rail, and about **(12 − 0.3) / 20 kΩ = 0.6 mA** flows in.
>
> Removing D4 does not remove the path: an unpowered CMOS input clamps to its own
> supply through an ESD diode, so GPIO35 would conduct at roughly the same current
> anyway. **The path is a property of feeding a divider from an always-live line,
> not of the clamp.** What bounds it is R3 — and that is the second reason 20 kΩ
> is better than 10 kΩ.
>
> 0.6 mA cannot start anything on the board: it holds the 3.3 V rail at about a
> diode drop, far below every device's operating threshold. It is nevertheless a
> parasitic draw, and the project claims
> [zero parasitic draw](../00-concept/README.md#zero-parasitic-draw). Whether the
> ILL feed is in fact live with the key out is
> [`OC-12`](../04-integration/README.md#open-checks-on-the-vehicle); if it is, the
> honest options are to accept 0.6 mA while the lights are on and say so, or to
> move the module's ILL tap to a line that dies with the ignition.
>
> **ILL is a real function and stays.** Following the dash rheostat has no other
> source, and it is read for relative brightness, so the top of the range
> compressing is harmless. Reference designators R1, R2, D3 and C5 remain retired
> from v0.1.7 and are not reused.

### Stage 3 · Analogue input (0-5 V sensor, optional) — on B-GAUGE

One divided input, kept for a single local sensor. **Nothing is specified to
connect to it**; it is two connector pins and four flat parts, and it is the first
thing to drop if anything else has to fit.

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| R5 | Resistor | **20 kΩ, 1 % metal film** | sensor → node_AN | upper |
| R6 | Resistor | **10 kΩ, 1 % metal film** | node_AN → GND | lower (5 V → 1.67 V) |
| D5 | Schottky clamp | BAT85 | node_AN → 3.3 V | clips |
| C7 | Ceramic | 100 nF | node_AN → GND | filter → ADC |

> **The old 10 k / 20 k was wrong the same way**: it puts **3.33 V** on the pin at
> a 5.00 V input, above the rail and above the top of ADC1's usable window, before
> any sensor had even been chosen. The first correction, 10 k / 10 k, only moved
> the number to 2.50 V — still outside the 150–2450 mV window, which is the very
> criterion used to condemn the ILL divider two stages up. **20 k / 10 k** gives
> **1.67 V at 5.00 V** and 1.83 V at 5.5 V, inside the window at both ends. Source
> impedance is 6.7 kΩ, which is high for an ESP32 ADC input and is why C7 sits at
> the pin; 10 k / 6.8 k would give 2.02 V and a 4.0 kΩ source if a 6.8 kΩ is ever
> bought.
>
> **This stage does not scale.** Wi-Fi claims ADC2 entirely
> ([ADR 0005](../decisions/0005-ota-in-maintenance-mode.md)), so only ADC1's six
> channels are usable; this node spends GPIO32 and GPIO33 on buttons and GPIO34/35
> on these two inputs, leaving GPIO36 and GPIO39. Those two are free by choice, and
> there is no room on a 3 × 7 cm board for the conditioning they would need. Analogue sensing beyond this one input is
> [Node C](node-c-sensors.md)'s job, on an external I²C ADC.

### Stage 4 · K-line transceiver (L9637D to OBD pin 7) — on B-PWR

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| U2 | Transceiver | L9637D, SO-8 on a SOIC-8→DIP-8 adapter | — | K-line ↔ UART |
| R7 | Resistor (RKO) | 510 Ω, **½ W metal oxide** | K → VS (12 V) | bus pull-up |
| C8 | Ceramic (CK) | 1 nF **C0G/NP0** | K → GND | bus filter (≤1.3 nF) |
| C9 | Ceramic | 100 nF X7R | VCC (3.3 V) → GND | logic decoupling |
| C10 | Ceramic | 100 nF **X7R, 50 V** | VS (12 V) → GND | power decoupling |

Pinout as used here, from ST's datasheet **Doc ID 1765**:

| Pin | Name | Goes to |
| --- | --- | --- |
| 1 | RX | umbilical pin 4 → ESP32 **RX2 (GPIO16)** |
| 2 | LO | **left open** — the pin has an internal pull-up to VCC |
| 3 | VCC | 3.3 V, from U1 on this same board |
| 4 | TX | umbilical pin 5 ← ESP32 **TX2 (GPIO17)** |
| 5 | GND | common |
| 6 | K | OBD pin 7, with R7 to VS and C8 to GND |
| 7 | VS | VBAT (12 V after D1) |
| 8 | LI | **tied to VS** |

> **Verify the pinout before the SOIC-8 goes onto the adapter.** Read pins 1 and 8
> off Figure 2 of the datasheet yourself. Swapping RX and LI puts a VS-referenced
> comparator on a logic line: nothing burns and nothing works.
>
> **LI and LO are the unused L line.** The datasheet states that leaving LI open is
> a defined condition — LO is then driven on — but gives no guidance for a
> K-line-only design, and there is no ST application note for this part. LI is
> tied to VS here because that is the idle state and draws a few microamps, while
> grounding it leaves LO sinking its internal pull-up continuously. **This is
> inference from the thresholds, not a quoted recommendation**, and it is one
> jumper to reverse.
>
> **R7 is a ½ W part, not the ⅛ W that R3–R6 are.** While the bus is held
> dominant it drops nearly the whole 11.6 V across 510 Ω — **0.26 W** — and SSM2
> holds it low for whole bytes at a time.
>
> **VCC at 3.3 V is inside the operating range (3–7 V) but the datasheet specifies
> it as guaranteed by design, tested only at 5 V.** RX is an open-drain output with
> an internal 5–20 kΩ pull-up to VCC, so it swings to about VCC − 0.15 V — clear of
> a 3.3 V input's threshold. TX's high threshold is an absolute 2.5 V, not a
> fraction of VCC, so **GPIO17 must be push-pull**, never open-drain.

> **The VCC = 0 hazard is gone.** Until v0.1.8 the transceiver's VCC came up the
> umbilical from the DevKit's regulator, so an unplugged cable or a dead gauge
> board left U2 at VS = 12 V with VCC at zero — a state ST's datasheet does not
> specify, on a K line shared with every scan tool that will ever be plugged into
> this car. Now U1 makes 3.3 V on the same board as U2, and the two cannot be
> separated.

The K-line runs from OBD pin 7 to **B-PWR**, which sits at the i59.
**Whether it arrives through the i59 adapter's spare pin 7 or on its own cable
beside it is not settled** — see the
[i59 adapter](assembly-and-wiring.md#i59-adapter-1-male--2-female).

### Stage 5 · Display, clock and buttons — on B-GAUGE

| Block | Connection | Component note |
| --- | --- | --- |
| OLED SSD1322 (SPI) | VCC 3.3 V · GND · SCLK 18 · MOSI 23 · CS 5 · DC 19 · RST 4 | set the jumpers to 4-wire SPI |
| RTC DS3231 (I²C) | VCC 3.3 V · GND · SDA 21 · SCL 22 | I²C pull-ups already on the module |
| 4 OEM buttons | GPIO 32/33/25/26 ↔ contact pad ↔ GND | `INPUT_PULLUP` + **100 nF X7R at each pin (C13–C16, not optional)** |

> **The 3.3 V budget, with a real number for the display.** U1 supplies the ESP32
> (240–350 mA at a transmit peak), the OLED (**310 mA typical, 340 mA max**), the
> DS3231 (~1 mA) and the L9637D (1.4–2.3 mA): about **550 mA typical, 700 mA
> peak**. The Recom is a 1 A part derated to roughly 0.8 A at 70 °C, so the peak is
> about 85 % of what it can deliver there. That is workable and it is not
> comfortable — **measure your own module's 3.3 V current** before the housing is
> closed, because the 310 mA figure is Newhaven's for the reference design and a
> generic module may differ. If it comes in much higher, the escape is the
> display's external-VCC jumper, which moves the panel supply off this rail.

> **The DS3231 is not on the board.** It is four wires on J4 and a 3D-printed case
> of its own: it is a bare module with a coin cell, it shorts against trim clips if
> it is loose in a console, and its cell has to stay reachable. Keep the cable to
> 20 cm — it is I²C, with the module's own pull-ups.
>
> **Fit a CR2032 and disable the module's charger.** The advice to fit a
> rechargeable LIR2032 was backwards. The ZS-042's charger is a 1N4148 and a 200 Ω
> resistor from VCC; **at VCC = 3.3 V it only conducts once the cell falls below
> about 2.7 V**, so an LIR2032 (3.6 V nominal) is never meaningfully recharged — it
> only discharges. Worse, Li-ion coin cells are rated to about +60 °C and a closed
> console reaches 70 °C. A CR2032 is Li-MnO₂, rated to +70 °C or beyond, and holds
> ~10 years. Remove the 200 Ω resistor or the diode anyway, so that a 5 V bench
> test can never push a primary cell toward 4.5 V.
>
> **Check what is actually on the module.** Cheap ZS-042 boards are often fitted
> with a DS3231**M** (MEMS, ±5 ppm) or a counterfeit rather than the DS3231SN. The
> catalogue's "±2 ppm" is the SN figure and only for 0 to +40 °C; over the full
> range the genuine part is ±3.5 ppm.

#### The buttons are the OEM ones, reused

The four controls are the car's existing **DISP**, **SET** and **− +** buttons.
They are not tactile switches: they are interdigitated contact pads on the OEM
board, closed by a conductive rubber pad. A teardown of a donor unit established
this — the finding, the alternatives and what it commits the PCB to are in
[ADR 0004](../decisions/0004-reuse-oem-contact-pad-buttons.md); the photographs
are indexed in [`photos/`](photos/README.md).

![The clock unit out of the dash, showing the button layout](photos/clock-unit-front.jpg)

![The OEM board, with the button contact pads outlined in red](photos/donor-pcb-contact-pads.jpg)

**Photos** — The car's unit, with DISP bottom left and the **− +** rocker and SET
at the right: the four functions the pin map assumes. Below, the donor board with
the contact pads outlined in red.

Wiring is therefore just `INPUT_PULLUP` on the GPIO and the pad's other side to
ground — no external conditioning. Mechanically the carrier must either retain the
OEM board's pad area or reproduce its geometry; that choice is open, and the pad
layout on the car's own unit is
[`OC-08`](../04-integration/README.md#open-checks-on-the-vehicle).

> **The ON/OFF control is not here.** The auto-lock toggle is a reused OEM switch
> on **Node A** ([ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md)).
> Node B only receives the mode change over ESP-NOW and confirms it on the OLED.
> No hardware on this node; firmware only.

## ESP32 pin map (Node B)

| Peripheral | Signal | GPIO | Note |
| --- | --- | --- | --- |
| OLED (SPI) | MOSI | 23 | 4-wire SPI |
| OLED (SPI) | SCLK | 18 | 4-wire SPI |
| OLED (SPI) | CS | 5 | 4-wire SPI |
| OLED (SPI) | DC | 19 | 4-wire SPI |
| OLED (SPI) | RST | 4 | 4-wire SPI |
| RTC (I²C) | SDA | 21 | DS3231 |
| RTC (I²C) | SCL | 22 | DS3231 |
| K-line (UART2) | RX | 16 | the DevKit's `RX2` pin · L9637D VCC = 3.3 V |
| K-line (UART2) | TX | 17 | the DevKit's `TX2` pin · push-pull, not open-drain |
| Buttons | DISP | 32 | `INPUT_PULLUP` |
| Buttons | SET | 33 | `INPUT_PULLUP` |
| Buttons | [+] | 25 | `INPUT_PULLUP` |
| Buttons | [−] | 26 | `INPUT_PULLUP` |
| ILL (dimming) | ADC | 35 | Stage 2 · input-only |
| Analogue sensor | ADC | 34 | Stage 3 · input-only |
| ESP-NOW | speed, transmit | — (radio) | → Node A |
| ESP-NOW | mode confirmation, receive | — (radio) | ← Node A, shown on the OLED |
| ESP-NOW | sensor channels, receive | — (radio) | ← Node C, v0.3 |

GPIO36 and GPIO39 (`VP` and `VN`) are the two ADC1 channels this node leaves
free — free by choice, not because Wi-Fi took them: ADC1 has six channels, and
this node spends GPIO32/33 on buttons and GPIO34/35 on the two divided inputs.

**The module is powered on its `3V3` pin, and `VIN` is left unconnected.** Never
plug USB in while the umbilical is connected: on a DevKit V1 the USB 5 V and the
VIN pin meet at the AMS1117's input with nothing separating them, so doing both at
once puts the host's supply in parallel with the Recom's.

## Schematics and physical layout

Four views here, coarse to fine, and the hole-by-hole build on its own page. Wire
colour code: **yellow +12 V · copper +5 V · red +3.3 V · grey GND · blue signal**.

### Power stage

![Node B power stage](diagrams/02-node-b-power-stage.png)

**Fig. 2** — The protection chain and the buck, all of it on B-PWR. Node A's
stage has the same shape but a 5 V Recom, because its relay coil needs 5 V; Node
B has no 5 V rail at all ([ADR 0008](../decisions/0008-node-b-runs-on-one-33-v-rail.md)).

### Signal interface (K-line, OLED, RTC)

![Node B signal interface](diagrams/03-node-b-signal-interface.png)

**Fig. 3** — The signal interface. The only 12 V nets are the L9637D's VS pin and
the 510 Ω bus pull-up, and after the split both are on B-PWR.

### Where it goes in the car

![The clock bay in the centre console, outlined in red](photos/clock-bay-in-dash.jpg)

**Photo** — The bay the gauge has to keep: between the upper storage compartment
and the head unit. Same position, same viewing angle, same night-time dimming
behaviour as the OEM trip computer.

![The donor housing at an angle, showing the lens layers and internal depth](photos/donor-housing-lens-layers.jpg)

**Photo** — Internal depth available behind the lens. The SSD1322 needs roughly
79 × 21 mm of active area and about 6 mm of depth; the carrier is 3 × 7 cm, so the
display is wider than the board and is mounted in the bezel, on a cable.
Confirm both against the car's own unit before committing to a board outline.

### Spatial layout

![Node B spatial layout](diagrams/04-node-b-spatial-layout.png)

**Fig. 4** — Both boards. Solid border = on a board; dashed = off the boards,
reached by cable.

### Grid plan

![Node B grid plan](diagrams/05-node-b-grid-plan.png)

**Fig. 5** — Zones on both 11 × 27 grids. B-GAUGE's connector rails are rows 21,
24 and 27; B-PWR uses three different edges.

### Hole by hole

Placement, the 64 solder-side jumpers across the two boards, the cut lists and the
order of work are in **[`node-b-build.md`](node-b-build.md)** — Figs. 15 to 20.
