# Cost and business

**The number to quote:** **₹47,886 ex-GST at 100 units** (≈ **₹56,505 with 18 % GST**). Prototype **₹64,616**.
Service **₹8,000/month**; payback **≈ 11.9 months**. These are estimates, not supplier quotes — re-check before a real order.

## What each file is

| File | What it is | Status |
|---|---|---|
| `01_AquaSentinel_Costed_BOM_Researched.xlsx` | Research base: every bought item, price and source, 23 Oct | Source data for **mechanics only**; its 23 Oct electronics rows are historical |
| `02_Pi_Based_Product_Cost_Estimate_2026-11-06.md` | Earlier estimate (₹1,18,580 prototype / ₹90,800 at 100) | Superseded, but kept because `03_…` builds from it |
| `03_Value_Engineered_Cost_48k_2026-11-07.md` | Value-engineering from ₹90,800 to ≈ ₹48,000, line by line | **Authoritative working document** |
| `04_AquaSentinel_Cost_48k_Value_Engineered.pdf` | Customer-facing 3-page summary of the same | **Quote this** |

## Final-build corrections (15 Nov 2026)

The 6–7 Nov documents were written before the final hardware change. They have now been corrected to the build actually made:

| Was written | Now says |
|---|---|
| Rain plate + LM393, ₹100 | Sensor Hub PCB v1.2 (blank + consumables), same ₹100 allowance |
| 2 × ADS1115, DS3231 RTC, three buck converters, ₹3,000 | Arduino Nano, 9 V step-up, 4.0 V step-down, passives, ₹3,000 allowance |
| Electronics line included “rain” | The 7 final sensors only |
| Customer PDF row | Corrected in place; the PDF is now the 15 Nov text |

The totals — **₹47,886 ex-GST at 100 units / ₹64,616 prototype** — are unchanged. The replacement parts sit inside the
same estimate-level allowances, so the change is within the estimate tolerance, not a new price. `02_…` still carries
the old line structure but now describes the final parts; `03_…` and `04_…pdf` agree with it.

`01_AquaSentinel_Costed_BOM_Researched.xlsx` is deliberately **not** rewritten: it is the 23 Oct engineering research
base and the source for the mechanical lines. Its ESP32/LTE/RTC electronics rows describe the R3 design as researched,
not the final 1:5 build. Quote only `04_…pdf`.

Do not present `02_…` as the current cost. Use `04_…pdf`, and say “estimate at 100 units, ex-GST”.
