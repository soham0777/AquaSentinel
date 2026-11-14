# SOLIDWORKS Simulation — R3 guide pole and pier bracket

Two static studies of the full-size R3:

| Study | Report | Result images | Model |
|---|---|---|---|
| Guide pole | `Pole_Static_Study_Report.docx` | `Pole_vonMises_Stress.png`, `Pole_Displacement.png` | `AquaSentinel_Guide_Pole_Simulation.SLDPRT` |
| Pier bracket | `Bracket_Static_Study_Report.docx` | `Bracket_vonMises_Stress.png`, `Bracket_Displacement.png` | `AquaSentinel_Pier_Bracket_Simulation.SLDPRT` |

## Headline results

- **Guide pole:** minimum safety factor **2.66**.
- **Peak stress:** **38.3 MPa** (FEA).
- Load cases: **pinned 54.8 MPa**; **pinned + couple 64.0 MPa**, against **316L yield 170 MPa**.

These are design-stage results; the R3 has not been built or load-tested.

## Presenting it

Say “simulated in SOLIDWORKS Simulation”, and give the load case when quoting a stress number. The lowest safety factor is
the honest headline (2.66), not the highest stress.
