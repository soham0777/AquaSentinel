# FDC post — draft for review (15 November 2026)

**Status:** draft only. Nothing here is on the 3DEXPERIENCE platform yet.
**Scope:** Part 1 only. Part 2 (the 5 October FDC submission) and the closing section "Electronics, as it was in October" stay exactly as they are live today.
**Title:** unchanged — `AquaSentinel — AG26-1500$41 — Sanjivani Hero's Journey`

Legend used below:
- `[PHOTO n]` a photograph only the team can take. Until it arrives, the render named beside it stays.
- `[KEEP]` media that is already in the live post and stays.
- `[NEW]` media to upload. The file is named.
- `[YOUR WORDS]` one sentence that should come from the team, not from me.

Every number in the text is followed in the "Sources" table at the end by the file it comes from.

---

## The post text

*Updated 15 November 2026. Part 1 is the build as it stands this week. Part 2 is our 5 October FDC submission, left as it was evaluated.*

Most of the waste that reaches our stretch of the Godavari arrives after dark, and that is also when nobody is sampling. So we built a float that does not need anyone there.

AquaSentinel rides a guide pole bolted to a bridge pier. Every 15 minutes it reads the water. If a reading crosses its line, the beacon turns red, an SMS goes out, and a bottle of that water is kept for the lab. It has no motor, no anchor and no GPS. The river lifts it.

We cannot bring our own laptop to the booth, so everything we would have shown you on a screen is on this page. If you have five minutes: read "Pour something in", look at the board we milled, then go to "What still does not work".

`[PHOTO 1]` The assembled 1:5 model on a table, with one of us beside it for scale.
Until then `[NEW]` `12_ELECTRONICS_MANUAL_1to5/images/live/live_overview_front.png`, captioned: *A render of the 1:5 model from our print files. Our photograph replaces this as soon as the model is assembled.*

### What is on our table

A 1:5 model of the float, printed in 37 parts. Seventeen of those we designed new in SOLIDWORKS for this model; the rest are scaled down from the full-size design.

The model is small. The sensors are not. The pH, dissolved-solids, turbidity and water-temperature probes are the real, full-size ones. They hang in a cage under the float, in a dish of water. Three more sit above the water: a light sensor, an air temperature and humidity sensor, and an MQ-3 that sniffs the sample bottle. That makes seven.

Under the dish, inside the plinth, are a circuit board we milled ourselves and a Raspberry Pi. On the mast is one light. Green means the water is normal. Red means it is not.

### Pour something in

This is the part we would like you to try. Change the water in the dish and watch what the model says.

| Put this in the dish | It should say | Because |
|---|---|---|
| Clean tap water | NORMAL, green light | the readings stay where it learned them |
| A spoon of salt | INDUSTRIAL, red light | dissolved solids jump |
| A little vinegar | ACIDIC, red light | pH falls |
| A spoon of soil | RUNOFF, red light | the water turns cloudy while the salts stay flat |
| Sanitiser on a tissue, held at the bottle | SOLVENT, red light | vapour above the sample |
| Pull out the temperature probe | SENSOR FAULT, blinking red | a dead sensor is never reported as clean water |

For the first 20 seconds it only watches, to learn what normal looks like in that dish. After that it wants two unusual readings out of three before it calls an event, so one bad reading cannot raise an alarm. When it does call one, the pump runs for five seconds and puts that water in the bottle.

It tells you what kind of change it saw. It does not tell you which chemical. That is what the bottle is for.

`[NEW]` three pictures of the Raspberry Pi's screen: `media/dashboard_NORMAL.png`, `media/dashboard_INDUSTRIAL.png`, `media/dashboard_SENSOR_FAULT.png`
Caption: *The Raspberry Pi's screen in three states. These pictures come from the simulator built into our software, which plays the six waters without any hardware. We will swap them for the screen from the real bench run.*

`[PHOTO 4 / VIDEO]` A 60-second phone video, one take: salt goes in, the screen changes, the light turns red, the pump runs, the SMS arrives on a phone. This is the single most convincing thing the post can carry. It can only be filmed after the bench test.

### The board we milled

`[PHOTO 2]` The milled board held in someone's hand, copper side or component side.
`[KEEP]` the two-view board render already in the post (*Our own circuit board: AquaSentinel Sensor Hub v1.2*).

