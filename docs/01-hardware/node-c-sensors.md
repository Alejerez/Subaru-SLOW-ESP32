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
| **Resistive NTC / RTD** | pull-up forms a divider; **3-wire** so lead resistance cancels | PT1000 surface sensors, coolant and oil temperature senders, ambient air |
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
- **Each sensor's return comes back to the node.** Never ground a sensor locally
  at the engine. The potential difference between engine and chassis ground is
  tens of millivolts, more during cranking, and it lands directly in the reading.

Protection per channel follows the pattern already used on Node B: series
resistor, divider, Schottky clamp to the 3.3 V rail, RC filter.

## The bulkhead connector

A single **sealed connector at the firewall** is the boundary between the two
environments. Engine-bay side: environmental connectors and cable. Cabin side: the
project's standard JST / Micro-Fit. Sealing is confined to that one connector
instead of being a property of the whole node.

**Specify it with spare pins from the first installation.** It is the hardest
element of the loom to change later, because changing it means re-sealing the
firewall pass-through. Its final pin count depends on the channel count, which is
an open item in [ADR 0006](../decisions/0006-node-c-analogue-front-end.md).

## Sensors fitted first

### Coolant level — catch tank

![The aluminium catch tank](photos/coolant-catch-tank.jpg)

**Photo** — The 2 L welded catch tank fitted to this car, which replaced the OEM
expansion bottle when the larger aluminium radiator went in. The radiator hose
connects to the lower spigot; the upper side spigot is blocked; the cap's pressure
function is defeated and the outlet at the cap is **open to atmosphere**.

**The tank is not pressurised.** That bounds the sensor's requirements usefully:
liquid up to roughly 105–110 °C, no pressure rating, no pressure-rated seal. It
also means standard float senders are usable.

**What is being measured, and what is not.** The purpose is *not* to measure
thermal expansion. It is to know **when to top up**, so the radiator never draws
air, and to know when the tank is close to overflowing. Thermal expansion — of the
order of 600 mL, which over this tank's cross-section is roughly **4 cm** of level
— is therefore a *disturbance*, not the signal.

That inverts the requirements from what one would first assume:

- **Resolution can be coarse.** Knowing which third of the tank you are in is
  enough. A reed-chain float sender with ~1 cm steps gives about ten usable steps
  over the tank height, which is more than the decision needs, and quantisation
  provides its own hysteresis. A continuous resistive float sender works equally
  well.
- **The reading only means something referred to a known thermal state.** A level
  taken hot and one taken cold differ by about a third of the tank. **The number
  that matters is the cold one**, captured on the first reading after a cold soak
  — in practice, when the key is turned in the morning. It is retained and
  displayed; the live level while driving is not a useful answer to "should I top
  up".

**Why cold, physically.** As the system cools it draws coolant back from the tank
into the radiator. If the tank empties during that draw-back, the radiator takes
air. In winter the fall from operating temperature to ambient is larger, more
volume is drawn back, and the tank must therefore start higher. The critical value
is the minimum of the cycle, which occurs fully cold.

**Working range.** There are no factory MIN/MAX marks on a custom tank, so they
are defined here by the tank's own geometry:

| Mark | Definition | Why |
| --- | --- | --- |
| **MIN** | 1 cm above the level of the lower spigot | keeps the radiator's return submerged so it never draws air |
| **MAX** | 1 cm below the upper spigot | leaves headroom so expansion does not reach the overflow path |

A check to run with real measurements before trusting the scale: **the cold level
must be at or above MIN, and cold level plus thermal expansion must stay at or
below MAX.** Since the expansion is around 4 cm, the usable cold-fill window is
not MIN-to-MAX — it is MIN to (MAX − expansion). If that window turns out to be
narrow or negative, the tank is too small for the system's expansion volume, which
is worth knowing.

**A second function from the same sensor: sudden-loss detection.** A failed hose
or a head gasket pushing coolant out shows as a **rapid, monotonic fall**. That is
easy to separate from slosh, which oscillates about zero, and from expansion,
which rises with temperature. It is a rate-of-change detector rather than a
threshold, and on track it warns before the temperature gauge does.

**Two things that are normal and should not be mistaken for faults.** The tank is
vented to atmosphere, so it loses a little coolant to evaporation over time — the
long record will show a slow downward drift that is not a leak. And a **stilling
well** around the float (a vertical tube, closed at the sides, open at the bottom
through a small orifice) damps slosh mechanically. With the reading taken cold it
is no longer essential, but it costs almost nothing if the sender mount is being
fabricated anyway, and it helps the sudden-loss detector while driving.

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
around 230 °C dry and well below that once moisture is absorbed, so a sensor that
covers up to ~250 °C spans the entire useful range: if it saturates, the brakes are
already past their limit.

Bonded rather than bolted. Every fastener on a caliper is safety-critical, and an
adhesive sensor avoids the question entirely.

Lead length: **2.5–3 m** to reach the cabin. Confirm before ordering — an earlier
draft assumed 1.5 m, from when the node was to live in the engine bay.

### Radiator ΔT

Two channels, radiator inlet and outlet. The **difference** is the diagnostic: a
falling ΔT at a given load points at a blocked radiator or a tired water pump.
Absolute coolant temperature is already available over SSM2 and on the car's Defi
gauges, so it is the delta and its trend that this adds.

Mounting is [not yet decided](../04-integration/README.md#open-checks-on-the-vehicle).
Surface sensors on the hoses are non-invasive but read below the true coolant
temperature and lag it; for a difference that bias partly cancels, though not
entirely, since flow and hose material differ between inlet and outlet. In-line
fittings are accurate but mean cutting hoses and accepting two more potential
leak points.

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

Every quantity here is slow. **About 1 Hz** is generous; several channels would be
adequate at 0.2 Hz. The speed message from Node B to Node A stays at 100–200 ms and
is not affected — ESP-NOW has ample capacity, and slowing that message would have
degraded the locking watchdog for no benefit.

Each reading carries a **validity flag**. An open or shorted sensor reports as
invalid and the gauge shows the channel as unavailable rather than displaying a
plausible wrong number — the same rule as
[stale data](../02-firmware/README.md#requirements-common-to-both-nodes).

## Open items

- Zero calibration of the level sender against MIN and MAX as defined above, on a
  properly bled, cold system.
- Radiator ΔT sensor mounting: surface or in-line.
- Final channel count, and therefore the pin count of the bulkhead connector.
- The ESP-NOW packet format, which with a third node becomes a small protocol
  rather than two message types — node identity, message type, version. This has
  to be settled **before** Node C is built. Tracked in
  [`docs/02-firmware/`](../02-firmware/README.md#open-items).
