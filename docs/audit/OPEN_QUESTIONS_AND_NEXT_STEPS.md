# Open questions and next steps

Everything here is a **proposal for your review**; nothing in the project has been changed. Priorities: **P0** (correctness or
safety; do before building hardware), **P1** (needed before any river trial), **P2** (quality and scale-up). Effort: S (hours),
M (days), L (weeks).

## 1. Open-question register
| ID | Question | Evidence available now | How to resolve |
|---|---|---|---|
| Q1 | What stage range and peak velocity does the Kopargaon site actually see? | 2 m / 1.5 m/s are assumptions; no public gauge data found | CWC / Maharashtra WRD gauge records; 1-year stage series; site survey |
| Q2 | How does the float behave in the pier's wake? | weathervane check assumes uniform flow; float sits 0.3–1.4 m behind a ~1.1 m pier | Flume test with a pier model, or video at the site with a dummy float |
| Q3 | Can the upward ultrasonic sensor measure stage across the full travel? | range 146–2146 mm; collar 48 mm off-axis; blind zone 20–25 cm | Full-scale mock-up test; compare with pressure/radar alternatives |
| Q4 | Which probe faces may be wiped? | R3 wipes all four tips incl. pH glass | Ask DFRobot; bench wipe-cycle test with calibration checks |
| Q5 | What are the real probe register maps and scaling? | turbidity confirmed (÷10); others assumed | DFRobot reference documents; bench read-out |
| Q6 | Is the SOLIDWORKS Pack and Go native feature geometry or imported bodies? | 67 files written in one minute; STEP export is facetted | Open in SOLIDWORKS and inspect the feature tree |
| Q7 | Which K&F exponent form is correct (u*/U or U/u*)? | two published transcriptions disagree | Read the 2002 paper's equation directly |
| Q8 | Is the "9.98 MLD Kopargaon" figure documented? | not found online | Obtain the NGT affidavit (EA 35/2023 in OA 673/2018) |
| Q9 | Does the claims register's "> 90 % of illicit discharges" match Burkhardt et al. (2022)? | paper exists; figure not confirmed | Read the paper; correct the citation |
| Q10 | What exactly does a sampled bottle prove legally? | §21 requires procedure an unattended float cannot follow | Legal opinion; talk to MPCB about triage-sample use |
| Q11 | How will samples be preserved and collected within holding times? | cassette insulated, not cooled | Agree a protocol with the receiving NABL lab |
| Q12 | What is the real power draw, especially of the beacon and LTE? | budget excludes the beacon; no measurements | Bench energy test with suitable instrumentation |
| Q13 | Which electrical design is intended (rail polarity, MOSFETs, I2C addresses)? | schematic is prose; firmware disagrees | Draw a real schematic; design review |
| Q14 | Who operates the station and receives alerts? Who may trigger public warnings or pump lockouts? | not defined | Stakeholder agreement (water-works, MPCB, gram panchayat) |
| Q15 | What do the pitch and journey videos say (audio)? | audio not reviewed | Transcribe and check against the evidence |
| Q16 | Licence status of third-party footage/photos in the videos and posters? | unknown | List sources; replace or license |
| Q17 | Which SOLIDWORKS version made the files? | old README badge said 2019; v2 guide says 2026 Student | Check file properties in SOLIDWORKS |
| Q18 | Is the "rights itself to 60°" statement meant as the angle of vanishing stability? | GZ positive at all computed angles to 60° | Extend the GZ curve to 90°+ |

## 2. Claims that need rewording (evidence-based)
| Where | Current wording | Evidence | Suggested direction |
|---|---|---|---|
| README, site, deck | "4.4 guide-pole safety factor", "1.3 mm sway" | fixed-end FEA idealisation; pinned 3.1, pinned + couple 2.66 | quote the conservative bound with the load case |
| README, firmware | CPCB "Class C" EC ≤ 2250 µS/cm | CPCB lists 2250 under Class E | "alarm level adopted from CPCB Class E (irrigation) EC limit" |
| README | "a single splash can't trigger a sample" | hard limits act on one reading and re-trigger | state the rule per track |
| Site hero, deck | beacon turns red, sends alert, seals sample (present tense) | not implemented | "is designed to" |
| Journey video | "deployment ready on the Godavari" | not built or tested | remove |
| Deck slide 7 | "66 parts native SOLIDWORKS" | unverified | verify (Q6) |
| Spec, dashboard | "legal chain of custody", "forensic grade", "< 0.8 % carry-over meeting EPA standard" | no evidence; §21 procedure | "triage sample for laboratory confirmation" |
| Claims register | "every number is cross-referenced here" | register holds v2 values; R3 numbers absent; references missing files | rebuild the register for R3 with links to files and scripts |
| analytics/dataset/README.md | describes another dataset | CSV schema/events differ | regenerate the README from the generator |
| exported_anomaly_weights.h | "validated Maharashtra river timeseries" | synthetic | "synthetic benchmark" |
| Dashboard | SMS registration confirmation; status pills; safety advice for real places | demo only | permanent demo watermark; remove the prompt |
| Cost | "≈ ₹1.34 lakh"; "1/25th of a station" | line items ₹1.38 lakh; stations measure more parameters | recompute; compare like for like |
| Deck speaker notes (release PPTX) | "fills one of four bottles, seals and time-stamps it"; "safety factor of 4.4"; "about 1.34 lakh" | the firmware never sets the clock, so the time stamp would be wrong; other items as above | reword together with the slides |

