# 0008 — Node B runs on one 3.3 V rail, made at B-PWR

- **Status:** Accepted
- **Date:** 2026-09-14
- **Affects:** Node B's supply, the umbilical, the DevKit's power pin, the BOM
- **Detail:** [`docs/01-hardware/node-b-gauge.md`](../01-hardware/node-b-gauge.md#node-b-is-built-as-two-boards)

## Context

[ADR 0007](0007-node-b-split-into-two-boards.md) put Node B's supply on B-PWR and
sent 5 V up the umbilical to the gauge board, where the DevKit's own AMS1117 made
the 3.3 V for the ESP32, the OLED, the DS3231 and — back down the same cable — the
L9637D. That ADR listed the 3.3 V budget as unresolved, with the honest note that
no current figure for the display existed anywhere in the project.

The figure exists. A 3.12" 256×64 SSD1322 module draws **310 mA typical, 340 mA
maximum** at 3.3 V in its default configuration, where the panel's high voltage is
generated on the module from the 3.3 V input (Newhaven NHD-3.12-25664UCY2, the
reference design the generic modules clone).

With the ESP32's 240–350 mA transmit peak on top, the AMS1117 would carry about
600 mA and dissipate **(5 − 3.3) × 0.6 ≈ 1.0 W** in a SOT-223 on a clone DevKit
with no copper pour — θ<sub>JA</sub> realistically 120–160 °C/W, so a 120–160 °C
rise. That exceeds the part's 125 °C junction limit on a 25 °C bench, let alone in
a closed console. It is not a marginal call: the previous arrangement cannot work
at any ambient.

## Alternatives considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| **Keep 5 V up the cable, add a 3.3 V regulator on B-GAUGE** | Umbilical unchanged | A linear part has the same 1 W problem wherever it sits. A switcher would work, but the Recom needs ≥7 V in and cannot run from 5 V, so this means a different part family for one board |
| **Use the display's external-VCC jumper**, panel supply from 12 V | Takes 300 mA off the logic rail entirely | Puts 12 V back in the clock bay, which is the property ADR 0007 was pleased to have removed |
| **Dim the display permanently** | No hardware change | Trades the one thing the gauge exists to do against a thermal problem that has a cheap fix |
| **Make 3.3 V at B-PWR and send that** *(chosen)* | One rail, one regulator, made where the 12 V already is | A different Recom variant, and the 5 V part already bought becomes a spare |

## Decision

**U1 on B-PWR is a Recom R-78E3.3-1.0, and 3.3 V is the only supply rail in Node
B.** The DevKit is fed on its **`3V3` pin** with `VIN` left unconnected, so the
module's own regulator is out of the circuit.

The umbilical drops from six wires to five: **+3.3 V, GND, ILL (divided), K-RX,
K-TX.**

Three consequences fall out of this rather than being designed for:

**The L9637D's VCC is now local.** ADR 0007 recorded an unresolved hazard — VS at
12 V with VCC at zero, when the umbilical is unplugged or the gauge board is dead,
in a state ST's datasheet does not specify, on a K line shared with every scan tool
that will ever touch this car. U1 and U2 are now on the same board and cannot be
separated. The hazard is gone, and so is the "3.3 V travels the other way" wire
that ADR 0007 had to warn people not to "fix".

**The crank margin improves.** The 3.3 V Recom's input range is **7–28 V** against
the 5 V part's 8–28 V, so with D1's 0.4 V the node holds regulation down to about
7.4 V at the connector instead of 8.4 V.

**Node A is unaffected** and keeps the 5 V part, because its relay coil needs 5 V.
The two nodes no longer share a regulator variant, which the catalogue now says
explicitly.

## Consequences

**The Recom is loaded to about 85 % of its derated capability.** 550 mA typical and
700 mA peak against 1 A derated to roughly 0.8 A at 70 °C. That is workable and it
is not comfortable, and it rests on a figure measured on a module that has not been
bought. **Measuring the display's actual 3.3 V current is now a build step**, and
if it comes in much higher the escape is the external-VCC jumper.

**C3 changes value for an unrelated reason.** The Recom's maximum capacitive load
is 220 µF and C3 sits on its output; the 470 µF specified since v0.1.0 is twice
that, on both nodes. C1 and C3 are now 100 µF on Node A and Node B alike.

**USB and the umbilical must never be connected together.** Feeding `3V3` directly
means the DevKit's regulator is unpowered — until USB arrives, when it starts
driving the same rail. The build page makes unplugging the umbilical step one of
flashing.

**One more part to buy.** The 5 V Recom bought for Node B becomes a spare. The
alternative was a regulator that cooks itself, so this is not a close call.

**Left unresolved**

- The display module's actual current, above.
- The Recom's own input filter: its datasheet calls for a 10 µF MLCC at the input,
  and an LC network for EN55032. B-PWR has C2 and no choke.
