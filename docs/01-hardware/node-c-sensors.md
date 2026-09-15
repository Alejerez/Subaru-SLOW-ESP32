# Node C — Analogue front end

ESP32 in the cabin, near the firewall pass-through. No display, no actuators: it
reads analogue and digital channels, validates them, and sends values to Node B
over ESP-NOW at about 1 Hz.

Planned for **v0.3** — see [`ROADMAP.md`](../../ROADMAP.md). The reasoning behind
its architecture and its location is in
[ADR 0006](../decisions/0006-node-c-analogue-front-end.md).

![Node C channel architecture](diagrams/11-node-c-channels.png)

**Fig. 11** — The node lives in the cabin; only the bulkhead connector has to
survive the engine bay. Channels are defined by type, so adding a sensor later
means using a free channel of the matching type rather than redesigning anything.

## Channel architecture

This is the part that matters. The sensors below are an instance of it, not a
definition of it.

| Channel type | Interface | Suits |
| --- | --- | --- |
| **Ratiometric 0–5 V** | sensor fed 5 V, returns 0–5 V, divided to 3.3 V. Single-ended, or differential where the run is long | boost, oil and fuel pressure, most aftermarket senders |
| **Resistive NTC / RTD** | pull-up forms a divider | PT1000 surface sensors, coolant and oil temperature senders, ambient air |
| **Digital in** | pulled up, switch to ground | float switches, fan state, any on/off |

Conversion is external: **ADS1115 over I²C** — 16 bit, programmable gain, four
addresses on one bus, and differential inputs. The ESP32's own ADC is not used for
measurement here; it is non-linear, noisy, its reference moves, and ADC2 is
unavailable altogether once Wi-Fi is in the firmware
([ADR 0005](../decisions/0005-ota-in-maintenance-mode.md)).

Two rules that apply to every channel:

- **Ratiometric sensors are measured against their own 5 V supply**, not against
  an absolute reference. Otherwise every variation of the supply appears as sensor
  error. For channels where the sensor draws enough current to matter, use four
  wires: supply, sense, signal, return.
