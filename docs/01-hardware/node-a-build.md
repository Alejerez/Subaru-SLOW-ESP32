# Node A — building the board

Hole-by-hole assembly for the Node A carrier: where every part goes, every jumper
on the solder side, and the order to do it in. Component values are in
[`node-a-locking.md`](node-a-locking.md); this page is the physical build.

Written for someone comfortable with electronics who has not wired a perfboard at
this density before.

## The board and how holes are named

**3 × 7 cm double-sided perfboard, 11 × 27 holes at 2.54 mm.**

Columns are lettered **A B C D E F G H J K L** — the letter I is skipped so it
cannot be read as a 1. Rows are numbered **1 to 27**, row 1 at the USB end. A hole
is a letter plus a number: `A27` is the bottom-left corner, `L1` the top-right.

Three facts decide the whole layout, and all three are measurements, not choices:

| | |
| --- | --- |
| The DevKit V1's pin rows are **25.4 mm apart — exactly 10 pitches** | so they land in column A and column L, and the module fills the board's width |
| Each row is **15 pins** | so the module owns rows 1–15 |
| The module body reaches **~8 mm past the end pins** | so rows 16–18 stay empty, and the PCB antenna sits over them |

The nine columns between the headers are covered by the module on top but wide
open underneath. That is where the wiring goes.

## Wire colours

Six colours, one job each. The figure colours match the wire you will actually cut.

| Wire | Carries |
| --- | --- |
| **Amarillo** | +12 V — both the raw IG line and VBAT after D1 |
| **Negro** | GND |
| **Verde** | +5 V, buck output |
| **Rojo** | +3.3 V, from the ESP32's own regulator |
| **Azul** | the two relay drives — IN1, IN2 |
| **Blanco** | the two signals that run to the OEM switch in the console — SW1, LED1 |

> **Three colours carry more than one net.** Amarillo Y1 (+12 V) and Y2 (VBAT) are
> separated by D1. Azul B1 (IN1) and B2 (IN2) are two different nets, and so are
> blanco W1 (SW1) and W2 (LED1). Same colour, never joined — go by the cut list,
> not by the colour.

