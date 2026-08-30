# 03 — Software

Host-side software and tooling: anything that runs off the vehicle — bench test
utilities, SSM2 exploration, logging, calibration helpers.

**Empty at v0.1.** The only tooling that exists so far is the figure generator in
[`scripts/`](../../scripts/), which is documentation infrastructure rather than
project software.

Two candidates already named in the source document, both deferred (see
[`ROADMAP.md`](../../ROADMAP.md)):

- **Extended data logging** — a Raspberry Pi with a Tactrix OpenPort 2.0 logging
  alongside the gauge rather than through it. Note that this shares the K-line
  with Node B, which is the one documented case where the gauge stops polling
  SSM2 and the locking node loses its speed source
  ([ADR 0002](../decisions/0002-speed-over-ssm2-not-vss.md)).
- **Calibration helper** — for setting the 20 km/h threshold and the L/100 km
  moving average against real SSM2 readings.

Code that ends up here is licensed **GPL-3.0-or-later**, like the firmware
(see [`LICENSE-SOFTWARE.txt`](../../LICENSE-SOFTWARE.txt)).
