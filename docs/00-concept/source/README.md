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

## What was deliberately left out

The source HTML contains a section with `id="cambios"` ("Cambios respecto de la
v1") marked `style="display:none"` — it does not render in the original document.
It describes an older revision of the design that has been superseded. **It is
out of scope and is not reproduced anywhere in this repository.** It remains
inside the HTML file only because the file is kept unmodified.
