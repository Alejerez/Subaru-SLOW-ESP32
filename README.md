# Subaru-ESP32-SLOW

### **S**SM2 **L**ink **O**ver **W**ireless

**Retromod instrumentation and speed-based central locking for a Subaru Legacy 3.0R (BL/BP chassis, EDM), built from ESP32 nodes linked by ESP-NOW.**

The car's OEM clock display is replaced by a monochrome OLED that polls the ECU
over **SSM2** on the K-line; a second, physically separate node next to the BIU
locks the doors above 20 km/h and unlocks them at a standstill. The nodes share no
wiring — only a radio link.

This repository is the engineering record: schematic-level design with exact
component values, pin maps, board layouts, firmware behaviour specification,
installation procedure, and the reasoning behind each decision. Prototype
revision **v0.1**; the hardware is specified and being sourced, the firmware is
specified but not yet written.

Start at [`docs/00-concept/README.md`](docs/00-concept/README.md).

*The name is a backronym, and an accurate one: an SSM2 link is exactly what
travels over the air between the nodes. That it also describes a 3.0R is a
coincidence nobody is obliged to accept.*

![System architecture](docs/01-hardware/diagrams/01-system-architecture.png)

---

## The constraint that drives everything: this is a retromod

**No colour screens. No IPS or TFT panels. Nothing that looks like an aftermarket
part.** The car must read as stock to anyone who did not install this.

That is not decoration — it is the top-level requirement, and it decides most of
the hardware:

| Retromod requirement | What it forces in the design |
| --- | --- |
| No colour / IPS / TFT display | Monochrome **OLED SSD1322**, 256×64, amber, behind the original red filter |
| Keep the OEM clock position | Board must fit the clock housing — hence the 11 × 27 hole carrier and the 90° header row |
| Reuse the OEM frame and bezel | The OLED is retained by a 3D-printed bezel inside the original housing, not by its own pins |
| Reuse OEM buttons | 4 existing buttons drive the gauge UI; the auto-lock ON/OFF is an **unused OEM switch**, not a new one |
| Reuse the original trip-computer position | Same bay, same viewing angle, same night-time illumination behaviour (ILL input follows the dash rheostat) |
| Fully reversible | Everything hangs off an i59 pass-through adapter and latching connectors; unplug it and the car is stock |

The auto-lock ON/OFF control is a good example: rather than drilling a new
button, it reuses the **windscreen-wiper de-icer switch** — a North-American
market option this EDM car does not have, so the switch position exists in the
console but does nothing. See [ADR 0003](docs/decisions/0003-onoff-button-direct-to-node-a.md).

![The unused OEM switch, marked in red](docs/01-hardware/photos/oem-switch-panel.jpg)

The gauge controls are the OEM buttons themselves. A donor unit was taken apart to
find out how they are built: contact pads on the OEM board, closed by a conductive
rubber pad — an ordinary dry contact an ESP32 input reads directly, with no new
buttons to design or fit. See
[ADR 0004](docs/decisions/0004-reuse-oem-contact-pad-buttons.md).

![The OEM board, with the button contact pads outlined in red](docs/01-hardware/photos/donor-pcb-contact-pads.jpg)

## Why ESP32, and why separate nodes

The ESP32 was chosen primarily for **ESP-NOW** — a connectionless peer-to-peer
protocol on the 2.4 GHz PHY needing no router, no pairing infrastructure and no
association. That single capability is what makes the architecture modular:

- **The gauge and the locking function are electrically unrelated** and live in
  different parts of the car (centre console vs. A-pillar / BIU). Splitting them
  avoids a long harness between the two and decouples their failures.
- **Speed is measured once and shared.** Node B already reads the ECU over SSM2,
  so vehicle speed comes from there and travels to Node A by radio — no VSS tap,
  no signal conditioning ([ADR 0002](docs/decisions/0002-speed-over-ssm2-not-vss.md)).
- **Growth is by adding nodes, not by adding wires.** The link is a **star** with
  Node B as the hub, and a third node —
  [**Node C**](docs/01-hardware/node-c-sensors.md), an analogue sensor front end —
  is designed for v0.3. Nodes are optional by default: the system degrades
  gracefully when one is not fitted
  ([ADR 0006](docs/decisions/0006-node-c-analogue-front-end.md)).

The ESP32 also brings enough on-chip peripherals for every role (UART for the
K-line, SPI for the OLED, I²C for the RTC and the sensor ADCs) on a single 3.3 V
part.

## Scope

**Locked for the first build** — nothing else is being designed until this works
in the car:

1. SSM2 acquisition over the K-line
2. Monochrome OLED gauge in the OEM clock position
3. Integration with the existing OEM buttons
4. Speed-based automatic central locking
5. **OTA firmware update over Wi-Fi**, in a deliberate maintenance mode
   ([ADR 0005](docs/decisions/0005-ota-in-maintenance-mode.md)) — Node A lives
   behind the A-pillar trim, and v0.1 is the phase with the most firmware
   iterations

Everything beyond that is planned in [`ROADMAP.md`](ROADMAP.md), tiered across
v0.2 (firmware only), v0.3 (new ESP-NOW nodes) and v0.4 (trackday mode), with the
items that were considered and rejected recorded alongside the ones that were
kept.

