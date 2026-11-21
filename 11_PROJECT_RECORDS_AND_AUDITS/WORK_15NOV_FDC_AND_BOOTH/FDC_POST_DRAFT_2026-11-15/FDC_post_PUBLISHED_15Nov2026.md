# FDC post as published, 15 November 2026 (final edit of the day)

- **Post:** "AquaSentinel — AG26-1500$41 — Sanjivani Hero's Journey", team community on 3DEXPERIENCE.
- **Copied from the live post after a reload.** Text only; picture and file positions are marked in brackets.
- **Media on the page:** 37, all loading. Added on 15 Nov: the two team photographs (`media/photo_1to5_float_on_stand.webp`, `media/photo_electronics_tray.webp`, confirmed unedited by the team), the 1:5 render, the dashboard picture (simulator), the board renders, the electronics manual Rev 2.0, and the corrected finale deck (replacing the 7 Nov file). Removed: the earlier board picture captioned "All 9 sensors", and the 7 Nov deck file.
- **Unchanged:** "Electronics, as it was in October", and everything evaluated in Part 2. One status paragraph was added under the Part 2 heading (quoted at the end). Both checked byte for byte in the editor before publishing.
- **Why each change was made:** `00_PROJECT_CONTROL/FDC_AUDIT_2026-11-15/FDC_audit_2026-11-15.pdf`.

---

*Updated 15 November 2026. Part 1 is the build as it stands four days before the finale. Part 2 is our 5 October FDC submission, left exactly as it was evaluated.*

The Godavari at Kopargaon does not announce a spill. At two in the morning it looks like water. A pipe empties, the colour barely changes, and by the time anyone takes a sample the river has moved on.

Kopargaon is not unusual. India counts 296 polluted river stretches and locations, and Maharashtra has 54 of them, more than any other state (CPCB, published 2025). Most monitoring points are still sampled by hand, once a month at best.

So we put a float under the bridge. Nobody has to be there at two.

It rides a guide pole clamped to the bridge pier and rises and falls with the river. No motor, no anchor. Every 15 minutes it reads the water. When something changes, its light turns red, an SMS goes out, and a pump fills a bottle with that water, at that minute, for the lab. A number can be argued with. A bottle with a time on it is harder to argue with.

We are not allowed to bring our own laptop to the booth, so everything we would have shown you on a screen is on this page. If you only have five minutes: read "Pour something in", look at the board we milled, then read "What still does not work".

Our printed 1:5 float on its stand. The probes, the dish and the electronics plinth are not fitted in this picture yet. `[photo]`

## What is on our table

A 1:5 copy of our float, printed in 37 parts. Seventeen of them we drew from scratch in SOLIDWORKS for this model. The other twenty come from our first 1:5 kit of the full-size design.

The model is small. The sensors are not.

Under the float hangs a cage, and in the cage are the real probes, full size: pH, dissolved solids, turbidity and water temperature, sitting in a Ø115 mm dish of water. A light sensor and an air temperature and humidity sensor sit on a small weather head above the water. Next to the sample bottle is an MQ-3, which smells the air above it. Seven sensors in all.

One thing we changed our minds about. In October we wrote that hobby turbidity boards leak, and we chose industrial probes, about ₹81,000 for four. In November we went back to hobby-grade boards, the same ones on this table, to bring the electronics from about ₹80,000 to about ₹11,000 a float. The price of that is drift, and no dissolved-oxygen reading. Industrial probes stay an option for a site that needs them.

Inside the plinth are a circuit board we milled ourselves and a Raspberry Pi. On top of the mast is one light. Green means the water is normal. Red means it is not.

The same model as designed, rendered from our print files, with the cage, the dish and the plinth in place. `[render]`

Our labelled sheet of the model from 7 November. One thing on it has changed since: the rain plate is gone, and its pocket on the weather plate stays empty. `[labelled sheet]`

## Pour something in

This is the part we would like you to try. Change the water in the dish and watch what the model says.

| Put this in the dish | It should say | Because |
|---|---|---|
| Clean tap water | NORMAL, green light | the readings stay where it learned them |
| A spoon of salt | INDUSTRIAL, red light | dissolved solids jump |
| A little vinegar | ACIDIC, red light | pH falls |
| A spoon of soil | RUNOFF, red light | the water turns cloudy while the salts stay flat |
| Sanitiser on a tissue, held at the bottle | SOLVENT, red light | vapour above the sample |
| Pull out the temperature probe | SENSOR FAULT, blinking red | a dead sensor is never reported as clean water |

For the first 20 seconds it only watches, learning what normal looks like in that dish. After that it needs two unusual readings out of three before it calls anything, so one bad reading cannot raise an alarm. When it does call one, the pump runs for five seconds and the bottle gets that water.

It tells you what kind of change it saw. It does not tell you which chemical. That is what the bottle is for.

The Raspberry Pi's screen: clean water, a spoon of salt, a pulled-out probe. These three come from the simulator built into our software, which plays the same six waters with no hardware attached. The screen from the real bench run replaces them when we have it. `[dashboard picture]`

## The board we milled

In October the Raspberry Pi read every sensor itself, through a tray of ten small boards. SOLIDWORKS found two clashes in that tray before we printed anything.

So we threw the tray out and drew one board in KiCad: 104 × 72 mm, copper on one side. We cut it on a desktop CNC on 12 November. An Arduino Nano sits in a socket in the middle, and every sensor has its own labelled header. `[board renders]`

