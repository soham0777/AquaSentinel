# AquaSentinel finale deck: fact check (16 Nov 2026)

Every number and claim in `AquaSentinel_Finale_7min.pptx` was checked against a project file, a calculation, or a public source.

- ✅ means verified.
- ✏️ means corrected in the deck today.
- 🟡 means a design estimate or proposal. The slide already says so.

## Problem (slides 2 to 5)

| Slide | Claim | Source | Status |
|---|---|---|---|
| 2 | Haridwar drive details: Upper Ganga Canal shut, 18-day drive, ≈150 t of waste, 10 km (Khadkhadi to Jwalapur), ≈200 people, litter back within days | Indian Weekender, 14 Nov 2026; Sunday Guardian; Tribune. The district administration said more than 100 t. | ✅ |
| 2 | ≈43% of India's people live in the Ganga basin | CAG (2017), cited in Parliament's Public Accounts Committee report (2001 census basis) | ✅ |
| 2 | The Godavari from Nashik to Nanded, past Kopargaon, is a listed polluted stretch | MPCB polluted-stretch list: Someshwar (Nashik) to Rahed (Nanded) | ✅ |
| 2 | Photo of waste on the Ganga bank | Wikimedia Commons, "Pollution of Ganga.jpg", Lane, CC BY 2.0 (2007). It is not a photo of Haridwar, and the caption does not claim it is. | ✅ |
| 3 | Photos: untreated sewage (Mutha, Pune, 2022); effluent foam (Loni Kalbhor, 2022); foam on the Mula (Pune, Nov 2024) | Wikimedia Commons: Taksheela, Pooja Tendulkar and Manshulad, all CC BY-SA 4.0. Credits are on each photo. | ✅ |
| 3 | India's towns make 72,368 million litres of sewage a day; installed plants can treat about 44% (31,841 MLD) | CPCB sewage inventory, March 2021 (PIB / Rajya Sabha reply) | ✅ |
| 3 | Dec 2024: dead fish in the Mula-Mutha, and the pollution board served Pune a notice over untreated sewage | Fish found at Naik Bet on 23 Dec 2024; MPCB show-cause notice dated 26 Dec 2024 (Free Press Journal, Lokmat Times, Bridge Chronicle) | ✅ |
| 3 | Maharashtra has 54 polluted stretches, the most in India, and most are checked by hand once a month at best | CPCB 2025 assessment; CPCB reply to NGT, OA 413/2025 ("monthly or quarterly") | ✏️ "once a month" became "once a month at best" |
| 4 | Spill curve, 02:00 discharge, 05:30 intake, 10:00 hand sample | Illustration; the slide says "not measured data" | 🟡 |
| 4 | AquaSentinel flags the spill at 02:30 | config.json: 2 of 3 readings make an event, so the second 15-minute reading triggers it. The 30-minute latency was confirmed by evaluate.py on synthetic data. | ✏️ was 02:15 |
| 5 | 296 polluted stretches and locations; 54 in Maharashtra; 1 sample a month; real-time station ₹35–40 lakh; 2,880 readings a month | CPCB 2025; NGT OA 413/2025; CSE. 96 readings a day × 30 days = 2,880. | ✅ |

## Solution and how it works