## Repository layout

```
.
├── docs/
│   ├── 00-concept/        Purpose, architecture, design rationale, status
│   │   └── source/        Original v0.1 design document (HTML, Spanish), kept verbatim
│   ├── 01-hardware/       Component catalogue, BOM, each node, wiring, figures, photos
│   ├── 02-firmware/       Link topology and behavioural specification
│   ├── 03-software/       Host-side / tooling notes (empty at v0.1)
│   ├── 04-integration/    Install sequence, multimeter checklist, open vehicle checks
│   ├── decisions/         Architecture decision records (why, not just what)
│   └── references.md      Datasheets, standards, prior art and forum sources
├── CHANGELOG.md           Versioned, dated release notes
├── firmware/              Node firmware — not yet written
├── hardware/              KiCad / EasyEDA project — the PCB track
├── software/              Supporting host software
├── scripts/               Figure generator (source of truth for every diagram)
├── ROADMAP.md             Locked v0.1 scope, and the tiered plan beyond it
├── CONTRIBUTING.md        Branch and review workflow
└── SETUP-GITHUB.md        How to create the repo and finish the licence, from scratch
```

## Figures

Every figure in `docs/01-hardware/diagrams/` is generated by
[`scripts/generate_diagrams.py`](scripts/generate_diagrams.py) — that script is
the editable source, and only the rendered PNGs are committed. They are drawn
dark-mode native, and the renderer refuses to pass silently: it checks every
element against the viewBox and every label against every other label. See
[`docs/01-hardware/diagrams/`](docs/01-hardware/diagrams/README.md).

## Prior art and credits

This project stands on published work by other people. It is a different design
— separate ESP32 nodes on ESP-NOW rather than a single Arduino — but the SSM2
groundwork and the "put a gauge in the clock pod" idea are not original here.

**Repositories** — [Obeisance/SubaruSSMClockPodMod](https://github.com/Obeisance/SubaruSSMClockPodMod),
the closest published analogue and the direct inspiration for the clock-pod
approach · [matprophet/subduino](https://github.com/matprophet/subduino) ·
[starlingcrossgte-svg/PROTOCOL](https://github.com/starlingcrossgte-svg/PROTOCOL) ·
[hrdwrbob/eingauge](https://github.com/hrdwrbob/eingauge) ·
[rpkish/Subduino-SSM](https://github.com/rpkish/Subduino-SSM).

**Forum work** — *"Clock pod mod with Subarb Select Monitor ECU polling and
Arduino"* by **Obeisance** on ClubWRX, ten-plus pages of build log behind the
first repository above; and *"Detailed SSM to Can-bus Convertor DIY"* by
**Ajzride** on The Factory Five Forum.

What each one is, what language it is in, its licence, and which have been
verified: [`docs/references.md`](docs/references.md).

## Use of AI

**Parts of this repository were produced with AI assistance (Claude, by
Anthropic).** Being specific about what that means:

- **Documentation:** the English documentation in `docs/` was drafted, structured
  and translated with Claude, from a Spanish-language design document written by
  the project author. The engineering content — architecture, component
  selection, values, pin assignments, installation procedure — is the author's.
- **Figures:** the diagram generator in `scripts/` was written with Claude, and
  the figures it produces were redrawn from hand-made SVGs in that original
  document.
- **Firmware and software:** AI assistance is expected to be used for the
  implementation in `firmware/` and `software/` as well, once it is written.

Neither the design decisions nor the measurements are AI-generated. Where a fact
could not be verified, the documentation says so explicitly rather than
guessing — see the open items in
[`docs/04-integration/README.md`](docs/04-integration/README.md#open-checks-on-the-vehicle).

## Licence

Dual-licensed, strong copyleft on both sides:

- **Hardware** (schematics, layouts, mechanical): **CERN-OHL-S v2** —
  [`LICENSE-HARDWARE.txt`](LICENSE-HARDWARE.txt), full text included.
- **Firmware and software**: **GPL-3.0-or-later** —
  [`LICENSE-SOFTWARE.txt`](LICENSE-SOFTWARE.txt). SPDX identifier is set; the
  full text still has to be inserted from an authoritative source, see
  [`SETUP-GITHUB.md`](SETUP-GITHUB.md) section 5.

### Third-party material — one exception

**[`docs/01-hardware/reference/`](docs/01-hardware/reference/README.md) contains
Subaru factory wiring diagrams. They are not the author's work and neither licence
above covers them.** They are included because the OEM circuits are what make the
design verifiable — which i59 pins are free, how the reused switch is wired
internally, and why unplugging the adapter really does restore the car. Anyone
redistributing or forking this repository should read the notice in that directory
and evaluate it for themselves; it also documents how to substitute redrawn
schematics if that is preferable, at no technical cost to the project.

## Status and next steps

- [ ] Complete `LICENSE-SOFTWARE.txt` with the official GPL-3.0 text
- [ ] Close the seven v0.1 [open checks on the vehicle](docs/04-integration/README.md#open-checks-on-the-vehicle) — they are measurements, not assumptions
- [ ] Define the ESP-NOW packet format before Node C is built
- [ ] Write the firmware for Nodes A and B from [`docs/02-firmware/`](docs/02-firmware/README.md)

