# 0003 — ON/OFF button: reused OEM switch, wired direct to Node A

- **Status:** Accepted
- **Date:** 2026-08-30
- **Affects:** Node A (Stage 4, pin map, firmware), Node B (firmware), ESP-NOW link topology, Fig. 1 and Fig. 7

## Context

The auto-lock function needs a way for the driver to disable it. The v0.1 design
document left this **explicitly open** — it described two options and marked the
choice "to be confirmed":

1. The toggle reaches Node A over ESP-NOW from the gauge (Node B), driven by one
   of the four OEM buttons already wired to Node B. The document flagged this as
   the recommended option, since it needs no extra wiring or hardware.
2. A dedicated button on Node A's GPIO27, using the internal pull-up.

Two facts, established after the document was written, change the picture:

- **The car has an unused OEM switch.** The windscreen-wiper de-icer button is a
  North-American-market option this EDM car does not have. The switch position
  exists in the console, is wired, and does nothing. Reusing it costs no new
  hardware and no new hole in the dash.
- **The retromod constraint favours it.** Reusing OEM controls rather than adding
  aftermarket ones is a top-level project requirement, not a preference (see the
  [README](../../README.md#the-constraint-that-drives-everything-this-is-a-retromod)).

With a physical switch available, option 2 stops being the expensive option.

## Alternatives considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| **Toggle over ESP-NOW from a Node B OEM button** (the document's recommendation) | No new wiring at all; confirmation on the OLED is trivial since the button and the display are on the same node | Spends one of only four OEM gauge buttons on a function unrelated to the gauge; the locking function then depends on the radio for *control* as well as for speed — a radio dropout means the driver cannot disable it; the control is nowhere near the doors it acts on |
| **New dedicated button on Node A GPIO27** | Local, direct, independent of the radio | Requires a new switch and drilling or otherwise mounting it — directly against the retromod constraint |
| **Reuse the unused OEM de-icer switch, wired direct to Node A GPIO27** *(chosen)* | Local and radio-independent control; no new hardware; no new hole; satisfies the retromod constraint exactly; frees all four gauge buttons for the gauge; the switch is already in a natural place for the driver | Adds one wire run from the console to the A-pillar; requires confirming the OEM switch's pinout, which may include an indicator lamp; needs a new ESP-NOW message in the reverse direction to confirm the mode on the OLED |

## Decision

The auto-lock ON/OFF control is the **unused OEM windscreen-wiper de-icer
switch**, wired **directly to Node A** on **GPIO27** with `INPUT_PULLUP`
(switch to ground). No additional components.

Because the display lives on the other node, **Node A sends a mode-change message
to Node B over ESP-NOW** whenever the button is pressed, and Node B shows a
confirmation on the OLED for ≈2 s (e.g. `AUTO-LOCK: ARMED` /
`AUTO-LOCK: DISABLED`) before returning to the previous page.

**The indicator LED already inside the switch is reused as a permanent tell-tale**
(amendment, see below), driven from Node A on GPIO33 and **lit while DISABLED**.

## Consequences

**Hardware**

- Node A gains a new input: GPIO27, `INPUT_PULLUP`, switch to ground. Documented
  as [Stage 4](../01-hardware/node-a-locking.md#stage-4--onoff-button-reused-oem-switch).
- A new cable run: console switch → Node A GPIO27, on a latching connector like
  every other enclosure output.
- No change to the BOM: the switch already exists in the car and the pull-up is
  internal to the ESP32.

**Firmware**

- **ESP-NOW becomes bidirectional.** Previously Node B → Node A only (speed).
  Now also Node A → Node B (mode change, event-driven). Both nodes initialise as
  sender *and* receiver.
- Node A owns the mode as local state; it no longer depends on a flag received
  over the radio. A radio dropout can no longer prevent the driver from disabling
  auto-lock.
- Node B gains an inbound-message handler and a transient OLED confirmation
  overlay. No new hardware on Node B.
- The four OEM gauge buttons are freed: they navigate and adjust the gauge only.

**Documentation**

- Fig. 1 and Fig. 7 show the bidirectional link and the direct GPIO27 wiring.
  These figures were **redrawn**, not annotated — the source document's versions
  depicted the unresolved state and the option that was *not* chosen. See
  [`docs/00-concept/source/README.md`](../00-concept/source/README.md#what-was-deliberately-changed).

**Left unresolved**

- **The indicator LED's electrical specification.** Whether it can be driven
  directly from a 3.3 V GPIO through its presumed internal resistor, needs a
  low-side MOSFET from the 12 V rail, or is better replaced outright with a modern
  high-efficiency LED. Tracked as an
  [open check on the vehicle](../04-integration/README.md#open-checks-on-the-vehicle).
- The debounce value for GPIO27 is not specified; it is an implementation choice.
  Tracked in [`docs/02-firmware/`](../02-firmware/README.md#open-items).
- The mode-change packet format is specified functionally, not at byte level.
  Tracked in the same place.
- Whether the switch's indicator lamp (if present) should be driven to show the
  armed state is **not decided** — it depends on the pin count above, and would
  need a driven output rather than just an input.

## Amendments

**2026-08-30 — the OEM circuit, and the tell-tale LED.** The factory wiring
diagram (WD-01 / WI-12551, kept in
[`docs/01-hardware/reference/`](../01-hardware/reference/README.md)) plus
inspection on the car resolved what this record had left open, and added
something it had not anticipated.

Settled:

- The switch has **four wires and all of them are present** in this car, even
  though the de-icer itself was never fitted. Pins 1–2 are the contact; pins 8–9
  an indicator LED.
- The contact is **momentary** — it does not latch, unlike the folding-mirror
  switch in the same console. This matters: a latching switch would have left the
  button's mechanical position permanently out of step with the software state,
  because the mode resets to ARMED at every ignition-on. The toggle logic in this
  record is therefore valid exactly as written.
- The OrG wire runs **console → BIU**, and Node A is installed at the BIU, so this
  leg needs no new cable.

Added:

- **The indicator LED is reused as a status tell-tale**, driven from Node A on
  GPIO33. It is **lit while DISABLED and dark while ARMED**: ARMED is the default
  and resets each ignition cycle, so the state worth signalling is the one the
  driver chose deliberately — the same convention as a "traction control off"
  lamp. A lamp permanently lit to indicate normal operation stops being read
  within a week.
- This improves on the OLED confirmation alone, which disappears after two
  seconds. Both are kept: the OLED announces the change, the LED holds the state.

Also carried over from the diagram: **pin 1 must be disconnected from the BIU
rather than tapped in parallel with it**, so the switch is electrically isolated
from the body control module. Reversibility is unaffected — plugging the OEM
connector back restores the car.
