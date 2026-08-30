# Photographs

Reference photographs taken by the project author. Working shots from the
development phase — good enough to establish fact, not presentation quality.
They will be retaken properly once the parts are final.

Stored as JPEG: these are photographs, and PNG costs roughly ten times the size
for no visible gain. The generated figures in [`../diagrams/`](../diagrams/) stay
PNG, where it does matter.

## The car's own unit

| File | Subject |
| --- | --- |
| `oem-switch-panel.jpg` | Switch panel to the left of the steering wheel. Outlined in red: the unused windscreen-wiper de-icer switch — a North-American-market option this EDM car does not have — repurposed as the auto-lock ON/OFF control. See [ADR 0003](../../decisions/0003-onoff-button-direct-to-node-a.md). |
| `clock-unit-front.jpg` | The clock / trip-computer unit out of the dash. Confirms the button layout the firmware assumes: **DISP** at bottom left, **− +** rocker and **SET** at the right. |
| `clock-bay-in-dash.jpg` | The bay in the centre console, outlined in red — between the upper storage compartment and the head unit. This is the position the retromod constraint requires the gauge to keep. |

## Donor unit (teardown)

A **second unit of the same generation and housing, in the base clock-only trim**
(one button fewer), was taken apart purely for investigation. It is *not* the unit
going into the car — the car keeps its trip-computer variant. Anything measured on
the donor has to be re-confirmed on the real unit before it is treated as final.

| File | Subject |
| --- | --- |
| `donor-pcb-contact-pads.jpg` | The OEM board: VFD display, its driver, and — outlined in red — the **interdigitated contact pads** the buttons work against. This is the finding that makes button reuse practical; see [ADR 0004](../../decisions/0004-reuse-oem-contact-pad-buttons.md). |
| `donor-lens-backlit.jpg` | The lens held against a white screen, in transmission. Shows a **red / burgundy filter band** across the display window, with smoked grey around it. |
| `donor-housing-lens-layers.jpg` | The housing at an angle: outer smoked lens, and the reddish inner panel behind it. Shows the internal depth available for the carrier board and the OLED. |

> **Open point on the display filter.** The two lens photographs read clearly red
> in transmission, while the unit installed in the car reads white when lit. Those
> two observations have not been reconciled — the donor is a different trim, so its
> lens may not be the same part. This decides whether the OLED should be amber (as
> the BOM currently specifies) or white, so it is tracked as an
> [open check](../../04-integration/README.md#open-checks-on-the-vehicle) rather
> than assumed either way.
