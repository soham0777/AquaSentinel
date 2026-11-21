# FDC post text as live on 15 November 2026

- **Post:** "AquaSentinel — AG26-1500$41 — Sanjivani Hero's Journey"
- **Where:** 3DSwym community "AAKRUTI_AG26-1500$41_Sanjivani Hero's Journey", AAKRUTI 2026 dashboard, tab "Your Community"
- **Author shown:** soham kadu · posted 10/5/2026 · marked "Edited"
- **Captured:** 15 November 2026, copied from the open post in the browser. Text only; the images, clips and attached files are not copied here. The *[image]*, *[file]* and *[clip]* tags and the Markdown headings were added while copying, judged from each caption; they are not part of the post.
- **Status of this file:** a record of what the post said. Do not correct it. The 7 November text is in `FDC_post_update_text_used_7Nov2026.md`.

---

15 November 2026. Part 1 is what we have built since the FDC. Part 2 is the 5 October submission, left as it was.

Most of the waste that reaches this stretch of river arrives after dark, and that is also when nobody is sampling. We built a float that does not need anyone there.

AquaSentinel rides a guide pole bolted to a bridge pier. Every 15 minutes it reads pH, TDS, turbidity, water temperature, air temperature and humidity, light, and MQ-3 vapour. If a reading crosses its line, the beacon turns red, an SMS goes out, and a 250 ml bottle of that water is kept for the lab. No motor, no anchor, no GPS: it climbs and falls with the river.

If you have five minutes, read to 20 November below, then open the CAD zip and the two simulation reports at the end.

*[image]* The R3 at full size: 66 parts, AISI 316L frame.

## What changed since 5 October

We milled our own board. 104 × 72 mm, single-sided, drawn in KiCad and cut on a desktop CNC on 12 November. The Nano sits in a socket; nine labelled connectors take the seven sensors, the beacon and the pump. On 13 November, on the bench, all seven channels answered through it, along with the beacon and the pump. The pH probe still reads raw voltage, so its numbers mean nothing until we calibrate it against buffers. The SIM800L is wired, but no message has left the board yet. Those are the two jobs left.

We printed the 1:5 model: 37 parts, of which 17 were designed from scratch for it. Four of the sensors are the real ones, sitting in a Ø115 mm glass dish; the Pi and the board go in the plinth. Assembly is this week.

*[file]* The build manual, 30 pages. Page 11 still shows the rain pocket we dropped in November; it stays empty.

We costed it properly. ₹47,900 to build one at 100 units, ₹64,600 for the unit on the bench, against ₹35 to 40 lakh for a real-time station. That is 73 to 84 sentinels for the price of one station. At ₹8,000 a month the hardware pays for itself in six, not the twelve we wrote in October. Every line is in the PDF.

## Watch it move

Three clips from the CAD animation. The first two come from our journey video.

*[clip]* Waste reaching the river at night.

*[clip]* A spill passes: the light turns red.

*[clip]* The 66 parts going together.

## What still does not work

The met plate has an empty rain pocket. The October bay had two clashes; SOLIDWORKS found them before we printed, and the board replaced that layout. Nothing here has been in the river yet. The two static studies are estimates, not tests, and the Pi-to-Nano link and the SMS are still unproven.

## 19 and 20 November

Booth on the 19th, pitch on the 20th. On the table: the 1:5 model running on real probes, the milled board, and the full-size R3 in CAD.

*[file]* The finale deck, 28 slides.

## Drawings of the full-size unit

Twelve steps from the pier brackets to the harness, then the drawing set with its design check sheet. Both came out of the R3 model; the checks are calculations, not test results.

## Team

| Role | Name |
|---|---|
| Team Leader · Project Lead | Soham Prabhakar Kadu |
| Member · System Design | Prasad Satish Ugale |
| Member · Electronics Lead | Bhakti Ajay Kadam |
| Member · Software Lead | Tanmay Nilesh Pendbhaje |
| Mentor | Dr. Kiran Wakchaure (Director Projects) |

Prasad Satish Ugale replaced Shriraj Ganesh Kamble; AAKRUTI approved the change on 22 October 2026. The FDC presentation in Part 2 still shows the earlier team.

## Electronics, as it was in October

The bay we submitted: Raspberry Pi, two ADS1115 boards, a DS3231 clock and the rain module, with the interference check and drawing AS-LIVE-ELEC-01. In November the Sensor Hub replaced all of it.

*[image]* First layout, on the printed tray.

*[file]* The 7-page electronics package: bay assembly, pin map, ADC channels, power rails.

*[file]* The 28 October design document behind that layout.

## Part 2: Our FDC submission (5 October 2026)

This is the Final Design Concept submission that was evaluated. We have not changed it, except the pitch video, which we updated on 7 November 2026 with our new team voice-over.

**Team & Product Details:**

| | |
|---|---|
| Team ID | AG26-1500$41 |
| Team Name | Sanjivani Hero's Journey |
| Final Theme | Robotics |
| Final Product Name | AquaSentinel – solar-powered floating river water-quality monitoring station (R3 design) |

**Final Presentation:**
Final Design Concept presentation, made on the official AAKRUTI FDC template.

**Pitch / Marketing Video:**
Our pitch video, voiced by our team: the problem, the AquaSentinel solution and its impact (updated 7 November 2026).

**Journey Video:**
Our AAKRUTI 2026 journey as a team: who we are, how we brainstormed the problem and how the idea grew.

**CAD Model:**
Complete SOLIDWORKS assembly (AquaSentinel R3, 66 parts) with all part files in one zip, packaged with SOLIDWORKS Pack and Go. Materials and part numbers are assigned to every part. Open AquaSentinel_R3_Assembly.SLDASM after extracting the zip.

**Additional Data:**
1. Simulation data (SOLIDWORKS Simulation, linear static studies) – pier bracket and guide pole: von Mises stress, displacement and the full study reports. These are design-stage estimates; the prototype has not yet been tested in water.
2. Rendered images of the product
