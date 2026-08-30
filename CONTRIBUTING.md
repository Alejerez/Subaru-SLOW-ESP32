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
| `fw/` | Firmware for either node |
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

## Milestones

Milestones are marked with **git tags**, not with a hand-maintained log:
`concept-v1`, `schematic-rev-a`, `pcb-v1`, `firmware-v0.1`.
[`CHANGELOG.md`](CHANGELOG.md) summarises those milestones in prose; `git log` is
the fine-grained record.

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

- Do not mark an open check resolved without an actual measurement on the
  vehicle, and say in the commit or PR how it was measured.
- Do not quietly reconcile a contradiction in the source document. Document it,
  as done for the [perfboard size](docs/01-hardware/README.md#perfboard-size-correction-to-the-source-document),
  and resolve it deliberately.
- Do not modify
  [`docs/00-concept/source/`](docs/00-concept/source/README.md) — it is the
  historical record and is kept verbatim.

## Licence of contributions

By contributing you agree that hardware contributions are licensed under
**CERN-OHL-S v2** and firmware/software contributions under
**GPL-3.0-or-later**, matching the rest of the repository.