| Slide | Claim | Source | Status |
|---|---|---|---|
| 6 | Red within two readings (about 30 min) | config.json (`confirm_needed` 2, `confirm_window` 3) | ✏️ was "in one cycle" |
| 7, 8, 21 | ₹47,886 a float at 100 units; ₹64,616 for the first; 73–84 sentinels per station | 08_COST_AND_BUSINESS/03_Value_Engineered_Cost_48k (total line, plus ₹35–40 lakh ÷ ₹47,886) | ✏️ was ₹48,000 / ≈75 / ₹65,000 |
| 9 | Delhi, Dec 2024: output at the Wazirabad plant cut by 25–50% (ammonia) | ThePrint / The Patriot, 23 Dec 2024 (Delhi Jal Board). The slide notes that AquaSentinel does not measure ammonia. | ✅ |
| 9 | Warna, Feb 2024: mass fish deaths near Bhadole and Chikurde from sugar-mill effluent | Drishti IAS summary of the inspection | ✅ |
| 9 | Jojari: Supreme Court said 2 million lives at risk, with treatment plants bypassed | Supreme Court, *In Re: 2 Million Lives at Risk*, 2025 INSC 1341 (21 Nov 2025). Drone photo: TheSlumPanda, CC BY-SA 4.0. | ✅ |
| 10 | Alert to action: who acts, and how | Our proposal; the slide says so | 🟡 |
| 11, 14 | pH < 6 or > 9; TDS > 1,400 ppm; 2 of 3; learns in 20 s; clears after 4 normal readings; 141 lines of Python | config.json; brain.py (exactly 141 lines) | ✅ |
| 12, A1 | All 14 design checks (2.27×, 143 mm, GM 0.551 m, SF 2.66 / 3.1, 5.8 mm, jam margins 8.62 / 1.72, 17.7 mm, 351 mm, 9.7 mm, rub rail 12 mm outboard, 101 pairs) | 04_R3_FULL_SIZE_DESIGN/05_Design_Checks/design_checks.json | ✅ |
| 15 | Electronics ≈ ₹80,000 → ≈ ₹11,000 a float | Cost notes (₹81,000 for four industrial probes); A5 electronics line ₹11,224 | ✅ |
| 16, 17 | 66 part numbers, 144 parts, 48.5 kg (48.54); native features | design_checks.json; _Native_rebuild_check.csv (712 features) | ✅ |
| 18, 19 | 37 printed parts, 17 new; a 0.5 L dish (Ø115 × 65 mm); six tests | LIVE model design notes | ✅ |
| 20 | Renders, including 3DEXCITE at dusk; ≈ 30 min by design | Render files; config.json | ✅ |
| 21 | ₹8,000 a month, 4 lab samples a year, payback ≈ 12 months, ≈ 40% margin over 5 years | 08_COST_AND_BUSINESS (fee ₹96,000 a year, margin ≈ 40%, payback 11.9 months, 5-year contract) | 🟡 proposal; the slide says so |
| 22 | Status line dated 15 Nov | Team to update before the 20th | 🟡 **update needed** |

## Backups

| Slide | Claim | Source | Status |
|---|---|---|---|
| A2 | FEA 38.3 MPa (SF 4.4); pinned 54.8 MPa (SF 3.1); with moment 64.0 MPa (SF 2.66); bracket 3.65 MPa | SOLIDWORKS Simulation reports; design_checks.json | ✅ |
| A3 | ≈ 18 Wh/day in timed mode; 61 Wh usable; ≈ 3 days without sun | Recomputed: parts sum to 18.3 Wh/day; 12.8 V × 6 Ah × 0.8 = 61 Wh; 61 ÷ 18 ≈ 3.3 days | ✏️ was "≈ 19"; the source line now reads "our power calculation". The original document cited was not found in the project. |
| A4 | Rules and status | config.json, brain.py; 4 of 4 synthetic events at 30 min latency (evaluate.py) | ✅ |
| A5 | Cost lines summing to ₹47,886; ₹56,505 with GST; ₹90,800 before cost-down | 03_Value_Engineered_Cost_48k | ✏️ was ₹47,900 / ₹56,500 / ₹64,600 |
| A6 | 296 on 271 rivers; ≈ 4,922 locations (2,265 on rivers); ₹35–40 lakh | CPCB 2025; NGT OA 413/2025; CSE | ✅ |
| A8 | International finale, 14–17 Feb 2027, Nashville | 3dexperienceworld.com | ✅ |

## Final-version slides (added 16 Nov, evening)

The deck now has 26 main slides, then the Q&A menu at slide 27 and the comparison at slide 28. Slide numbers in the tables above refer to the earlier version.

