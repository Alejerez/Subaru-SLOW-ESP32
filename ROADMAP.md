# Roadmap

## Locked scope — first build (v0.1)

Nothing outside this list is being designed, wired or costed until it works in
the car. This is deliberate: the point of v0.1 is to prove the SSM2 link, the
display integration and the locking logic against real vehicle wiring.

1. **SSM2 acquisition** — poll the ECU over the K-line (ISO 9141-2, 10400 baud)
   through an L9637D transceiver on OBD pin 7.
2. **Monochrome OLED gauge** — SSD1322 256×64 in the OEM clock position, behind
   the original red filter, retained by a 3D-printed bezel.
3. **OEM button integration** — the four existing buttons drive page navigation
   and settings; the unused wiper de-icer switch becomes the auto-lock ON/OFF.
4. **Speed-based automatic central locking** — lock above 20 km/h, unlock at a
   standstill, via two relay pulses into BIU pins 15 and 29.

Completion criteria are the install sequence and multimeter checklist in
[`docs/04-integration/README.md`](docs/04-integration/README.md), plus the six
open vehicle checks listed there.

## Additional features — list in progress

**A list of additional features is currently being drawn up and is not part of
this revision.** It will be added here once it exists. Deliberately empty rather
than filled with speculation.

Two items were already named in the v0.1 source document as future work, and are
recorded here so they are not lost — they are *not* a commitment, and they are
not part of the locked scope above:

- **TPMS** — surface aftermarket tyre-pressure data as a gauge page.
- **Extended data logging** — a Raspberry Pi with a Tactrix OpenPort 2.0 logging
  alongside the gauge, rather than through it.

Anything added to this list should say which node it lands on, or whether it
becomes a new ESP-NOW node of its own — that is the whole reason the
architecture is split (see [ADR 0002](docs/decisions/0002-speed-over-ssm2-not-vss.md)
and the ESP-NOW rationale in the [README](README.md#why-esp32-and-why-two-nodes)).

## v0.2 — from perfboard to PCB

Once v0.1 is validated in the vehicle:

- Move both carriers from perfboard to a **formal PCB** (KiCad or EasyEDA,
  Gerbers under `hardware/`), keeping the modules socketed and the edge
  connectors latching.
- Fabrication options considered in the source document: local (CAEM, PCB Chile)
  or JLCPCB / PCBWay; turnkey assembly (Enerful, KELTRONIC, CIGA) if the board is
  worth not hand-populating.
- Re-verify the enclosure fit against the OEM clock housing before committing to
  a board outline — the retromod constraint does not relax at v0.2.

## Documentation and tooling

- [ ] Insert the official GPL-3.0 text into `LICENSE-SOFTWARE.txt`
      (see [`SETUP-GITHUB.md`](SETUP-GITHUB.md) §5)
- [ ] Add CI that regenerates the figures when `scripts/generate_diagrams.py`
      changes — the generator and its overflow/collision checks already run
      headless, so this is mostly workflow plumbing. Not added yet because it
      has never been executed in a real pipeline.
- [ ] Document the toolchain and flashing procedure for both nodes once the
      firmware exists.
