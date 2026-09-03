# 02 — Firmware

> Behavioural specification, not code. The implementation lives in `/firmware` at
> the repository root and **has not been written yet** — see the
> [prototype status](../00-concept/README.md#prototype-status-v01).

This is where behaviour is defined. Component values, pin maps and layout are in
[`docs/01-hardware/`](../01-hardware/README.md).

## Link topology

**A star, with Node B as the hub** — it is the node with the display. Every node
runs Arduino-ESP32 or ESP-IDF on a fixed ESP-NOW channel, each knowing its peers'
MAC addresses.

| Direction | Payload | Cadence | From |
| --- | --- | --- | --- |
| B → A | vehicle speed | every 100–200 ms | v0.1 |
| A → B | auto-lock mode change | on button press | v0.1 · [ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md) |
| B → A | maintenance-mode command | from the gauge menu | v0.1 · [ADR 0005](../decisions/0005-ota-in-maintenance-mode.md) |
| A → B | firmware version on return from maintenance | event | v0.1 |
| C → B | sensor channels | about 1 Hz | v0.3 · [ADR 0006](../decisions/0006-node-c-analogue-front-end.md) |

Node A and Node C never exchange anything. Adding Node C does not touch the speed
message, and slowing that message was considered and rejected — it would have
forced the fail-safe watchdog above 2 s for no benefit.

Two consequences, both requirements rather than details:

- **The packet format is a protocol, not two message types.** With three or more
  nodes it needs a node identity, a message type and a version field. Settle it
  **before Node C is built**, or the format gets patched with hardware already in
  the car.
- **Nodes are optional by default.** The gauge must not break because a node is
  absent; its channels display as unavailable, the same rule as stale data below.

## Requirements for every node

Properties the v0.1 firmware has to have. Retrofitting any of them later is worse
than building them in.

- **Maintenance mode for OTA.** Wi-Fi and ESP-NOW are never up together. The node
  enters maintenance mode deliberately from the gauge menu and returns on the next
  boot; the flag lives in RTC memory (`RTC_NOINIT_ATTR`) with a magic value, so it
  survives the intentional restart and is cleared by removing power. Dual-partition
  OTA with rollback, a timeout, refusal to enter while the car is moving, and a
  firmware-version report on return. [ADR 0005](../decisions/0005-ota-in-maintenance-mode.md).
- **Burn-in mitigation on the OLED.** The display shows a clock in a fixed position
  for the life of the car. Pixel shifting and brightness management are v0.1
  concerns; a panel damaged over a year cannot be fixed in software afterwards.
- **Stale-data indication.** If SSM2 stops answering or a radio peer drops, the
  affected values are shown as unavailable, never left frozen at the last reading.
  This is correctness, not presentation.

## Node B — gauge

- **Init:** UART at 10400 baud for SSM2 through the L9637D; SPI for the SSD1322;
  I²C for the DS3231; ESP-NOW as both sender and receiver.
- **SSM2 acquisition:** cyclically poll RPM, MAF, speed, coolant temperature,
  O2/AFR, IAM, throttle opening and battery voltage. SSM2 is request/response by
  address.
- **Fuel consumption:** instantaneous L/100 km from **MAF** and the air/fuel ratio
  — fuel flow = MAF ÷ AFR, integrated against speed. Moving average to stabilise it.
- **UI:** render pages on the OLED (clock from the RTC, consumption, AFR, IAM). The
  four OEM buttons navigate pages and adjust settings; they **do not** control the
  auto-lock, which moved to Node A.
- **Transmit:** speed every 100–200 ms.
- **Receive:** on a mode change from Node A, show `AUTO-LOCK: ARMED` /
  `AUTO-LOCK: DISABLED` for ≈2 s, then return to the page that was showing.

## Node A — locking

![Node A state machine](../01-hardware/diagrams/06-node-a-state-machine.png)

**Fig. 6** — Node A state machine. State is not persisted; every ignition-on
starts ARMED.

- **Init:** ESP-NOW as receiver and sender; GPIO25/26 outputs to the relays, idle
  inactive; GPIO33 output for the tell-tale LED; GPIO34 senses ignition; GPIO27
  `INPUT_PULLUP` for the ON/OFF button. Initial state **ARMED**.
- **Receive:** update speed on each packet from Node B. If none arrive for the
  watchdog interval, **do not actuate** — never lock blind.
- **Button:** read GPIO27 with software debounce. Each press toggles ARMED ⇄
  DISABLED. The mode is local state on Node A.
- **State machine:** while ARMED, crossing 20 km/h upward → LOCK pulse; reaching
  0 km/h → UNLOCK pulse. Hysteresis prevents repeating a pulse. While DISABLED,
  neither happens.
- **Pulses:** energise the relay for ≈0.4 s and release. Never hold.
- **Confirmation:** on every mode change, send the new state to Node B for the OLED.
- **Tell-tale LED:** GPIO33 **lit while DISABLED, dark while ARMED**. Unlike the
  OLED message it does not time out — it is the persistent indication of the
  exceptional state.
- **Per-cycle reset:** state is not persisted; every IG-on starts ARMED.

## Node C — analogue front end (v0.3)

Not built. Reads its channels, flags each reading valid or invalid, and sends the
set to Node B at about 1 Hz. Specification in
[`node-c-sensors.md`](../01-hardware/node-c-sensors.md).

## v0.1 parameters

| Parameter | Value | Note |
| --- | --- | --- |
| Lock threshold | 20 km/h | adjustable in firmware |
| Unlock threshold | 0 km/h | sustained stop |
| Relay pulse duration | ≈0.4 s | negative pulse to the BIU |
| ESP-NOW interval, speed B → A | 100–200 ms | speed only |
| Radio watchdog | ≈1 s | no packets → do not actuate |
| SSM2 baud rate | 10400 | K-line ISO 9141 |
| Initial state | ARMED | per ignition cycle |
| ON/OFF button | GPIO27, `INPUT_PULLUP` | debounce value to be defined |
| Tell-tale LED | GPIO33, output | lit while DISABLED · drive method pending `OC-07` |
| OLED confirmation duration | ≈2 s | after a mode change |

## Open items

- [ ] Implementation in `/firmware` for Node A and Node B.
- [ ] **Define the ESP-NOW protocol before Node C is built**: node identity,
      message type and version, for every direction in the table above. Currently
      specified functionally, not at byte level.
- [ ] **Assign Node B's ignition-sense pin.** Stage 2 specifies the divider but no
      GPIO; GPIO36 and GPIO39 are the free ADC1 pins. Decide whether Node B needs
      ignition sensing at all, given that it is powered from IG and therefore only
      runs when the ignition is on.
- [ ] Debounce value for the GPIO27 button — shared with the OEM contact pads
      ([ADR 0004](../decisions/0004-reuse-oem-contact-pad-buttons.md)).
- [ ] How the tell-tale LED is driven, once
      [`OC-07`](../04-integration/README.md#open-checks-on-the-vehicle) is measured.
- [ ] Toolchain and flashing procedure per node — board definitions, build, upload.
- [ ] OTA transport and its authentication: HTTP upload to a SoftAP, a pull from
      the home network, or signed images. This matters more than in a typical hobby
      project, because Node A actuates the door locks.
- [ ] Maintenance-mode timeout, and whether Node B may enter it while Node A
      already is.
- [ ] Partition table for dual-partition OTA with rollback.