In October the Raspberry Pi read every sensor itself, through a tray of ten small boards. SOLIDWORKS found two clashes in that tray before we printed anything. So we drew one board in KiCad instead: 104 × 72 mm, copper on one side only. We cut it on a desktop CNC on 12 November. An Arduino Nano plugs into the middle, and each sensor has its own labelled header.

Two things we learned the slow way. Windows blocked the usual milling program on our laptop, so we wrote a small sender of our own to drive the machine. And the pH board and the dissolved-solids board disturb each other when both are powered in the same water, so the Nano switches the dissolved-solids board on only for the moment it is read.

On 13 November, on the bench, all seven sensors answered through this board, and the beacon and the pump ran from it.

`[YOUR WORDS]` One sentence about that day, in the team's own voice. For example who was at the bench, or what happened the first time the light turned red. I have not written this because I was not there.

`[NEW]` `12_ELECTRONICS_MANUAL_1to5/AquaSentinel_LIVE_1to5_Electronics_Assembly_Manual.pdf`
Caption: *The electronics manual, 17 pages: the board, how each sensor is wired, the six waters, and what to do when something is wrong.*

`[KEEP]` the 30-page build manual, with its existing caption: *The build manual, 30 pages. Page 11 still shows the rain pocket we dropped in November; it stays empty.*

`[PHOTO 3]` The bench: the Nano, the dish with the probes in it, and live readings on a screen.

### The software

The Nano sends one line of readings every second over USB. The Raspberry Pi reads it, decides, switches the light and the pump, sends the SMS through a SIM800L, and saves every reading to a file. The rules that decide are about 140 lines of Python. We kept them short so that anyone can read them and argue with them.

### The full-size float

`[KEEP]` the R3 picture that is at the top of the post today (*The R3 at full size: 66 parts, AISI 316L frame.*) moves here.

The model on the table is a 1:5 copy of this. The R3 is 66 parts and 48.5 kg, drawn as one SOLIDWORKS assembly. It climbs a 2-inch pole on eight rollers and follows the river through 2 m of rise. It has not been built. It exists as CAD, drawings and calculations.

CAD stopped us twice. Our second version put the pole straight through the middle of the electronics pod. And when we added up the real masses, the float came to 48.5 kg, not the 25.4 kg we had assumed, so the hulls had to grow.

`[KEEP]` the three clips, under their existing heading and captions (*Watch it move*).
`[KEEP]` the R3 manual and the drawing set, with the existing sentence: *Twelve steps from the pier brackets to the harness, then the drawing set with its design check sheet. Both came out of the R3 model; the checks are calculations, not test results.*

### What it costs

₹47,900 to build one at 100 units, and ₹64,600 for the first one. A real-time monitoring station costs ₹35 to 40 lakh. That is 73 to 84 sentinels for the price of one station. At ₹8,000 a month the hardware pays for itself in about twelve months, after the cost of monthly service. These are estimates from supplier listings, not quotes. Every line is in the PDF.

`[KEEP]` the cost PDF.

### What still does not work

- The pH probe still reads raw voltage. Its numbers mean nothing until we calibrate it against buffers.
- The SIM800L is wired, but no message has left the board yet.
- The link from the Nano to the Raspberry Pi has not been run from end to end.
- The printed model has not been assembled or put in water as a whole.
- The met plate has an empty pocket where the rain sensor used to go. We dropped it in November.
- Nothing here has been in the river. The two static studies are estimates, not tests.

We will cross these off here as each one is done.

### 19 and 20 November

Booth on the 19th, pitch on the 20th. On the table: the 1:5 model running on real probes, the milled board, and the full-size R3 in CAD.

`[KEEP]` the booth picture and the finale deck (*The finale deck, 28 slides.*).

### Team

`[KEEP]` the team table and the sentence about Prasad replacing Shriraj, unchanged.

### Electronics, as it was in October

`[KEEP]` unchanged.

## Part 2: Our FDC submission (5 October 2026)

`[KEEP]` unchanged, every word and every file.

---

## What changes against the live post

