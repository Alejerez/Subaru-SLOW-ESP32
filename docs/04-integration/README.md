# 04 — Integration with the vehicle

Vehicle: **Subaru Legacy 3.0R, BL/BP chassis, EDM.**

## Install sequence

1. **Bench-test each node** on a fused 12 V supply. Verify 5.0 V out of the buck
   and that the ESP32 powers up.
2. **Build and verify Node B stage by stage** (power, dividers, K-line, OLED, RTC,
   buttons). Measure 3.3 V where it belongs; **no ESP32 input may exceed 3.3 V**.
3. **Build and verify Node A** (power, ignition sensing, relays, ON/OFF switch
   input). Listen for the relays clicking.
4. **Build the i59 adapter** from the three iWire pieces and check continuity pin
   by pin before it goes anywhere near the car.
5. **Disconnect the battery.** Only now does work start on the vehicle.
6. **Install Node A next to the BIU.** Confirm pins 15 / 29 with a multimeter
   (pressing the physical lock/unlock button). Connect the relays, IG and ground.
7. **Run the K-line** from OBD pin 7 (confirm ≈12 V at rest with the key on) to
   the console, away from noise sources.
8. **Install Node B:** plug the adapter into the i59, mount the OLED in the
   housing, refit the smoked lens.
9. **Wire SW1** — the reused OEM switch — from the console to Node A's GPIO27,
   reusing the factory OrG run to the BIU, and disconnecting it from the BIU at the
   switch connector. Characterise the indicator LED first if it is to be driven as a
   tell-tale (see the open checks below).
