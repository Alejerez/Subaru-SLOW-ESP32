# 0006 — Node C: an analogue front end, in the cabin

- **Status:** Accepted
- **Date:** 2026-08-30
- **Affects:** system architecture (the ESP-NOW link becomes a star), connector standard, roadmap v0.3
- **Detail:** [`docs/01-hardware/node-c-sensors.md`](../01-hardware/node-c-sensors.md)

## Context

Several roadmap items need analogue sensors that neither existing node can take.
Node B's analogue budget is two ADC1 channels once Wi-Fi claims ADC2
([ADR 0005](0005-ota-in-maintenance-mode.md)), and it sits on a 3 × 7 cm board in
the clock housing with no room to grow. Node A is deliberately sparse and lives at
the BIU.

The sensors themselves are mostly in the engine bay, or reached through it:
coolant level in the catch tank, radiator inlet and outlet temperature, ambient
air, battery voltage, brake caliper temperature at the wheels, and — for anyone
reproducing this on a turbocharged car — boost.

The goal stated for this node was not "read these five sensors". It was **to make
adding an analogue sensor later a small job**. That framing is what the design has
to satisfy, and a node specified as a fixed list of sensors would not satisfy it.

## Alternatives considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| **Extend Node B** | No new node, no new radio peer | No physical room on a 3 × 7 cm board in the clock housing; only two ADC1 channels left; loads the node that drives the display and polls SSM2 with unrelated work; couples the sensor package to the gauge so neither can be removed alone |
| **Node C in the engine bay**, next to the sensors | Shortest sensor runs | Needs an IP67 enclosure, a vent membrane against condensation, sealed connectors that are not the project standard, and an ESP32 working near its 85 °C ambient limit with heat soak after shutdown. Radio has to cross a steel firewall. Servicing means opening the bonnet |
| **Node C in the cabin**, at the firewall pass-through *(chosen)* | None of the above: standard enclosure, standard connectors, benign temperature, no condensation management, no firewall in the radio path, serviceable from inside | Sensor runs grow to 2–3 m and cross the engine bay, so they pick up noise; every sensor wire has to cross the firewall |

## Decision

**Node C is an analogue front end, located in the cabin, near the firewall
pass-through.** It has no display and no actuators. It reads channels, validates
them, and sends values to Node B over ESP-NOW at about 1 Hz.

Three parts to the decision:

**Channels are defined by type, not by sensor.** The node provides ratiometric
0–5 V channels, resistive NTC/RTD channels on three wires, and digital inputs.
Adding a sensor later means using a free channel of the matching type, not
redesigning the node. The specific sensors fitted first are documented in
[`node-c-sensors.md`](../01-hardware/node-c-sensors.md) as an instance of that
architecture, not as the architecture itself.

**Conversion is external, on ADS1115s over I²C** — 16-bit, programmable gain,
four addresses on one bus, and **differential inputs**. That last point is what
pays for the cabin location: a 3 m run past ignition coils and injectors picks up
noise, and a differential pair rejects it. Differential channels cost twice as
many inputs, so they are used where the run demands it, not everywhere.

**The environmental boundary is a sealed bulkhead connector at the firewall, not
the node.** Engine-bay side: environmental connectors and cable. Cabin side: the
project's normal JST/Micro-Fit standard. Sealing is confined to one connector
instead of contaminating the whole node. That connector is specified **with spare
pins from the first installation**, because it is the hardest part of the loom to
change afterwards — changing it means re-sealing the firewall pass-through.

## Consequences

**Makes easier**

- The node uses the same enclosure, connector and temperature assumptions as
  Nodes A and B. The project keeps one set of standards instead of two.
- Adding a sensor becomes "plug it in on the engine-bay side of the bulkhead and
  assign a free channel" — the stated goal.
- No IP67 enclosure, no vent membrane, no Deutsch connectors, no thermal derating
  of the ESP32, and **no firewall in the radio path**, which removes an entire
  open question about antenna variants.

**Makes harder / commits us to**

- **The ESP-NOW link becomes a star.** Until now it was Node B ↔ Node A. Node C
  sends to Node B, which is the display. This promotes the packet-format open item
  from a detail to a small protocol: node identity, message type and version have
  to be defined **before** Node C is built, or the format gets patched with
  hardware already installed.
- Analogue runs of 2–3 m through the engine bay. Mitigated by differential
  channels, heavy filtering (every quantity here is slow), and the rule below.
- **Every sensor's return comes back to the node**, never grounded locally at the
  engine. There are tens of millivolts between engine and chassis ground, more
  during cranking, and that difference otherwise lands inside the measurement.
- The caliper temperature sensors were specified with 1.5 m leads on the
  assumption of an engine-bay node. From the cabin they are longer — see the
  [cable schedule](../01-hardware/assembly-and-wiring.md#cable-lengths).

**A property worth naming**

The radio link **breaks the ground loop between the engine bay and the cabin**. A
wired system would have to carry the potential difference between the two grounds;
this one measures locally against its own reference and transmits numbers. It is a
benefit of the wireless architecture that had not been written down.

**Optionality becomes an architectural rule**

Node C is the first genuinely optional node. The gauge must not break because it
is absent: unavailable channels display as unavailable, exactly as
[stale data](../02-firmware/README.md#requirements-for-every-node) already
requires. **Nodes are optional by default and the system degrades gracefully.**

**Left unresolved**

- Where the radiator ΔT sensors mount — surface on the hoses, or in-line fittings.
  Recorded as an [open check](../04-integration/README.md#open-checks-on-the-vehicle).
- The zero calibration of the coolant level sender: this is a custom tank with no
  factory MIN/MAX marks, so the reference has to be established empirically.
- The final channel count, and therefore the pin count of the bulkhead connector.
- Battery **current** was considered and dropped. Its main use — cranking health —
  is served by voltage alone, and measuring it properly means a shunt in the main
  battery cable or a Hall sensor, across a dynamic range from milliamps to
  hundreds of amps. Parasitic draw, the other use, is measured with the ignition
  off, and this system is dead with the key out by design: a node awake to measure
  parasitic draw *is* parasitic draw.
- Thermocouples were considered and dropped in favour of PT1000 RTDs, which need
  no alloy-specific extension wire and no cold-junction compensation. See
  [`node-c-sensors.md`](../01-hardware/node-c-sensors.md#caliper-temperature).
