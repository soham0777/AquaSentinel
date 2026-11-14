# Cost and business

**The number to quote:** **₹47,886 ex-GST at 100 units** (≈ **₹56,505 with 18 % GST**). Prototype **₹64,616**.
Service **₹8,000/month**; payback **≈ 11.9 months**. These are estimates, not supplier quotes — re-check before a real order.

## What each file is

| File | What it is | Status |
|---|---|---|
| `01_AquaSentinel_Costed_BOM_Researched.xlsx` | Research base: every bought item, price, source, 23 Oct | Source data |
| `02_Pi_Based_Product_Cost_Estimate_2026-11-06.md` | Earlier estimate (₹1,18,580 prototype / ₹90,800 at 100) | **Superseded** — kept because `03_…` builds from it |
| `03_Value_Engineered_Cost_48k_2026-11-07.md` | Value-engineering from ₹90,800 to ≈ ₹48,000, line by line | **Authoritative working document** |
| `04_AquaSentinel_Cost_48k_Value_Engineered.pdf` | Customer-facing 2-page summary of the same | **Quote this** |

## Known issues to correct before quoting

The two documents were written before the final hardware change and still contain:

- a **rain plate + LM393** line (removed from the build);
- **2 × ADS1115, DS3231 RTC, three buck converters** in the bench-additions line (the final build uses a Nano on the Sensor Hub PCB; one 9 V step-up and one 4.0 V step-down);
- an electronics count based on the Pi reading sensors directly.

The total is dominated by mechanics, so these lines are small, but the wording must match the build (Art. 10). They are
tracked as P2 in `00_PROJECT_CONTROL/PROJECT_IDENTIFICATION_AND_CRITICAL_PATH_2026-11-14.md`.

Do not present `02_…` as the current cost. Use `04_…pdf`, and say “estimate at 100 units, ex-GST”.
