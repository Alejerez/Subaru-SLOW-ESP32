# Figures

Twenty figures, `01-` to `20-`, numbered in the order they appear in the
documentation. **PNG only** — the SVG is an intermediate render artefact and is
not committed.

| # | File | Appears in |
| --- | --- | --- |
| 1 | `01-system-architecture.png` | [Concept](../../00-concept/README.md#architecture), [README](../../../README.md) |
| 2 | `02-node-b-power-stage.png` | [Node B](../node-b-gauge.md#power-stage) |
| 3 | `03-node-b-signal-interface.png` | [Node B](../node-b-gauge.md#signal-interface-k-line-oled-rtc) |
| 4 | `04-node-b-spatial-layout.png` | [Node B](../node-b-gauge.md#spatial-layout) |
| 5 | `05-node-b-grid-plan.png` | [Node B](../node-b-gauge.md#grid-plan) |
| 6 | `06-node-a-state-machine.png` | [Firmware, Node A](../../02-firmware/README.md#node-a--locking) |
| 7 | `07-node-a-interface.png` | [Node A](../node-a-locking.md#interface-schematic) |
| 8 | `08-node-a-spatial-layout.png` | [Node A](../node-a-locking.md#spatial-layout) |
| 9 | `09-node-a-grid-plan.png` | [Node A](../node-a-locking.md#grid-plan) |
| 10 | `10-carrier-concept.png` | [Assembly and wiring](../assembly-and-wiring.md#the-carrier-boards) |
| 11 | `11-node-c-channels.png` | [Node C](../node-c-sensors.md#channel-architecture) |
| 12 | `12-node-a-placement.png` | [Node A build](../node-a-build.md#component-side) |
| 13 | `13-node-a-solder-side.png` | [Node A build](../node-a-build.md#solder-side) |
| 14 | `14-node-a-technique.png` | [Node A build](../node-a-build.md#how-to-mount-and-solder-it) |
| 15 | `15-node-b-two-boards.png` | [Node B build](../node-b-build.md#node-b-is-two-boards) |
| 16 | `16-node-b-gauge-placement.png` | [Node B build](../node-b-build.md#component-side) |
| 17 | `17-node-b-gauge-solder-side.png` | [Node B build](../node-b-build.md#solder-side) |
| 18 | `18-node-b-pwr-placement.png` | [Node B build](../node-b-build.md#component-side-1) |
| 19 | `19-node-b-pwr-solder-side.png` | [Node B build](../node-b-build.md#solder-side-1) |
| 20 | `20-node-b-technique.png` | [Node B build](../node-b-build.md#what-node-b-needs-that-node-a-did-not) |

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
- **Automated checks.** Before anything is drawn,
  [`scripts/check_figure_text.py`](../../../scripts/check_figure_text.py) reads
  every string literal inside every figure function and compares it against the
  component tables the boards are built from: a retired part name, or a value
  that disagrees with the layout, stops the run. After rendering, every element
  is tested against the viewBox and every label against every other label.
  Overflow or collision is reported and the run exits non-zero rather than
  quietly emitting a broken figure.

  > This check exists because of a real defect. Between v0.1.5 and v0.1.8 the
  > layouts moved to SB1100, P6KE20A, 100 µF reservoirs and a 3.3 V-only Node B
  > while ten figures went on drawing SS34, SMAJ18A, 470 µF and a 5 V rail — and
  > Fig. 14's polarity panel still named holes the parts had moved out of. Prose
  > gets reviewed; strings buried in drawing code do not, so they are checked
  > mechanically instead. Fig. 14's polarity table is now generated from the
  > layout rather than typed.

### Colour code

Carried over from the source document, and used consistently in the schematic
and layout figures:

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

> **One deliberate exception, in the build figures.** Figures 12–14 and 16–19 draw
> wires in the colour of the reel the builder actually cuts from, and +5 V is
> **green** there because copper-coloured wire is not in the box. Both build pages
> say so at the head of their colour table. Node B has no 5 V rail at all since
> v0.1.8, so the clash only arises on Node A.