| Change | Why |
|---|---|
| "What changed since 5 October" becomes "What is on our table", "Pour something in", "The board we milled", "The software" | The live post is a change log. It makes sense to us, not to someone meeting the project for the first time. A judge with no laptop demo needs to be walked round the table. |
| New section "Pour something in" with the six waters | This is the demo. Today the post does not mention it at all. |
| Three dashboard pictures, labelled as simulator | Without our laptop the judge cannot see the screen. |
| Electronics manual Rev 2.0 added | The post carries the October electronics package but not the current manual. |
| R3 picture moves from the top to "The full-size float" | The top of the post should show what is on the table, ideally as a photograph. |
| "a 250 ml bottle" becomes "a bottle" | The pump runs 5 seconds; the volume has not been measured. |
| "our stretch of the Godavari" | Names the river. The live text says "this stretch of river". |
| "What still does not work" becomes a list, with two items added | The live paragraph does not say that the model is unassembled, and hides the pH and SMS gaps two sections earlier. |
| "These are estimates from supplier listings, not quotes" added to cost | The cost PDF says so; the post did not. |

**Media count:** Part 1 goes from 14 items to 18 now (one model render, three dashboard pictures and the electronics manual added; nothing removed), and to 22 when the three photographs and the bench video arrive. Part 2 stays at 18.

## What I need from the team

1. `[PHOTO 1]` the assembled model on a table, with a person in frame for scale.
2. `[PHOTO 2]` the milled board in a hand.
3. `[PHOTO 3]` the bench with probes in the dish and readings on a screen.
4. `[VIDEO]` 60 seconds, one take, of the real chain.
5. `[YOUR WORDS]` one sentence about the 13 November bench day.
6. After the bench test: which items of "What still does not work" can be crossed off.

Plain phone photographs are better than polished ones. Daylight, no filter, no added text. Every picture in the project folder today is a render, a diagram or a screenshot, and that is the main reason the post reads as machine-made.

## Sources

| Statement in the draft | Where it comes from |
|---|---|
| Reads every 15 minutes; beacon, SMS, bottle; no motor, anchor or GPS | live post; finale deck slide 1 and 7 |
| Godavari | `14_RASPBERRY_PI_SOFTWARE/aquasentinel/config.json` (`site_name`); finale deck slide 2 notes |
| 37 printed parts, 17 designed new | `02_LIVE_MODEL_1to5/01_FINAL_STL/PARTS_LIST.csv`; finale deck slide 11 |
| Seven sensors and where each sits | `12_ELECTRONICS_MANUAL_1to5/PCB_SENSOR_HUB_v1/PCB_v1.2_BUILD_AND_PINOUT.md`; electronics manual Rev 2.0 |
| Green normal, red event, blinking red fault | `14_RASPBERRY_PI_SOFTWARE/aquasentinel/aquasentinel/core.py` (`BEACON`), Nano firmware `setBeacon` |
| The six waters and their classes | `PI_SETUP_AND_OPERATION.md`; `tools/self_test.py` (passes on simulated data) |
| 20 seconds of learning; 2 of 3; pump 5 seconds | `config.json` (`learn_seconds`, `confirm_needed`, `confirm_window`, `sample_pump_seconds`) |
| October design: ten boards on a tray, two clashes found in SOLIDWORKS | `12_ELECTRONICS_MANUAL_1to5/MANUAL_AUDIT_2026-11-14.md`; live post |
| Board 104 × 72 mm, single-sided, KiCad, milled 12 November | `PCB_v1.2_BUILD_AND_PINOUT.md` |
| Windows blocked the milling program; own sender written | `PCB_v1.2_BUILD_AND_PINOUT.md`, "Machine notes" |
| TDS board powered only while read because it disturbs pH | Nano firmware, `loop()` comment and `PIN_TDS_PWR` |
| All seven sensors, beacon and pump answered on 13 November | live post; `HANDOFF_TO_AI_2026-11-15.md` section 3. This is a team report; there is no log file of that bench run in the folder. |
| One line per second over USB; CSV log; SIM800L | Nano firmware; `core.py`; `sms.py` |
| Decision rules about 140 lines | `aquasentinel/brain.py` is 141 lines |
| R3: 66 parts, 48.5 kg, 2-inch pole, eight rollers, 2 m rise | `05_R3_FULL_SIZE_CAD/05_Design_Checks/design_checks.json`; finale deck slide 8 |
| Pole through the pod in v2; 25.4 kg became 48.5 kg | finale deck slide 28 |
| ₹47,900, ₹64,600, ₹35–40 lakh, 73–84, twelve months, estimates | `07_COST_AND_BUSINESS/03_Value_Engineered_Cost_48k_2026-11-07.md` and `04_…pdf` |
| Each item under "What still does not work" | `00_START_HERE.md` status block; `config.json`; live post |
