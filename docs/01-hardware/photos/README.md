# Photographs

Reference photographs taken by the project author. Working shots from the
development phase — good enough to establish fact, not presentation quality.

JPEG, because these are photographs; PNG would cost roughly ten times the size for
no visible gain. The generated figures in [`../diagrams/`](../diagrams/) stay PNG,
where it does matter.

This page is an **index**: what each file shows and which document relies on it.
The findings themselves live in those documents.

## The car's own unit

| File | Subject | Used by |
| --- | --- | --- |
| `oem-switch-panel.jpg` | Switch panel left of the steering wheel. Outlined in red: the unused wiper de-icer switch, repurposed as the auto-lock ON/OFF control | [ADR 0003](../../decisions/0003-onoff-button-direct-to-node-a.md) |
| `clock-unit-front.jpg` | The clock / trip-computer unit out of the dash. DISP bottom left, **− +** rocker and SET at the right | [Node B, Stage 5](../node-b-gauge.md#stage-5--display-clock-and-buttons) |
| `clock-bay-in-dash.jpg` | The bay in the centre console, outlined in red — the position the retromod constraint requires the gauge to keep | [Node B](../node-b-gauge.md#where-it-goes-in-the-car) |
| `coolant-catch-tank.jpg` | The 2 L welded catch tank that replaced the OEM expansion bottle. Cap outlet open to atmosphere, pressure function defeated — the tank is **not pressurised** | [Node C](../node-c-sensors.md#coolant-level--catch-tank) |

## Donor unit (teardown)

A **second unit of the same generation and housing, in the base clock-only trim**
(one button fewer), taken apart for investigation. It is *not* the unit going into
the car. Anything measured on it must be re-confirmed on the real unit —
[`OC-05`](../../04-integration/README.md#open-checks-on-the-vehicle) and
[`OC-08`](../../04-integration/README.md#open-checks-on-the-vehicle).

| File | Subject | Used by |
| --- | --- | --- |
| `donor-pcb-contact-pads.jpg` | The OEM board: VFD display, its driver, and — outlined in red — the **interdigitated contact pads** the buttons work against | [ADR 0004](../../decisions/0004-reuse-oem-contact-pad-buttons.md) |
| `donor-lens-backlit.jpg` | The lens against a white screen, in transmission: a **red / burgundy filter band** across the display window, smoked grey around it | [display colour](../README.md#display-colour-amber-or-white-still-open) |
| `donor-housing-lens-layers.jpg` | The housing at an angle: outer smoked lens, reddish inner panel, and the internal depth available for the carrier and the OLED | [Node B](../node-b-gauge.md#where-it-goes-in-the-car) |
