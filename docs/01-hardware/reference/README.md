# OEM reference material

Factory documentation consulted while designing this system. Kept here because
several design decisions only make sense with the original circuit in front of
you.

Stored as PNG, unlike the [photographs](../photos/README.md): these are line
drawings, and JPEG compression rings badly on sharp black-on-white edges.

| File | Subject |
| --- | --- |
| `wiper-deicer-circuit-wd-01.png` | Factory wiring diagram **WD-01 / WI-12551**, wiper de-icer circuit. Establishes the internal wiring of the push switch this project reuses — see [Node A, Stage 4](../node-a-locking.md#stage-4--onoff-button-reused-oem-switch) and [ADR 0003](../../decisions/0003-onoff-button-direct-to-node-a.md). |

## Provenance and licence

**These are Subaru factory service documents, reproduced here for repair and
reference purposes. They are not the project author's work and are not covered by
this repository's licences** — neither CERN-OHL-S v2 for the hardware nor
GPL-3.0-or-later for the software extends to them. They are included because
understanding the OEM circuit is a prerequisite for reproducing this project
safely on the same vehicle.

If that becomes a problem for redistribution, the fix is to replace the image
with a redrawn schematic of only the relevant portion — the four switch terminals
and what each connects to — which is factual circuit information rather than a
reproduction of the document. The written description in
[Node A, Stage 4](../node-a-locking.md#stage-4--onoff-button-reused-oem-switch)
already carries everything the project actually depends on, so nothing is lost by
doing that.
