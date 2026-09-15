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

- **The car must be a K-line car for any of this to apply.** The 3.0R moved from
  SSM2-over-K-line to SSM2-over-CAN between MY2006 and MY2007: the MY2006 EDM
  calibration `D0XJ001R` is `flashmethod sti05`, the MY2007 `D2UH003R` is
  `subarucan`. This car is MY2006, so it is K-line — which is what the L9637D
  hardware assumes. Confirm empirically at the OBD port before wiring: activity on
  **pin 7** means K-line; **pins 6 and 14 populated** means CAN.

- **Init:** UART at **4800 baud, 8N1** for SSM2 through the L9637D; SPI for the SSD1322;
  I²C for the DS3231; ESP-NOW as both sender and receiver.
- **SSM2 acquisition:** cyclically poll RPM, MAF, speed, coolant temperature,
  O2/AFR, IAM, throttle opening and battery voltage. SSM2 is request/response by
  address. Four properties of the protocol, each taken from working
  implementations rather than assumed:
  - **4800 baud, 8N1.** Not 10400 — that is generic ISO 9141-2 OBD-II, the
    ELM327's default, and a different protocol on the same wire. RomRaider's
    `SSMProtocol` (ISO 9141) returns 4800/8/1/no-parity; FreeSSM opens the port at
    `4800, 8, 'N', 1` and has to send `ATIB48` to drag an ELM327 off 10400.
  - **No initialisation sequence.** No 5-baud slow init, no fast init, no
    keep-alive. Open the port and start sending. What the tools call "ECU init" is
    an ordinary application-layer packet (`80 10 F0 01 BF 40`) that returns the ECU
    id and a capability bitmask.
  - **Frame:** `0x80`, destination (`0x10` = ECU), source (`0xF0` = tool), length,
    data, checksum — the low 8 bits of the sum of every preceding byte.
  - **Parse by the length byte, not by gaps.** SSM2 does not obey ISO 14230
    timing, so message boundaries cannot be found by timeout. Budget about 55 ms
    per request/response and keep the inter-byte gap under 5 ms.
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

- **Init, and the order matters.** **Write GPIO25 and GPIO26 high *before* making
  them outputs**, not after. The ESP32's output register holds 0 after reset, so
  `pinMode(pin, OUTPUT)` drives the pin low the instant it takes effect; on an
  active-LOW relay module that energises the coil for however long the rest of
  `setup()` takes — tens to hundreds of milliseconds, against the ~5–10 ms an
  SRD-05 needs to pick up. The result is a door actuation on **every boot**,
  including every crank brown-out. Correct sequence:
  `digitalWrite(25, HIGH); digitalWrite(26, HIGH); pinMode(25, OUTPUT); pinMode(26, OUTPUT);`
  The hardware default is safe — a floating IN reads high — but only until firmware
  touches the pin.
- **Never energise both relay channels at once.** They ground BIU pins 15 and 29,
  and grounding both together is an undefined command to the body module. The
  interlock is in firmware; there is none in hardware.
- Then: ESP-NOW as receiver and sender; GPIO33 output for the tell-tale;
  GPIO27 `INPUT_PULLUP` for the ON/OFF button. Initial state **ARMED**. The node is
  fed from IG, so it does not sense the ignition — running is proof enough.
- **Receive:** update speed on each packet from Node B. If none arrive for the
  watchdog interval, **do not actuate** — never lock blind.
- **Button:** read GPIO27 with software debounce. Each press toggles ARMED ⇄
  DISABLED. The mode is local state on Node A.
- **State machine:** while ARMED, crossing 20 km/h upward → LOCK pulse; reaching
  0 km/h → UNLOCK pulse. Hysteresis prevents repeating a pulse. While DISABLED,
  neither happens.

  > **Unlocking at 0 km/h means unlocking at every traffic light**, not on
  > ignition-off. That is what the source document specified and it is what this
  > table says; it is a deliberate choice about convenience against security, and
  > it is recorded here so it is a choice rather than an oversight. Changing it to
  > unlock on ignition-off, or on the door handle, is a firmware change only.
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
| SSM2 baud rate | **4800, 8N1** | K-line ISO 9141 · no init sequence |
| Initial state | ARMED | per ignition cycle |
| ON/OFF button | GPIO27, `INPUT_PULLUP` | via R9 1 kΩ and C12 100 nF; debounce value to be defined |
| Tell-tale | GPIO33, output | via the R8 footprint (0 Ω link) · lit while DISABLED · drive method pending `OC-07` |
| OLED confirmation duration | ≈2 s | after a mode change |

## Open items

- [ ] Implementation in `/firmware` for Node A and Node B.
- [ ] **Define the ESP-NOW protocol before Node C is built**: node identity,
      message type and version, for every direction in the table above. Currently
      specified functionally, not at byte level. Note that Node C's coolant
      cold-capture needs a **B → C** direction that the link table does not yet
      have — see [`node-c-sensors.md`](../01-hardware/node-c-sensors.md#coolant-level--catch-tank).
- [ ] **Relay init ordering and the two-channel interlock**, both above. They are
      firmware requirements with a hardware consequence, so they belong in the
      first Node A build rather than a later one.
- [ ] **Burn-in specifics for the OLED.** The requirement is already listed above;
      what is not decided is the mechanism — how many pixels, how often, and
      whether the display sleeps on a timer. The panel's own specification warns
      that active pixels degrade faster than inactive ones, and this gauge shows
      fixed labels for the life of the car.
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