This differs from the [figure colour code](README.md#wire-colour-code) in one place:
+5 V is **verde** here because copper-coloured wire is not in the box.

## Read this before the iron is hot

1. **Check your module's silkscreen against Fig. 12.** DevKit V1 clones exist with
   a different pin order. Find `VIN`, `GND`, `D33`, `D25`, `D26`, `D27` and
   `3V3` on your own board and confirm each sits in the row drawn. Everything else
   on this page depends on it.
2. **SS34 and SMAJ18A are usually surface-mount (SMA).** If yours are, either
   solder each across two adjacent pads on the solder side, or use the axial
   through-hole equivalents — **1N5822** for D1 and **P6KE18A** for D2 — which is
   what the drawings assume.
3. **Use a slow-blow (T) 2 A fuse.** 940 µF of bulk capacitance draws a brief
   inrush at key-on that a fast fuse can nuisance-trip.
4. **Leave the row-1 edge reachable.** The USB connector overhangs it, and the
   first flash and any recovery go through it. OTA only works once working
   firmware is already on the node ([ADR 0005](../decisions/0005-ota-in-maintenance-mode.md)).

## Component side

![Node A component placement](diagrams/12-node-a-placement.png)

**Fig. 12** — Every part and the holes it occupies, seen from above.

| Ref | Part | Holes | Mounting |
| --- | --- | --- | --- |
| J1 | IG input, 2-pin 90° header | `A27` +12 V · `B27` GND | header |
| J2 | Relay, 5-pin 90° header | `D27` JD-VCC · `E27` GND · `F27` IN1 · `G27` IN2 · `H27` VCC | header |
| J3 | OEM switch, 2-pin 90° header | `K27` SW1 · `L27` LED1 | header |
| D1 | SS34 / 1N5822 | `A26` anode · `A25` cathode | standing, 1 pitch |
| D2 | SMAJ18A / P6KE18A | `A24` cathode (**band**, VBAT) · `C24` anode (GND) | flat, 2 pitches |
| C1 | 470 µF / 35 V | `A23` + · `C23` − | radial, 2 pitches |
| U1 | Recom R-78E5.0-1.0 | `B21` +Vin · `C21` GND · `D21` +Vout | SIP3, three in a row |
| C3 | 470 µF / 16 V | `D19` + · `B19` − | radial, 2 pitches |
| U2 | ESP32 DevKit V1 | `A1`–`A15` and `L1`–`L15`, in female headers | socketed |

Eight parts and three connectors. **Columns A–D, rows 19–27** carry everything:
12 V in, the protection chain and the buck, with **column C** as the ground spine
running the height of it. **Columns E to L in rows 19–26 are empty** — 77 free
holes, deliberate headroom.

## Solder side

![Node A solder-side jumpers](diagrams/13-node-a-solder-side.png)

**Fig. 13** — The thirteen jumpers. **The board is flipped, so column A is on the
right.** Work from this figure with the board actually turned over and the letters
will line up; mirroring it again in your head is the classic way to wire a
perfboard backwards.

A run is one piece of wire soldered to every hole listed for it, in order.

| id | Wire | Solder at | Cut | What it does |
| --- | --- | --- | --- | --- |
| Y1 | amarillo | `A27` `A26` | 15 mm | IG input to D1's anode |
| Y2 | amarillo | `A25` `A24` `A23` `B21` | 25 mm | VBAT: D1 → D2 → C1+ → buck input |
| N1 | negro | `E27` `C27` `C24` `C23` `C21` | 32 mm | relay GND → spine → D2, C1−, buck |
| N2 | negro | `B27` `C27` | 15 mm | input GND onto the spine |
| N3 | negro | `C21` `B19` | 20 mm | spine to C3− |
| N4 | negro | `C21` `A2` | 65 mm | spine to the ESP32's GND |
| G1 | verde | `D19` `D21` `D27` | 32 mm | C3+ → buck output → relay JD-VCC |
| G2 | verde | `D21` `A1` | 70 mm | 5 V to the ESP32's VIN |
| R1w | rojo | `L15` `H27` | 50 mm | 3.3 V to the relay's VCC |
| B1 | azul | `A8` `F27` | 73 mm | GPIO25 to relay IN1 |
| B2 | azul | `A7` `G27` | 78 mm | GPIO26 to relay IN2 |
| W1 | blanco | `A6` `K27` | 88 mm | GPIO27 to SW1 |
| W2 | blanco | `A9` `L27` | 83 mm | GPIO33 to LED1 |

**646 mm of wire in total.** Lengths include 12 mm of slack for stripping and bends.

`C27` carries no component — it is a bare pad used as a junction, so three leads do
not have to share D2's.

**One run lies across a pad that belongs to something else:** N1 passes over `D27`,
the relay's JD-VCC pin. The wire is insulated, so this is fine — solder N1 after the
row-27 headers are in and press it flat. (G2 also passes over `D19`, but that pad is
the same +5 V net, so it does not matter either way.)

## How to mount and solder it

![Node A mounting technique](diagrams/14-node-a-technique.png)

**Fig. 14** — Standing versus flat axial parts, polarity, sockets, one jumper, and
the mirror rule.

## Order of work

Each stage ends with a measurement. **Do not go to the next stage until the
previous one passes** — finding a fault in stage 2 is ten minutes, finding it in
stage 7 is an afternoon.

### 1 · Sockets and connectors

Solder the two 15-way female headers into `A1`–`A15` and `L1`–`L15`, and the three
90° headers along row 27. Tack one pin of each female header, plug the ESP32 in,
check it sits square and flat, then solder the rest.

**Test:** the module plugs in and out without force. Continuity from each header
socket to its own pad and to nothing else.

### 2 · Power stage, no ESP32 fitted

Fit D1, D2, C1, U1, C3, then runs Y1, Y2, N1, N2, N3, N4, G1, G2.

**Test:** with the module *out* of its sockets, feed 12 V into J1 through a fused
bench supply. Measure at `D21`: **5.0 V ± 0.1 V**. Measure `A1` (the VIN socket):
the same 5.0 V. Measure `A2`: 0 V to supply negative. Then reverse the supply leads
deliberately for a moment — nothing should happen and nothing should get warm,
because D1 blocks and everything else sits behind it.

### 3 · ESP32

Plug the module in and power up.

**Test:** the module's power LED lights. Measure `L15`: **3.3 V**.

Then **disconnect the 12 V supply**, plug in USB, and flash a blink sketch to
confirm the toolchain works before anything else is added. Do not run both supplies
at once: on most DevKit V1 boards USB's 5 V and the VIN pin are tied together with
nothing between them, so an external 5 V and the USB host end up driving the same
node.

### 4 · Relay outputs

Add B1, B2 and **R1w** — without R1w the relay's opto side has no supply and nothing
will click. Connect the relay module to J2 with its **VCC–JD-VCC jumper removed**.

**Test, and this one matters:** power up with the relay connected but **its contacts
wired to nothing**. Neither relay may click at power-up or during boot. Then drive
GPIO25 and GPIO26 from firmware and confirm each clicks the channel you expect.

> **Confirm the module's polarity before it ever sees the BIU.** Most 2-channel
> opto modules are **active-LOW**: IN pulled low energises the relay. A floating pin
> then reads high and the relay stays off, which is the safe default — but check
> yours. A module that is active-HIGH will lock the doors every time the node boots.
>
> **Also confirm it works with VCC at 3.3 V.** These modules size the opto's
> resistor for 5 V, so at 3.3 V the LED gets about (3.3 − 1.2) / 1 kΩ ≈ **2 mA**,
> usually plenty — and when the GPIO goes high there is 0 V across the LED, so *off*
> is unambiguous.
>
> If a channel will not trip, **do not simply move VCC to 5 V.** A push-pull GPIO
> sitting at 3.3 V still leaves 1.7 V across the LED and its resistor — above a
> PC817's ~1.2 V forward voltage — so roughly 0.5 mA keeps flowing and the relay may
> never release. The correct fix is VCC at 5 V **with GPIO25/26 configured
> open-drain**, so "off" is a floating pin and no current can flow.

### 5 · Switch and tell-tale

Add W1 and W2.

**Test:** short `K27` to ground and confirm GPIO27 reads low. Leave the LED1 wire
unconnected at the switch end until
[`OC-07`](../04-integration/README.md#open-checks-on-the-vehicle) is measured on the
bench — the OEM indicator's series resistor is presumed internal and sized for 12 V,
and that has not been confirmed.

### 6 · Feed and ground resistance, before the trim goes back

Do this **with the node unplugged from J1**, on the resistance range — not by
watching for a voltage drop.

1. Touch the meter's probes together and note the lead resistance. Subtract it from
   every reading below.
2. Measure from the **fuse output** to the J1 harness's +12 V pin.
3. Measure from the J1 harness's GND pin to the **chassis stud** the node grounds to.

**Each should be well under 1 Ω.** Anything above that is a bad crimp, a corroded
fuse holder or a paint-insulated ground stud — fix it now, while the panel is open.

> **Why resistance and not voltage.** The obvious test is to watch the supply sag
> while a relay pulses. It does not work here. The relay coil runs off the **5 V**
> rail and draws ~71 mA; through the buck that is only a **~34 mA** step at the 12 V
> input, and the node's own steady draw is about the same. A properly bad 1 Ω joint
> then produces **34 mV** — invisible on a handheld meter in a car. You would need
> roughly **12 Ω**, an effectively broken wire, before a 0.5 V droop appeared. The
> load is too small to reveal the fault, so measure the joint itself.

### 7 · Inspection

Under a magnifier, with the board tilted to the light:

- Every joint shiny and concave, none domed or dull.
- Tug every jumper. A joint that moves is cold — reheat it, do not add solder.
- No stray solder bridging adjacent pads, especially along row 27.
- Every wire flat against the board, nothing standing proud where the enclosure
  will press on it.

Then run the [multimeter checklist](../04-integration/README.md#multimeter-checklist)
before the board goes anywhere near the car.

## What leaves the board

Nine wires, on three latching connectors along row 27, all exiting the same edge.

| Connector | To | Wires |
| --- | --- | --- |
| J1 | fuse box / chassis at the A-pillar | +12 V IG (fused, 2 A slow-blow), GND |
| J2 | the relay module, off the board | JD-VCC, GND, IN1, IN2, VCC |
| J3 | the OEM switch at connector i78 | SW1 (pin 1), LED1 (pin 8) |

The relay's own contacts go to BIU pins 15 and 29 — see
[Stage 2](node-a-locking.md#stage-2--relays-to-the-biu) and
[`OC-02`](../04-integration/README.md#open-checks-on-the-vehicle). The switch's pin
2 and the LED's pin 9 stay on their factory chassis grounds; nothing on this
connector returns through the board.

## Open on this board

- **`OC-07`** — the tell-tale LED's electrical specification. Until it is measured,
  W2 is fitted but left unconnected at the switch end.
- **The relay module's polarity and its behaviour at 3.3 V**, both bench tests in
  stage 4 above. Record what you find.
- **Rows 19–26 keep 77 of their 88 holes free**, and five ADC1 inputs are unused —
  GPIO32, plus the input-only GPIO34, 35, 36 and 39.
  That is deliberate headroom: the ignition divider that used to sit there was
  removed in v0.1.7 because it had no job the rest of the system was not already
  doing better. Anything added here should respect ADC1's 150–2450 mV band [19].
- The buck sits three rows from the module's antenna end. If the ESP-NOW link turns
  out weak on the bench, that distance is the first thing to suspect and now the
  easiest to change.
