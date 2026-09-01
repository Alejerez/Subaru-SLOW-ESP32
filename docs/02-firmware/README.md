# 02 — Firmware

> Behavioural specification, not code. The implementation lives in `/firmware` at
> the repository root and **has not been written yet** — see the
> [prototype status](../00-concept/README.md#prototype-status-v01).

## Link topology

Both nodes run Arduino-ESP32 or ESP-IDF. The ESP-NOW link is **bidirectional**,
on a fixed channel; each node knows the other's MAC:

| Direction | Payload | Cadence |
| --- | --- | --- |
| Node B → Node A | current vehicle speed | periodic, every 100–200 ms |
| Node A → Node B | auto-lock mode change | event, only when the button is pressed |

The reverse direction exists because of
[ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md): the ON/OFF button
is local to Node A, so Node B has to be told when the mode changes in order to
confirm it on the OLED.

## Requirements common to both nodes

These are not features. They are properties the v0.1 firmware has to have, and
retrofitting any of them later is worse than building them in.

- **Maintenance mode for OTA.** Wi-Fi and ESP-NOW are never up at the same time;
  the node is put into maintenance mode deliberately, from the gauge menu, and
  returns to normal on the next boot. Flag in RTC memory (`RTC_NOINIT_ATTR`) with
  a magic value, so it survives the intentional restart and is cleared by removing
  power. Dual-partition OTA with rollback. Timeout back to normal, refusal to
  enter while the car is moving, and a firmware-version report over ESP-NOW on
  return. Full reasoning and the unresolved parts in
  [ADR 0005](../decisions/0005-ota-in-maintenance-mode.md).
- **Burn-in mitigation on the OLED.** The display shows a clock in a fixed
  position for the life of the car. Pixel shifting and brightness management are
  v0.1 concerns; a panel damaged over a year of use cannot be fixed in software
  afterwards.
- **Stale-data indication.** If SSM2 stops responding or ESP-NOW drops, the
  affected values must be shown as unavailable, never left frozen at the last
  reading. This is correctness, not presentation: a gauge that silently displays
  an old number is worse than one that displays nothing.

## Node B (gauge) — tasks

- **Init:** UART at 10400 baud for SSM2 through the L9637D; SPI for the SSD1322
  OLED; I²C for the DS3231; ESP-NOW as **both** sender and receiver.
- **SSM2 acquisition:** cyclically poll the ECU parameters — RPM, MAF, speed,
  coolant temperature, O2/AFR, IAM, throttle opening, battery voltage. SSM2 is
  request/response by address.
- **Fuel consumption:** instantaneous L/100 km from **MAF** and the air/fuel ratio
  (AFR from the narrowband O2): fuel flow = MAF ÷ AFR, integrated against speed to
  give L/100 km. Moving average to stabilise the reading.
- **UI:** render pages on the OLED (clock from the RTC, consumption, AFR, IAM, and
  whatever else is defined). The four OEM buttons navigate pages and adjust
  settings — they **no longer control the auto-lock** (that moved to Node A).
- **ESP-NOW transmit:** send a packet with the current speed every 100–200 ms.
- **ESP-NOW receive:** on a mode-change message from Node A, show a confirmation
  on the OLED (e.g. `AUTO-LOCK: ARMED` / `AUTO-LOCK: DISABLED`) for ≈2 s, then
  return to the page that was showing.

## Node A (locking) — tasks

- **Init:** ESP-NOW as **both** receiver and sender; GPIO25/26 as outputs to the
  relays (idle = inactive); GPIO33 as an output for the tell-tale LED; GPIO34
  senses ignition; GPIO27 as an input with
  `INPUT_PULLUP` for the ON/OFF button (the reused OEM switch — see
  [`node-a-locking.md`](../01-hardware/node-a-locking.md#stage-4--onoff-button-reused-oem-switch)).
  Initial state = **ARMED**.
- **Receive:** update speed on each ESP-NOW packet from Node B. If no packets
  arrive for a while (watchdog), do not actuate — fail-safe: never lock blind.
- **ON/OFF button:** read GPIO27 with software debounce. Each press toggles the
  local mode **ARMED ⇄ DISABLED**. The mode is local state on Node A — it no
  longer depends on a flag received over the radio.
- **State machine:** ARMED ⇄ DISABLED per the local button. While ARMED: crossing
  20 km/h upward (using the speed received from Node B) → LOCK pulse; reaching
  0 km/h → UNLOCK pulse. Hysteresis prevents repeating the pulse (e.g. lock at
  ≥20, rearm the condition below some threshold).
- **Pulses:** energise the relevant relay for ≈0.4 s and release. Never hold.
- **User confirmation:** whenever the button changes the mode, send an ESP-NOW
  message to Node B carrying the new state, so it can be shown on the OLED.
- **Tell-tale LED:** drive GPIO33 to match the mode — **lit while DISABLED, dark
  while ARMED**. This is the OEM indicator inside the reused switch (i78 pins
  8–9, see [Node A Stage 4](../01-hardware/node-a-locking.md#stage-4--onoff-button-reused-oem-switch)).
  Unlike the OLED message it does not time out: it is the persistent indication of
  the exceptional state.
- **Per-cycle reset:** state is not persisted; every IG-on starts ARMED.

## v0.1 parameters

| Parameter | v0.1 value | Note |
| --- | --- | --- |
| Lock threshold | 20 km/h | adjustable in firmware |
| Unlock threshold | 0 km/h | sustained stop |
| Relay pulse duration | ≈0.4 s | negative pulse to the BIU |
| ESP-NOW interval (speed, B→A) | 100–200 ms | speed only |
| Radio watchdog | ≈1 s | no packets → do not actuate |
| SSM2 baud rate | 10400 | K-line ISO 9141 |
| Initial state | ARMED | per ignition cycle |
| ON/OFF button | GPIO27, `INPUT_PULLUP` | software debounce, value to be defined |
| Tell-tale LED | GPIO33, output | lit while DISABLED · drive method pending the LED's electrical spec |
| OLED confirmation duration | ≈2 s | after a mode change (Node A → Node B over ESP-NOW) |

## Open items

- [ ] Implementation in `/firmware` (Node A and Node B) — integration phase
- [ ] Define the exact ESP-NOW packet format in **both** directions (fields, size,
      protocol version): speed (B → A) and mode change (A → B). Currently
      specified only functionally, not at byte level
- [ ] Define the debounce value for the GPIO27 button
- [ ] Decide how the tell-tale LED is driven, once its electrical specification
      is known — directly from GPIO33, through a low-side MOSFET, or with the
      OEM LED replaced (see the
      [open checks](../04-integration/README.md#open-checks-on-the-vehicle))
- [ ] Document the toolchain and flashing procedure for each node (board
      definitions, build, upload) — not documented yet
- [ ] Define the OTA transport and its authentication — HTTP upload to a SoftAP,
      a pull from the home network, or signed images. This matters more than in a
      typical hobby project, given that Node A actuates the door locks
- [ ] Define the maintenance-mode timeout, and whether Node B may enter it while
      Node A is already in it
- [ ] Define the partition table for dual-partition OTA with rollback
