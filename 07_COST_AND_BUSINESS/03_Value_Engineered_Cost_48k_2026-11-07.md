# AquaSentinel: value-engineered production cost ≈ ₹48,000 (7 Nov 2026)

Target set by the team: a sentinel at about ₹50,000. Starting point: the Raspberry Pi version of R3 at ₹1,18,580 (prototype) / ₹90,800 (100 units), from `02_Pi_Based_Product_Cost_Estimate_2026-11-06.md` and the researched costed BOM (23 Oct).

**How the cost falls:** the parts bolted to the bridge move from 316L stainless to galvanised steel; welded and anodised aluminium parts become bolted or HDPE parts; the wiper and the cool-box sampler are dropped (the Pi sensor set does not use them); fasteners, assembly and freight are scaled for 100 units. **Float mass is unchanged** (steel replaces stainless of the same density; HDPE parts are lighter), so the buoyancy and stability checks still hold. The guide pole keeps its 2-inch section; galvanised pipe steel yields at ≥ 210 MPa against 170 MPa for 316L, so the quoted pole safety factor (2.66) stays conservative.

| Group | Item | At 100 before (₹) | Prototype (₹) | At 100 units (₹) | Change |
|---|---|---|---|---|---|
| Bridge kit | Guide pole, 2-inch | 7,253 | 1,529 | 1,479 | 316L stainless → heavy-class GI pipe (same section; yield ≥ 210 MPa vs 170 MPa) |
| Bridge kit | Pier brackets (2) | 9,708 | 3,251 | 2,601 | 316L TIG weldment → hot-dip galvanised MS, MIG welded |
| Bridge kit | Pole clamp caps (2) + stage target | 2,830 | 1,171 | 871 | 316L → galvanised MS |
| Bridge kit | Stop collars, top cap, buffers | 1,350 | 1,350 | 1,250 | unchanged (bought) |
| Bridge kit | Anchors + injection mortar | 2,460 | 1,500 | 1,380 | A4 stainless studs → HDG studs |
| Float | Twin hulls, foam-filled | 2,988 | 9,868 | 2,988 | unchanged: rotomoulded PE at volume (prototype: welded PE sheet) |
| Float | Crossbeams (4) | 2,970 | 1,796 | 1,652 | aluminium SHS kept; anodising dropped |
| Float | Equipment deck | 3,305 | 1,000 | 900 | laser-cut aluminium tread plate → 10 mm HDPE marine board |
| Float | Guide carriage (fixed half + gate) | 8,750 | 3,200 | 2,400 | TIG-welded laser-cut weldments → bolted aluminium angle |
| Float | Guide rollers UHMW-PE (8) | 1,492 | 2,233 | 1,492 | unchanged |
| Float | Hinge + latch pins, struts | 1,440 | 1,300 | 1,130 | struts 316L → GI tube; pins stay stainless |
| Float | Sensor well: sleeve, hatch ring, guard cage, deflector | 4,129 | 1,940 | 1,567 | hatch ring 316L → HDPE; cage 316L → galvanised MS |
| Float | Sensor cartridge (cap, spine, spiders, handle) | 2,955 | 1,300 | 1,030 | machined acetal + wiper drive → turned HDPE cap; wiper removed (Pi set has no wiper) |
| Float | Wiper arm + brushes | 447 | 0 | 0 | removed (not used by the Raspberry Pi sensor set) |
| Float | Pod rails/plate, canopy, mast, handles | 4,925 | 1,900 | 1,520 | aluminium/316L → HDPE board, aluminium angle, GI conduit; 4 handles → 2 |
| Float | Sampler strainer + bottle rack | 1,131 | 900 | 734 | carousel cassette → simple 4-bottle HDPE rack |
| Electronics | Pi 3B+, pH, TDS, turbidity, DS18B20, DHT11, MQ-3, rain, LDR, SIM800L, pump, driver, LED | – | 7,189 | 6,111 | team hardware at retail; −15 % volume |
| Electronics | 2 × ADS1115, RTC, bucks, passives, SD card, buffers | – | 2,542 | 2,161 | bench additions |
| Electronics | Wake-up timer | – | 555 | 472 | ₹3,000 timer board → TPL5110 timer module |
| Electronics | Enclosure, glands, harness, antenna, beacon LEDs | – | 2,610 | 2,480 | IP67 PC box + strobes → IP65 ABS box + 12 V LED modules |
| Power | 20 W solar, 12.8 V 6 Ah LiFePO4, MPPT, fuse | 2,758 | 3,322 | 2,758 | unchanged |
| Sampler | Bottles, caps, tubing | 650 | 760 | 650 | cool-box cassette dropped |
| Fasteners | Bolts, roller axles, lifting eyes, bought mech. | 4,680 | 4,400 | 3,460 | A4 stainless → A2 + HDG; 4 lifting eyes → 2 |
| Assembly | Assembly, leak test + calibration, freight, mould share | 10,326 | 9,000 | 6,800 | jigged bolted assembly; rotomould ₹2.5 lakh over 100 units |
| **Total** | | **90,800** | **64,616** | **47,886** | |

- **Per sentinel in production (100 units): ≈ ₹47,886 ex-GST ≈ ₹56,505 with GST.** Bridge kit ₹7,581, float ₹40,305.
- First prototype (1 unit): ≈ ₹64,616 ex-GST.
- One real-time station (₹35–40 lakh, CSE) = about **73–84 sentinels**.

## Service model at ₹8,000 a month

Cost to serve one float a year: ₹57,177 (hardware over 5 years ₹9,577; installation ₹3,000; monthly visit ₹18,000; probes and buffers ₹9,000; SIM ₹2,400; alerts ₹1,200; 4 lab samples ₹14,000). Fee ₹96,000 a year → **margin ≈ 40 %**, hardware paid back in **≈ 11.9 months**.

## Rates used and their basis

- Galvanised steel fabrication ₹100/kg: GI/MS stock ₹70–85/kg plus hot-dip galvanising ₹16–35/kg (Indian supplier listings, Nov 2026). 2-inch heavy GI pipe ₹80/kg.
- TPL5110 timer module ≈ ₹555 ex-GST (Evelta); team hardware at retail prices from the 6 Nov estimate.
- Everything else from the researched costed BOM (23 Oct). **These are estimates: get 3 supplier quotes before quoting a customer.**

## Trade-offs to state honestly

- Galvanised steel needs an annual coating check (stainless did not). Fasteners in water stay stainless.
- The CAD and drawings still show 316L; this is the production cost-down plan, to be modelled in SOLIDWORKS before the pilot.
- Hobby-grade sensors, no dissolved oxygen, 2G SMS: alerts rely on sudden change and monthly calibration.