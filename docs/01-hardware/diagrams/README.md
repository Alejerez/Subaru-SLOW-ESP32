# Figures

Eleven figures, `01-` to `11-`, numbered in the order they appear in the
documentation. **PNG only** — the SVG is an intermediate render artefact and is
not committed.

| # | File | Appears in |
| --- | --- | --- |
| 1 | `01-system-architecture.png` | [Concept](../../00-concept/README.md#architecture), [README](../../../README.md) |
| 2 | `02-node-b-power-stage.png` | [Node B](../node-b-gauge.md#power-stage) |
| 3 | `03-node-b-signal-interface.png` | [Node B](../node-b-gauge.md#signal-interface-k-line-oled-rtc) |
| 4 | `04-node-b-spatial-layout.png` | [Node B](../node-b-gauge.md#full-spatial-layout) |
| 5 | `05-node-b-grid-plan.png` | [Node B](../node-b-gauge.md#exact-plan-on-the-perfboard-grid) |
| 6 | `06-node-a-state-machine.png` | [Firmware, Node A](../../02-firmware/README.md#node-a--locking) |
| 7 | `07-node-a-interface.png` | [Node A](../node-a-locking.md#interface-schematic) |
| 8 | `08-node-a-spatial-layout.png` | [Node A](../node-a-locking.md#spatial-layout) |
| 9 | `09-node-a-grid-plan.png` | [Node A](../node-a-locking.md#grid-plan) |
| 10 | `10-carrier-concept.png` | [Assembly and wiring](../assembly-and-wiring.md#the-carrier-board-per-node) |
| 11 | `11-node-c-channels.png` | [Node C](../node-c-sensors.md#channel-architecture) |

## How they are produced

The source of truth is [`scripts/generate_diagrams.py`](../../../scripts/generate_diagrams.py)
— a Python script that emits SVG, which
[`scripts/svg_to_png.py`](../../../scripts/svg_to_png.py) renders to PNG through
headless Chromium at 2× device scale. To rebuild every figure:

```bash
python3 scripts/generate_diagrams.py
```

### Why it is built this way

The figures in the v0.1 source document were hand-written SVG embedded in the
HTML. Extracting them mechanically exposed three problems that could not be fixed
by re-rendering:

- **They were drawn for a dark page but rendered on white**, which inverts badly
  when the documentation is read in dark mode.
- **Labels overflowed their boxes** — text wider than the rectangle it sat in.
- **Arrowheads collided with the labels they pointed at.**

Redrawing from code fixes all three by construction:

- **Dark-mode native.** Dark canvas, light strokes. They read correctly in dark
  mode and remain perfectly legible in light mode, where they appear as a dark
  card.
- **Monospace everywhere.** DejaVu Sans Mono has a fixed advance width of
  0.60238 em, so text width is exactly computable and boxes are sized from their
  content rather than guessed.
- **Automated checks.** After rendering, every element is tested against the
  viewBox and every label against every other label. Overflow or collision is
  reported and the run exits non-zero rather than quietly emitting a broken
  figure.

### Colour code

Consistent across every figure, carried over from the source document:

| Colour | Net |
| --- | --- |
| Yellow | +12 V |
| Orange | +5 V |
| Red | +3.3 V |
| Grey | GND |
| Blue | Signal |
| Cyan (dashed) | ESP-NOW — radio, no wire |
| Green | Node A |
| Purple | Node B |
| Pink | Node C |
