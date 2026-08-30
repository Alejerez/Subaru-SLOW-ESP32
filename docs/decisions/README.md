# Architecture decision records

Design decisions with their reasoning, in the format popularised by Michael
Nygard: **Context · Alternatives considered · Decision · Consequences.**

A commit message explains *what* changed. An ADR explains *why*, and — more
usefully — what was rejected and at what cost. Six months later, that is the part
nobody remembers.

## When to write one

Write an ADR when a choice:

- rules out an alternative that a reasonable person would have picked;
- has consequences that outlive the commit that introduced it;
- changes an interface between the two nodes;
- resolves something the source document left open.

Do **not** write one for a component swap with no design consequence, or for a
value that follows directly from a datasheet.

## Records

| # | Title | Status |
| --- | --- | --- |
| [0001](0001-template.md) | Template | — |
| [0002](0002-speed-over-ssm2-not-vss.md) | Vehicle speed over SSM2, not from the VSS | Accepted |
| [0003](0003-onoff-button-direct-to-node-a.md) | ON/OFF button: reused OEM switch, wired direct to Node A | Accepted |

Numbering is sequential and never reused. A superseded record is not deleted —
its status changes to `Superseded by NNNN` and it stays in place, because the
reasoning that led to it is part of the history.
