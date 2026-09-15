# 0007 — Node B is two boards, split by voltage domain

- **Status:** Accepted · amended by [ADR 0008](0008-node-b-runs-on-one-33-v-rail.md)
- **Date:** 2026-09-14
- **Affects:** Node B hardware, the cable schedule, the i59 K-line question, the install sequence
- **Detail:** [`docs/01-hardware/node-b-build.md`](../01-hardware/node-b-build.md)

## Context

Node B was specified as one 3 × 7 cm perfboard carrying the ESP32, a 12 V→5 V
supply, two divided ADC inputs, a K-line transceiver, and connectors for the OLED,
the RTC and four buttons. The board size was
[confirmed by measurement](../01-hardware/README.md#perfboard-size-correction-to-the-source-document)
rather than assumed.

Laying it out hole by hole made the problem arithmetic rather than opinion. A
socketed DevKit V1 occupies columns A and L, rows 1–15, and its body and PCB
antenna reach to row 18. The only full-height space left is rows 19–27:
**639 mm²**. Three rails of connectors — 23 wires leave this node — take **324 mm²**
of that. What is left is not one block: the rails cut it into strips **at most
3.5 mm deep**, and the only usable area is the column band A–D that the rails do
not reach, **198 mm², about 10 mm wide**, of which C3 takes 50.

The parts that had to go there are C1, the Recom buck (11.6 × 8.5 mm, 99 mm²),
the L9637D on a DIP-8 adapter (9 × 10.5 mm, 95 mm²) and four small diodes and
capacitors: **about 310 mm²**. Three of them are **8.5–10.5 mm deep**, against a
10 mm-wide block with 148 mm² left in it and 3.5 mm strips everywhere else. The
binding constraint is shape, not area, and no rearrangement recovers it.

There was no discovery here that a bigger board would not have solved. The board
size is fixed by the OEM clock bay the retromod constraint requires the gauge to
keep, so the board could not grow.

## Alternatives considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| **A larger gauge board** | One board, no umbilical, no split | The bay is the OEM clock bay and the carrier has to fit it. This is the constraint the whole project exists to respect |
| **Drop Stage 3, the analogue input** | Frees 2 connector positions and 4 parts | Recovers ~30 mm² of strip area, and none of the depth the three big parts need. Does not close the gap, and spends a documented capability for nothing |
| **Surface-mount passives on the solder side** | Frees real area | Changes the parts already bought, and puts components on the face the 31 jumpers run across. The tall parts — C1, the buck, the adapter — are the problem, and none of them has an SMD equivalent that helps |
| **Split off only the supply**, keeping the transceiver on the gauge board | One fewer part to move | Leaves 12 V in the clock bay for the L9637D's VS pin and the 510 Ω pull-up, and leaves the adapter's 95 mm² on the crowded board. Half the benefit for the same cable |
| **Split by voltage domain** *(chosen)* | Everything above 5 V lives on one board, at the end of the harness where the 12 V already arrives | A second board, a second enclosure, and a six-wire cable that has to be made and rung out correctly |

## Decision

**Node B is built as two boards, and the split is by voltage domain.**

- **B-PWR**, at the i59 adapter: the fuse's load side, D1, D2, C1, C2, the Recom
  buck and C4; the ILL divider R3/R4; and the L9637D with R7, C8, C9 and C10.
- **B-GAUGE**, in the clock bay: the ESP32, C3 and C11, the clamps and filters of
  the two ADC chains, and the five connectors.

They are joined by an umbilical, 15–20 cm, latching at both ends. **ADR 0008 cut
it from six wires to five** when Node B moved to a single 3.3 V rail; the pin list
lives in [`node-b-build.md`](../01-hardware/node-b-build.md#1--the-umbilical-first).

Two parts of this are decisions in their own right.

**The transceiver goes with the 12 V, not with the UART.** Its VS pin and its
510 Ω pull-up are 12 V parts; its RX and TX are 3.3 V logic at 4800 baud, which
travels 20 cm of cable without noticing. Putting it on B-PWR also puts it where
the K wire arrives.

**The ILL divider is split across the two boards.** R3 and R4 set the ratio on
B-PWR, so the dash rheostat's 12 V never leaves that board; D4 and C6 clamp and
filter at the ADC pin, where a filter belongs. The cable carries a 1.7–2.3 V node
at 2.8 kΩ instead of a 12 V line into the clock bay.

> **Superseded.** This ADR originally sent 5 V up the umbilical and had the
> gauge board's DevKit make 3.3 V for everything, including the L9637D back down
> the same cable — an arrangement it flagged as looking like a mistake. It was
> one: the display draws ~310 mA at 3.3 V, which the DevKit's regulator cannot
> supply. [ADR 0008](0008-node-b-runs-on-one-33-v-rail.md) makes 3.3 V at B-PWR
> instead.

## Consequences

**No 12 V reaches the clock bay.** The highest net on B-GAUGE is 5 V. That is a
better property than the one it replaces, and it was not the reason for the split.

**Each board can be bench-tested alone**, and the build order exploits it: B-PWR's
supply and transceiver are proved before B-GAUGE exists. The one asymmetry is that
B-PWR needs an external 3.3 V on the bench, because its 3.3 V normally comes from
the other board.

**The umbilical is a new single point of failure**, a five-wire cable carrying
power, a reference-sensitive analogue node and a UART. It is made first and
rung out pin to pin before either board is mounted.

**Three perfboards instead of two**, all the same 3 × 7 cm part, so one printed
tray design fits all three. B-PWR uses 43 of its 297 holes and can be snapped
shorter if the console space demands it.

**The i59 K-line question is narrowed but not closed.** The K wire now terminates
at B-PWR, which sits at the i59, so the layout figures no longer disagree with the
[adapter's pin table](../01-hardware/assembly-and-wiring.md#i59-adapter-1-male--2-female);
what is left is only how the wire gets there. Still
[recorded, not reconciled](../../CONTRIBUTING.md#what-must-not-be-silently-fixed).

**Left unresolved**

- **LI and LO on the L9637D.** ST's datasheet states that an open LI is a defined
  condition but gives no guidance for a K-line-only design, and there is no
  application note for the part. LI is tied to VS by inference from the threshold
  and current specifications, not from a quoted recommendation. One jumper.
- ~~The 3.3 V budget.~~ **Resolved, and against this ADR**, by
  [ADR 0008](0008-node-b-runs-on-one-33-v-rail.md).
- **Where B-PWR physically mounts** behind the i59, and whether its enclosure and
  B-GAUGE's can share a printed design.