10. **Reconnect the battery** and run the [multimeter checklist](#multimeter-checklist).
11. **Firmware and calibration** (next phase): pair the ESP-NOW peers and set the
    20 km/h threshold against the SSM2 reading.

## Multimeter checklist

- 2 A fuse on every 12 V feed.
- Buck output = 5.0 V ±0.1 V (both nodes).
- 3.3 V at VCC of the ESP32, OLED, RTC and L9637D.
- No ESP32 input exceeds 3.3 V (measure IGN, ILL and the analogue input after
  their dividers).
- Correct continuity across the three i59 connectors.
- Pin 10 (constant B+) **not** connected to the supply — passed through to the OEM
  connector only.
- Pin 5 (OEM UART to the combination meter) passed through and **not driven**.
- BIU pins 15 / 29 confirmed by pulsing the physical button.
- OBD pin 7 at ≈12 V at rest with the key on.
- Solid common ground between the nodes, the BIU and the i59.
- Key removed: 0 V on the supply of both nodes.

## Field notes (troubleshooting and judgement calls)

- **DS3231 and its cell.** Many "ZS-042" modules include a circuit that tries to
  **charge** the cell. With a CR2032 (not rechargeable) that is dangerous: use a
  rechargeable **LIR2032**, or disable charging by removing the module's charge
  resistor.
- **Dependence on speed.** Locking needs speed over ESP-NOW. It arms when it
  receives valid data; at start-up there is ~1–2 s with no data (you are not doing
  20 km/h yet, so it does not matter).
- **Wi-Fi current spikes.** The 470 µF on the 5 V rail absorbs the radio spikes;
  with the R-78E5.0-1.0 (1 A) plus that capacitor there is ample headroom
  (ESP-NOW is short bursts). Do not use an LM7805 — it gets hot.
- **K-line not responding.** Check: 510 Ω pull-up, VS = 12 V, VCC = 3.3 V, RX/TX
  not swapped. Before that, confirm with FreeSSM that the car responds on that
  K-line at all.
- **Relay module on 3.3 V.** Feed the coil from 5 V (JD-VCC) and the logic from
  3.3 V (remove the VCC–JD-VCC jumper). The GPIO then drives the opto without
  trouble.
- **Reversibility.** Everything hangs off the i59 adapter and the K-line. Unplug
  and the car is stock. Photograph every joint in case you need to reverse it.

## Open checks on the vehicle

Points that depend on the actual wiring of this EDM car and must be confirmed
before or during installation. **These are not assumptions — they are
measurements to make.**

Seven of these belong to v0.1 and must be closed before the car is driven with the
system fitted; three more belong to Node C in v0.3 and are listed at the end.

Five come from the v0.1 source document. Factory wiring diagrams have since
answered part of the first one; the rest are untouched, and nothing has been
marked resolved without evidence:

- **i59 connector (85201AG200):** the pin *functions* are established from factory
  diagram CLK-01 — pins 1 ILL, 5 UART, 6 GND, 8 IG, 9 ACC, 10 constant B+, with
  2, 3, 4 and 7 unused. What still has to be confirmed on the actual connector is
  the **wire colours** (pin 8 differs between LHD and RHD; this car is LHD, so IG
  should be GB) and that the **cavities for 2, 3, 4 and 7 are physically empty**
  before routing the K-line through pin 7. See
  [i59 adapter](../01-hardware/assembly-and-wiring.md#i59-adapter-1-male--2-female).
- **BIU pins:** confirm that **pin 15 = lock** and **pin 29 = unlock** by pulsing
  each line to ground with a test lead and watching the actuator, before
  connecting the relays.
- **IG source at the A-pillar:** verify with a multimeter that the chosen line
  sits at 12 V only with the ignition on, and falls to 0 with the key out.
- **SSM2 speed:** confirm that the speed parameter reads correctly from this car's
  ECU, and establish its unit and scale.
- **Display filter and OLED colour:** establish what the car's own lens actually
  does. The donor unit's lens reads red in transmission, yet the installed unit
  reads white when lit. Confirm by eye, day and night, and settle whether the
  OLED should be amber (as the BOM provisionally says) or white. See
  [display colour](../01-hardware/README.md#display-colour-amber-or-white-still-open).

Two more were added as the design progressed.

From the ON/OFF button decision
([ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md)):

- ~~**Reused OEM switch (wiper de-icer):** confirm how many pins it has and what
  each one does.~~ **Resolved** from the factory wiring diagram plus inspection on
  the car: four wires, all present. Pins 1–2 are a momentary contact (it does not
  latch), pins 8–9 an indicator LED. Documented in
  [Node A, Stage 4](../01-hardware/node-a-locking.md#the-oem-circuit).
- **Indicator LED inside the OEM switch:** establish polarity, whether an internal
  series resistor exists and its approximate value, and the brightness obtained
  driving it directly from a 3.3 V GPIO. Use a current-limited bench supply ramped
  from zero, not an ohmmeter. Decide from that whether it can be GPIO-driven with
  no components, needs a low-side MOSFET from the 12 V rail, or is better replaced
  with a modern high-efficiency LED — a twenty-year-old indicator LED is dim by
  current standards and of unknown remaining life.

From the button-reuse decision ([ADR 0004](../decisions/0004-reuse-oem-contact-pad-buttons.md)):

- **Contact pads on the car's own unit:** the pad count, layout and finish were
  established on a donor unit in the base clock-only trim, which has one button
  fewer. Confirm them against the car's trip-computer unit before cutting the OEM
  board or laying out the carrier.

From the Node C design ([ADR 0006](../decisions/0006-node-c-analogue-front-end.md)) —
these apply when that node is built, in v0.3:

- **Zero calibration of the coolant level sender.** The catch tank is an aftermarket
  part with no factory MIN/MAX marks. With the system properly bled and cold, record
  the sender value at MIN (1 cm above the lower spigot) and at MAX (1 cm below the
  upper spigot). Then verify the arithmetic that matters: cold level ≥ MIN, and cold
  level plus thermal expansion ≤ MAX. See
  [Node C](../01-hardware/node-c-sensors.md#coolant-level--catch-tank).
- **Radiator ΔT sensor mounting** — surface on the hoses, or in-line fittings.
  Surface is non-invasive but reads low and lags; in-line is accurate but means
  cutting hoses and adding two potential leak points.
- **Channel count, and therefore the bulkhead connector's pin count.** Settle it
  before the firewall pass-through is sealed, and include spare pins: this is the
  hardest part of the loom to change afterwards.

Track them as repository issues (or a PR checklist) so there is a record.
