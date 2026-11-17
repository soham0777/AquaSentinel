# AquaSentinel: cost and business model, the numbers to use

**Use only these figures.** On 17 Nov 2026 they were checked against all of these, and all match:
- the finale deck;
- the FDC post;
- the booth prints;
- the cost sheet.

All costs are estimates from Indian supplier listings (Nov 2026), before GST unless marked. Get 3 supplier quotes before quoting a customer.

## Build cost: one float with its bridge kit

| | ₹ |
|---|---|
| **At 100 units, before GST** | **47,886 (say "about ₹48,000")** |
| At 100 units, with 18 % GST | 56,505 |
| First prototype (1 unit), before GST | 64,616 |
| Before value engineering (100 units) | 90,800 |

**Where the ₹47,886 goes** (the 7 lines on deck slide 25):

| Line | ₹ |
|---|---|
| Float: hulls, carriage, deck, sensor cartridge | 15,413 |
| Electronics + sensors (Raspberry Pi set) | 11,224 |
| Bridge kit: pole, brackets | 7,581 |
| Assembly, test, freight, mould share | 6,800 |
| Fasteners + bought parts | 3,460 |
| Solar + battery | 2,758 |
| Sample bottles + tubing | 650 |
| **Total** | **47,886** |

The bridge kit is ₹7,581 and the float is ₹40,305. Moving from industrial probes to the Raspberry Pi set cut the electronics from about ₹80,000 to ₹11,224.

## Running it: the service model (a proposal, to test in the pilot)

| | ₹ a year |
|---|---|
| Monthly visit + calibration | 18,000 |
| 4 lab samples | 14,000 |
| Hardware, spread over 5 years | 9,577 |
| Probes and buffers | 9,000 |
| Installation, spread over 5 years | 3,000 |
| SIM | 2,400 |
| Alerts | 1,200 |
| **Cost to serve one float** | **57,177** |

- **Fee:** ₹8,000 a month = ₹96,000 a year, paid by a pollution board or water-works, for everything.
- **Margin:** about 40 %. **Hardware payback:** about 12 months (11.9).
- **Five years:** ₹4.8 lakh a float, everything included (₹96,000 × 5).

## Compared with a real-time station

- One CPCB-type real-time station: **₹35–40 lakh**, for the instruments alone (CSE).
- At build cost, that is **73–84 AquaSentinels**.
- Fully serviced for 5 years, it is **7 to 8 AquaSentinels**, watching 7 to 8 bridges instead of one.

## Files in this folder

| File | Use it for |
|---|---|
| `00_COST_SUMMARY_READ_FIRST.md` | this page: the numbers to say and print |
| `03_Value_Engineered_Cost_48k_2026-11-07.md` | the full line-by-line working, rates and trade-offs (the deck cites this file) |
| `04_AquaSentinel_Cost_48k_Value_Engineered.pdf` | the printable cost sheet (on the FDC and in the print pack) |
| `_superseded_DO_NOT_QUOTE/` | earlier working only: the 23 Oct workbook for the ESP32 industrial-probe design, and the 6 Nov first-pass estimate |

## Figures that are wrong now: never quote these

| Old figure | Where it came from | Use instead |
|---|---|---|
| ₹1,48,054 a float; ₹3 lakh outright; ₹12,000 a month on 3 years; 311 stretches | 23 Oct workbook (ESP32 + industrial probes) | ₹47,886; ₹8,000 a month on 5 years; 296 stretches |
| ₹80,485 electronics; ₹1.19 lakh prototype | 6 Nov first pass | ₹11,224 electronics; ₹64,616 prototype |
| ₹47,900 / ₹64,600 / ₹65,000 | rounded figures in older drafts | ₹47,886 (≈ ₹48,000) / ₹64,616 |
