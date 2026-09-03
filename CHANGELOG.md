# Changelog

Format after [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versioning after [Semantic Versioning](https://semver.org/).

## How this changelog is kept

**Every push that changes meaning gets one entry, one version number, one date
and one git tag.** A push that only fixes a typo, reflows text or regenerates an
unchanged figure gets none.

| Rule | |
| --- | --- |
| **Version** | `MAJOR.MINOR.PATCH`, tracking the [roadmap](ROADMAP.md#at-a-glance)'s feature releases. The repository is documentation-only for now, so it sits at `0.1.x` and the patch number advances with each documentation release. `0.2.0` arrives with the v0.2 feature set, not merely with the first firmware. |
| **ID** | The version is the ID. Each entry also names the tag and the commit it closed at, so any entry can be diffed. |
| **Date** | ISO `YYYY-MM-DD`, the date of that commit. |
| **Order** | Newest first. `[Unreleased]` collects work not yet tagged. |
| **Categories** | Only these, in this order: **Added · Changed · Deprecated · Removed · Fixed · Resolved · Unresolved · Security**. Two are this project's own, and no entry invents a third: `Resolved` is an [open check](docs/04-integration/README.md#open-checks-on-the-vehicle) closed by an actual measurement, cited by its `OC-nn` id; `Unresolved` is a contradiction found and deliberately *not* reconciled, per [CONTRIBUTING](CONTRIBUTING.md#what-must-not-be-silently-fixed). Empty categories are omitted, not listed as "nothing". |
| **Scope** | The changelog says **what changed**. It does not re-argue *why* — that is the [decision records](docs/decisions/README.md) — and it does not restate the content of the document it points at. |

Tagging a release:

```bash
git tag -a v0.1.5 -m "docs: integrate Node C and remove duplicated content"
git push --tags
```

## [Unreleased]

Nothing yet.

## [0.1.5] — 2026-09-03

Tag `v0.1.5`

Node C was documented in its own files but never propagated into the documents
that describe the system as a whole. Closing that exposed a wider problem — the
same reasoning argued in three or four places, and fourteen factual
contradictions — so this release also establishes one owner per topic and the
rules at the top of this file.

### Added

- **A document ownership map** in [`CONTRIBUTING.md`](CONTRIBUTING.md#who-owns-which-topic):
  one owner per topic, everyone else links. Duplication is now a rule violation
  rather than a matter of taste.
- **Stable ids for the open checks** (`OC-01` … `OC-11`) in a single table with a
  status column, in [`docs/04-integration/`](docs/04-integration/README.md#open-checks-on-the-vehicle).
  Other documents cite the id instead of restating the check.
- Node C entries in the component catalogue, BOM, cable schedule and connector
  standard, all marked **v0.3** so nothing is bought for the first build.
- ADS1115 and IEC 60751 (PT1000) in [`docs/references.md`](docs/references.md).

### Changed

- **Fig. 1 redrawn as a star**, with Node B as the hub and Node C shown dashed and
  labelled *not built*. The architecture diagram had still shown two nodes.
- **Node A's state machine moved to [`docs/02-firmware/`](docs/02-firmware/README.md)**,
  along with Fig. 6. Behaviour belongs in the behaviour specification; the hardware
  document keeps stages, values and the pin map.
- Reasoning that had been argued in two or three places at once is now argued once,
  in the record that owns it, and cited elsewhere: the donor teardown, the
  ground-loop property, the tell-tale LED convention, the bulkhead connector, the
  sensor-return rule and the prior-art descriptions.
- [`docs/00-concept/`](docs/00-concept/README.md) lost its *Structural decisions*
  list, which summarised the *Design rationale* section immediately below it.
- Entries in this file were renumbered from four undated `[Unreleased]` blocks
  into dated versions `0.1.1`–`0.1.4`, and the invented per-entry categories were
  folded into the standard set.

### Fixed

- `docs/02-firmware/` described the ESP-NOW link as **bidirectional** in one
  paragraph and as **a star** fifteen lines later.
- [Node B, Stage 3](docs/01-hardware/node-b-gauge.md#stage-3--analogue-input-0-5-v-sensor-optional)
  and the BOM still recommended a **MAX31855 thermocouple amplifier**, which
  [ADR 0006](docs/decisions/0006-node-c-analogue-front-end.md) had replaced with
  PT1000 RTDs. Same error in the roadmap's *Discarded* section.
- The figure count in [`docs/01-hardware/`](docs/01-hardware/README.md) said ten;
  there are eleven.
- The root README counted **six** open checks where every other document counted
  seven.
- `assembly-and-wiring.md` listed a Dupont crimp die as an essential tool in a
  document whose stated rule is to avoid Dupont connectors in a car.
- Node A's relay firing rule appeared twice in the same document, once as a
  blockquote at each end.
- "Two nodes" corrected to three, or to the wording that is still true of v0.1,
  in the README, the concept document, the hardware index and the ADR index.
- The **Recom R-78E5.0-1.0's input range** was given as 6.5–32 V in one document
  and 7–28 V in another. The datasheet says **8–28 V**; both were wrong, and the
  8 V floor is now noted as a real limit during cranking.
- Node A's C5 row described ground as connected to GPIO34.
- A field note told the builder "red = 12 V" in a repository whose colour code
  makes red +3.3 V.
- The PCB was still called "the v0.2 PCB" in six places after the roadmap made it a
  parallel track rather than a feature version.
- ADR 0003 listed a new cable run and an undecided lamp behaviour that its own
  amendment had already closed. Struck through and pointed at the amendment rather
  than rewritten.
- Figs 7, 8 and 9 omitted the tell-tale LED's connector, added in v0.1.2.
- Node B's pin-map rows for the radio had three cells in a four-column table.

### Unresolved

- **The K-line's route into Node B.** The i59 pin table routes it through the
  adapter on spare pin 7; the layout figures and the cable schedule give it its own
  cable from the OBD port. The source document contains both. Recorded in
  [i59 adapter](docs/01-hardware/assembly-and-wiring.md#i59-adapter-1-male--2-female);
  to be settled before the adapter is built.
- **Node B has no ignition-sense GPIO.** Stage 2 specifies the divider; no pin map
  assigns it. Tracked in [`docs/02-firmware/`](docs/02-firmware/README.md#open-items).

## [0.1.4] — 2026-09-02

Tag `v0.1.4` · commit `cd55d55`

A third node enters the design. Specified, not built — it belongs to v0.3.
Reasoning in [ADR 0006](docs/decisions/0006-node-c-analogue-front-end.md).

### Added

- [`docs/01-hardware/node-c-sensors.md`](docs/01-hardware/node-c-sensors.md) and
  ADR 0006: **Node C, an analogue front end in the cabin**, at the firewall
  pass-through. Channels are typed — ratiometric 0–5 V, resistive NTC/RTD on three
  wires, digital in — on ADS1115s over I²C. The environmental boundary is a sealed
  bulkhead connector, not the node.
- Sensors fitted first: coolant level, caliper temperature, radiator ΔT, ambient
  air, battery voltage. Boost is documented as a free channel, not a feature.
- Fig. 11 and a photograph of the catch tank.
- Open checks `OC-09`, `OC-10`, `OC-11`.

### Changed

- **The ESP-NOW topology becomes a star**, Node B the hub. The packet format is
  promoted from an implementation detail to a protocol — node identity, message
  type, version — to be settled *before* Node C is built.
- **Nodes are optional by default.** The gauge degrades gracefully when one is
  absent, showing its channels as unavailable.
- The speed message to Node A stays at 100–200 ms; slowing it to 2 s was rejected.

## [0.1.3] — 2026-09-01

Tag `v0.1.3` · commit `0e3b7e1`

### Added

- `docs/01-hardware/reference/clock-circuit-clk-01.png` — factory diagram CLK-01.
- A full i59 pin table in
  [i59 adapter](docs/01-hardware/assembly-and-wiring.md#i59-adapter-1-male--2-female):
  pins 1 ILL, 5 UART, 6 GND, 8 IG, 9 ACC, 10 constant B+, and **2, 3, 4 and 7
  carrying nothing**. The K-line therefore rides on a terminal the factory circuit
  does not use.
- A reversibility section grounded in that diagram.
- ⚠️ Pin 5 is a live serial link to the combination meter. The adapter passes it
  through and must not drive it.

### Changed

- The root README and
  [`docs/01-hardware/reference/`](docs/01-hardware/reference/README.md) now state
  that the factory diagrams are **not covered by either of this repository's
  licences**, and document how to substitute redrawn schematics.
- The multimeter checklist gained a check that pin 5 is passed through, not driven.

### Resolved

- `OC-01` partially: the i59 pin *functions* are established. Wire colours and
  empty cavities still need confirming on the car.

## [0.1.2] — 2026-09-01

Tag `v0.1.2` · commit `25cc7ad`

### Added

- `docs/01-hardware/reference/wiper-deicer-circuit-wd-01.png` — factory diagram
  WD-01 / WI-12551.
- A circuit walkthrough in
  [Node A, Stage 4](docs/01-hardware/node-a-locking.md#the-oem-circuit): what each
  of the switch's four terminals does, and why pin 1 must be **disconnected from
  the BIU** rather than tapped in parallel with it.
- **Tell-tale LED.** The indicator already inside the OEM switch (i78 pins 8–9) is
  driven from Node A on GPIO33, **lit while DISABLED**.
- Open check `OC-07`, the LED's electrical specification.

### Changed

- [ADR 0003](docs/decisions/0003-onoff-button-direct-to-node-a.md) amended: four
  wires, all present; pins 1–2 a **momentary** contact; pins 8–9 the LED.
- The SW1 run needs **no new cable** — the factory OrG wire already goes from the
  console to the BIU, where Node A sits.

### Resolved

- `OC-06`, the switch's pin count, from the diagram plus inspection on the car.

## [0.1.1] — 2026-08-31

Tag `v0.1.1` · commit `428a945`

### Added

- [`ROADMAP.md`](ROADMAP.md) as a tiered plan: **v0.1** prototype base, **v0.2**
  firmware only, **v0.3** new nodes, **v0.4** trackday mode, plus standby and
  discarded items. Every entry states whether it needs new hardware.
- A **storage rule**: configuration may persist to internal flash; telemetry may
  not, and goes to an SD card on the node that produces it.
- [ADR 0005](docs/decisions/0005-ota-in-maintenance-mode.md): OTA in a deliberate
  maintenance mode, with a timeout, a refusal to enter while moving, a
  firmware-version report on return, and dual-partition rollback.
- Two firmware requirements in v0.1: **OLED burn-in mitigation** and
  **stale-data indication**.

### Changed

- **The v0.1 locked scope grows from four items to five**: OTA joins it, to be
  built last, after the other four work on the bench.
- Version numbers now denote feature releases. The perfboard-to-PCB migration
  became a parallel hardware track rather than "v0.2", which it had collided with.
- **ADC2 is unusable once Wi-Fi is in the firmware.** On Node B only GPIO36 and
  GPIO39 remain spare; further analogue sensing needs an external I²C ADC. This is
  what later made Node C necessary.

## [0.1.0] — 2026-08-30

Tag `v0.1.0` · commit `daf02c2`

First release. Project named **Subaru-ESP32-SLOW** — *SSM2 Link Over Wireless*.
All documentation derives from the v0.1 design document, kept verbatim in
[`docs/00-concept/source/`](docs/00-concept/source/README.md).

### Added

- Repository structure: `docs/` by phase (00-concept … 04-integration),
  `docs/decisions/`, `scripts/`, and the empty `firmware/`, `hardware/`,
  `software/` trees.
- Full technical content in English: purpose, architecture, design rationale,
  component catalogue, BOM, per-stage values and pin maps, wiring and assembly,
  consumables and tooling, firmware behaviour, install sequence and multimeter
  checklist.
- Ten figures, drawn from code rather than extracted, dark-mode native, with
  automated overflow and collision checking
  ([`scripts/generate_diagrams.py`](scripts/generate_diagrams.py)).
- Six reference photographs, including a teardown of a donor unit.
- [ADR 0002](docs/decisions/0002-speed-over-ssm2-not-vss.md) speed over SSM2 not
  the VSS; [ADR 0003](docs/decisions/0003-onoff-button-direct-to-node-a.md) the
  ON/OFF button as a reused OEM switch wired direct to Node A;
  [ADR 0004](docs/decisions/0004-reuse-oem-contact-pad-buttons.md) the gauge
  controls as the OEM contact pads.
- The **retromod constraint** stated as a top-level requirement, and the
  **ESP-NOW modularity rationale** behind the ESP32 choice.
- Prior art and credits, and a disclosure of where AI assistance was used.
- Licences: CERN-OHL-S v2 for hardware, GPL-3.0-or-later for firmware and software
  (SPDX set; full text still to be inserted — see
  [`SETUP-GITHUB.md`](SETUP-GITHUB.md) §5).
- [`CONTRIBUTING.md`](CONTRIBUTING.md) and [`SETUP-GITHUB.md`](SETUP-GITHUB.md).

### Fixed

- One contradiction in the source document: its BOM gave two perfboard sizes that
  disagreed with the layout figures. Both nodes use 3 × 7 cm (11 × 27 holes).

<!--
Compare links, once the remote exists. Replace OWNER:
[Unreleased]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.5...HEAD
[0.1.5]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/OWNER/Subaru-ESP32-SLOW/releases/tag/v0.1.0
-->
