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
git tag -a v0.1.7 -m "docs: remove the ignition divider from both nodes"
git push --tags
```

## [Unreleased]

Nothing yet.

## [0.1.7] — 2026-09-13

Tag `v0.1.7`

**The ignition divider is removed from both nodes.** It was specified in the v0.1
source document, carried through four revisions of this repository, and documented
as protected by a clamp that does not conduct. None of that was caught until the
board layout forced a real number onto a real pin.

### Removed

- **Node A: R1, R2, D3, C5**, and with them five jumper runs: `Y3` (VBAT to the
  divider), `N5` (its ground return), the old `B1` (the divider node) and old `B2`
  (node_IGN to GPIO34), plus `R2w`, which disappeared when the 3.3 V feed stopped
  needing to reach the clamp and became a single run straight to the relay's VCC.
  The old `B3`/`B4` are renumbered `B1`/`B2` and are unchanged electrically.
  **18 runs become 13, and 790 mm of wire becomes 646 mm.** GPIO34 is freed, and
  rows 19–26 go from 69 free holes to **77**.
- **Node B: R1, R2, D3, C5** — the ignition half of Stage 2. It never had a GPIO
  assigned in any revision, so it was four parts soldered to nothing. **The ILL
  divider stays**: following the dash rheostat is a real function with no other
  source. Those four designators are retired, not reused.

### Fixed

- The documentation claimed **D3 protected the ignition input**. It did not. A BAT85
  to the 3.3 V rail conducts above about 3.6 V; with 10 k / 3.3 k fed from VBAT the
  node reaches only **3.47 V** at a 14.4 V charging voltage. The divider alone set
  the pin voltage, 0.13 V under the ESP32's absolute maximum, with nothing in
  reserve. That claim was this repository's, not the source document's.
- The input could not be read either. ADC1 at 11 dB has a suggested range of
  **150–2450 mV** [19]; the node passed 2.45 V at about 10.3 V at the connector and
  pinned at full scale near 12.9 V. With the engine running it returned 4095 and
  nothing else.
- Node A's stages renumbered 1–3 and every anchor repointed: `OC-02`, `OC-03`,
  ADR 0003, the reference index and the build page.
- The solder-side figure's run count, total wire length and shared-colour note are
  now **computed from the layout data** instead of typed into the drawing, which is
  how they went stale in the first place.

### Added

- **A feed-and-ground resistance check** in the
  [multimeter checklist](docs/04-integration/README.md#multimeter-checklist) and as
  stage 6 of the build: with the node unplugged, measure fuse output → J1's +12 V pin
  and J1's GND pin → the chassis stud, each well under 1 Ω.

  The first draft of this check asked for a *voltage droop* while pulsing a relay,
  which does not work: the coil runs off the 5 V rail, so the step at the 12 V input
  is only ~34 mA, and a properly bad 1 Ω joint produces 34 mV. It would have taken
  about 12 Ω — a broken wire — to trip the stated 0.5 V threshold. Measuring the
  joint's resistance directly is the test that actually finds the fault.

### Why removed rather than re-ratioed

Changing R2 would have made the input readable. It would not have given it a job.
The node is **fed from IG**, so being powered already proves the ignition is on;
battery voltage is polled by Node B over SSM2 and planned properly on Node C with a
16-bit ADC at the battery. No use case survived that something else was not already
doing better, and a component without a job is debt on a hand-soldered board.

Cost of the error: none of these parts appears as its own BOM line — all four come
from assortments bought for Node B regardless, so the removal produces spares, not
waste.

## [0.1.6] — 2026-09-13

Tag `v0.1.6`

The parts arrived, so Node A gets a bench build: not a schematic, but which hole
every lead goes in and every jumper on the solder side.

### Added

- [`docs/01-hardware/node-a-build.md`](docs/01-hardware/node-a-build.md) — the
  hole-by-hole build. Placement table, an **18-jumper cut list** (790 mm of wire)
  with the hole sequence and cut length for each, a six-colour wire convention
  matched to what is in the box, and seven build stages each ending in a
  measurement that has to pass before the next one starts.
- **Fig. 12** component side, **Fig. 13** solder side (mirrored, as the board
  actually is when flipped), **Fig. 14** mounting and soldering technique.
- Three verified facts the layout rests on, now recorded rather than assumed: the
  DevKit V1's pin rows are **25.4 mm apart, exactly 10 pitches** [1], so the module
  fills the board's width and rows 16–18 stay empty under its antenna; the physical
  pin order of the 30-pin board [2]; and the Recom SIP3 pinout and 2.54 mm pitch [3].
- Two bench tests promoted to conditions of the build: **neither relay may click at
  power-up** (these modules are usually active-LOW, and an active-HIGH one would
  lock the doors on every boot), and the relay must be confirmed to switch with
  **VCC at 3.3 V** — with the note that raising VCC to 5 V is *not* the fallback,
  since a push-pull GPIO at 3.3 V still leaves 1.7 V across the opto and may never
  let the relay release.
- ESP-IDF's ADC attenuation table in [`docs/references.md`](docs/references.md) [19].

### Changed

- **The ignition divider is fed from VBAT, after D1**, rather than from the raw IG
  line. It costs 0.4 V on a signal only ever compared against a firmware threshold,
  and puts the divider behind the reverse-polarity diode like everything else.
  Node A's Stage 2 updated so the two pages do not disagree. *(The divider itself was
  removed in 0.1.7; that stage no longer exists.)*
- **Fig. 9's zone plan corrected.** It had the ESP32 on 14 rows instead of 15 and
  put the divider and the connectors in rows that the real layout uses for
  something else. It is now a zone summary of Fig. 12 and says so.
- The BOM's **2 A fuse is specified slow-blow (T)** — 940 µF of bulk capacitance
  draws an inrush at key-on that a fast fuse can nuisance-trip.

### Unresolved

- **What the ignition-sense inputs are for.** Both nodes are powered from IG, so
  being awake already proves the ignition is on. If the answer is supply
  monitoring, Node A's 10 k / 3.3 k divider is the wrong ratio — it leaves ADC1's
  suggested 150–2450 mV band above about 10.3 V at the connector and pins at full
  scale near 12.9 V, so with the engine running GPIO34 reads 4095 and nothing
  else. The clamp diode does not rescue this: at 14.4 V the node sits at 3.47 V,
  below the BAT85's conduction point, so the divider alone sets the voltage,
  0.13 V under the ESP32's absolute maximum. Recorded, not silently re-specified —
  the fix is one resistor, but the question of purpose comes first. Tracked in
  [`docs/02-firmware/`](docs/02-firmware/README.md#open-items).
- **W2 (the tell-tale LED run) is fitted but left unconnected at the switch end**
  until [`OC-07`](docs/04-integration/README.md#open-checks-on-the-vehicle) is
  measured.

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
[Unreleased]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.7...HEAD
[0.1.7]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.6...v0.1.7
[0.1.6]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.5...v0.1.6
[0.1.5]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.4...v0.1.5
[0.1.4]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.3...v0.1.4
[0.1.3]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.2...v0.1.3
[0.1.2]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.1...v0.1.2
[0.1.1]: https://github.com/OWNER/Subaru-ESP32-SLOW/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/OWNER/Subaru-ESP32-SLOW/releases/tag/v0.1.0
-->
