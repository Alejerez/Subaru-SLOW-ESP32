# Changelog

Milestones in prose. Not a mirror of every commit — for the fine detail, `git log`
and the tags are the source of truth.

Format after [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); one git tag
per meaningful milestone, pointing at the commit where it closed.

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
- Photograph of the OEM switch panel identifying the unused de-icer button.
- ADR [0002](docs/decisions/0002-speed-over-ssm2-not-vss.md): vehicle speed over
  SSM2, not from the VSS.
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

- **Six open checks on the vehicle**, none treated as resolved — see
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
