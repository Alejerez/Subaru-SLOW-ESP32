# Node A — Central locking

ESP32 next to the BIU (Body Integrated Unit), A-pillar. A **leaf of the ESP-NOW
star**: it receives speed from Node B, sends back the mode when the button is
pressed, and exchanges nothing with Node C.

Deliberately simple — power, relays, one button, one LED. There
is no VSS hardware at all ([ADR 0002](../decisions/0002-speed-over-ssm2-not-vss.md)),
and the auto-lock ON/OFF switch is physically on **this** node
([ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md)).

**Behaviour is specified in [`docs/02-firmware/`](../02-firmware/README.md#node-a--locking).**
**The bench build — hole-by-hole placement, jumpers and soldering order — is in
[`node-a-build.md`](node-a-build.md).** This page is the stages, values, pin map
and layout.

## Stages and exact values

### Stage 1 · Power (IG to 5 V)

The same chain as [Node B's supply](node-b-gauge.md#stage-1--power-ig-to-33-v--on-b-pwr),
with one difference that matters: Node A's buck is the **5 V** part, because the
relay module's coil needs 5 V.

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| F1 | Fuse + holder | **1 A slow-blow** | inline in +12 V (IG), before J1 | opens on a short |
| D1 | Schottky | **SB1100** (1 A, 100 V, DO-41) | +12 V → VBAT | reverse polarity, and 100 V of reverse rating against negative transients |
| D2 | Unidirectional TVS | **P6KE20A** (DO-15) | VBAT → GND | transients; V<sub>RWM</sub> 17.1 V, clamps at ~27.7 V |
| C1 | Electrolytic | **100 µF / 35 V, 105 °C** | VBAT → GND | input reserve |
| C2 | Ceramic | 100 nF **X7R, 50 V** | VBAT → GND | HF filter at the buck input |
| U1 | Switching regulator | Recom R-78E5.0-1.0 | VBAT → 5 V | **input 8–28 V**, 5 V / 1 A |
| C3 | Electrolytic | **100 µF / 16 V, 105 °C** | 5 V → GND | radio bursts |
| C4 | Ceramic | 100 nF X7R | 5 V → GND | HF filter at the buck output |
| C11 | Ceramic | 100 nF X7R | 5 V → GND, at the DevKit's VIN/GND pins | input cap for the module's own regulator |

> **Five of these changed in v0.1.8, and three are corrections rather than
> refinements.**
>
> **C3 was 470 µF, and the Recom's maximum capacitive load is 220 µF.** C3 sits on
> its output, so the old value was twice the limit: the module current-limits into
> the capacitor at start-up and hiccups instead of coming up, worst at the low
> input voltage of a cold crank. 100 µF is inside the limit with C4 and C11
> counted, and it cuts the inrush enough to drop the fuse from 2 A to 1 A.
>
> **SS34 and SMAJ18A are surface-mount parts, and the axial substitutes this
> repository named could not be fitted.** A 1N5822 is DO-201AD: 1.2–1.3 mm leads
> against 1 mm perfboard holes. A P6KE18A is DO-15: a 6.6 mm body against a
> 5.08 mm hole span. SB1100 (DO-41, 0.8 mm leads) and P6KE20A on a 3-pitch
> footprint both fit. P6KE20A also clamps at 27.7 V rather than the SMAJ18A's
> 29.2 V, which is the first time this design's TVS has actually been below the
> buck's 28 V input maximum.
>
> **C2, C4 and C11 did not exist.** The page used to say the stage was identical
> to Node B's, which carried all three; Node A carried none, and its only 5 V
> decoupling was an electrolytic 70 mm of wire from the module's VIN pin.
>
> **The node still resets while cranking**, and that is accepted: the Recom needs
> 8 V, D1 costs 0.4 V, and 100 µF holds about 2 ms. State is not persisted, so
> every ignition cycle starts ARMED.
>
> **D2 sits behind D1 and therefore cannot protect it.** A negative transient on
> the IG feed is blocked by D1 and never reaches the TVS, so it appears across
> D1's reverse rating — which is why D1 is now a 100 V part. This is an
> IG-switched cabin feed downstream of the fuse box, not a raw battery line, so
> the exposure is modest; it is recorded rather than designed around.

### Stage 2 · Relays to the BIU

| Ref | Component | Control connection | Contacts |
| --- | --- | --- | --- |
| K1 | 2-channel relay module (5 V) | VCC→3.3 V · JD-VCC→5 V (jumper removed) · IN1→GPIO25 · IN2→GPIO26 | — |
| K1·CH1 | LOCK relay | GPIO25 | COM→BIU p15 · NO→GND |
| K1·CH2 | UNLOCK relay | GPIO26 | COM→BIU p29 · NO→GND |

> **Pulse, not level.** COM goes to the BIU wire and NO to ground, so energising a
> relay momentarily grounds that wire — a negative pulse. It is never held; the
> [pulse duration](../02-firmware/README.md#v01-parameters) is a firmware parameter.

### Stage 3 · ON/OFF button (reused OEM switch)

An unused OEM switch — the **windscreen-wiper de-icer**, a North-American-market
option this EDM car does not have — wired **directly to Node A**. It does not go
through Node B and does not travel over ESP-NOW; why, and what was rejected, is in
[ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md).

![The unused OEM switch, marked in red](photos/oem-switch-panel.jpg)

**Photo** — The switch panel to the left of the steering wheel. The button marked
in red is the unused wiper de-icer switch that becomes the auto-lock ON/OFF
control.

#### The OEM circuit

![Factory wiring diagram of the wiper de-icer circuit](reference/wiper-deicer-circuit-wd-01.png)

**Figure** — Factory wiring diagram WD-01 / WI-12551. The push switch is the
block outlined in red; its connector, **i78 (blue)**, is outlined at the bottom.
See [reference material](reference/README.md) for provenance and licensing.

In the factory circuit the switch does *not* drive the de-icer relay directly.
Two fuses feed the circuit — F/B no. 9 (constant, LB) to the relay contacts and
F/B no. 4 (ignition, GY) to the relay coil — and the relay's contact output (RY)
feeds both the heating element and the switch. The coil's return path goes to the
**Body Integrated Unit**, which is what decides to energise it; that is why the
BIU sits in the middle rather than the switch simply closing the coil circuit.

The switch itself is **two devices in one body**, and that is the finding that
matters here:

| Pin | Wire | Goes to | What it is |
| --- | --- | --- | --- |
| **1** | OrG | BIU pin A14 | switch contact, high side |
| **2** | B | chassis ground | switch contact, low side |
| **8** | RY | relay contact output | indicator LED, high side |
| **9** | B | chassis ground | indicator LED, low side |

So the button is a **momentary contact between pins 1 and 2** (confirmed by
inspection on this car — unlike the folding-mirror switch in the same console, it
does not latch), plus an **indicator LED between pins 8 and 9** that in the
factory circuit lights only when the de-icer element is actually energised, not
when the button is pressed.

#### What the project takes from it

**Pins 1 and 2, and nothing else.** Pin 2 is already at chassis ground and pin 1
is a dry contact — exactly the topology this stage needs: `INPUT_PULLUP` on
GPIO27, other side to ground. No divider, no clamp, no conditioning.

**No new cable.** The OrG wire already runs console → BIU, and the BIU is where
Node A is installed — see the [cable schedule](assembly-and-wiring.md#cable-lengths).

> ⚠️ **Disconnect pin 1 from the BIU; do not tap it in parallel.** Sharing the node
> between the BIU's input and the ESP32's pull-up would signal every press to both.
> Even with no de-icer to operate, "probably harmless" is not a standard to apply
> to a body control module. Disconnecting at the switch connector also keeps the
> modification reversible.

#### The tell-tale LED

With no de-icer relay fitted, pin 8 receives nothing and the OEM indicator never
lights. Driven from Node A instead it becomes a status light **inside the OEM
button** — the most retromod outcome available.

It signals **DISABLED, not ARMED** — the reasoning is in
[ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md#amendments).

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| SW1 | OEM switch contact (i78 pins 1–2) | — | GPIO27 ← R9 ← switch ↔ GND | momentary; toggles ARMED ⇄ DISABLED |
| R9 | Resistor | 1 kΩ | switch → node_SW1 | series limit on a wire that leaves the cabin |
| C12 | Ceramic | 100 nF X7R | node_SW1 → GND | filter and ESD path, at the pin |
| LED1 | OEM indicator (i78 pins 8–9) | — | GPIO33 → R8 → pin 8 · pin 9 to GND | lit while DISABLED |
| R8 | Resistor | **0 Ω link until `OC-07`** | GPIO33 → pin 8 | the footprint that lets a value be fitted later |

> **SW1 gets 1 kΩ and 100 nF, which it did not have before.** The input relies on
> the ESP32's ~45 kΩ internal pull-up, and it is the only input that leaves the
> enclosure — it reuses the factory OrG run, metres of unshielded wire through the
> dash. A 45 kΩ node on the end of that is an antenna with no series resistance
> and no ESD path. Two parts fix it; the [ADR 0004](../decisions/0004-reuse-oem-contact-pad-buttons.md)
> argument that the internal pull-up suffices was written for Node B's 100 mm
> button pads, not for this run.
>
> Note also that the switch's pin 2 returns to the **console** ground while the
> board references the **A-pillar** stud. Any offset between the two appears
> directly on the input; with a 0.8 V threshold there is room for it, but it is
> worth knowing.

**How the tell-tale is driven is `OC-07`, and it is more open than this page used
to admit.** The factory diagram draws it as an LED, but a lamp and an LED are
drawn alike, and a 2006 switch tell-tale may well be an incandescent bulb — which
on a GPIO would destroy the pin. Even granting an LED, the claim that its series
resistor sits inside the switch body is an inference from the absence of a
discrete part on a wiring diagram, and the "roughly 2 mA" that followed was a
guess resting on that inference.

So the board now carries **R8 as a footprint with a 0 Ω link in it**, and `W5`
stays disconnected at the switch end until the load is measured with a
current-limited supply ramped from zero. Measuring first also settles whether the
fallbacks — a low-side MOSFET from the protected 12 V rail, or replacing the
twenty-year-old indicator — are needed at all:
[`OC-07`](../04-integration/README.md#open-checks-on-the-vehicle).

**Whether pin 8's wire even reaches the node is not established.** ADR 0003 rules
out a new cable run on the grounds that the OrG wire already runs console → BIU;
that argument covers pin 1. Pin 8 is the RY wire, which the factory diagram routes
to the de-icer relay's contact output — a relay this car does not have, at a
location this repository has never identified. The [cable
schedule](assembly-and-wiring.md#cable-lengths) has a row for SW1 and none for
LED1 for exactly that reason.

## ESP32 pin map (Node A)

| Function | GPIO | Note |
| --- | --- | --- |
| LOCK relay (IN1) | 25 | → BIU p15 |
| UNLOCK relay (IN2) | 26 | → BIU p29 |
| ON/OFF button | 27 | `INPUT_PULLUP` · reused OEM switch contact (i78 pins 1–2), see Stage 3 |
| Status tell-tale | 33 | output · OEM indicator LED (i78 pins 8–9), lit while DISABLED |
| Speed (receive) | — (radio) | ESP-NOW ← Node B |
| Mode confirmation (transmit) | — (radio) | ESP-NOW → Node B, to show on the OLED |

**Spare:** five ADC1 inputs are free — GPIO32, and the input-only GPIO34, 35, 36 and
39 — and rows 19–26 of the board keep 77 empty holes. The ignition divider that used to occupy GPIO34 was removed in
v0.1.7 — the node is fed from IG, so being powered already proves the ignition is
on, and battery voltage is measured better by [Node B over SSM2](../02-firmware/README.md#node-b--gauge)
and by [Node C](node-c-sensors.md#ambient-air-and-battery-voltage).

## Schematics and layout

The state machine, the thresholds and the pulse timing are in
[`docs/02-firmware/`](../02-firmware/README.md#node-a--locking), with Fig. 6.

### Interface schematic

![Node A interface](diagrams/07-node-a-interface.png)

**Fig. 7** — Node A interface. The relay module sits off the board with its screw
terminals. The ON/OFF button is wired straight to GPIO27 with the internal
pull-up; the ESP-NOW link carries speed inbound and the mode change outbound.

### Spatial layout

![Node A spatial layout](diagrams/08-node-a-spatial-layout.png)

**Fig. 8** — Node A spatial layout. Speed arrives over ESP-NOW with no cable; the
ON/OFF switch is wired directly to the node (Stage 3). The relay module sits off
the board with its terminals facing the BIU. IG is taken at the A-pillar.

### Grid plan

![Node A grid plan](diagrams/09-node-a-grid-plan.png)

**Fig. 9** — Node A grid plan, by zone. The relay module is external, so the free
area is deliberate headroom for later I/O. The exact hole-by-hole layout is
[Fig. 12](node-a-build.md#component-side); same 3 × 7 cm board as Node B, see
[perfboard size](README.md#perfboard-size-correction-to-the-source-document).
