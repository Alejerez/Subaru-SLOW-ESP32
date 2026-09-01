# Changelog

Milestones in prose. Not a mirror of every commit — for the fine detail, `git log`
and the tags are the source of truth.

Format after [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); one git tag
per meaningful milestone, pointing at the commit where it closed.

## [Unreleased] — clock circuit documented, reversibility evidenced

The factory wiring diagram for the clock circuit independently confirms the i59
adapter design and turns "the modification is reversible" into something a reader
can verify rather than take on trust.

### Added

- `docs/01-hardware/reference/clock-circuit-clk-01.png` — factory diagram CLK-01,
  the clock (i59) circuit.
- A full pin table for the i59 connector in
  [i59 adapter](docs/01-hardware/assembly-and-wiring.md#i59-adapter-1-male--2-female),
  taken from the diagram: pins 1 ILL, 5 UART, 6 GND, 8 IG, 9 ACC, 10 constant B+,
  and **2, 3, 4 and 7 carrying nothing**. The K-line therefore rides on a terminal
  the factory circuit does not use at all.
- A **reversibility section** grounded in that diagram: nothing is cut or spliced,
  every OEM signal passes through unbroken, and the constant B+ on pin 10 is
  declined on purpose because the DS3231's own cell replaces the function it served.
- ⚠️ **Pin 5 is a live serial link between the clock and the combination meter.**
  The adapter passes it through and must not drive it. Noted as strictly hands-off,
  with passive listening recorded as a research item that is in no roadmap version.

### Changed

- Root [README](README.md) now carries an explicit **third-party material** notice
  under Licence, and the notice in
  [`docs/01-hardware/reference/`](docs/01-hardware/reference/README.md) was
  strengthened: the factory diagrams are the property of their copyright holder,
  **neither CERN-OHL-S v2 nor GPL-3.0-or-later extends to that directory**, and
  anyone redistributing or forking the repository should evaluate it themselves.
  How to substitute redrawn schematics at no technical cost is documented there.
- Multimeter checklist gained a check that pin 5 is passed through and not driven.

### Partially resolved

- The i59 open check: pin *functions* are now established from the diagram. What
  remains is confirming **wire colours** on the real connector — pin 8 differs
  between LHD and RHD, and this car is LHD — and that the cavities for pins 2, 3, 4
  and 7 are physically empty.

## [Unreleased] — OEM switch circuit documented

The factory wiring diagram for the wiper de-icer circuit resolves what ADR 0003
had left open about the reused switch, and turns up a component the design had
not accounted for.

### Added

- [`docs/01-hardware/reference/`](docs/01-hardware/reference/README.md) — factory
  wiring diagram WD-01 / WI-12551, with an explicit note that Subaru service
  documents are **not covered by this repository's licences**.
- A circuit walkthrough in
  [Node A, Stage 4](docs/01-hardware/node-a-locking.md#the-oem-circuit): what each
  of the switch's four terminals does, where the project's signal comes from, and
  why pin 1 must be disconnected from the Body Integrated Unit rather than tapped
  in parallel with it.
- **Tell-tale LED.** The indicator already inside the OEM switch (connector i78,
  pins 8–9) is reused as a status light, driven from Node A on **GPIO33** and
  **lit while DISABLED** — the exceptional state, on the same convention as a
  "traction control off" lamp. The OLED announces the change; the LED holds the
  state after the message has gone.

### Changed

- ADR [0003](docs/decisions/0003-onoff-button-direct-to-node-a.md) amended: the
  switch has four wires, all present in this car; pins 1–2 are a **momentary**
  contact (it does not latch, unlike the folding-mirror switch), pins 8–9 the LED.
  The momentary confirmation matters — a latching switch would have left the
  button's physical position permanently out of step with a mode that resets at
  every ignition-on.
- The SW1 cable run is **no new cable**: the factory OrG wire already goes from
  the console to the BIU, which is where Node A is installed.

### Resolved

- Open check on the OEM switch's pin count — answered by the wiring diagram plus
  inspection on the car.

### Still open

- The LED's electrical specification: polarity, whether its series resistor is
  internal, and whether ~2 mA from a 3.3 V GPIO is bright enough to avoid any
  driver at all. Replacing the twenty-year-old LED with a modern high-efficiency
  one is also under consideration.

## [Unreleased] — roadmap of potential features

Adds a **roadmap of potential features to be developed if the v0.1 prototype
succeeds**, and promotes one item into the v0.1 locked scope. No hardware or
firmware exists yet for anything below v0.1 — this is planning, recorded so the
reasoning behind each inclusion and each rejection survives.

### Added

- [`ROADMAP.md`](ROADMAP.md) rewritten as a tiered plan: **v0.1** (prototype
  base), **v0.2** (firmware only, no new hardware), **v0.3** (new ESP-NOW nodes:
  GPS + IMU, caliper thermocouple, TPMS), **v0.4** (trackday mode), plus standby
  and discarded items. Every entry states whether it needs new hardware.
- A **storage rule** in the roadmap, since several items depend on it:
  configuration may be persisted to internal flash; telemetry may not, and goes to
  an SD card on the node that produces it.
- ADR [0005](docs/decisions/0005-ota-in-maintenance-mode.md): **OTA firmware
  update in a deliberate maintenance mode.** Wi-Fi and ESP-NOW never run
  simultaneously — they contend for the channel — so a node is put into
  maintenance mode from the gauge menu, reboots with a flag held in RTC memory,
  updates, and returns to normal on the next boot. Includes a timeout, a
  refusal to enter while the car is moving, a firmware-version report on return,
  and dual-partition rollback.
- Two firmware requirements added to v0.1 in
  [`docs/02-firmware/`](docs/02-firmware/README.md): **OLED burn-in mitigation**
  and **stale-data indication** (a gauge must never freeze on the last reading
  when its source stops answering).

### Changed

- **v0.1 locked scope grows from four items to five**: OTA joins it. Node A sits
  behind the A-pillar trim and v0.1 is the phase with the most firmware
  iterations, so cable-only reflashing would dominate the effort. It is to be
  built last within v0.1, after the other four work on the bench.
- Version numbers now denote **feature releases**. The perfboard-to-PCB migration
  is documented as a parallel hardware track rather than as "v0.2", which it
  previously collided with.

### Known consequences

- **ADC2 is no longer usable** once Wi-Fi is in the firmware, so only ADC1
  channels can be relied on. On Node B that leaves GPIO36 and GPIO39 spare; any
  further analogue sensing needs an external I²C ADC. This is a design input for
  the PCB, recorded in ADR 0005.
- Automatic locking is inactive while Node A is in maintenance mode, and
  deliberately disabled in trackday mode — in the latter case so that doors stay
  unlocked for marshal access.

## [0.1.0] — 2026-08-30

First commit. Project named **Subaru-ESP32-SLOW** — *SSM2 Link Over Wireless*. All documentation derives from the v0.1 design document
("Documento matriz v0.1 · Prototipo Cierre + Gauge · Subaru Legacy 3.0R"), kept
verbatim in [`docs/00-concept/source/`](docs/00-concept/source/README.md).

### Added

- Repository structure: `docs/` by phase (00-concept … 04-integration),
  `docs/decisions/` (ADRs), `scripts/` (figure generator), and the empty
  `firmware/`, `hardware/`, `software/` trees.
- Full technical content in English: purpose, architecture, design rationale,
  component catalogue, BOM, per-stage values and pin maps for both nodes, wiring
  and assembly, consumables and tooling, firmware behaviour specification,
  install sequence and multimeter checklist.
- Ten figures, drawn from code rather than extracted, dark-mode native, with
  automated overflow and collision checking
  ([`scripts/generate_diagrams.py`](scripts/generate_diagrams.py)).
- Six reference photographs (`docs/01-hardware/photos/`): the car's switch panel,
  clock unit and clock bay, plus a teardown of a donor unit — same generation and
  housing, base clock-only trim — showing the board, the button contact pads and
  the lens layers.
- ADR [0002](docs/decisions/0002-speed-over-ssm2-not-vss.md): vehicle speed over
  SSM2, not from the VSS.
- ADR [0004](docs/decisions/0004-reuse-oem-contact-pad-buttons.md): the four gauge
  controls reuse the OEM **contact-pad** buttons — established by the teardown —
  rather than new switches or a new bezel.
- ADR [0003](docs/decisions/0003-onoff-button-direct-to-node-a.md): the ON/OFF
  button is the unused OEM wiper de-icer switch, wired direct to Node A on
  GPIO27; ESP-NOW becomes bidirectional so the mode can be confirmed on the OLED.
- Explicit statement of the **retromod constraint** as a top-level requirement,
  and of the **ESP-NOW modularity rationale** behind the ESP32 choice.
- Prior art and credits for the repositories and forum threads this work builds
  on, and a disclosure of where AI assistance was used.
- Licences: CERN-OHL-S v2 for hardware (full text included), GPL-3.0-or-later for
  firmware and software (SPDX set; full text still to be inserted — see
  [`SETUP-GITHUB.md`](SETUP-GITHUB.md) §5).
- [`CONTRIBUTING.md`](CONTRIBUTING.md), [`ROADMAP.md`](ROADMAP.md) with the locked
  first-build scope, and [`SETUP-GITHUB.md`](SETUP-GITHUB.md).

### Known open items

- **Seven open checks on the vehicle**, none treated as resolved — see
  [`docs/04-integration/`](docs/04-integration/README.md#open-checks-on-the-vehicle).
- **One contradiction in the source document corrected:** its BOM row gave two
  different perfboard sizes that disagreed with the layout figures. Both nodes use
  a 3 × 7 cm board (11 × 27 holes) — see
  [`docs/01-hardware/`](docs/01-hardware/README.md#perfboard-size-correction-to-the-source-document).
- One reference (The Factory Five Forum thread) could not be verified
  independently; flagged as such in [`docs/references.md`](docs/references.md).

<!--
## [pcb-v1] — YYYY-MM-DD
### Added
- ...
### Changed
- ...
-->
