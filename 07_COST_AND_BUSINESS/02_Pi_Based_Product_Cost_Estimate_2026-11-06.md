# AquaSentinel: cost of the Raspberry Pi product (estimate, 6 Nov 2026)

**Team decision, 6 Nov 2026:** the components used in the 1:5 LIVE model are the components of the final product. The R3
mechanics (float, guide pole, bridge kit, solar, sampler) stay as costed on 23 Oct. The industrial RS485 probes, ESP32 and
LTE modem are replaced by the team's Raspberry Pi electronics.

All figures are **estimates**. The mechanics come from `01_AquaSentinel_Costed_BOM_Researched.xlsx` (23 Oct, ex-GST). The
electronics are indicative Indian retail prices (incl. 18 % GST, converted to ex-GST by ÷ 1.18) found on 6 Nov 2026, or
marked *est.* where no listing was found. Re-check prices before quoting to a customer.

## 1. Electronics and sensors (replaces ₹80,485 of probes + ESP32 electronics)

| Item | Price incl. GST | Basis |
|---|---|---|
| Raspberry Pi 3 Model B+ | ₹4,294 | Tanotis listing |
| pH board PH-4502C + E-201-C probe | ₹1,199 | probe ₹699 (FlyRobo) + board ₹500 *est.* |
| TDS Meter V1.0 | ₹769 | FlyRobo |
| Turbidity sensor (SEN0189 type) | ₹950 | *est.* from ≈ US$10 distributor prices |
| DS18B20 waterproof probe | ₹199 | Robodo |
| DHT11 | ₹100 | *est.* |
| MQ-3 module | ₹123 | FlyRobo |
| Rain plate + LM393 board | ₹100 | *est.* |
| LDR module | ₹60 | *est.* |
| SIM800L GSM/GPRS | ₹449 | Probots |
| Mini submersible pump 3–6 V | ₹150 | *est.* |
| MX1508 ("mini L298N") driver | ₹70 | *est.* |
| Bicolour LED, resistors | ₹20 | *est.* |
| **Team hardware subtotal** | **₹8,483** | |
| Bench additions: 2 × ADS1115, DS3231, 3 buck converters, passives, MOSFETs, perfboard, 32 GB card, pH buffers | ₹3,000 | `03_ELECTRONICS_RASPBERRY_PI` design, section 12 |
| Wake-up timer board (Pi wakes every 15 min) | ₹3,000 | *est.*, same document |
| **Subtotal incl. GST** | **₹14,483** | **= ₹12,274 ex-GST** |

Field items (ex-GST, from the 23 Oct costed BOM): IP67 enclosure ₹1,500 · IP68 cable glands ₹700 · cable harness ₹1,400 ·
antenna + bulkhead ₹560 · red/green LED strobes ₹1,524 = **₹5,684**.

**Electronics and sensors, ex-GST: ≈ ₹17,958** (was ₹80,485: sensors ₹69,001 + electronics ₹11,484).

## 2. Float + bridge kit, one unit, ex-GST

| Group | Prototype | At 100 units | Source |
|---|---|---|---|
| Fabricated parts (hulls, deck, carriage, pole, brackets) | 76,172 | 53,463 | costed BOM |
| Electronics + sensors (section 1) | 17,958 | 15,264 | −15 % volume *assumption* |
| Assembly, test, freight | 12,038 | 10,326 | costed BOM (6,600 + 5,438; 4,800 + 5,526) |
| Fasteners + bought mechanical | 7,240 | 7,140 | costed BOM |
| Power (20 W solar, 6 Ah LiFePO4, charger) | 3,322 | 2,758 | costed BOM |
| Sampler (bottles, caps, tubing, cassette) | 1,850 | 1,850 | costed BOM |
| **Total, float + bridge kit** | **₹1,18,580 ≈ ₹1.19 lakh** | **₹90,800 ≈ ₹0.91 lakh** | |
| of which the bridge kit | ₹29,218 | ₹24,309 | costed BOM |
| of which the float | ≈ ₹89,362 | ≈ ₹66,491 | |
| Incl. 18 % GST | ≈ ₹1.40 lakh | ≈ ₹1.07 lakh | |

Versus the semi-final R3 (₹1,86,710 prototype / ₹1,48,054 at 100): **−₹68,130 (−36 %)**.

Dropped with the industrial probes: dissolved oxygen, the river-level sensor, the wiper, the 4-bottle carousel and LTE.
The float still rides the river on its pole; it no longer *measures* river level.

## 3. Service model (fee unchanged: ₹12,000 a month, 5-year contract)

| Per float per year | ₹ | Basis |
|---|---|---|
| Hardware (₹90,800 over 5 years) | 18,160 | at 100 units |
| Installation (₹15,000 once, over 5 years) | 3,000 | assumption (unchanged) |
| Monthly service visit × 12 | 18,000 | assumption (unchanged) |
| Consumables: probes, buffers, TDS standard | 9,000 | assumption (unchanged; hobby probes are cheap but replaced more often) |
| SIM and SMS | 2,400 | assumption (unchanged) |
| Dashboard and alerts | 1,200 | assumption (unchanged) |
| Lab analysis, 4 event samples | 14,000 | ₹3,500 a sample package |
| **Cost to serve** | **65,760** | was 77,211 |
| Fee | 1,44,000 | proposal |
| **Gross margin** | **≈ 54 %** | was ≈ 46 % |
| **Hardware payback** | **≈ 11 months** | 90,800 ÷ (12,000 − 47,600/12) |
| Outright sale, installed | ≈ ₹2 lakh | ≈ 1.6 × hardware, as before |

## 4. Honest trade-offs (say them before the jury does)

- Hobby-grade sensors are less exact and drift faster than industrial probes. Alerts rely on **sudden change** against a
  learned baseline, not on absolute values; pH and TDS are calibrated at every monthly visit.
- pH and TDS boards disturb each other in the same water: they are powered one at a time.
- No dissolved oxygen, so sewage is detected only weakly (turbidity, pH, TDS). An optical DO probe is the first optional
  upgrade (≈ ₹19,000 ex-GST).
- SIM800L is 2G only. A 4G module (≈ ₹1,900) is the upgrade path if 2G is switched off.
- The MQ-3 is a vapour **indicator** in the sample bottle's air space, not a concentration in water.
