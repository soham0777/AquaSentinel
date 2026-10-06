# Hardware · electronics and cost

| File | Contents |
|---|---|
| [`kicad/AquaSentinel_Mainboard.kicad_sch`](kicad/AquaSentinel_Mainboard.kicad_sch) | KiCad schematic of the ESP32 carrier: RS485 transceiver, power gating, modem, microSD, beacon and pump drivers |
| [`power_budget.csv`](power_budget.csv) | duty-cycled energy per subsystem: ≈ 3.4 Wh/day estimated load |
| [`AquaSentinel_Cost_Estimate_BOM.csv`](AquaSentinel_Cost_Estimate_BOM.csv) | itemised prototype cost estimate (≈ ₹1.34 lakh, ₹81k of it the four industrial probes) |
| [`bench_energy_test_procedure.md`](bench_energy_test_procedure.md) | how to measure the real daily energy with an INA226 logger |

> The cost sheet was priced on the v2 layout. Its electronics, probes and sampler match R3; the mechanical lines
> (hull size, roller span) are from v2. The R3 mechanical BOM with masses is [`../mechanical/cad/BOM_R3.csv`](../mechanical/cad/BOM_R3.csv).
> All costs are catalogue estimates; dated supplier quotes are still needed.
