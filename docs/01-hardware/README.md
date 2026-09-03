# 01 — Hardware

Components, per-stage values, pin maps, wiring and assembly. Purpose and
architecture are in [`docs/00-concept/`](../00-concept/README.md); behaviour is in
[`docs/02-firmware/`](../02-firmware/README.md). This page owns the **catalogue and
the BOM** — what each part is and how many. Why a part was chosen is in the
[design rationale](../00-concept/README.md#design-rationale) or in a
[decision record](../decisions/README.md).

- [`node-b-gauge.md`](node-b-gauge.md) — Node B (gauge, hub): stages, values, schematics, layout, pin map
- [`node-a-locking.md`](node-a-locking.md) — Node A (locking): stages, values, schematics, layout, pin map
- [`node-c-sensors.md`](node-c-sensors.md) — Node C (analogue front end): channel architecture, sensors, bulkhead connector — **v0.3, not built**
- [`assembly-and-wiring.md`](assembly-and-wiring.md) — i59 adapter, connectors, carrier board, cable schedule, consumables and tools
- [`diagrams/`](diagrams/) — the eleven figures (PNG, dark-mode native); regenerate with [`scripts/generate_diagrams.py`](../../scripts/generate_diagrams.py)
- [`reference/`](reference/) — factory wiring diagrams, **outside this repository's licences**
- [`photos/`](photos/) — reference photographs of the vehicle's OEM parts

The KiCad / EasyEDA project lives in `/hardware` at the repository root, not here. The perfboard-to-PCB migration is a [parallel hardware track](../../ROADMAP.md#hardware-track-perfboard-to-pcb), not a feature version.

## Component catalogue

Quantities are for the **v0.1 build: Nodes A and B**. Some parts are used on both;
each node's stage tables give the per-node detail.

- **ESP32 DevKit V1 ×2** — *the brain of each node.* WROOM-32, 3.3 V logic, Wi-Fi/BT (used for ESP-NOW). Powered with 5 V on its 5V pin.
- **OLED SSD1322 3.12" ×1** — *the display.* 256×64 mono, SPI, 3.3 V. Active area ≈79 × 21 mm, ≈6 mm deep. Amber or white is [`OC-05`](../04-integration/README.md#open-checks-on-the-vehicle).
- **RTC DS3231 ×1** — *timekeeping with the key out.* I²C, own cell, TCXO ±2 ppm.
- **L9637D K-line transceiver ×1** — *12 V K-line ↔ 3.3 V UART.* On a breakout with labelled pads.
- **Recom R-78E5.0-1.0 ×2** — *12→5 V supply.* Encapsulated switcher, 7805 drop-in (IN·GND·OUT), **8–28 V in**, 5.0 V / 1 A out, 85–93 % efficient [5]. Budget alternative: MP1584EN, which must be trimmed to 5.00 V.
- **2-channel relay module ×1** — *pulses the BIU lines.* Opto-isolated, 5 V coil, 10 A contacts. One channel locks, the other unlocks.
- **Schottky SS34 ×2** — *reverse-polarity protection,* in series with +12 V.
- **TVS SMAJ18A ×2** — *transient absorber,* 12 V rail to ground.
- **Capacitors** — 4× 470 µF (2× 35 V + 2× 16 V) reserve and Wi-Fi spikes, ~10× 100 nF HF filtering, 2× 1 nF, 2× 1 µF.
- **Resistors** — 10k ×6, 3.3k ×3, 20k ×2, 510 Ω ×2. The pairs scale 12 V and 5 V into the ESP32's 3.3 V range.
- **BAT85 clamp diodes ×6** — *the safety ceiling* on every divided input.
- **iWire i59 connectors (1 male + 2 female)** — build the gauge's reversible adapter. **Posi-Tap** as needed for reversible joints to car wires.
- **2 A fuse + holder ×2** — on every 12 V feed, no exceptions.

### Node C parts — v0.3, not for the first build

- **ESP32 DevKit V1 ×1** — a third node, same part as the other two.
- **ADS1115 ×n** — 16-bit I²C ADC, programmable gain, four addresses on one bus, **differential inputs**. Count follows [`OC-11`](../04-integration/README.md#open-checks-on-the-vehicle).
- **PT1000 surface RTDs ×2** — caliper temperature, 3-wire, to ~250 °C, bonded with high-temperature adhesive.
- **NTC sensors ×3** — radiator inlet and outlet, ambient air.
- **Float sender ×1** — coolant level in the catch tank; reed-chain or continuous resistive. Needs a bung welded to the tank.
- **Sealed bulkhead connector ×1** — the environmental boundary at the firewall, specified with spare pins.

## BOM with indicative prices

CLP = Chilean retail; USD = AliExpress/Mouser. No VSS parts — removed, see
[ADR 0002](../decisions/0002-speed-over-ssm2-not-vss.md). Passives are listed
with exact values.

| Item | Value / spec | Qty | ≈ Price | Where |
| --- | --- | --- | --- | --- |
| ESP32 DevKit V1 | WROOM-32, 30 pin | 2 | $7k CLP ea | CL retail / Ali |
| OLED SSD1322 3.12" | 256×64 SPI amber — colour still open, see below | 1 | US$18–28 | Ali / Amazon |
| RTC DS3231 | module + coin cell | 1 | $2–3k CLP | CL retail |
| L9637D breakout | K-line ISO 9141 | 1 | US$4–10 | Ali / Mouser |
| Buck **Recom R-78E5.0-1.0** | encapsulated switcher 5 V/1 A · drop-in 7805 · in 8–28 V (budget alt: MP1584EN) | 2 | US$6–9 ea | Mouser / DigiKey |
| 2-ch relay module | opto, 5 V coil, 10 A | 1 | $4–6k CLP | CL retail |
| Schottky SS34 | 3 A / 40 V | 2 | $1k | CL retail / Ali |
| TVS SMAJ18A | unidirectional 400 W | 2 | $1k | Ali / Mouser |
| Electrolytics | 470 µF/35 V and 470 µF/16 V | 4 | $2k | CL retail |
| Ceramics | 100 nF ×10, 1 nF ×2, 1 µF ×2 | set | $2k | CL retail |
| Resistors | 10k ×6, 3.3k ×3, 20k ×2, 510 Ω ×2 | set | $2k | CL retail |
| Clamp diodes | BAT85 ×6 (or 5.1 V zener) | set | $2k | CL retail / Ali |
| Fuses + holders | 2 A inline | 2 | $2k | auto parts |
| i59 connectors | 1 male + 2 female | 3 | US$5–12 ea | iWire |
| **Double-sided perfboard** (carrier) | FR4 2.54 mm, 5-size kit + M/F headers — **use 3 × 7 cm (11 × 27 holes) for both** | 1 kit | US$10–15 | [Amazon kit](https://www.amazon.com/Soldering-Electronic-Compatible-Ar-duino-Connector/dp/B0948VC6P4) / Ali / ML |
| Wire, heatshrink, Posi-Tap, enclosure, grommets | assembly | — | $15k CLP | local |

*Prices are as recorded in the v0.1 source document. They have not been verified
or refreshed.*

**Node C — v0.3, do not buy for the first build.** No prices recorded yet.

| Item | Value / spec | Qty |
| --- | --- | --- |
| ESP32 DevKit V1 | WROOM-32, 30 pin | 1 |
| ADS1115 breakout | 16-bit I²C ADC, differential | per `OC-11` |
| PT1000 surface RTD | to ~250 °C, 3-wire, adhesive-bonded | 2 |
| NTC sensor | radiator in / out, ambient | 3 |
| Coolant float sender | reed-chain or continuous resistive, unpressurised | 1 |
| Sealed bulkhead connector | with spare pins | 1 |

### Display colour: amber or white, still open

The BOM specifies **amber**, justified in the source document as passing better
through a red OEM filter. That justification is now in question: the donor unit's
lens reads clearly red in transmission, but the unit installed in the car reads
**white** when lit, as does the head unit below it — the red items on that part of
the dash are button legends and knob rings, not displays.

![The donor unit's lens against a white screen](photos/donor-lens-backlit.jpg)

The donor is the base clock-only trim, so its lens may not be the same part. Until
that is settled on the car, **the BOM row above is provisional** —
[`OC-05`](../04-integration/README.md#open-checks-on-the-vehicle).

### Perfboard size: correction to the source document

**Nodes A and B use a 3 × 7 cm board — 11 × 27 holes at 2.54 mm pitch.** Confirmed
by the project author.

The source document contradicted itself, and the contradiction is recorded because
it is easy to reintroduce: its BOM said "7 × 9 cm for Node B, 5 × 7 cm for Node A"
while the layout figures for *both* drew a 3 × 7 cm board — which at 2.54 mm pitch
is exactly the 11 × 27 grid the Node B plan is titled with. The BOM row was wrong.

The figures ([Fig. 5](node-b-gauge.md#exact-plan-on-the-perfboard-grid),
[Fig. 9](node-a-locking.md#grid-plan)) are therefore the authority on board size,
and Node B's grid plan is the density check.

## Wire colour code

Used consistently across every figure and every stage table:

| Colour | Net |
| --- | --- |
| Yellow | +12 V |
| Copper / orange | +5 V |
| Red | +3.3 V |
| Grey | GND |
| Blue | Signal |
| Cyan | ESP-NOW (radio, no wire) |