| Slide | Claim | Source | Status |
|---|---|---|---|
| 16 "Our own board" | 10 boards gave way to one; SOLIDWORKS found 2 clashes; Sensor Hub v1.2 in KiCad, 104 × 72 mm, single-sided, 0 design-check errors; milled 12 Nov with our own G-code sender; all 7 sensors answered 13 Nov; TDS powered only while read | PCB_v1.2_BUILD_AND_PINOUT.md; FDC "The board we milled" | ✅ |
| 17 "Dashboard" | Screens showing NORMAL, INDUSTRIAL, ACIDIC, RUNOFF, SOLVENT and SENSOR FAULT | Captures from our software's simulator (FDC media, 15 Nov); the slide says so | ✅ |
| 22 "Proof on the table" | R3 manual 27 pages, 12 steps; 1:5 build manual 31 pages, 24 steps; electronics manual 17 pages, rev 2.0; cost sheet 3 pages; 6 drawings | Page counts read from the PDFs; FDC text | ✅ |
| 25 "Design thinking" | 14/14 checks, 2 FEA studies, 4/4 synthetic spills at 30 min, 7 sensors on the bench, CAD caught two mistakes | design_checks.json; evaluate.py results; FDC | ✅ |
| 25 | Status line dated 16 Nov | Team to update before the 20th | 🟡 **update needed** |
| 11 "After the alert" | Behaviour of our software: the SMS text format; at most one SMS every 10 minutes; 2 of 3 readings make an event; the event clears after 4 normal readings; no sample is taken on a sensor fault; there is no all-clear SMS yet | core.py, brain.py, config.json | ✅ |
| 11 | Who does what for each alert type; the Water Act §21 formal sample | Our proposed playbook, to agree with each agency in the pilot (the slide says so); §21 as in backup A7 | 🟡 |
| All | Speaker notes rewritten as one script. After the playbook slide was added it runs 6:38 in total. The Q&A menu is now slide 28. | Same sources as the slides | ✅ |

## Review round (16 Nov, night)

The deck now has 27 main slides. The Q&A menu is at slide 28 and the comparison at slide 29.

| Slide | Claim | Source | Status |
|---|---|---|---|
| 2 | Photo replaced with waste in the Ganga, so there are no buffaloes in the shot | Same Commons photo, cropped (Lane, CC BY 2.0) | ✅ |
| 10 | The SMS on the phone uses our real message format; the values shown are an example | core.py SMS format | ✅ |
| 10 | Government dashboard and public news feed | Not built yet; marked PLANNED on the slide | 🟡 |
| 15 | Event simulation: 02:15 watch, 02:30 event, all clear at 04:00 after 4 normal readings | Rules from config.json and brain.py. The readings are simulated, and the slide says so. | 🟡 simulated |
| 16, 25 | Build cost ₹47,886 ≈ ₹48,000, in 7 lines; ₹56,505 with GST | 03_Value_Engineered_Cost_48k | ✅ |
| 19 | 66 part numbers = 66 distinct designs; 144 = total pieces (16 bolts, 8 rollers, 8 axles, 8 anchors, 8 beam end caps, 4 crossbeams) | 01_BOM_R3.csv: 66 rows, quantities sum to 144 | ✅ |
| 9 | Photos: a man collecting plastic from the Yamuna, Delhi (2007); waste on the Panchganga ghat, Kolhapur (2016) | Wikimedia Commons: "Floating rag picker (1803617563).jpg", Koshy Koshy, CC BY 2.0; "Panchganga ghat.jpg", Ardent Nebulous, CC BY-SA 4.0. They show the rivers, not the 2024 incidents, and the captions name only the river and place. | ✅ |
| 21 | "live 19 Nov" chip removed | — | ✏️ |
| 22 | Demo tiles now show real dashboard screens | Captures from our software's simulator | ✅ |
| 25 | Running cost ₹57,177 a year (visit 18,000; lab 14,000; hardware 9,577; probes 9,000; installation 3,000; SIM 2,400; alerts 1,200). Fee ₹96,000 a year; ₹4.8 lakh over 5 years = ₹96,000 × 5. "7 to 8 floats" = ₹35–40 lakh ÷ ₹4.8 lakh. | 08_COST_AND_BUSINESS; CSE for the station cost | 🟡 proposal; the slide says so |

## Wording rule kept

The R3 geometry started in our own Python design code. All 66 parts were rebuilt as native, editable SOLIDWORKS features on 16 Nov. The deck never says "designed natively in SOLIDWORKS".
