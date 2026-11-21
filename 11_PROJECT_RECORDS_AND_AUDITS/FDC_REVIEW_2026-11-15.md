# FDC review — what to change and what to leave, 15 November 2026

This reviews the whole live submission, Part 1 and Part 2, against the project files, the organisers' rules and the code. It starts with the one structural problem, then gives an ordered list. Each item says what is wrong, why it matters, and the exact words to use.

## The structural problem: the page describes two different machines and never says so

Part 2 is the R3 concept: a 1.0 × 0.8 × 0.9 m float, 48.5 kg, 66 parts, four industrial probes (pH, EC, DO, turbidity) plus temperature and river level, an ESP32 with LTE, 20 W solar, a 4-bottle sampler, a wiper and a 2 m pole travel. Part 1 is the bench model: a 1:5 print with seven low-cost modules (pH, TDS, turbidity, DS18B20, DHT11, LDR, MQ-3), an Arduino Nano on your own board, a Raspberry Pi, and a glass dish. A judge reading top to bottom will see the sensor list change, the electronics change, the price fall from ₹1.34 lakh to ₹64,600 and the mass disappear, and will conclude the team is confused or inflating. The fix is one short paragraph, high in Part 1, that names the two machines and why they differ. Suggested text:

> There are two machines on this page. The R3 in Part 2 is the full-size product we designed for the FDC: four industrial probes, a river-level sensor, an ESP32 with LTE and a four-bottle sampler, at about ₹1.3 lakh. The model we built for the booth is a 1:5 demonstrator around seven low-cost modules, a Nano and a Raspberry Pi, at ₹64,600. The demonstrator proves the sensing, the decision logic and the beacon; it is not the product's sensor set, and we say so wherever the numbers differ.

That single paragraph dissolves most of the apparent contradictions below and turns them into a design decision you can defend.

## Fix first: three compliance items

**1. The post title must go back to the required pattern.** The organisers' Task 6 requires `AAKRUTI_FDC_TeamID_TeamName`. On 15 November the title was changed to "AquaSentinel — AG26-1500$41 — Sanjivani Hero's Journey", which breaks that pattern. This is my change and my mistake: it reads better but it is not what the task asked for. Restore exactly: `AAKRUTI_FDC_AG26-1500$41_Sanjivani Hero's Journey`. If you want the human title, put it as the first line of the body, not in the title field.

**2. Check the community banner, then decide about the hero images.** The 2 November organiser instruction was "add all rendered images; hero images for the banner". The six hero images were removed from the post on 15 November as part of the rewrite. If the team community's banner was already set from them, nothing is lost. If it was not, restore at least three at full resolution — the R3 render, the R3 on its pole, and the 1:5 model — under a plain heading such as "Renders", with no numbering.

**3. The public GitHub README still says eight sensors.** `github.com/soham0777/AquaSentinel` is an older snapshot whose README says "one Raspberry Pi, eight sensors" and shows a rain-sensor diagram. If any QR code, slide or business card points there, a judge can land on a contradiction that is not on the post at all. Either push the corrected local README or add a one-line banner at the top: "This repository is the semi-final snapshot. The final build has seven sensors and no rain sensor; see the 14 November electronics manual."

## Part 2: the FDC record

**4. Do not rewrite the FDC deck, videos or CAD.** They are the artifacts that were evaluated on 5 October. Replacing them now would look like altering the record, and the rules treat false statements seriously. Leave the 13-slide deck, both videos and the CAD zip as they are.

**5. Add a three-line status box at the top of Part 2.** Right now the only explanation of what is superseded lives in Part 1, and a judge who jumps to Part 2 through a link will miss it. Put this under the "Part 2" heading, before the team table:

> This is the submission that was evaluated on 5 October 2026, kept as it was. Three things have moved since: Prasad Ugale replaced Shriraj Kamble on 22 October with AAKRUTI's approval, so the deck still lists the earlier team; the electronics bay in the CAD (Raspberry Pi, two ADS1115 boards, a DS3231 clock, a rain module) was replaced by our own Sensor Hub and an Arduino Nano in November; and the costs in the deck are the October estimates, not the November build.

**6. Reword the intro sentence.** "We have not changed it, except the pitch video" contradicts itself in one line. Use: "Nothing below has been edited since 5 October, except the pitch video, which was re-voiced on 7 November. The files are otherwise exactly as evaluated."

**7. Add the one-page official FDC report.** `AG26-1500$41_FDC_Official_Report.pdf` is the formal summary sheet and is not among the post's attachments. Adding it under Team & Product Details makes the record complete and costs nothing.

**8. Remove the four stray blank paragraphs** between the template headings. They render as empty gaps and make the section look unmaintained.

**9. The team table in the deck is fine.** It shows Shriraj because that was the team on 5 October, and item 5 explains it. Do not edit the deck to add Prasad.

## Claims that will not survive a sharp question

