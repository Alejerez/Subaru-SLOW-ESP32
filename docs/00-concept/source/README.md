# Source document

`Documento_matriz_v0.1_Legacy_3.0R.html` is the original v0.1 design document
("Documento matriz v0.1 · Prototipo Cierre + Gauge · Subaru Legacy 3.0R"),
written in Spanish by the project author. It is kept here **verbatim and
unmodified** as the provenance for everything in `docs/`.

Everything in this repository derives from it. Where the two disagree, this file
is the historical record and the Markdown documentation is the current truth —
the differences are enumerated below and each one is traceable to a decision
record.

## What was carried over

- All technical content: architecture, design rationale, component catalogue,
  BOM, per-stage component values, pin maps, board layouts, wiring, consumables
  and tooling, firmware behaviour, install sequence, multimeter checklist, field
  notes, and the open vehicle checks.
- The bibliography and web sources, into [`docs/references.md`](../../references.md).

## What was deliberately changed

- **Language.** The documentation is in English; the source is in Spanish.
  Technical values (pin numbers, component values, part numbers, prices) were
  carried across unchanged.
- **Figures were redrawn, not extracted.** The source contains ten hand-written
  SVG diagrams. An earlier attempt extracted them mechanically, which surfaced
  three problems: they were drawn for a dark page but rendered on white, several
  labels overflowed their boxes, and arrowheads collided with text. They are now
  regenerated from [`scripts/generate_diagrams.py`](../../../scripts/generate_diagrams.py),
  dark-mode native, with automated overflow and collision checks. Only PNGs are
  committed.
- **Figure numbering was corrected.** The source labelled one figure "Fig. 5"
  twice, and numbered two Node A figures 9 and 8 in the order they appear. The
  figures are now numbered 1–10 in reading order.
- **Fig. 7 (Node A interface) now shows the resolved design.** The source drew the
  ON/OFF button arriving over ESP-NOW from Node B, with a dedicated GPIO27 button
  as an unconfirmed alternative. That was decided the other way — see
  [ADR 0003](../../decisions/0003-onoff-button-direct-to-node-a.md) — and the
  redrawn figure shows the decision, not the open question.

## Errors found in the source, and where they were corrected

The source is provenance, not an authority. These are factual errors carried in it
that this repository has since found and fixed; each is listed so the difference
is not mistaken for a transcription mistake.

| In the source | Corrected to | Where |
| --- | --- | --- |
| Board size: BOM said 7 × 9 cm for Node B and 5 × 7 cm for Node A, while both layout figures drew 3 × 7 cm | **3 × 7 cm**, 11 × 27 holes, for every board | v0.1.1 · [perfboard size](../../01-hardware/README.md#perfboard-size-correction-to-the-source-document) |
| An ignition divider on both nodes, with a clamp described as protecting it | Removed. It had no GPIO in any revision, and the clamp never conducted | v0.1.7 · [CHANGELOG](../../../CHANGELOG.md) |
| ILL divider 10 k / 3.3 k | **20 k / 3.3 k.** The original puts 3.57 V on an ESP32 pin at 14.4 V | v0.1.8 · [Node B Stage 2](../../01-hardware/node-b-gauge.md#stage-2--illumination-ill-sensing) |
| Analogue divider 10 k / 20 k | **20 k / 10 k.** The original puts 3.33 V on an ESP32 pin at 5.00 V | v0.1.8 · [Node B Stage 3](../../01-hardware/node-b-gauge.md#stage-3--analogue-input-0-5-v-sensor-optional--on-b-gauge) |
| SSM2 at **10400 baud** | **4800 baud, 8N1.** 10400 is generic ISO 9141-2 OBD-II, not SSM2 | v0.1.8 · [firmware](../../02-firmware/README.md#node-b--gauge) |
| The DevKit's right-hand pin row, read from the wrong end | **`3V3` is beside `VIN` at the USB end**, not at the antenna end. Reversed in every layout from v0.1.0 | v0.1.8 · [`board_lib.py`](../../../scripts/board_lib.py) |
| Reservoir capacitors of **470 µF** on the buck output | **100 µF.** The Recom's maximum capacitive load is 220 µF | v0.1.8 · [Node A Stage 1](../../01-hardware/node-a-locking.md#stage-1--power-ig-to-5-v) |
| A **2 A** fuse on a node drawing ~250 mA | **1 A slow-blow** | v0.1.8 |
| **1N5822 / P6KE18A** offered as axial substitutes | **SB1100 / P6KE20A.** The originals do not physically fit a 2.54 mm perfboard | v0.1.8 · [Node A build](../../01-hardware/node-a-build.md#read-this-before-the-iron-is-hot) |
| Node A's power stage described as *identical* to Node B's | It never carried Node B's three ceramics. All three added | v0.1.8 |
| The tell-tale's series resistor assumed to be inside the OEM switch | Unknown, and the part may not be an LED. A resistor footprint (R8) now exists | v0.1.8 · [`OC-07`](../../04-integration/README.md#open-checks-on-the-vehicle) |

## What was deliberately left out

The source HTML contains a section with `id="cambios"` ("Cambios respecto de la
v1") marked `style="display:none"` — it does not render in the original document.
It describes an older revision of the design that has been superseded. **It is
out of scope and is not reproduced anywhere in this repository.** It remains
inside the HTML file only because the file is kept unmodified.
