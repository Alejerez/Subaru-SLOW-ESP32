# 0005 — OTA firmware update in a deliberate maintenance mode

- **Status:** Accepted
- **Date:** 2026-08-30
- **Affects:** both nodes (v0.1 scope), the ESP-NOW link, the analogue input budget, the security surface of the locking node

## Context

Node A lives behind the A-pillar trim. Reflashing it over a cable means
dismantling interior every time, and v0.1 is precisely the phase with the most
firmware iterations — the SSM2 parameter set, the display pages and the locking
thresholds will all be adjusted against the real car. Node B is more accessible
but still requires pulling the bezel.

The obvious answer is over-the-air updates. The obvious implementation — leave
Wi-Fi running — does not work here, for three separate reasons:

1. **ESP-NOW and Wi-Fi contend for the channel.** ESP-NOW runs on a fixed
   channel. A node associated with an access point is forced onto the AP's
   channel; if that differs from the peer's, the inter-node link degrades or
   stops. This is the standard ESP-NOW failure mode, not an edge case.
2. **The locking node must not reboot while driving.** Node A actuates the door
   locks from received speed. A firmware update landing at 100 km/h is not a
   situation to design around; it is one to make impossible.
3. **An always-on update endpoint on the node that controls the door locks is a
   way into the car.** A SoftAP with a weak password sitting there permanently is
   a poor trade for convenience.

## Alternatives considered

| Alternative | Pros | Cons |
| --- | --- | --- |
| **Cable only, no OTA** | Nothing new to build; no radio surface at all | Every Node A iteration means removing A-pillar trim. During the phase with the most iterations, this is the dominant cost |
| **Wi-Fi always on, OTA whenever** | Simplest to think about; update any time | Breaks ESP-NOW through channel contention; permanent attack surface on the locking node; allows an update mid-drive |
| **Deliberate maintenance mode, entered from the gauge menu** *(chosen)* | Wi-Fi and ESP-NOW are never up together, so no channel conflict; the car is stationary and the driver is present by construction; no permanent endpoint | A mode to design, enter, confirm and exit; the flag has to survive a reboot; needs a way to drive Node A, which has no display |

## Decision

**OTA runs only in a maintenance mode, entered on purpose, one boot at a time.**

The flow:

1. From the OLED menu, using the OEM buttons, the user selects a target node —
   any node, not only the local one.
2. That node sets a flag and reboots. For Node A the instruction travels over
   ESP-NOW, using the same Node B → Node A direction the link already carries.
3. On restart the node sees the flag, brings up Wi-Fi **with ESP-NOW suspended**,
   and serves the update.
4. After the update, or on timeout, it reboots normally: Wi-Fi down, ESP-NOW up.

**The flag lives in RTC memory** (`RTC_NOINIT_ATTR`), guarded by a magic value to
distinguish a deliberate write from uninitialised content at cold boot. RTC slow
memory survives a software restart but is lost when power is removed, which is
exactly the semantics wanted: the mode carries across the intentional reboot, and
cutting the ignition is always a way out. It also writes nothing to flash.

Three guards are part of the decision, not implementation details:

- **Timeout.** If no update arrives within a set period, the node reboots into
  normal mode by itself. Without this, one mistaken entry leaves the locking node
  offline indefinitely.
- **Speed interlock.** Node B knows vehicle speed; entering maintenance mode is
  refused while the car is moving.
- **Return confirmation.** While Node A is updating, ESP-NOW is down and Node B
  cannot see it. Confirmation is the complete cycle: on rebooting normally, Node A
  reports its firmware version over ESP-NOW and Node B displays it. If it does not
  reappear within a set time, the gauge says so.

**Dual-partition OTA with rollback** (the ESP-IDF `esp_ota` mechanism) is
required. The maintenance-mode design protects against entering the mode by
mistake; it does nothing about a bad image, and a bricked node behind the
A-pillar is worse than no OTA at all.

## Consequences

**Makes easier**

- Firmware iteration on Node A without touching interior trim — the reason this
  is in v0.1 rather than later.
- The web administration interface planned for v0.2 reuses the same Wi-Fi and the
  same maintenance-mode rule, at no additional architectural cost.
- Trackday log download over Wi-Fi (v0.4) reuses the same stack, and is two
  orders of magnitude faster than Bluetooth would be.

**Makes harder / commits us to**

- **ADC2 becomes unusable.** The ESP32's Wi-Fi driver takes ADC2, so only ADC1
  channels can be relied on. On Node B, GPIO 32/33 are buttons, 34 is the analogue
  input and 35 is ILL — which leaves **GPIO36 and GPIO39, and nothing else**. Any
  further analogue sensing needs an external I²C ADC (an ADS1115 on the RTC's
  existing bus is the natural choice, and gives better linearity than the ESP32's
  own ADC besides). This constrains the carrier PCB, so it is a design input now, not
  a discovery later.
- Wi-Fi and ESP-NOW are **mutually exclusive by design**. Any future feature that
  wants both at once is not a small change — it is a revisit of this record.
- Node A must be drivable from Node B's menu, which makes the ESP-NOW link
  carry a control message class beyond the mode confirmation of
  [ADR 0003](0003-onoff-button-direct-to-node-a.md).
- Auto-locking is inactive while Node A is in maintenance mode. Acceptable, since
  the car is stationary by construction, but it is a real behaviour to document
  for the user.

**Left unresolved**

- Transport and authentication of the update itself — HTTP upload to a SoftAP, a
  pull from the home network, or signed images. Signing matters more here than in
  a typical hobby project, given what Node A controls.
- The timeout value, and how the entry is presented in the menu.
- Whether Node B should refuse to enter maintenance mode itself while Node A is
  already in it, to avoid both nodes being deaf at once.
