# Security and risk register

Scope: the repository at `840f1a6` and the system it describes. No secret values are reproduced here. Severity: Critical / High /
Medium / Low. Likelihood: Likely / Possible / Unlikely (in the stated context). "Verify" says how to prove the mitigation works.

## 1. Secrets and sensitive data scan
* Patterns searched in **all three revisions** (git grep over every blob): API keys, tokens, passwords, private-key headers, AWS
  (`AKIA…`), GitHub (`ghp_`, `github_pat_`), Slack, Google (`AIza…`), MQTT URLs, Wi-Fi SSIDs, APN settings; high-signal key formats
  also in STEP files and the base64-heavy `docs/viewer.html`. **No credentials found.** Commits after the first only changed README
  and website content.
* Personal and environment data that is public in the repository (not secret, listed for awareness):
  commit author e-mail (git history); team names, roles and photos (slides, journey video); the Windows user folder and an
  AI-agent scratch path (`C:\Users\dell\.gemini\antigravity\scratch\AquaSentinel_AAKRUTI\FDC_Submission\3_Simulation`) embedded in
  both simulation DOCX reports; DOCX author "dell"/"soham kadu"; a third-party name in the deck PDF's author field; site
  coordinates in the v2 spec example. Consider stripping document metadata before future releases and using GitHub's no-reply e-mail.

## 2. Register

