# Roadmap

Feature releases for the system, from the locked first build outwards. Everything
past v0.1 is a **statement of intent, not a commitment** — items move, get
demoted, or get cut once the reality of the car and the firmware says so.

Two conventions used throughout:

- **Version numbers are feature releases**, not board revisions. The
  perfboard-to-PCB migration is a [parallel hardware track](#hardware-track-perfboard-to-pcb)
  that lands when it lands.
- Every item says whether it needs **new hardware** or is firmware on what
  already exists. That distinction is what keeps this list from pretending that
  everything costs the same.

## At a glance

| Version | Theme | Adds | New hardware |
| --- | --- | --- | --- |
| **[v0.1](#v01--prototype-base)** | Prototype base | SSM2 acquisition · OLED gauge · OEM buttons · speed-based locking · **OTA over Wi-Fi** · burn-in mitigation · stale-data indication | None |
| **[v0.2](#v02--firmware-only)** | Firmware only | DTC read/clear · fuel trims · knock alerts per bank · gear indicator · threshold alarms · web admin · system health page | None |
| **[v0.3](#v03--new-nodes)** | New nodes | GPS + IMU node · lap timing · time sync · caliper temperature · TPMS | GPS/IMU node · thermocouple node · TPMS node + aftermarket sensors |
| **[v0.4](#v04--trackday-mode)** | Trackday mode | Trackday mode · session logging · peak summary · log download · optional removable display | SD card · removable display (optional) |
| **[Standby](#standby)** | — | Charging-system monitor · oil and water instrumentation for other cars | To be defined |
| **[Discarded](#discarded-and-why)** | — | Trip and maintenance records · phone Bluetooth · IR caliper sensor | — |

## A rule about storage

This system is fed entirely from IG and dies with the key. That shaped a rule
worth stating once, because several items below depend on it:

- **Configuration may be persisted.** Circuit coordinates, alarm thresholds, the
  manual clock offset — kilobytes, written once every few months. Internal flash
  (NVS) handles this without concern.
- **Telemetry may not go to internal flash.** Blackbox buffers and trackday
  sessions are megabytes written at high frequency; that wears the ESP32's flash
  out. Telemetry goes to an **SD card** on the node that produces it.

Anything that needs *continuously updated state surviving for years* — a trip
odometer, service intervals — is out of scope entirely. See
[Discarded](#discarded-and-why).

---

## v0.1 — prototype base

The locked scope. Nothing outside this list is being designed, wired or costed
until it works in the car: the point of v0.1 is to prove the SSM2 link, the
display integration and the locking logic against real vehicle wiring.

1. **SSM2 acquisition** — poll the ECU over the K-line (ISO 9141-2, 10400 baud)
   through an L9637D transceiver on OBD pin 7.
2. **Monochrome OLED gauge** — SSD1322 256×64 in the OEM clock position, retained
   by a 3D-printed bezel. Amber or white is still open, see
   [display colour](docs/01-hardware/README.md#display-colour-amber-or-white-still-open).
3. **OEM button integration** — the four existing contact-pad buttons drive page
   navigation and settings ([ADR 0004](docs/decisions/0004-reuse-oem-contact-pad-buttons.md));
   the unused wiper de-icer switch becomes the auto-lock ON/OFF
   ([ADR 0003](docs/decisions/0003-onoff-button-direct-to-node-a.md)).
4. **Speed-based automatic central locking** — lock above 20 km/h, unlock at a
   standstill, via two relay pulses into BIU pins 15 and 29.
5. **OTA firmware update over Wi-Fi**, in a deliberate maintenance mode —
   [ADR 0005](docs/decisions/0005-ota-in-maintenance-mode.md). Promoted into v0.1
   because v0.1 is the phase with the most firmware iterations, and Node A lives
   behind the A-pillar trim where cable reflashing means dismantling interior.
   Build it **last** in v0.1, once the other four work on the bench.

Two firmware requirements that are not features but belong in v0.1 anyway:

- **Burn-in mitigation.** A mono OLED showing a clock in a fixed position for the
  entire life of the car will burn in. Pixel shifting and brightness management
  are v0.1 problems, not something to retrofit after a year of damage.
- **Stale-data indication.** If SSM2 stops answering or the ESP-NOW link drops,
  the display must say so rather than freeze on the last value. A gauge that lies
  is worse than a gauge that is blank.

Completion criteria are the install sequence and multimeter checklist in
[`docs/04-integration/`](docs/04-integration/README.md), plus the seven open
vehicle checks listed there.

## v0.2 — firmware only

No new hardware. Everything here runs on the two nodes as built for v0.1.

- **DTC read.** Trouble codes on the gauge, no laptop and no Tactrix.
- **DTC clear** — user-initiated only, with a deliberate second confirmation.
  Before clearing, the **freeze frame is read and displayed on screen**, so the
  evidence reaches the person rather than being discarded. It is shown, not
  stored — no persistence involved. Clearing also wipes readiness monitors, and
  the confirmation step should say so.
- **Fuel trims, both banks.** STFT and LTFT are what expose a vacuum leak or a
  tired MAF long before a light comes on. The EZ30 is a flat six with two banks;
  show both, never one averaged number.
- **Knock alerts per bank.** Feedback Knock Correction and Fine Knock Learn are
  available per bank on this engine (banks 1 and 2). Alert on correction becoming
  active or on learned knock drifting — distinct from merely displaying IAM.
- **Gear indicator**, computed from the speed / RPM ratio.
- **Threshold alarms.** Coolant temperature first, since it already arrives over
  SSM2 for free. The framework matters more than the first alarm: any parameter
  should be able to raise an alert page. Note that dedicated gauges *display* but
  do not *alarm* — this covers the case where nobody is looking at them.
- **Web administration interface.** Settings, thresholds and diagnostics from a
  browser, reusing the Wi-Fi brought in by [ADR 0005](docs/decisions/0005-ota-in-maintenance-mode.md)
  and therefore subject to the same maintenance-mode rule.
- **System health page.** Firmware version per node and ESP-NOW link quality.
  With two or more nodes and OTA in the picture, this is the first thing anyone
  will want to look at when something misbehaves.

## v0.3 — new nodes

Each of these is a node, not a feature. They join the existing ESP-NOW link,
which is the entire reason the architecture was split in two.

### GPS + IMU node

- 10 Hz position fix. 1 Hz consumer GPS is useless for lap timing or for
  correlating G-force. 10 Hz is the practical floor; 20 Hz is available on some
  modules but the solution quality drops, and 10 Hz already gives roughly 2.8 m
  of travel between fixes at 100 km/h, which interpolates to well inside amateur
  lap-timing accuracy.
- Antenna at the windscreen base or the roof. Under the dash will not work.
- Battery-backed module, so a warm start does not cost 30 s of waiting.
- **This node closes the trade-off documented in
  [ADR 0002](docs/decisions/0002-speed-over-ssm2-not-vss.md).** Today the locking
  function depends on Node B polling SSM2; a GPS speed source makes Node A
  independent of it. That is a better reason to build this node than the
  speedometer is.
- **Lap timing**, with start/finish coordinates for different circuits, loadable
  and stored as configuration.
- **Clock synchronisation of minutes and seconds only.** The hour stays manual.
  GPS provides UTC, and converting UTC to local time is the entire problem —
  Chile's DST dates are set by decree and have changed repeatedly, and Magallanes
  keeps a different offset year-round. Syncing only mm:ss corrects the DS3231's
  drift (±2 ppm, about a minute a year), which is the only thing that actually
  needs correcting, and puts no timezone rules in firmware at all.

### Caliper temperature node

- **Type K thermocouple in contact with the caliper body**, through a MAX31855
  amplifier. Not an infrared sensor: the common IR parts saturate around 380 °C
  while track rotors go well past that, and their accuracy degrades exactly when
  the sensor's own body is sitting next to a glowing brake.
- Be clear about what this measures. Caliper body temperature is neither rotor
  nor pad temperature — it lags and reads much lower. What it is a good proxy for
  is **brake fluid temperature**, which is what causes fade and a long pedal. For
  a street car on track that is the more actionable number.
- The MAX31855 is SPI, and Node B's SPI bus already carries the OLED. Either give
  it its own chip select, or put the amplifier on the trackday node instead.

### TPMS node

- **This car has no factory TPMS** — the EU mandate post-dates it — so this means
  buying aftermarket sensors.
- **BLE sensors, read natively by the ESP32.** This avoids the 433 MHz path
  entirely: no RF front end, no per-brand protocol reverse engineering.
- Its own node. BLE and ESP-NOW share the same 2.4 GHz transceiver and time-slice
  against each other, so keeping the scanning off Node B keeps the gauge and the
  speed link clean.
- If using valve-cap sensors on track, fit **metal valve stems**. Cap sensors add
  mass at the end of the stem and circuit speeds punish that.

## v0.4 — trackday mode

A distinct operating mode, entered deliberately, that changes what the system is
for. Last in the sequence because it depends on almost everything above.

- **Comfort functions off, starting with automatic central locking.** The strong
  argument is not resource saving, it is safety: **in an off you want the doors
  unlocked so marshals can open them.** Everything else that competes for
  resources steps aside too; the system concentrates on acquisition, logging and
  showing what matters.
- **Session logging to SD card**, per the [storage rule](#a-rule-about-storage).
- **Peak and session summary** — max coolant, max oil temperature, minimum
  voltage, maximum lateral and longitudinal G. Coming back to the pits you want
  the extremes of the session, not an instantaneous reading.
- **Log download over Wi-Fi**, reusing the OTA stack — or simply by pulling the SD
  card. Not over Bluetooth: BLE moves 5–20 kB/s in practice, and a 30-minute
  session at 10 Hz across twenty channels is several megabytes, which is ten
  minutes of fragile transfer.
- **The mode must be visually unmistakable, and must exit on an ignition cycle** —
  the same pattern as the auto-lock mode in
  [ADR 0003](docs/decisions/0003-onoff-button-direct-to-node-a.md). Driving on the
  street with the locking silently disabled is the failure to design against.
- **Optional removable trackday display.** The retromod constraint puts the gauge
  in the clock bay, which is right for daily driving and poor for a circuit — at
  eight tenths nobody looks at the centre console. A temporary display or a bright
  alert LED at the A-pillar, plugged in for the event and removed afterwards, is
  exactly what the ESP-NOW architecture is for, and the car stays stock during the
  week. The same pages must remain usable on the daily OLED, for the day the
  removable one is left at home.

## Standby

Wanted, but blocked on something.

- **Charging-system monitor.** Cranking voltage drop is the cheapest predictor of
  a dying battery or alternator. It must be measured with a **local analogue
  input**, not over SSM2: the ECU's reported voltage is coarse, and during
  cranking the SSM2 link is precisely when polling stalls. Deferred because it
  needs its own sensing stage designed.
- **Oil pressure, oil temperature, coolant temperature instrumentation.** Already
  covered on this car by dedicated Defi gauges in the 1DIN space, so it is not
  being built — but it stays listed as an option for anyone reproducing this
  project without them. Oil pressure in particular is the parameter that warns
  you an old engine is about to let go on track, ahead of temperature.
- **Reading the existing Defi senders for logging.** Those sensors are already
  fitted; if their senders are voltage-output, a high-impedance ESP32 input can
  read them in parallel and bring oil pressure and temperature into the trackday
  log for free. Verify the sender type first — a resistive sender working into the
  gauge's own divider *will* have its reading disturbed by a parallel load.

## Discarded, and why

Recorded so they are not re-proposed without new information.

- **Trip meters and maintenance records** — trip A/B, range to empty, service
  intervals and their history. They need an absolute odometer, which SSM2 does not
  reliably expose, and continuously updated state persisted for years. Integrating
  distance from speed drifts, and a service reminder that disagrees with the dash
  is worse than none.
- **Phone Bluetooth: Spotify/Tidal metadata and incoming caller ID.** A phone
  holds A2DP with one device at a time, and that link belongs to the head unit.
  Dropping the phone link removes both features together, which is consistent.
- **Infrared caliper temperature sensing.** Superseded by the contact thermocouple
  above, for the reasons given there.
- **Extended logging on a Raspberry Pi with a Tactrix OpenPort**, proposed in the
  v0.1 source document. Superseded by trackday logging on an SD card. Note that
  any Tactrix session on the same K-line is also the one documented case where
  Node B stops polling SSM2.

## Hardware track: perfboard to PCB

Independent of the feature releases above. Once v0.1 is validated in the car:

- Move both carriers from perfboard to a **formal PCB** (KiCad or EasyEDA,
  Gerbers under `hardware/`), keeping the modules socketed and the edge connectors
  latching.
- The button contact-pad area has to be resolved at the same time: either the OEM
  board's pad region is retained and wired in, or the PCB reproduces the pad
  geometry with a suitable surface finish. See
  [ADR 0004](docs/decisions/0004-reuse-oem-contact-pad-buttons.md).
- Fabrication options from the source document: local (CAEM, PCB Chile) or
  JLCPCB / PCBWay; turnkey assembly (Enerful, KELTRONIC, CIGA) if the board is
  worth not hand-populating.
- Re-verify the enclosure fit against the OEM clock housing before committing to a
  board outline — the retromod constraint does not relax.

Practically this lands around v0.3, when several new nodes are being built at
once and hand-populating four perfboards stops being reasonable.

## Documentation and tooling

- [ ] Insert the official GPL-3.0 text into `LICENSE-SOFTWARE.txt`
      (see [`SETUP-GITHUB.md`](SETUP-GITHUB.md) §5)
- [ ] Add CI that regenerates the figures when `scripts/generate_diagrams.py`
      changes — the generator and its overflow/collision checks already run
      headless, so this is mostly workflow plumbing. Not added yet because it has
      never been executed in a real pipeline.
- [ ] Document the toolchain and flashing procedure for both nodes once the
      firmware exists.
