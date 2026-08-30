# 0004 — Reuse the OEM contact-pad buttons as the gauge controls

- **Status:** Accepted
- **Date:** 2026-08-30
- **Affects:** Node B (Stage 5, pin map), the v0.2 carrier PCB, the retromod constraint
- **Evidence:** teardown of a donor unit — [`docs/01-hardware/photos/`](../01-hardware/photos/README.md)

## Context

The gauge needs four controls: page navigation and settings. The
[retromod constraint](../../README.md#the-constraint-that-drives-everything-this-is-a-retromod)
rules out anything that reads as aftermarket, so adding new buttons — or a new
bezel carrying them — was never attractive. The question was whether the existing
OEM buttons could be driven by the ESP32 instead, and that depended on how they
are actually built, which the v0.1 design document never established.

To find out without risking the car's own unit, a **second unit of the same
generation and housing was bought and taken apart**: the base clock-only trim,
which has one button fewer but is otherwise the same assembly.

The teardown answered it. The buttons are not discrete tactile switches soldered
to the board. They are **interdigitated contact pads etched on the OEM PCB**,
closed by a conductive rubber pad behind the bezel — the same construction used in
remote controls and appliance keypads. Visible, outlined in red, in
[`donor-pcb-contact-pads.jpg`](../01-hardware/photos/donor-pcb-contact-pads.jpg).

That construction is the good case: a pad closure is an ordinary dry contact with
no OEM silicon in the path.

## Alternatives considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| **Reuse the OEM contact pads, wired to ESP32 inputs** *(chosen)* | Keeps the OEM bezel, travel and feel exactly; nothing to design, print or fit; satisfies the retromod constraint outright; a pad closure is a plain dry contact, directly usable with `INPUT_PULLUP` | The pad geometry has to be carried over to the new board, or the OEM board's button area retained; conductive rubber ages and can go intermittent |
| New tactile switches on the carrier, behind the OEM bezel | Clean, known, cheap parts; deterministic contact resistance | Travel and click would have to be matched to the OEM rubber, or the bezel feels wrong; alignment against the existing bezel is fiddly |
| A new bezel with new buttons | Full freedom over layout | Directly against the retromod constraint — this is the one thing the project exists to avoid |

## Decision

**The OEM contact pads are reused as the four gauge controls**, wired to the
ESP32 with `INPUT_PULLUP` and the pad's other side to ground — the pin mapping
already specified in [Node B, Stage 5](../01-hardware/node-b-gauge.md#stage-5--display-clock-and-buttons)
(GPIO 32/33/25/26) is unchanged; what this record settles is *how* the buttons
physically get there.

Concretely, either the OEM board's pad area is cut out and retained and wired to
the carrier, or the carrier reproduces the pad geometry so the original rubber
lands on it. Which of the two is an open point, below.

## Consequences

**Makes easier**

- No button hardware to design, source or fit. The OEM bezel, rubber and travel
  are kept as they are.
- Electrically trivial: a pad closure is a dry contact. The ESP32's internal
  pull-up (~45 kΩ) is high enough that even a conductive-rubber contact of a few
  kΩ pulls the pin firmly below the logic-low threshold, so no external
  conditioning is needed beyond the debounce already specified.

**Makes harder / commits us to**

- **The v0.2 PCB is no longer free-form in that area.** If the carrier reproduces
  the pads, their geometry, spacing and surface finish have to match what the OEM
  rubber expects — the pads are usually carbon- or gold-finished, and bare tinned
  copper oxidises and goes intermittent.
- **Ageing contacts.** Conductive rubber and its pads degrade. Clean both with
  isopropyl alcohol during assembly, and expect contact resistance to rise over
  the years rather than fail outright.
- The donor is the base trim with one button fewer. The pad layout on the car's
  own trip-computer unit must be confirmed against it before anything is cut or
  laid out.

**Left unresolved**

- **Retain the OEM pad area, or reproduce it on the carrier?** Retaining is lower
  risk and keeps the original finish; reproducing is tidier and avoids a second
  board inside the housing. Decide when the car's own unit is opened.
- The exact pad count and layout on the car's unit — see the
  [open checks](../04-integration/README.md#open-checks-on-the-vehicle).
- Debounce value, shared with the [ADR 0003](0003-onoff-button-direct-to-node-a.md)
  button; tracked in [`docs/02-firmware/`](../02-firmware/README.md#open-items).