### 2.1 Firmware and decision logic
| ID | Finding | Evidence | Severity | Likelihood | Impact | Mitigation | Verify |
|---|---|---|---|---|---|---|---|
| R1 | Firmware does not compile (undefined types, macros, methods) | [CODE_REVIEW F1](CODE_REVIEW.md#1-summary-of-findings) | Critical | Certain | No device behaviour exists | Rewrite logger/telemetry against `SensorReadings`/`AnomalyResult`; pin the platform; CI build | `pio run` in CI passes |
| R2 | Dead or disconnected probes read as normal water; validity flags ignored; mixed failures can mark a fallback value valid | sensor_interface.cpp:112-153, anomaly_engine.cpp:80-178; scenario B 0/4 detected | Critical | Likely in the field | Beacon shows "safe" during a spill; silent data corruption | Return NaN on failure; health = worst of the reads; engine skips invalid channels and raises a SENSOR-FAULT state shown differently from "safe"; never update baselines from invalid data | Unit tests with simulated timeouts; bench test with a probe unplugged |
| R3 | Beacon, valve, carousel, wiper, modem not implemented | CODE_REVIEW F3 | Critical | Certain | Claimed actions do not happen | Implement drivers (PCA9685, AT commands), with feedback (limit switch, current sense) | Hardware-in-the-loop test of each actuator |
| R4 | Stage constant, clock never set, 1 s warm-up | CODE_REVIEW F4 | High | Certain | Wrong stage, meaningless time stamps, wrong diurnal bins, unsettled DO | DS3231 driver + network time; real stage driver; warm-up per probe datasheet | Logged time vs reference over 7 days; stage vs staff gauge |
| R5 | Learned state and learning counter lost on any power-on or brown-out reset | anomaly_engine.cpp:14-26; scenario C | High | Likely (modem bursts, low battery) | 7-day blind window for statistical detection after every reset | Persist baselines and counters in NVS (wear-levelled, e.g. hourly); check `esp_reset_reason()` | Pull power mid-run; verify continuity |
| R6 | Hard-limit trips trigger the sampler every reading; 4 bottles exhausted by the first events | anomaly_engine.cpp:91-98; audit replay | High | Likely | No sample for later events | One trigger per event; reserve policy (e.g. keep one bottle); report bottles left | Replay benchmark; count bottles per event |
| R7 | Stale EVENT state after a learning-period trip (3 false EVENT cycles) | audit replay rows 672-674 | Medium | Possible | False red light / alert after day 7 | Reset risk state when learning ends; unit test | Replay shows 0 alarms outside events |
| R8 | Power-rail polarity contradicts the schematic notes | sensor_interface.cpp:20-40 vs kicad_sch:55-58 | High | Likely if built from notes | Probes off while being read; on while sleeping | Decide the circuit, then fix firmware; hold GPIO state in deep sleep | Scope the rail during a wake cycle |
| R9 | RS485 settings vs probe defaults (address 1, 4800 baud for pH/EC/turbidity; firmware 9600, IDs 1-4); no inter-poll delay | config.h:65-68; DFRobot wikis | High | Certain at first power-up | No probe answers | Commissioning tool to set address/baud per probe; ≥ 200 ms polling interval; validate reply header | Bench bus with all four probes |
| R10 | GPIO electrical details: AO3401A VGS ±12 V exceeded by the battery rail; GPIO34/35 have no pull-ups; GPIO14 toggles at boot; PCA9685/INA226 both 0x40 | kicad_sch:26, config.h | High | Likely | Gate damage, floating inputs, pump twitch, I2C conflict | ±20 V-rated P-FET or gate clamp; external pull-ups; gate pull-down; different I2C address straps | Schematic review + bench |
| R11 | Evidence log and sample records have no integrity protection; SD writes not atomic | microsd_logger.cpp, autosampler.cpp | Medium | Possible | Records disputable; corruption on power loss | Hash chain per record + device signing key in secure storage; journaled writes; time from a trusted source | Tamper test; power-cut test |
| R12 | Telemetry has no security design (no TLS, auth, replay protection); proposed remote pump lockout | telemetry_comm.cpp; dashboard | High | Certain if deployed as is | Spoofed alerts or lockouts; data tampering | TLS 1.2+ with per-device credentials; signed messages; human confirmation before any pump action; rate limits | Threat model + penetration test before pilot |

### 2.2 Development tools and website
| ID | Finding | Evidence | Severity | Likelihood | Impact | Mitigation | Verify |
|---|---|---|---|---|---|---|---|
| R13 | Local `serve.py` writes any POST body into project folders; no origin/token check or size limit | serve.py:23-39 | Medium | Unlikely (dev only, localhost) | A malicious page open in the same browser could overwrite viewer/drawings/checks | Random token per session; check `Origin`; size cap; bind only while capturing | Cross-origin POST is rejected |
| R14 | Viewer renders GLB metadata with `innerHTML` and loads `?glb=` from any URL when no model is embedded | template.html:296, 306, 764 | Medium | Unlikely | XSS in the local tool; chained with R13 can write files | Use `textContent`; restrict `glb` to same-origin paths | Crafted GLB with `<img onerror>` shows as text |
| R15 | CDN scripts without Subresource Integrity (three.js 0.169.0, occt-import-js 0.0.23, mp4-muxer 5.1.3); Google Fonts | template.html:76-77, 702; step_check.html:2; index.html:15 | Low | Unlikely | Supply-chain script injection on the public site | Vendor the files into `docs/` or add `integrity` hashes; self-host fonts | Hash check in CI |
| R16 | Unpinned toolchains: `platform = espressif32`, Python without requirements | platformio.ini:2 | Medium | Likely over time | Builds change silently | Pin platform/library versions; `requirements.txt` with versions | Clean rebuild matches |
| R17 | Scripts overwrite tracked files when run (build, generator, trainer, drawings) | build.py:276-283, 340-406 | Medium | Likely | Unreviewed diffs to published artefacts | Output directory argument defaulting to a build folder; publish step explicit | `git status` clean after a test build |
| R18 | Public dashboard can look live (demo banner can be switched off; "NODE 01: ACTIVE"; "River water is safe"); SMS sign-up confirms a registration that does not exist; printable "Legal Chain-of-Custody" sheet with demo values; references the municipal water cell and Yesgaon supply | app.js:575-595, index.html:47-58, 265, 381-449 | High | Possible | Members of the public or officials act on fake status; reputational and legal exposure | Permanent, non-dismissable "DEMO – not live data" watermark in all three languages; remove the SMS prompt; mark the CoC sheet "SAMPLE"; avoid naming real agencies | Review by a non-team reader |
| R19 | Claims that outrun the evidence: present-tense capabilities on the site, "deployment ready" in the journey video, "SF 4.4" (fixed-end idealisation), "Class C" EC limit, "native SOLIDWORKS", "legal evidence" | see [OPEN_QUESTIONS](OPEN_QUESTIONS_AND_NEXT_STEPS.md) | Medium | Certain | Credibility with juries, regulators and partners | Align wording with the verified status matrix in [SYSTEM_ARCHITECTURE](../architecture/SYSTEM_ARCHITECTURE.md#5-implementation-status-matrix) | Claims register updated to R3 with evidence links |
| R20 | `docs/` is the GitHub Pages root: any Markdown committed there (including these audit files) would be published and passed through Jekyll | repository settings (`has_pages`) | Low | Possible | Internal audit material published; Liquid syntax can break the site build | Keep audit docs on this branch, or add `.nojekyll`, or move them outside `docs/` before merging | Pages build after merge |

### 2.3 Physical deployment failure modes
| ID | Mode | Cause | Severity | Likelihood | Mitigation | Verify |
|---|---|---|---|---|---|---|
| P1 | Float pinned under the upper stop and flooded | stage above the 2 m design range (assumption) | High | Possible in monsoon | Size travel from gauge records; storm procedure to remove float; float switch/alert at top stop | Site hydrology study; flood drill |
| P2 | Float hanging on the lower stop | water below the design minimum | Medium | Possible in dry season | Lower bracket below the recorded minimum; analyse the hang case | Calculation + dry-run test |
| P3 | Pole overstress or fatigue | debris impact, VIV, carriage couple | Medium | Unlikely at design loads | Dynamic factor on debris; VIV screening; inspection | Hand calc per DNV-RP-C205 style screening; strain gauge in pilot |
| P4 | Carriage jams or lags | silt in roller bores, seized rollers, pole tolerance | Medium | Possible | Wear-resistant bushings; measure pipe; inspection interval | Carriage rig test with silty water |
| P5 | Gate pins or lugs fail, float released | drag + debris through gate rollers | High | Unknown | Analyse and test pins/lugs; lanyards; secondary retention | Proof load 2× design |
| P6 | Yaw oscillation and pier impacts | unsteady pier wake | Medium | Likely | Flume test; fenders; consider an upstream-face or side mounting | Flume / site video |
| P7 | Hull puncture | debris, vandalism | Low | Possible | Foam fill (already) | Flood-one-hull test in tank |
| P8 | Electronics flooding / condensation | IP67 limit, vent failure, glands | High | Possible | IP68 for exposed parts; desiccant; drip loops; humidity sensor | Immersion + thermal cycling test |
| P9 | Battery overheating or deep discharge | sun, high load (beacon), monsoon | Medium | Possible | Measure load; beacon power design; low-voltage cut-off; charge temperature limits | 72 h bench energy test with corrected instrumentation |
| P10 | Brown-out from modem bursts | 2 A peaks | High | Likely | Bulk capacitance; separate rail; supervisor | Scope during LTE attach |
| P11 | Biofouling and drift | warm, nutrient-rich water | High | Certain | Cleaning schedule; wiper on optical faces only; drift checks per USGS TM1-D3 | Weekly field checks vs reference meter |
| P12 | Stage reading wrong | blind zone, collar echo | Medium | Likely | Redesign sensor/target or use pressure/radar sensing | Mock-up test |
| P13 | Sample unusable | no cooling, holding time, wrong bottle, no §21 procedure | High | Likely | Treat as triage sample; lab protocol; cooled cassette or prompt collection | Lab pilot with spiked samples |
| P14 | Theft or vandalism on a public bridge | accessibility | Medium | Possible | Tamper alerts, locks, community engagement | Pilot observation |
| P15 | False public alarm or missed alarm | algorithm limits, sensor faults | High | Possible | Distinct fault state; human-in-the-loop for public warnings; agreed protocol with authorities | Pilot false-alarm budget |
| P16 | Navigation hazard or light confusion | red/green beacon on the water | Medium | Possible | Consult waterway authority; yellow special-mark light if required | Written approval |
| P17 | Unsafe service work over water | float cannot carry a person; 44–49 kg lifts | High | Likely without a plan | Boat-based procedure, PPE, two-person lifts, rescue plan | Method statement reviewed before field work |

## 3. Recommended verification sequence before any claim of deployment readiness
1. **Bench (electronics):** build a real schematic and board; firmware compiles in CI; each actuator and probe proven on the bench;
   72-hour energy log with suitable instrumentation; brown-out and power-cut tests; fault-injection tests for every probe.
2. **Bench (mechanical):** carriage rig, stage-sensor mock-up, gate proof load, enclosure immersion.
3. **Tank test:** draft, trim, heel, flooded-hull survival, sampler purge/fill volumes.
4. **Controlled river trial (permits, supervised, no public signalling):** two to four weeks with daily checks, co-located lab grab
   samples, reference sonde; record false alarms, fouling, drift, yaw behaviour.
5. **Pilot with authorities:** agreed alert protocol and responsibilities before the beacon is shown to the public; independent
   review of claims.