- **Each sensor's return comes back to the node** — never grounded locally at the
  engine, for the reason given in
  [ADR 0006](../decisions/0006-node-c-analogue-front-end.md#consequences).

Protection per channel follows the pattern already used on Node B: series
resistor, divider, Schottky clamp to the 3.3 V rail, RC filter.

## The bulkhead connector

A single **sealed connector at the firewall** is the boundary between the two
environments — environmental connectors and cable on the engine-bay side, the
project's standard Micro-Fit on the cabin side. It is specified **with spare pins
from the first installation**; its pin count is
[`OC-11`](../04-integration/README.md#open-checks-on-the-vehicle). Why the boundary
is the connector and not the node is in
[ADR 0006](../decisions/0006-node-c-analogue-front-end.md#decision).

## Sensors fitted first

### Coolant level — catch tank

![The aluminium catch tank](photos/coolant-catch-tank.jpg)

**Photo** — The 2 L welded catch tank fitted to this car, which replaced the OEM
expansion bottle when the larger aluminium radiator went in. The radiator hose
connects to the lower spigot; the upper side spigot is blocked; the cap's pressure
function is defeated and the outlet at the cap is **open to atmosphere**.

**The tank is not pressurised.** That bounds the sensor usefully: liquid to
roughly 105–110 °C, no pressure rating, no pressure-rated seal. Standard float
senders are usable.

**What is measured, and what is not.** The purpose is to know **when to top up**,
so the radiator never draws air, and when the tank is near overflowing. Thermal
expansion — assume **about 600 mL** until it is measured, which over this tank's cross-section is roughly **4 cm**
of level — is a *disturbance*, not the signal. Two consequences:

- **Resolution can be coarse.** Knowing which third of the tank you are in is
  enough. A reed-chain sender with ~1 cm steps gives about ten usable steps, and
  quantisation provides its own hysteresis. A continuous resistive sender works
  equally well.
- **Only the cold reading means anything.** Hot and cold levels differ by about a
  third of the tank. The number that matters is captured on the first reading
  after a cold soak — in practice when the key is turned in the morning. It is
  retained and displayed; the live level while driving does not answer "should I
  top up".

**Why cold.** As the system cools it draws coolant back from the tank into the
radiator; if the tank empties during that draw-back, the radiator takes air. In
winter the fall from operating temperature to ambient is larger, more volume is
drawn back, and the tank must start higher. The critical value is the minimum of
the cycle, which occurs fully cold.

**Working range.** No factory marks exist on a custom tank, so they come from its
geometry:

| Mark | Definition | Why |
| --- | --- | --- |
| **MIN** | 1 cm above the lower spigot | keeps the radiator's return submerged so it never draws air |
| **MAX** | 1 cm below the upper spigot | leaves headroom so expansion does not reach the overflow path |

Since expansion is around 4 cm, **the usable cold-fill window is MIN to
(MAX − expansion)**, not MIN to MAX. If that window turns out narrow or negative,
the tank is too small for the system's expansion volume — worth knowing. Verify
against real measurements: [`OC-09`](../04-integration/README.md#open-checks-on-the-vehicle).

**Sudden-loss detection, from the same sensor.** A failed hose or a head gasket
pushing coolant out shows as a **rapid, monotonic fall** — easy to separate from
slosh, which oscillates about zero, and from expansion, which rises with
temperature. A rate-of-change detector, not a threshold, and on track it warns
before the temperature gauge does.

**Two normal behaviours that are not faults.** The tank is vented, so it loses a
little coolant to evaporation: the long record shows a slow downward drift that is
not a leak. And a **stilling well** around the float — a vertical tube open at the
bottom through a small orifice — damps slosh mechanically. With the reading taken
cold it is not essential, but it costs almost nothing if the sender mount is being
fabricated anyway.

Mounting: a bung welded to the tank's top face. This tank is already an aftermarket
part fabricated for this car, so adding a bung is ordinary fabrication — the
project's rule against modifying OEM parts does not apply to it.

### Caliper temperature

**PT1000 surface RTDs, bonded with high-temperature adhesive**, one per front
caliper. Not thermocouples, and not infrared.

The RTD avoids both problems that make a thermocouple awkward here. It needs **no
alloy-specific extension wire** — ordinary copper, with a third wire to cancel lead
resistance — and **no cold-junction compensation**, so nothing has to know the
temperature of the connector or of the amplifier. It is simply a resistance, which
lands on a resistive channel like any other.

Range suits the measurement. A typical surface PT1000 reaches 200–250 °C. What is
being measured is the **caliper body**, which is neither rotor nor pad temperature
— it lags and reads much lower — but is a good proxy for **brake fluid
temperature**, which is what produces fade and a long pedal. Good DOT4 boils
at least 230 °C dry — that is the DOT4 *minimum*, and racing DOT4 reaches 300–320 °C — and well below that once moisture is absorbed, so a sensor that
covers up to ~250 °C spans the entire useful range: if it saturates, the brakes are
already past their limit.

Bonded rather than bolted. Every fastener on a caliper is safety-critical, and an
adhesive sensor avoids the question entirely.

Lead length is in the [cable schedule](assembly-and-wiring.md#cable-lengths).

### Radiator inlet and outlet

Two channels, radiator inlet and outlet. The **difference** is the diagnostic: a
falling ΔT at a given load points at a blocked radiator or a tired water pump.
Absolute coolant temperature is already available over SSM2 and on the car's Defi
gauges, so it is the delta and its trend that this adds.

Mounting is [`OC-10`](../04-integration/README.md#open-checks-on-the-vehicle):
surface sensors on the hoses are non-invasive but read low and lag, though for a
*difference* that bias partly cancels; in-line fittings are accurate but mean
cutting hoses and accepting two more leak points.

### Ambient air, and battery voltage

**Ambient air:** one NTC, sited in the engine bay or behind the front bumper.

**Battery voltage:** a divider at the battery. Measured locally rather than taken
from SSM2 because the ECU's reported voltage is coarse, and because **during
cranking — exactly when the reading is interesting — SSM2 polling stalls**. Battery
*current* was considered and deliberately left out; see *Left unresolved* in
[ADR 0006](../decisions/0006-node-c-analogue-front-end.md).

### Boost — provision only

Not fitted: this car is naturally aspirated. It is listed because a boost sensor is
a 3-wire ratiometric 0–5 V device, which is to say **it is not a feature of this
node at all — it is one free 0–5 V channel**. Anyone reproducing this project on a
turbocharged car connects the sensor and assigns a channel. Documenting it costs
nothing and demonstrates that the channel-typed architecture does what it claims.

## Update rate and validity

Every quantity here is slow; several channels would be adequate at 0.2 Hz. The
cadence, the validity flag and what they mean for the radio link are specified in
[`docs/02-firmware/`](../02-firmware/README.md#link-topology).

## Open items

- [`OC-09`](../04-integration/README.md#open-checks-on-the-vehicle) — level sender
  zero calibration against MIN and MAX, on a bled, cold system.
- [`OC-10`](../04-integration/README.md#open-checks-on-the-vehicle) — radiator ΔT
  sensor mounting.
- [`OC-11`](../04-integration/README.md#open-checks-on-the-vehicle) — channel
  count, and therefore the bulkhead connector's pin count.
- The **ESP-NOW packet format**, which with a third node becomes a small protocol.
  Settle it **before** Node C is built —
  [`docs/02-firmware/`](../02-firmware/README.md#open-items).

## What must be specified before this node is built

This node is a **channel architecture with no numbers in it**. That is not the
same as being wrong, and it is worth stating plainly, because two sibling nodes
carried resistor dividers that put more than 3.3 V on an ESP32 pin for eight
releases, and the reason nobody caught them earlier is that nobody could: the
values were inherited rather than derived. Node C is in the state those dividers
were in before v0.1.8 — except that here the values do not exist at all, so the
same review cannot even be run.

Nothing below changes the architecture. It is the list of things that have to
acquire a number, and the specific traps found when the arithmetic was attempted.

### A per-channel table, and the rule it has to satisfy

Every channel needs: excitation voltage, divider or pull-up values, the ADS1115's
own **VDD**, the PGA setting, worst-case node voltage at worst-case input, source
impedance, and filter corner. The rule they must satisfy is the ADS1115's, and it
is not the one the ESP32 taught us:

> **Do not apply more than VDD + 0.3 V to an analogue input, whatever the PGA.**
> A ±6.144 V or ±4.096 V full-scale setting does not extend the input range — it
> only throws resolution away, and full-scale codes become unreachable. So the
> ADC's supply, the excitation and every divider have to be chosen together.

Input impedance is gain-dependent and collapses at the sensitive settings:
differential 22 MΩ at ±6.144 V down to 710 kΩ at ±0.256 V, and **common-mode
100 kΩ** at the two lowest ranges. A low-level channel — a 0–190 Ω float sender —
naturally wants those ranges, where a 10 kΩ source costs over 1 % of reading. The
table has to budget source impedance against the chosen PGA, per channel.

### Three claims in this page that do not survive arithmetic

**"3-wire so lead resistance cancels" was removed above.** On **PT1000** it buys
almost nothing: 3 m of 22 AWG is 0.318 Ω round trip against 3.62 Ω/K at 250 °C —
**0.09 °C**. Three-wire is a PT100 practice, where the same error is 0.83 °C. And
it cannot work as drawn anyway: with a pull-up divider and a multiplexed ADC, the
third wire does nothing unless a reference resistor or current source is specified
and firmware takes a second measurement, and none of that exists here. Meanwhile
the errors that *do* dominate are unspecified — **1 % on the excitation rail is
15.8 °C at 250 °C**, and 1 % on the pull-up is 5.4 °C. Either specify a
ratiometric front end (a 0.1 % reference resistor in series, both legs measured,
ratio taken in firmware) or go 2-wire, accept 0.09 °C, and free two bulkhead pins.
The same applies to the NTCs, where 3-wire buys **0.013 °C**.

**"Ratiometric sensors are measured against their own 5 V supply" cannot be done
by powering the ADC from that supply.** The ADS1115 has an integrated reference
and cannot use an external one. The only way to honour the rule is to divide the
5 V rail into a channel of its own and take the ratio in firmware — which costs a
channel, and which nothing here specifies.

**The ADS1115's four addresses are a ceiling, not just a feature.** Four chips is
**16 single-ended or 8 differential inputs, total**. The first installation already
wants 8 measurement channels; add the rail channel ratiometric operation needs,
put the 3 m caliper runs on differential pairs as [ADR 0006](../decisions/0006-node-c-analogue-front-end.md)
argues they should be, and the realistic count is 3–4 chips — the whole address
space, with no headroom. The ADR's stated goal is "to make adding an analogue
sensor later a small job", and the bulkhead connector is deliberately
over-provisioned with spare pins for exactly that. Those spare pins would lead to
a full bus. The escape is a second I²C bus on a spare GPIO pair, or a mux ahead of
one ADS1115 — decide which, and say so, **before `OC-11` closes and the firewall
is sealed.**

### The battery channel is `OC-12` again, on a permanently live feed

The cable schedule runs battery voltage from the battery post, fused at the
battery, to the bulkhead. That is a **constant** supply, and Node C is fed from IG
and dead with the key out — the exact mechanism
[`OC-12`](../04-integration/README.md#open-checks-on-the-vehicle) exists to
measure on Node B's ILL line, except that this one is live all the time rather
than only when the lights are on.

With a 68 k / 10 k divider the node wants 1.54 V at rest; with the ADC's rail at
0 V its input structure clamps near 0.6 V and **(12.6 − 0.6) / 68 k ≈ 176 µA**
flows into the dead rail, continuously, for as long as the car is parked. That is
1.5 Ah a year against a principle this project states as
[zero parasitic draw](../00-concept/README.md#zero-parasitic-draw).

**Feed the divider's top leg from the node's own IG-switched 12 V, not the battery
post.** Then verify that IG stays live through START on this chassis, because the
channel's stated justification is the cranking measurement. A genuine key-out
reading would need a high-side switch, not a bare resistor.

### The node has no power stage

The catalogue's Node C block lists an ESP32, ADS1115s, sensors and the bulkhead
connector. There is **no buck, no fuse, no Schottky, no TVS, no bulk capacitance,
no perfboard and no connectors**, and the v0.1 quantities are explicitly for Nodes
A and B. The integration page's rule is "1 A fuse on every 12 V feed, no
exceptions"; Node C has no instance of it.

Note also that the obvious reuse does not fit its own justification: the 5 V Recom
needs **8 V in**, and the node whose reason for measuring battery voltage locally
is *"during cranking — exactly when the reading is interesting"* is the node most
likely to brown out during cranking. The 3.3 V variant's 7 V helps and does not
solve it. Either specify hold-up capacitance sized for the dip, or state plainly
that the sub-8 V part of a crank is not measured.

### Input protection is inherited from a node with a different ADC

"Protection per channel follows the pattern already used on Node B" imports a
topology designed for a 12-bit ESP32 input on a 3.3 V rail. Two problems: the
clamp must go to **the ADS1115's** VDD, which is unspecified; and BAT85 is the
wrong clamp for a 16-bit front end, where its reverse leakage is a drifting error
on a node whose LSB is 62.5 µV. A low-leakage part such as BAV199 costs the same.
The series resistor is not optional either — it is what limits the current when a
sensor wire shorts to 12 V in the engine bay — and its value fights the source-
impedance budget above. Nobody has arbitrated that fight.

### The caliper run is specified by length and the word "shielded"

Missing, all of it: the jacket's temperature rating (the sensor is bonded to a
body that reaches 250 °C; ordinary automotive PVC is 85–125 °C, so the first
stretch needs PTFE or fibreglass); **which end the shield is grounded at** — both
ends would create precisely the engine-bay-to-cabin ground loop ADR 0006 names as
the architecture's signature benefit; routing across moving suspension and
steering lock-to-lock; and the adhesive, which has no product, no rating and no
surface prep, for a bond that must survive 250 °C and brake dust for the life of
the car. Its failure mode is silent: the sensor debonds and reads *low*, which is
the direction that does not alarm.

### Two smaller corrections

**The radiator ΔT claim is dominated by sensor matching, not resolution.** With
generic 10 k NTCs, a 1 % R25 mismatch is 0.34 °C but a **3 % beta mismatch is
2.5 °C** — on a 10–15 °C signal, a fifth of the reading. Either specify
interchangeable-class parts or a two-point bath calibration, or say that only the
*trend* is meaningful and only while the same two sensors stay fitted.

**An "ambient" NTC in the engine bay does not read ambient.** It reads heat soak:
15–30 °C high while driving and 60–90 °C after shutdown. The bumper is the only
one of the two locations offered that works, and ambient is used in the winter
draw-back reasoning that sets the coolant MIN mark.
