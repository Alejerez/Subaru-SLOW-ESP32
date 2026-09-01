# OEM reference material

Factory documentation consulted while designing this system, kept here because
several design decisions only make sense with the original circuit in front of
you — and because reproducing this project on another car means checking it
against the same drawings.

Stored as PNG, unlike the [photographs](../photos/README.md): these are line
drawings, and JPEG compression rings badly on sharp black-on-white edges.

| File | Circuit | What it establishes for this project |
| --- | --- | --- |
| `clock-circuit-clk-01.png` | **CLK-01** — clock (i59) | Which of the ten i59 pins the factory circuit uses and which are free, the existence of a serial link between the clock and the combination meter, and the four buttons switching to ground. Underpins the [i59 adapter](../assembly-and-wiring.md#i59-adapter-1-male--2-female) and the reversibility argument. |
| `wiper-deicer-circuit-wd-01.png` | **WD-01 / WI-12551** — wiper de-icer | The internal wiring of the push switch this project reuses: pins 1–2 a momentary contact, pins 8–9 an indicator LED. Underpins [Node A, Stage 4](../node-a-locking.md#stage-4--onoff-button-reused-oem-switch) and [ADR 0003](../../decisions/0003-onoff-button-direct-to-node-a.md). |

---

## Provenance and licence — please read

> **These are Subaru factory service documents. They are the property of their
> copyright holder, they are NOT the work of this project's author, and they are
> NOT covered by this repository's licences.**
>
> Neither **CERN-OHL-S v2** ([`LICENSE-HARDWARE.txt`](../../../LICENSE-HARDWARE.txt))
> nor **GPL-3.0-or-later** ([`LICENSE-SOFTWARE.txt`](../../../LICENSE-SOFTWARE.txt))
> extends to the contents of this directory. Any grant of rights those licences
> make over the rest of the repository stops at this folder.

They are reproduced here for **repair, diagnosis and reference purposes**:
understanding the OEM circuit is a prerequisite for reproducing this project
safely on the same vehicle, and for verifying that the modification really is
reversible rather than merely claimed to be.

**If you redistribute this repository, or fork it, this directory is your
responsibility to evaluate.** What is acceptable as reference material for repair
in one jurisdiction may not be in another.

If that becomes a problem, the fix is straightforward and costs the project
nothing: **replace each image with a redrawn schematic of only the relevant
portion** — the i59 pin functions, or the four switch terminals and what each
connects to. That is factual circuit information rather than a reproduction of
someone's document. The written descriptions in
[`assembly-and-wiring.md`](../assembly-and-wiring.md#i59-adapter-1-male--2-female)
and [`node-a-locking.md`](../node-a-locking.md#the-oem-circuit) already carry
everything the design actually depends on, so nothing technical is lost by making
that substitution.