**10. The payback sentence is wrong, and it is my error.** The post says the hardware "pays for itself in six, not the twelve we wrote in October". That is naive arithmetic: ₹48,000 divided by ₹8,000. The service model counts the cost of serving the float — ₹57,177 a year, mostly monthly visits, probes, buffers and lab samples — so the year's net margin is about ₹38,800 and the payback is about a year, not six months. The attached PDF is right and the post is wrong. Replace with:

> At ₹8,000 a month the fee also has to cover the cost of serving the float, about ₹57,000 a year, so the hardware pays back in about a year. The cost PDF works it through.

**11. Explain the price fall from ₹1.3 lakh to ₹64,600.** The FDC deck quotes ₹81,000 for four industrial probes plus ₹53,000 of build, about ₹1.34 lakh. The November estimate starts from ₹1,18,580 for the Pi version, and the unit on the bench is ₹64,600 because the seven modules cost a few thousand rupees in total. Without that chain, the drop looks invented. Add after the cost paragraph:

> The October estimate was ₹1.3 lakh, and ₹81,000 of that was four industrial probes. The value-engineered model brought it to ₹1.19 lakh, and swapping to the seven low-cost modules brought the bench unit to ₹64,600. What we lose is probe-grade accuracy and dissolved oxygen; that is the trade, and it is why the model is a demonstrator, not the product.

**12. Say why the sensor set differs.** The R3 concept reads pH, EC, DO, turbidity, temperature and river level; the model reads pH, TDS, turbidity, water temperature, air temperature, humidity, light and vapour. Both lists are true and they are not the same list. Item 10's paragraph covers the reason; make sure the two lists never appear without it.

**13. Fix the sentence that never published.** The post still says "Four of the sensors are the real ones". The 1:1 cage means every probe is full-size. Replace with: "The sensor cage is 1:1, so every probe is the real one."

**14. The "4.4 safety factor" needs one clause.** The FDC deck calls 4.4 a pole safety factor; it is yield divided by the 38.3 MPa peak stress without the couple. With the couple the figure is 2.66. If a judge does the arithmetic, say it first: "4.4 is yield over the peak stress; with the couple included it is 2.66."

## Attachments that need attention

**15. The two study reports are the weakest files on the post.** `Pole_Static_Study_Report.docx` prints the displacement unit as "am" and shows "1.255e+07 am" where it means 1.255 mm; `Bracket_Static_Study_Report.docx` still contains unfilled template tokens such as `<Model_Name/>` and `<Published_Date/>`, and both reports end with an empty Conclusion. If these DOCX files are the attachments, replace them with clean PDFs of the same studies — same numbers, fixed units, a filled header and a two-sentence conclusion. Keep the originals alongside, labelled "raw export". Do not change a number.

**16. State the results where a judge will read them.** Add one caption line under the simulation files: "Pole: 871.283 N reaction, 38.32 MPa peak, 1.255 mm sway. Bracket: 459.157 N, 3.651 MPa, 0.00411 mm. Both are linear static studies at design load; nothing has been tested in water."

## What is still wrong in the finale deck (Part 1, not the FDC)

**17. Slide 22, the A4 appendix, is still the 7 November version.** It says hard limits act at once, a baseline for every hour of the day, seven days of learning, a baseline saved to disk, pH and TDS never powered together, and the decision logic "being coded in Python". The code does none of those things: one baseline per parameter, a two-of-three window, memory only, pH always powered, logic written and passing its self-test. Either rewrite the slide or drop it from the appendix — an outdated appendix is worse than no appendix.

**18. Slide 10 repeats the hourly baseline and immediate hard limits** and should get the same correction.

**19. Slide 15 still carries the 7 November status chip** ("electronics wiring and code are under way") and says "4 of 4 spills flagged in a 30-day test" without "simulated". Fix both, and change the chip to: "Printed; sensors, beacon and pump bench-proven; pH calibration and SMS in progress."

**20. Export a fresh PDF and test it elsewhere.** The PPTX was updated on 15 November; the PDF beside it is from 7 November. A venue laptop that cannot open the PPTX currently shows the rain version.

## Videos

**21. The journey video's night footage is the only rule risk that can disqualify.** Article 7.4 forbids third-party copyright, and the source of the night and river footage was never confirmed. Either replace those clips with your own render or footage, or put a credit line with permission under the video. Silence is the worst option.

**22. Listen to the pitch video once with the sensor list in hand.** It was re-voiced on 8 November, before the build settled on seven modules. If it says "eight sensors" or shows a rain sensor, re-cut that section; the video is the one attachment you cannot correct with a caption.

## Do not touch

The 7 November PDF export, the `09_SUBMISSIONS_AND_CERTIFICATES` records, the audit CSVs and reports in `00_PROJECT_CONTROL`, the archive, and the "FDC Submission" tag. They are evidence of what was submitted and when. If a correction is needed against them, add a dated note; do not edit the file.

## The order I would do this in

Restore the title first, because it is a rule item and takes a minute. Then add the two bridge paragraphs — the two machines, and the price chain — because they prevent the questions that hurt most. Then the status box at the top of Part 2 and the payback correction. Then the report PDFs. Then the deck appendix and the fresh export. Leave the videos for last, because they take the longest and carry the only legal risk.
