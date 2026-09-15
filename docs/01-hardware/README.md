# 01 — Hardware

Components, per-stage values, pin maps, wiring and assembly. Purpose and
architecture are in [`docs/00-concept/`](../00-concept/README.md); behaviour is in
[`docs/02-firmware/`](../02-firmware/README.md). This page owns the **catalogue and
the BOM** — what each part is and how many. Why a part was chosen is in the
[design rationale](../00-concept/README.md#design-rationale) or in a
[decision record](../decisions/README.md).

- [`node-b-gauge.md`](node-b-gauge.md) — Node B (gauge, hub): stages, values, schematics, layout, pin map
- [`node-a-locking.md`](node-a-locking.md) — Node A (locking): stages, values, schematics, layout, pin map
- [`node-a-build.md`](node-a-build.md) — Node A **bench build**: hole-by-hole placement, the 22 solder-side jumpers, soldering order and test points
- [`node-b-build.md`](node-b-build.md) — Node B **bench build**: both boards, hole-by-hole placement, the 64 solder-side jumpers, soldering order and test points
- [`node-c-sensors.md`](node-c-sensors.md) — Node C (analogue front end): channel architecture, sensors, bulkhead connector — **v0.3, not built**
- [`assembly-and-wiring.md`](assembly-and-wiring.md) — i59 adapter, connectors, carrier board, cable schedule, consumables and tools
- [`diagrams/`](diagrams/) — the twenty figures (PNG, dark-mode native); regenerate with [`scripts/generate_diagrams.py`](../../scripts/generate_diagrams.py)
- [`reference/`](reference/) — factory wiring diagrams, **outside this repository's licences**
- [`photos/`](photos/) — reference photographs of the vehicle's OEM parts

The KiCad / EasyEDA project lives in `/hardware` at the repository root, not here. The perfboard-to-PCB migration is a [parallel hardware track](../../ROADMAP.md#hardware-track-perfboard-to-pcb), not a feature version.

## Component catalogue

Quantities are for the **v0.1 build: Nodes A and B**. Some parts are used on both;
each node's stage tables give the per-node detail.

- **ESP32 DevKit V1 ×2** — *the brain of each node.* WROOM-32, 3.3 V logic, Wi-Fi/BT (used for ESP-NOW). Powered with 5 V on its 5V pin.
- **OLED SSD1322 3.12" ×1** — *the display.* 256×64 mono, SPI, 3.3 V. Active area ≈79 × 21 mm, ≈6 mm deep. **Draws about 310 mA typical / 340 mA maximum at 3.3 V** with the panel supply generated on the module (Newhaven NHD-3.12-25664UCY2, the reference design these clone). That number sizes Node B's whole supply — [ADR 0008](../decisions/0008-node-b-runs-on-one-33-v-rail.md) — and it has not yet been measured on the module that will actually be fitted. Amber or white is [`OC-05`](../04-integration/README.md#open-checks-on-the-vehicle).
- **RTC DS3231 ×1** — *timekeeping with the key out.* I²C, own cell. TCXO **±2 ppm over 0 to +40 °C, ±3.5 ppm over the full range** — and that is the DS3231SN; cheap ZS-042 boards are often fitted with a DS3231M (MEMS, ±5 ppm) or a counterfeit, so check the marking. Fit a **CR2032** and disable the module's trickle charger: at VCC = 3.3 V it cannot recharge an LIR2032 anyway, and Li-ion coin cells are not rated for a 70 °C console.
- **L9637D K-line transceiver ×1** — *12 V K-line ↔ 3.3 V UART.* SO-8; **no breakout exists for this part**, so it goes on a generic **SOIC-8 → DIP-8 adapter** and R7/C8/C9/C10 are fitted as discretes. Pinout must be read off ST's datasheet, Doc ID 1765, before soldering.
- **Recom R-78E5.0-1.0 ×1** — *Node A's 12→5 V supply,* because its relay coil needs 5 V. Encapsulated switcher, 7805 drop-in (IN·GND·OUT), **8–28 V in**, 5.0 V / 1 A, 85–93 % efficient [5].
- **Recom R-78E3.3-1.0 ×1** — *Node B's 12→3.3 V supply.* Same package and pinout, **7–28 V in**, 3.3 V / 1 A, 330 kHz. Node B has no 5 V rail at all and its DevKit is fed on the `3V3` pin — [ADR 0008](../decisions/0008-node-b-runs-on-one-33-v-rail.md). **Maximum capacitive load on the output of either variant is 220 µF**, which is why the reservoirs are 100 µF and not 470 µF.
- **2-channel relay module ×1** — *pulses the BIU lines.* Opto-isolated, 5 V coil, 10 A contacts. One channel locks, the other unlocks.
- **Schottky, in series with +12 V ×2** — **SB1100** (1 A, 100 V, DO-41) is the specified part: 100 V of reverse rating, because the TVS sits behind it and cannot protect it from negative transients, and 0.8 mm leads that fit a perfboard. SS34 (SMA) works if surface-mount is acceptable; **1N5822 does not** — its DO-201AD leads are 1.2–1.3 mm against 1 mm holes.
- **Unidirectional TVS ×2** — **P6KE20A** (DO-15) is the specified part: V<sub>RWM</sub> 17.1 V, clamping ~27.7 V, which is the first value in this design that stays under the buck's 28 V input maximum. SMAJ18A (SMA) clamps at 29.2 V and is the surface-mount alternative; **P6KE18A is not a substitute** — its standoff is 15.3 V, only 0.9 V above a 14.4 V charging rail.
- **Electrolytics — 100 µF, not 470 µF, and 105 °C** — 2× 100 µF/35 V (the input reserve on each node) and 2× 100 µF/16 V (the output reservoir on each). **470 µF exceeds the Recom's 220 µF maximum capacitive load**, and an 85 °C part at a 70 °C console ambient is a five-year component where a 105 °C / ≥2000 h part is a forty-year one. Ø6.3 keeps them clear of the connector shells. The 470 µF parts already bought become spares.
- **Ceramics — the dielectric is part of the specification.** ~14× **100 nF X7R** (three of them 50 V, on nets a TVS can clamp to 27.7 V), 1× **1 nF C0G/NP0** (the K-line filter, where the value is a spec rather than a target), 1× **1 µF X7R** (the ILL filter), 1× **10 µF X7R** (B-GAUGE's decoupling at the module's 3V3 pin). A Y5V part of the same marking loses up to **82 %** of its capacitance by −30 °C, which is exactly when the crank transient arrives.
- **Resistors** — 10k ×6, 3.3k ×3, 20k ×2, 510 Ω ×2, as an assortment. The v0.1 build uses **both 20 kΩ** (the upper leg of each of Node B's dividers), **one 3.3 kΩ and one 10 kΩ** (their lower legs) and **one 510 Ω** (the K-line pull-up). Sizes are not interchangeable: R3–R6 are **⅛ W** so they fit a 2-pitch footprint, and **R7 is ½ W** because it drops 0.26 W whenever the K bus is held dominant. Node A uses none since the ignition dividers were removed in v0.1.7.
- **BAT85 clamp diodes ×6** — *the second line of defence* on every divided input. The v0.1 build uses **two**, both on Node B. They clamp at 3.3 V + 0.32 V = **3.62 V**, which is the ESP32's absolute maximum rather than a margin below it: the resistors are the protection, and the clamps are what catches a fault the resistors did not anticipate. Do not reduce R3 or R5 on the assumption that the diodes will cope.
- **iWire i59 connectors (1 male + 2 female)** — build the gauge's reversible adapter. **Posi-Tap** as needed for reversible joints to car wires.
- **1 A fuse + holder ×2** — on every 12 V feed, no exceptions. Each node draws 215–250 mA, so 1 A is three times the load and half the fault current of the 2 A this project used to specify; a 2 A fuse carries a 1.9 A chafe fault indefinitely. **Slow-blow (T)**: the inrush into 100 µF is I²t ≈ 0.02 A²s, nowhere near a 1 A time-lag fuse's melting I²t, but a fast fuse is still the wrong characteristic for a capacitive load.

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
| RTC DS3231 | module + **CR2032** (not LIR2032) | 1 | $2–3k CLP | CL retail |
| L9637D, SO-8 | K-line ISO 9141 | 1 | US$4–10 | Mouser / Ali |
| SOIC-8 → DIP-8 adapter | unpopulated, + 2 × 4 male pins | 1 | US$1 | Ali |
| Buck **Recom R-78E5.0-1.0** | 5 V / 1 A, in 8–28 V — **Node A only** | 1 | US$6–9 | Mouser / DigiKey |
| Buck **Recom R-78E3.3-1.0** | 3.3 V / 1 A, in 7–28 V — **Node B only** | 1 | US$6–9 | Mouser / DigiKey |
| 2-ch relay module | opto, 5 V coil, 10 A | 1 | $4–6k CLP | CL retail |
| Schottky **SB1100** | 1 A / 100 V, DO-41 axial | 2 | $1k | CL retail / Ali |
| TVS **P6KE20A** | unidirectional 600 W, DO-15 axial | 2 | $1k | Ali / Mouser |
| Electrolytics | **100 µF/35 V and 100 µF/16 V, 105 °C, Ø6.3** | 4 | $2k | CL retail |
| Ceramics | **100 nF X7R ×14** (3 of them 50 V), **1 nF C0G ×2**, **1 µF X7R ×2**, **10 µF X7R ×1** | set | $2k | CL retail |
| Resistors | 10k ×6, 3.3k ×3, 20k ×2, 1k ×2 — ⅛ W, and **20k/10k as 1 % metal film**; 510 Ω ×2, **one of them ½ W metal oxide** | set | $2k | CL retail |
| Clamp diodes | BAT85 ×6 | set | $2k | CL retail / Ali |
| Fuses + holders | **1 A** inline, **slow-blow (T)** | 2 | $2k | auto parts |
| i59 connectors | 1 male + 2 female | 3 | US$5–12 ea | iWire |
| **Double-sided perfboard** (carrier) | FR4 2.54 mm, 5-size kit + M/F headers — **three 3 × 7 cm boards (11 × 27 holes): Node A, B-GAUGE, B-PWR** | 1 kit | US$10–15 | [Amazon kit](https://www.amazon.com/Soldering-Electronic-Compatible-Ar-duino-Connector/dp/B0948VC6P4) / Ali / ML |
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

**Every board in this project is 3 × 7 cm — 11 × 27 holes at 2.54 mm pitch.**
Measured by the project author in v0.1.8; Node A uses one, Node B uses two.

The source document contradicted itself, and the contradiction is recorded because
it is easy to reintroduce: its BOM said "7 × 9 cm for Node B, 5 × 7 cm for Node A"
while the layout figures for *both* drew a 3 × 7 cm board — which at 2.54 mm pitch
is exactly the 11 × 27 grid the Node B plan is titled with. The BOM row was wrong.

The figures ([Fig. 5](node-b-gauge.md#grid-plan),
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
