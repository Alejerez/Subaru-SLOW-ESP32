# 04 — Integration with the vehicle

Vehicle: **Subaru Legacy 3.0R, BL/BP chassis, EDM.**

Covers only what happens at the car: the order things are installed, what to
measure, and what is still unknown about this particular vehicle. Component
values are in [`docs/01-hardware/`](../01-hardware/README.md); behaviour is in
[`docs/02-firmware/`](../02-firmware/README.md).

## Install sequence

Node C is not part of this sequence — it is v0.3 and has not been built.

1. **Bench-test each node** on a fused 12 V supply. Verify 5.0 V out of the buck
   and that the ESP32 powers up.
2. **Build and verify Node B's two boards stage by stage**, following
   [`node-b-build.md`](../01-hardware/node-b-build.md#order-of-work): the umbilical
   first, then B-PWR (supply, K-line, ILL divider), then B-GAUGE. Its stage 3 test —
   that the transceiver idles K high and follows TX — must pass on the bench before
   the K wire is ever connected to the car.
3. **Build and verify Node A** stage by stage, following
   [`node-a-build.md`](../01-hardware/node-a-build.md#order-of-work). Its stage 4
   test — that neither relay clicks at power-up — must pass before the module is
   ever connected to the BIU.
4. **Build the i59 adapter** from the three iWire pieces and check continuity pin
   by pin before it goes anywhere near the car. Settle first whether the K-line
   runs through the adapter or beside it —
   [still open](../01-hardware/assembly-and-wiring.md#i59-adapter-1-male--2-female).
5. **Disconnect the battery.** Only now does work start on the vehicle.
6. **Install Node A next to the BIU.** Confirm `OC-02` first. Connect the relays,
   IG and ground.
7. **Run the K-line** from OBD pin 7 to the console, away from noise sources.
8. **Install Node B:** **B-PWR** beside the i59 with its three cables, the
   umbilical through to **B-GAUGE** in the clock bay, the OLED mounted in the
   housing, the DS3231 in its printed case, then refit the smoked lens.
9. **Wire SW1** from the console to Node A's GPIO27, reusing the factory OrG run
   and disconnecting it from the BIU at the switch connector. Settle `OC-07`
   before wiring the tell-tale LED.
10. **Reconnect the battery** and run the [multimeter checklist](#multimeter-checklist).
11. **Firmware and calibration:** pair the ESP-NOW peers and set the 20 km/h
    threshold against the SSM2 reading.

## Multimeter checklist

- **1 A slow-blow** fuse on every 12 V feed.
- Buck output: **5.0 V ±0.1 V on Node A**, **3.30 V ±0.07 V on B-PWR**. They are different Recom variants — [ADR 0008](../decisions/0008-node-b-runs-on-one-33-v-rail.md).
- 3.3 V at VCC of the ESP32, OLED, RTC and L9637D. On Node B they all come from B-PWR's buck; on Node A the 3.3 V for the relay's logic side comes from the DevKit's own regulator at hole `L1` — **`L1`, not `L15`**, which is the check that catches a module fitted the wrong way round in the layout.
- **The umbilical rung out pin to pin** before either Node B board is mounted. Its
  two ends are identical 5-pin housings, so nothing else catches a swap, and a
  swap reaches both boards at once.
- No ESP32 input exceeds 3.3 V — on Node B, **with the node powered**, measure ILL
  and the analogue input after their dividers: **1.70 V at GPIO35 with 12 V on
  ILL**, **1.67 V at GPIO34 with 5.0 V on the sensor input**. Both clamps go to the
  3.3 V rail, so an unpowered board reads low and means nothing. Node A has no
  divided input.
- **The OLED's 3.3 V current, measured in amps not by touch.** The reference module
  draws 310 mA typical and 340 mA maximum; with the ESP32's transmit peak the rail
  reaches about 700 mA against a Recom derated to ~0.8 A at 70 °C. Put a meter in
  series with the display's 3.3 V lead and record the number.
- **Node A feed and ground, measured as resistance with the node unplugged** and the
  meter's lead resistance subtracted: fuse output → J1 +12 V pin, and J1 GND pin →
  the chassis stud. **Each well under 1 Ω.** The node draws only tens of milliamps,
  so a bad joint never shows as a voltage drop — see
  [stage 6](../01-hardware/node-a-build.md#6--feed-and-ground-resistance-before-the-trim-goes-back).
- Correct continuity across the three i59 connectors.
- i59 pin 10 (constant B+) **not** connected to the module.
- i59 pin 5 (UART to the combination meter) passed through and **not driven**.
- BIU pins 15 / 29 confirmed by pulsing the physical button.
- OBD pin 7 at ≈12 V at rest with the key on.
- Solid common ground between the nodes, the BIU and the i59.
- Key removed: 0 V on the supply of both nodes.

## Field notes

Judgement calls that only show up during installation.

- **DS3231 and its cell.** Many "ZS-042" modules try to **charge** the cell. With a
  CR2032, which is not rechargeable, that is dangerous: fit a rechargeable
  **LIR2032**, or remove the module's charge resistor.
- **Start-up gap.** Locking arms only when valid speed arrives over ESP-NOW, so
  there is ~1–2 s after ignition with no data. Harmless: the car is not doing
  20 km/h yet.
- **Do not substitute an LM7805** for the R-78E5.0-1.0. It gets hot in a closed
  housing, which is the reason the switcher was specified.
- **K-line not responding.** Check the 510 Ω pull-up, VS = 12 V, VCC = 3.3 V, and
  RX/TX not swapped — and that GPIO17 is driven push-pull, since the L9637D's TX
  threshold is an absolute 2.5 V rather than a fraction of VCC. Before any of that,
  confirm with FreeSSM that the car answers on that K-line at all.
- **Relay module on 3.3 V.** Coil from 5 V (JD-VCC), logic from 3.3 V, jumper
  removed. The GPIO then drives the opto without trouble.
- **Photograph every joint** before it is buttoned up. Reversibility is only useful
  if you can remember what it reverses to.

## Open checks on the vehicle

Values that depend on this particular car and **must be measured, not assumed**.
Every id below is stable: other documents cite `OC-nn` rather than restating the
check.

**Eight belong to v0.1** and must be closed before the car is driven with the
system fitted. **Three belong to Node C in v0.3.** One is resolved.

| id | Check | Status | Detail |
| --- | --- | --- | --- |
| **OC-01** | i59 connector: **wire colours** on the real connector (pin 8 differs LHD/RHD — this car is LHD, so IG should be GB), and that the **cavities for pins 2, 3, 4 and 7 are physically empty** before routing the K-line through pin 7 | Partially resolved — pin *functions* established from CLK-01 in v0.1.3 | [i59 adapter](../01-hardware/assembly-and-wiring.md#i59-adapter-1-male--2-female) |
| **OC-02** | BIU **pin 15 = lock, pin 29 = unlock**. Pulse each line to ground with a test lead and watch the actuator, before connecting the relays | Open · v0.1 | [Node A, Stage 2](../01-hardware/node-a-locking.md#stage-2--relays-to-the-biu) |
| **OC-03** | **IG source at the A-pillar**: 12 V only with the ignition on, 0 V with the key out | Open · v0.1 | [Node A, Stage 1](../01-hardware/node-a-locking.md#stage-1--power-ig-to-5-v) |
| **OC-04** | **SSM2 speed** reads correctly from this car's ECU; establish its unit and scale | Open · v0.1 | [ADR 0002](../decisions/0002-speed-over-ssm2-not-vss.md) |
| **OC-05** | **Display filter and OLED colour.** The donor lens reads red in transmission; the installed unit reads white when lit. Confirm by eye, day and night, and settle amber or white | Open · v0.1 | [display colour](../01-hardware/README.md#display-colour-amber-or-white-still-open) |
| **OC-06** | OEM switch pin count and function | **Resolved** in v0.1.2 — four wires, all present; pins 1–2 a momentary contact, pins 8–9 an LED | [the OEM circuit](../01-hardware/node-a-locking.md#the-oem-circuit) |
| **OC-07** | **Indicator LED specification**: polarity, whether the series resistor is internal and roughly its value, and the brightness driven from a 3.3 V GPIO. Use a current-limited supply ramped from zero, not an ohmmeter | Open · v0.1 | [tell-tale LED](../01-hardware/node-a-locking.md#the-tell-tale-led) |
| **OC-08** | **Contact pads on the car's own unit**: count, layout and finish. They were established on a donor in the base trim, which has one button fewer | Open · v0.1 | [ADR 0004](../decisions/0004-reuse-oem-contact-pad-buttons.md) |
| **OC-09** | **Coolant level sender zero.** With the system bled and cold, record the sender value at MIN and at MAX, then verify: cold level ≥ MIN, and cold level + expansion ≤ MAX | Open · v0.3 | [coolant level](../01-hardware/node-c-sensors.md#coolant-level--catch-tank) |
| **OC-10** | **Radiator ΔT sensor mounting**: surface on the hoses, or in-line fittings | Open · v0.3 | [radiator inlet and outlet](../01-hardware/node-c-sensors.md#radiator-inlet-and-outlet) |
| **OC-11** | **Channel count**, and therefore the bulkhead connector's pin count. Settle it before the firewall pass-through is sealed, and include spare pins | Open · v0.3 | [bulkhead connector](../01-hardware/node-c-sensors.md#the-bulkhead-connector) |
| **OC-12** | **Is the ILL feed live with the key out?** i59 pin 1 comes from the tail and illumination relay, which the light switch works. With the key out and the park lights on, measure i59 pin 1. If it is at battery voltage, the module's ILL divider draws ~0.6 mA into a dead board — small, but not the zero the design claims | Open · v0.1 | [Node B, Stage 2](../01-hardware/node-b-gauge.md#stage-2--illumination-ill-sensing) |

Track them as repository issues so there is a record. A check is marked resolved
only against an actual measurement, and the entry says how it was measured
([CONTRIBUTING](../../CONTRIBUTING.md#what-must-not-be-silently-fixed)).
