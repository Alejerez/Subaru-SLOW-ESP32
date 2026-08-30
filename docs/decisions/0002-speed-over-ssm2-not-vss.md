# 0002 — Vehicle speed over SSM2, not from the VSS

- **Status:** Accepted
- **Date:** 2026-08-30 (transcribed from the v0.1 design document, which had already settled it)
- **Affects:** Node A (hardware and firmware), Node B (firmware), BOM, cable schedule
- **Source:** transcribed from
  [`docs/00-concept/source/Documento_matriz_v0.1_Legacy_3.0R.html`](../00-concept/source/Documento_matriz_v0.1_Legacy_3.0R.html),
  sections "Fundamentos de diseño" and "Propósito"

## Context

The speed-based locking function needs vehicle speed. On the BL/BP chassis, speed
is distributed from the **ABS module**; there is no single, documented "VSS" pin
or wire that can be tapped with confidence. Locating a usable square-wave signal
would require time, instrumentation, and probing wiring whose function is not
documented for this market variant.

Meanwhile Node B is already reading the ECU over **SSM2** on the K-line for the
gauge, and vehicle speed is one of the parameters SSM2 exposes.

An earlier revision of the design had Node A tapping the VSS itself and using an
**LM393** comparator to condition the signal.

## Alternatives considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| **Tap the VSS at Node A** (with an LM393 comparator) | Speed is local to the node that needs it; no dependency on the other node or on the radio | No single documented VSS wire on BL/BP — speed comes from the ABS module; finding and validating it costs bench time and probing; adds a comparator, its passives and a conditioning stage to Node A; the wire has to be found again on any other car |
| **Read speed over SSM2 on Node B and send it by radio** *(chosen)* | Zero extra hardware — the SSM2 link already exists for the gauge; nothing to find or probe in the loom; Node A gets simpler (no comparator, no VSS conditioning); speed arrives already in engineering units | Locking depends on Node B running and polling SSM2; adds a radio link into the safety-relevant path; needs a watchdog so the node never actuates on stale data |
| **A separate speed sensor** (GPS, accelerometer) | Independent of both the car and the other node | New hardware, new failure mode, poor low-speed accuracy; solves a problem the SSM2 link already solves |

## Decision

**Node A does not tap the VSS and uses no comparator.** It receives vehicle speed
from Node B over ESP-NOW; Node B obtains it from the ECU over SSM2.

All VSS-related parts (LM393 and its passives) are removed from the BOM, and the
VSS run is removed from the cable schedule.

## Consequences

**Makes easier**

- Node A collapses to: power stage + ignition sensing + relays + one button. Its
  grid plan is mostly empty as a result (Fig. 9).
- No probing of undocumented loom wiring to find a signal.
- Speed arrives as a value, not as a frequency to be converted and calibrated.

**Makes harder / commits us to**

- **Locking depends on Node B.** If Node B is not polling SSM2, Node A has no
  speed. Both nodes are powered whenever the car is being driven, so this holds
  in practice — with one documented exception: a deliberate session with a
  Tactrix on the same K-line.
- **A radio link is now in the actuation path.** The firmware must implement a
  watchdog (≈1 s): with no packets, Node A does not actuate. Fail-safe is "do
  nothing", never "lock blind".
- The SSM2 speed parameter's unit and scale must be confirmed on this car — one
  of the [open checks](../04-integration/README.md#open-checks-on-the-vehicle).

**Unresolved by this decision**

- The exact ESP-NOW packet format is specified only functionally, not at byte
  level. Tracked in [`docs/02-firmware/`](../02-firmware/README.md#open-items).
