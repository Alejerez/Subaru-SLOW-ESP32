# Node A — Central locking

ESP32 next to the BIU (Body Integrated Unit), A-pillar. Receives vehicle speed
from Node B over ESP-NOW and drives the relays that pulse the BIU's lock and
unlock lines.

Deliberately simple: power + ignition sensing + relays + one button. Speed
arrives by radio, so there is no VSS hardware at all
([ADR 0002](../decisions/0002-speed-over-ssm2-not-vss.md)). The auto-lock ON/OFF
switch lives physically on **this** node
([ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md)).

## Stages and exact values

### Stage 1 · Power (IG to 5 V)

Identical to [Node B's power stage](node-b-gauge.md#stage-1--power-ig-to-5-v).

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| F1 | Fuse | 2 A | series +12 V (IG) | protection |
| D1 | Schottky | SS34 | +12 V → VBAT | reverse polarity |
| D2 | TVS | SMAJ18A | VBAT → GND | transients |
| C1 | Electrolytic | 470 µF / 35 V | VBAT → GND | reserve |
| U1 | Switching regulator | Recom R-78E5.0-1.0 | VBAT → 5 V | fixed 12 V→5 V (7805 drop-in) |
| C3 | Electrolytic | 470 µF / 16 V | 5 V → GND | Wi-Fi spikes |

### Stage 2 · Ignition sensing

| Ref | Component | Value | Connection |
| --- | --- | --- | --- |
| R1 | Resistor | 10 kΩ | IG → node_IGN |
| R2 | Resistor | 3.3 kΩ | node_IGN → GND |
| D3 | Schottky clamp | BAT85 | node_IGN → 3.3 V |
| C5 | Ceramic | 100 nF | node_IGN → GND → GPIO34 |

### Stage 3 · Relays to the BIU

| Ref | Component | Control connection | Contacts |
| --- | --- | --- | --- |
| K1 | 2-channel relay module (5 V) | VCC→3.3 V · JD-VCC→5 V (jumper removed) · IN1→GPIO25 · IN2→GPIO26 | — |
| K1·CH1 | LOCK relay | GPIO25 | COM→BIU p15 · NO→GND |
| K1·CH2 | UNLOCK relay | GPIO26 | COM→BIU p29 · NO→GND |

> **Firing rule.** Each relay is energised for a **short pulse (≈0.4 s)**, never
> held. COM to the BIU wire, NO to ground: energising momentarily grounds the
> wire — a negative pulse — which locks or unlocks.

### Stage 4 · ON/OFF button (reused OEM switch)

A physical OEM switch already in the car, originally for the **windscreen-wiper
de-icer** — a North-American-market option this EDM car does not have — unused,
repurposed as the auto-lock toggle. Wired **directly to Node A**: it does not go
through Node B and does not travel over ESP-NOW. See
[ADR 0003](../decisions/0003-onoff-button-direct-to-node-a.md).

![The unused OEM switch, marked in red](photos/oem-switch-panel.jpg)

**Photo** — The switch panel to the left of the steering wheel. The button marked
in red is the unused wiper de-icer switch that becomes the auto-lock ON/OFF
control.

#### The OEM circuit

![Factory wiring diagram of the wiper de-icer circuit](reference/wiper-deicer-circuit-wd-01.png)

**Figure** — Factory wiring diagram WD-01 / WI-12551. The push switch is the
block outlined in red; its connector, **i78 (blue)**, is outlined at the bottom.
See [reference material](reference/README.md) for provenance and licensing.

In the factory circuit the switch does *not* drive the de-icer relay directly.
Two fuses feed the circuit — F/B no. 9 (constant, LB) to the relay contacts and
F/B no. 4 (ignition, GY) to the relay coil — and the relay's contact output (RY)
feeds both the heating element and the switch. The coil's return path goes to the
**Body Integrated Unit**, which is what decides to energise it; that is why the
BIU sits in the middle rather than the switch simply closing the coil circuit.

The switch itself is **two devices in one body**, and that is the finding that
matters here:

| Pin | Wire | Goes to | What it is |
| --- | --- | --- | --- |
| **1** | OrG | BIU pin A14 | switch contact, high side |
| **2** | B | chassis ground | switch contact, low side |
| **8** | RY | relay contact output | indicator LED, high side |
| **9** | B | chassis ground | indicator LED, low side |

So the button is a **momentary contact between pins 1 and 2** (confirmed by
inspection on this car — unlike the folding-mirror switch in the same console, it
does not latch), plus an **indicator LED between pins 8 and 9** that in the
factory circuit lights only when the de-icer element is actually energised, not
when the button is pressed.

#### What this gives the project

**The signal comes from pins 1 and 2, and nothing else.** Pin 2 is already at
chassis ground and pin 1 is a dry contact, which is exactly the topology this
stage specifies: `INPUT_PULLUP` on GPIO27 with the other side to ground. No
divider, no clamp, no conditioning — the switch's own factory ground closes the
circuit.

**The harness run already exists.** The OrG wire runs from the console to the
BIU, and the BIU is where Node A is installed. The wiring in this car is populated
even though the de-icer itself was never fitted, so this leg needs no new cable
pulled through the dash — see the [cable schedule](assembly-and-wiring.md#cable-lengths).

**The indicator LED is reusable as a tell-tale.** With no de-icer relay fitted,
pin 8 receives nothing and the LED never lights. Driven from Node A instead, it
becomes an OEM-looking status light *inside the OEM button* — the most retromod
outcome available, and something the design did not previously have. It signals
**DISABLED**, not ARMED: armed is the default and resets at every ignition-on, so
the state worth reminding you about is the one you chose deliberately, in the same
way a "traction control off" lamp works. A permanently lit lamp indicating normal
operation becomes invisible within a week.

> ⚠️ **Do not tap pin 1 in parallel with the BIU.** The BIU's own input and the
> ESP32's pull-up would share the node, and every press would be signalled to
> both. Even though the BIU has no de-icer to operate, "probably harmless" is not
> a standard to apply to a body control module. Disconnect OrG at the switch
> connector and run pin 1 to Node A on its own, which also keeps the modification
> fully reversible: plugging the OEM connector back restores the car.

| Ref | Component | Value | Connection | Function |
| --- | --- | --- | --- | --- |
| SW1 | OEM switch contact (i78 pins 1–2) | — | GPIO27 ↔ switch ↔ GND | momentary; toggles ARMED ⇄ DISABLED |
| LED1 | OEM indicator LED (i78 pins 8–9) | — | GPIO33 → pin 8 · pin 9 to GND | lit while DISABLED |

*No additional components on the switch contact: it uses the ESP32's internal
pull-up on GPIO27 (`INPUT_PULLUP`), the same approach the source document
specified for this option.*

> ⚠️ **Open check: the LED's electrical specification.** The factory diagram shows
> no discrete series resistor in the 8–9 path, so the current-limiting resistor is
> almost certainly inside the switch body, sized for 12 V. If so, driving that same
> circuit from a 3.3 V GPIO yields roughly 2 mA — dim, but a dashboard tell-tale at
> 2 mA is perfectly visible in a dark cabin, and it would need **no components at
> all** and no modification to the factory ground on pin 9.
>
> Establish on the bench, before designing any driver: LED polarity; whether an
> internal resistor exists and roughly its value (use a current-limited supply
> ramped from zero, not an ohmmeter — the diode makes resistance readings
> meaningless); and the actual brightness at 3.3 V judged in low light. If it is
> too dim, the fallback is a low-side N-channel MOSFET with pin 8 fed from Node A's
> protected 12 V rail, which costs one component and requires lifting pin 9 from
> its factory ground. **Replacing the OEM LED with a modern high-efficiency one is
> also on the table** and may be the better answer, since a twenty-year-old
> indicator LED is both dim by current standards and of unknown remaining life.
> Tracked in [`docs/04-integration/`](../04-integration/README.md#open-checks-on-the-vehicle).

## ESP32 pin map (Node A)

| Function | GPIO | Note |
| --- | --- | --- |
| Ignition sensing | 34 | ADC · Stage 2 |
| LOCK relay (IN1) | 25 | → BIU p15 |
| UNLOCK relay (IN2) | 26 | → BIU p29 |
| ON/OFF button | 27 | `INPUT_PULLUP` · reused OEM switch contact (i78 pins 1–2), see Stage 4 |
| Status tell-tale | 33 | output · OEM indicator LED (i78 pins 8–9), lit while DISABLED |
| Speed (receive) | — (radio) | ESP-NOW ← Node B |
| Mode confirmation (transmit) | — (radio) | ESP-NOW → Node B, to show on the OLED |

## Behaviour, schematics and layout

### Functional behaviour

Node A receives speed from Node B over ESP-NOW and drives the relays that pulse
the BIU lines. The ON/OFF button on GPIO27 is local to this node. The logic is a
simple state machine:

- **Start-up:** on power-up (IG on) the system starts **ARMED** by default.
- **Lock:** while ARMED, on reaching **v ≥ 20 km/h**, emit a lock pulse on CH1 →
  BIU pin 15.
- **Unlock:** while ARMED, on coming to a stop (**v = 0 km/h**), emit an unlock
  pulse on CH2 → BIU pin 29.
- **Re-locking** falls out of the cycle: if the car stops (unlock) and passes
  20 km/h again, it locks again. No door-ajar signal is read.
- **Disabling:** the physical button (GPIO27) toggles between ARMED and
  **DISABLED** on each press. While DISABLED it neither locks nor unlocks
  automatically. Disabling is valid **for that ignition cycle only**: switch off
  and on again and it starts ARMED.
- **User confirmation:** whenever the button changes the mode, Node A sends the
  change to Node B over ESP-NOW, which displays it on the OLED (e.g.
  `AUTO-LOCK: ARMED` / `AUTO-LOCK: DISABLED`) for a couple of seconds before
  returning to the previous page. See [`docs/02-firmware/`](../02-firmware/README.md).
- **Persistent indication:** the OEM indicator LED inside the button is lit while
  the system is DISABLED and dark while ARMED, so the exceptional state stays
  visible after the OLED message has gone.
- **Threshold:** 20 km/h, parameterised in firmware.

![Node A state machine](diagrams/06-node-a-state-machine.png)

**Fig. 6** — Node A state machine. State is not persisted; every ignition-on
starts ARMED.

### Interface schematic

![Node A interface](diagrams/07-node-a-interface.png)

**Fig. 7** — Node A interface. The relay module sits off the board with its screw
terminals. The ON/OFF button is wired straight to GPIO27 with the internal
pull-up; the ESP-NOW link carries speed inbound and the mode change outbound.

### Spatial layout

![Node A spatial layout](diagrams/08-node-a-spatial-layout.png)

**Fig. 8** — Node A spatial layout. Speed arrives over ESP-NOW with no cable; the
ON/OFF switch is wired directly to the node (Stage 4). The relay module sits off
the board with its terminals facing the BIU. IG is taken at the A-pillar.

### Grid plan

![Node A grid plan](diagrams/09-node-a-grid-plan.png)

**Fig. 9** — Node A grid plan. Far emptier than Node B: only the ESP32, the power
stage, one divider and the connectors — the relay module is external. The free
area is deliberate headroom for later I/O. Same 3 × 7 cm board as Node B — see
[perfboard size](README.md#perfboard-size-correction-to-the-source-document).

> **Pulse, not level.** Each relay is energised for a short pulse (≈0.4 s), never
> held. COM to the BIU wire, NO to ground: energising momentarily grounds the wire
> (a negative pulse), which locks or unlocks.
