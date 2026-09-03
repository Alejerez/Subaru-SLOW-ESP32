# Contributing

A small project: the author plus one or two trusted collaborators. The workflow
below is sized for that, not for a large open-source project.

## Branch and review

`main` is always in a state someone could build from. Work happens on branches
and reaches `main` through a pull request, even when you are the only person
working that day — the PR is where the reasoning gets written down.

```bash
git checkout -b hw/relay-stage
# ... changes ...
git add <files>
git commit -m "hw: specify the relay coil supply and jumper removal"
git push -u origin hw/relay-stage
```

Then open a pull request and merge after review.

Branch prefixes, matching the documentation structure:

| Prefix | For |
| --- | --- |
| `hw/` | Hardware: schematics, values, layout, BOM |
| `fw/` | Firmware for any node |
| `sw/` | Host-side software and tooling |
| `docs/` | Documentation, figures, decision records |
| `fix/` | Corrections to any of the above |

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/), with the
project's own type set: `feat:`, `fix:`, `docs:`, `hw:`, `fw:`, `sw:`, `chore:`.

The subject line says *what* changed. If the change involves a design decision —
something a reasonable person might have done differently — the *why* belongs in
a decision record, not in the commit body. See
[`docs/decisions/README.md`](docs/decisions/README.md) for when to write one.

## Releases and the changelog

Every push that changes meaning gets **one version, one date, one tag and one
[`CHANGELOG.md`](CHANGELOG.md) entry**. A typo fix or a reflow gets none. The
rules — version scheme, the allowed categories, and the line between what belongs
in the changelog and what belongs in a decision record — are stated at the top of
[`CHANGELOG.md`](CHANGELOG.md) itself.

```bash
git tag -a v0.1.6 -m "short description"
git push --tags
```

`git log` remains the fine-grained record; the changelog is the readable one.

## Who owns which topic

**Every fact has exactly one home.** Other documents link to it; they do not
restate it. This is the rule that keeps the repository from drifting into four
slightly different versions of the same paragraph — which it had done before
v0.1.5.

| Topic | Owner | Everyone else |
| --- | --- | --- |
| The retromod constraint | [`README.md`](README.md) | link |
| System architecture, why it is shaped this way | [`docs/00-concept/`](docs/00-concept/README.md) | link |
| Why a part or approach was chosen | the relevant [ADR](docs/decisions/README.md), or the [design rationale](docs/00-concept/README.md#design-rationale) | link — never re-argue |
| Component identity, quantity, price | [`docs/01-hardware/README.md`](docs/01-hardware/README.md) | link |
| Per-stage values, pin maps, layout | that node's own page | link |
| Physical build: adapter, connectors, carrier, cable schedule, tools | [`assembly-and-wiring.md`](docs/01-hardware/assembly-and-wiring.md) | link |
| Behaviour, state machines, timing, the ESP-NOW protocol | [`docs/02-firmware/`](docs/02-firmware/README.md) | link |
| What must be measured on the car | [`docs/04-integration/`](docs/04-integration/README.md#open-checks-on-the-vehicle), as `OC-nn` | cite the id |
| What is planned and what was rejected | [`ROADMAP.md`](ROADMAP.md) | link |
| What changed and when | [`CHANGELOG.md`](CHANGELOG.md) | — |
| Photographs and factory diagrams | the `photos/` and `reference/` indexes | caption + link |

Two corollaries worth stating outright:

- **A hardware page describes hardware.** If you find yourself writing a state
  machine or a timing rule in `docs/01-hardware/`, it belongs in
  `docs/02-firmware/`.
- **The changelog says what changed, not why.** The *why* is an ADR. An entry that
  re-argues a decision is a duplicate that will fall out of date on its own.

## Figures

Never hand-edit a PNG in `docs/01-hardware/diagrams/`. Edit
[`scripts/generate_diagrams.py`](scripts/generate_diagrams.py) and regenerate:

```bash
python3 scripts/generate_diagrams.py
```

Commit the regenerated PNGs together with the script change, so the figure and
its source never drift apart. The generator fails loudly on label overflow or
collisions — if it reports a problem, fix the layout rather than committing the
image anyway.

## What must not be silently "fixed"

This project documents a car that has not been fully measured yet. Several values
are **open checks**, not assumptions — see
[`docs/04-integration/`](docs/04-integration/README.md#open-checks-on-the-vehicle).

- Do not mark an `OC-nn` resolved without an actual measurement on the vehicle, and
  say in the commit or PR how it was measured.
- Do not quietly reconcile a contradiction in the source document. Record it, as
  done for the [perfboard size](docs/01-hardware/README.md#perfboard-size-correction-to-the-source-document),
  and resolve it deliberately.
- Do not modify [`docs/00-concept/source/`](docs/00-concept/source/README.md) — it
  is the historical record and is kept verbatim.
- Do not edit a past changelog entry to make history look tidier. Correct it in the
  current entry instead.

## Licence of contributions

By contributing you agree that hardware contributions are licensed under
**CERN-OHL-S v2** and firmware/software contributions under
**GPL-3.0-or-later**, matching the rest of the repository.