Two things we learned the slow way. Windows blocked the usual milling program on our laptop, so we wrote our own small sender to drive the machine. And the pH board and the dissolved-solids board disturb each other when both are powered in the same water, so the Nano switches the dissolved-solids board on only for the moment it reads it.

On 13 November, on the bench, all seven sensors answered through this board, and the light and the pump ran from it.

The electronics, wired in the tray: the Raspberry Pi on the left, our Sensor Hub board with the Arduino Nano in the middle, and the TDS board and the other sensor and power boards around it. `[photo]`

The electronics manual, 17 pages, revision 2.0 of 14 November: the board, how each sensor is wired, the six waters, and what to do when something goes wrong. `[file]`

The build manual, 30 pages. Page 11 still shows the rain pocket we dropped in November; it stays empty. `[file]`

## The software

The Nano sends one line of readings every second over a USB cable. The Raspberry Pi reads it, decides, switches the light and the pump, sends the SMS through a SIM800L, and writes every reading to a file. The rules that decide are 141 lines of Python. We kept them short on purpose, so anyone can read them and argue with them.

## The full-size float

The R3 at full size: 66 parts, AISI 316L frame. `[render]`

The model on the table is a 1:5 copy of this. The R3 is 66 parts and 48.5 kg in one SOLIDWORKS assembly. It climbs a 2-inch pole on eight rollers and follows the river through 2 m of rise. It has not been built. It exists as CAD, drawings and calculations.

CAD stopped us twice. Our second version ran the pole straight through the middle of the electronics pod. And when we finally added up the real masses, the float came to 48.5 kg, not the 25.4 kg we had guessed, so the hulls had to grow.

Twelve steps from the pier brackets to the harness, then the drawing set with its design check sheet. Both came out of the R3 model; the checks are calculations, not test results. `[R3 manual]` `[drawing set]`

### Watch it move

Three clips from the CAD animation. The first two come from our journey video. `[three clips]`

## Who it is for

Three people have a moment when a spill matters. The water-works operator at the town intake, who needs to know in time to close it. The pollution board officer, who needs water taken at the right minute, not next month. And the people at the ghat, who need a light they can read from the bank, without a phone or an app.

Better instruments exist. A CPCB real-time station measures 17 parameters every 15 minutes and costs ₹35 to 40 lakh, which is why there are so few. A YSI EXO2 sonde is reference-grade, but it needs a mount, a logger and a modem built around it. A sampler like the ISCO 6712 bottles water on a trigger but does not read the river itself. Ours is cruder than all three. What it does is all of those jobs at once, on a bridge pier, for a fraction of the price.

We think a pollution board or a water-works would pay ₹8,000 a month for one float, with installation, a monthly service visit, the alerts and four lab samples a year included. That fee is our proposal; nobody has agreed to it yet. We would start with three floats at Kopargaon.

## What it costs

₹47,900 to build one at 100 units, and ₹64,600 for the first one. A real-time monitoring station costs ₹35 to 40 lakh, which is 73 to 84 of these. At ₹8,000 a month the hardware pays for itself in about twelve months, after the cost of monthly service. That price assumes galvanised steel for the parts bolted to the bridge; the CAD still shows 316L stainless. All of this is our estimate from supplier listings. None of it is a quote yet. Every line is in the PDF. `[cost PDF]`

## What still does not work

- The pH probe still reads raw voltage. Until we calibrate it against buffers, its numbers mean nothing.
- The SIM800L is wired. No message has left the board yet.
- The Raspberry Pi has not yet read the board from end to end.
- The float is printed and on its stand. The probes, the dish and the plinth are not fitted to it yet.
- The weather plate has an empty pocket where the rain sensor used to go. We dropped it in November.
- Slime and algae can foul a probe in a river within a week or two. We removed the wiper to save cost and have nothing in its place yet.
- On paper the float lasts about three days without sun, and only if the Raspberry Pi sleeps between readings. We have not measured it.
- A flood above 2 m holds the float under at the top stop. We need gauge data for the site before any pilot.
- Nothing here has been in the river. The two stress studies are estimates, not tests.

We will cross these off on this page as each one is done.

## 19 and 20 November

Booth on the 19th, pitch on the 20th. On the table: the 1:5 model running on real probes, the milled board, and the full-size R3 in CAD. `[render]`

The finale deck, 28 slides, as corrected on 15 November. `[file]`

After the finale: a full-size float in a tank, to check its draft, the 2 m of travel and the roller friction. Then, once the bridge owner, the river authority and MPCB give permission, 30 days on the Godavari at Kopargaon, with every alert checked against a lab sample.

There is still a lot we do not know. We have not run the tank test. We have not been in the river. The pH probe is still waiting for its buffers. Ask us about any of it.

## Team

(unchanged table) Prasad Satish Ugale replaced Shriraj Ganesh Kamble; AAKRUTI approved the change on 22 October 2026. The FDC presentation in Part 2 still shows the earlier team.

---

**Status paragraph added under the Part 2 heading:**

What has moved since this was evaluated. The electronics went from an ESP32 with four industrial RS485 probes, dissolved oxygen included, and an LTE modem, to a Raspberry Pi, an Arduino Nano, seven hobby-grade sensors and a 2G SMS modem. The ultrasonic level sensor and the wiper were removed, and the bottle carousel became a simple four-bottle rack. The prototype estimate went from ₹1.34 lakh to ₹64,600. Slide 7 calls the 66 R3 parts native SOLIDWORKS; they are imported bodies, which we assembled and simulated in SOLIDWORKS.
