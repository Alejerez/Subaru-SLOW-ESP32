# References

Bracketed numbers cited from
[`docs/00-concept/README.md`](00-concept/README.md#design-rationale) and the
hardware documentation.

## Standards and datasheets

1. International Organization for Standardization, *ISO 9141-2:1994 — Road vehicles — Diagnostic systems — Part 2: CARB requirements for interchange of digital information*. Geneva: ISO, 1994.
2. STMicroelectronics, *L9637 — Monolithic bus driver with ISO 9141 interface*, datasheet. [Online]. Available: https://www.st.com/resource/en/datasheet/l9637.pdf
3. Espressif Systems, *ESP-NOW User Guide*, ESP-IDF Programming Guide. [Online]. Available: https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_now.html
4. Espressif Systems, *ESP32 Series Datasheet*. [Online]. Available: https://www.espressif.com/sites/default/files/documentation/esp32_datasheet_en.pdf
5. RECOM Power GmbH, *R-78E-1.0 Series — DC/DC Switching Regulator*, datasheet. [Online]. Available: https://recom-power.com
6. Solomon Systech, *SSD1322 — Dot Matrix OLED/PLED Segment/Common Driver with Controller*, datasheet.
7. Analog Devices (Maxim Integrated), *DS3231 — Extremely Accurate I²C-Integrated RTC/TCXO/Crystal*, datasheet. [Online]. Available: https://www.analog.com/media/en/technical-documentation/data-sheets/DS3231.pdf
8. NXP Semiconductors, *UM10204 — I²C-bus specification and user manual*, rev. 7.0, 2021.
9. International Organization for Standardization, *ISO 7637-2 — Road vehicles — Electrical disturbances from conduction and coupling — Part 2*. Geneva: ISO.
10. SAE International, *J1211 — Handbook for Robustness Validation of Automotive Electrical/Electronic Modules*. Warrendale, PA: SAE.
11. P. Horowitz and W. Hill, *The Art of Electronics*, 3rd ed. Cambridge, U.K.: Cambridge Univ. Press, 2015.
12. Robert Bosch GmbH, *Automotive Handbook*, 10th ed. Karlsruhe, Germany: Bosch, 2018.
13. RomRaider Project, *Subaru Select Monitor (SSM2) — logging protocol and definitions*, open-source documentation. [Online]. Available: https://www.romraider.com
14. Molex LLC, *Micro-Fit 3.0 Connector System — Product Specification PS-43045*. [Online]. Available: https://www.molex.com
15. Texas Instruments, *ADS1113/ADS1114/ADS1115 — Ultra-Small, Low-Power, 16-Bit ADC with Internal Reference, Oscillator and Programmable Comparator*, datasheet SBAS444. [Online]. Available: https://www.ti.com/lit/ds/symlink/ads1115.pdf
16. International Electrotechnical Commission, *IEC 60751 — Industrial platinum resistance thermometers and platinum temperature sensors*. Geneva: IEC. *(Defines the Pt100/Pt1000 resistance–temperature relationship used by the caliper sensors.)*

## Prior art

Published work this project builds on. Each entry was opened and read while
assembling this repository unless marked otherwise.

| Project | What it is | Language / platform | Licence |
| --- | --- | --- | --- |
| [Obeisance/SubaruSSMClockPodMod](https://github.com/Obeisance/SubaruSSMClockPodMod) | Arduino code for OBD communication with a GD-chassis Subaru WRX; routines for the Subaru Select Monitor protocol driving a clock-pod display. README dated 2015-03-29, titled "Subaru Clock Pod Mod V3". The closest published analogue to this project. | Arduino / C++ | Not stated |
| [matprophet/subduino](https://github.com/matprophet/subduino) | Arduino project for Subaru SSM to CAN-bus conversion. Polls a WRX/STi ECU over SSM2 on the K-line by addressing specific parameters rather than block reads (which the author reports as unreliable), then emits CAN packets. Uses a CAN shield with an MC33660 serial-to-K-line adapter. | Arduino | Not stated |
| [starlingcrossgte-svg/PROTOCOL](https://github.com/starlingcrossgte-svg/PROTOCOL) | Android tool for Subaru SSM2 diagnostics over K-line and CAN: live parameter logging from ECU and TCM, DTC read/clear, and bench firmware read/write for SH7058 (ISO-TP and UDS). Supports Tactrix OpenPort, OBDLink, STN and FT232 KKL adapters. **Not an Arduino project** — the author marks it unfinished and experimental, with explicit warnings against firmware writing. | Java / Android | GPL-3.0 |
| [hrdwrbob/eingauge](https://github.com/hrdwrbob/eingauge) | A gauge system in Python with an Arduino back end connected to sensors, with support planned for other data acquisition. Not Subaru-specific. Author describes it as "very much in progress". | Python + Arduino | Not stated |
| [rpkish/Subduino-SSM](https://github.com/rpkish/Subduino-SSM) | SSM2-on-microcontroller precedent, cited in the v0.1 source document. *Not independently opened while assembling this repository.* | Arduino | Not stated |

## Forum sources

- **"Clock pod mod with Subarb Select Monitor ECU polling and Arduino"** by *Obeisance*, ClubWRX — [thread](https://www.clubwrx.net/threads/clock-pod-mod-with-subarb-select-monitor-ecu-polling-and-arduino.134423369/). Ten-plus pages of build log behind `Obeisance/SubaruSSMClockPodMod` above. Title and author confirmed by search; the misspelling "Subarb" is the thread's own. The page itself is behind a paywall/robot check and could not be read directly while assembling this repository.
- **"Detailed SSM to Can-bus Convertor DIY"** by *Ajzride*, The Factory Five Forum — [thread](https://thefactoryfiveforum.com/thread/119120). Cited by the project author. **Not verified while assembling this repository:** the forum requires JavaScript and returned no readable content to the fetch tool, so neither the title nor the author could be confirmed independently. The subject matter matches `matprophet/subduino` above.

## Web sources cited by the v0.1 source document

Reproduced as the original document cited them. **These were not independently
re-verified** when this repository was assembled.

1. K-line on OBD-II pin 7 (ISO 9141-2 / KWP2000), idle-high at Vbatt, 510 Ω pull-up. [PinoutGuide](https://pinoutguide.com/CarElectronics/car_obd2_pinout.shtml) · [obd-cable](https://obd-cable.com/iso-9141-2-k-line-5-baud-handshake-guide/)
2. L9637D transceiver: RKO 510 Ω, CK ≤1.3 nF, VS at battery, VCC at logic level, RX/TX with internal pull-up. [ST datasheet](https://www.st.com/resource/en/datasheet/l9637.pdf)
3. BL/BP speed distributed from the ABS module (no single VSS) → read over SSM2 instead. [Go-Parts P0500](https://www.go-parts.com/garage/obd-p0500-subaru-legacy-2005-2009-ej253-2-5l)
4. Locking via the BIU: lock p15, unlock p29, negative pulse. [ModifiedLife](https://www.modifiedlife.com/2005-subaru-legacy-auto-alarm-wiring-schematic/)
5. ESP-NOW (ESP32 ↔ ESP32 without a router). [Espressif](https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/network/esp_now.html)
6. OLED 3.12" SSD1322 256×64, ≈79 × 21 mm active, 3.3 V. [Winstar](https://www.winstar.com.tw/products/oled-module/graphic-oled-display/3_12-oled.html)
7. Subaru connectors: [iWire](https://iwireusa.com/). Chilean suppliers: [MCI](https://mcielectronics.cl/) · [Altronics](https://altronics.cl/) · [MaxElectrónica](https://maxelectronica.cl/) · [Especificar](https://especificar.cl/)