## 3. Prioritised work plan (proposals)

### P0 — correctness and safety (before building electronics)
| # | Work | Effort | Done when |
|---|---|---|---|
| 1 | Make the firmware compile: one data model; rewrite `microsd_logger` and `telemetry_comm`; pin PlatformIO platform and libs; CI build | M | `pio run` passes in CI |
| 2 | Fail-safe sensing: NaN on failure, worst-of health, engine ignores invalid channels and shows a distinct SENSOR-FAULT state | M | unit tests: dead probe → fault state, never "normal" |
| 3 | Fix the decision state machine: reset after learning; one trigger per event; persist baselines/counters in NVS; reset-reason handling | S–M | replay: no alarms outside events; survives power cycles |
| 4 | Real electrical design: schematic and PCB with ±20 V P-FETs (or gate clamp), correct polarity, pull-ups/downs, I2C addresses, modem supply | L | design review signed off |
| 5 | Dashboard honesty: permanent demo watermark; remove SMS prompt; mark CoC sample | S | reviewed by an outsider |
| 6 | Correct published claims (§2) and rebuild the claims register for R3 | S | each number links to a file or script |

### P1 — before a supervised river trial
| # | Work | Effort |
|---|---|---|
| 7 | Implement actuator drivers with feedback (PCA9685 beacon/wiper/valve, carousel home sensor, pump direction), RTC driver, stage sensor driver | L |
| 8 | Probe commissioning tool (address/baud), warm-up per probe, ≥ 200 ms polling, reply validation | M |
| 9 | Pole check with the carriage couple, gate pin/lug check, flood over-topping and low-water hang cases, VIV screening | M |
| 10 | Stage-sensor mock-up (Q3) and redesign if needed | M |
| 11 | Event-level evaluation in `evaluate.py`; harder synthetic benchmark; baselines incl. CANARY | M |
| 12 | Fix the dispersion formula and the mixing-length validity limit | S |
| 13 | Sampling protocol with the lab (bottles, preservation, holding times); legal advice on the sample's status | M |
| 14 | Weigh components; tank test; carriage rig; enclosure immersion test | L |
| 15 | Telemetry backend design with TLS and per-device credentials; no automated pump actions | L |
| 16 | Site data (Q1) and pier-owner / waterway permissions; beacon colour with the authority ([risk P16](SECURITY_AND_RISK_REGISTER.md#23-physical-deployment-failure-modes)) | L |

### P2 — quality and scale-up
| # | Work | Effort |
|---|---|---|
| 17 | Scripts write to an output folder by default; `requirements.txt`; regression test that rebuilds and diffs outputs | S |
| 18 | Commit the drawing-view pipeline inputs (or generate views in Python) so the drawing set is reproducible | M |
| 19 | Harden `serve.py` (token, origin check, size cap) and the viewer (`textContent`, same-origin `glb`) | S |
| 20 | Vendor or SRI-pin CDN scripts; self-host fonts | S |
| 21 | Fix DWG-05 handle inserts; process-specific tolerances; replace probe envelopes with supplier STEP | S |
| 22 | Replace v2 documents with R3 versions or move them to an `archive/` folder | S |
| 23 | Consider an established open platform (EnviroDIY Mayfly / Monitor My Watershed) for the pilot logger | M |

## 4. What I would do first
P0-1 to P0-3 are pure software and testable today with the audit's replay scripts; they remove the most dangerous behaviour (a dead
sensor showing "safe") and make every later bench test meaningful. In parallel, P0-6 costs little and protects the project's
credibility. None of this has been started; tell me which items you want and I will propose concrete changes for review on a branch.
