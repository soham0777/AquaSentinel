# AquaSentinel Sensor Hub PCB v1.2

Single-sided carrier board for the 1:5 LIVE model electronics. The Arduino Nano plugs into a socket; every module connects with jumper cables to a labelled header. The Raspberry Pi stays separate: USB cable to the Nano, 3 wires from its UART to J18.

- **Board:** 104 x 72 mm, copper on one side only, milled on the TwoTrees TTC-450 Pro on 12 Nov 2026.
- **Checks:** KiCad DRC found 0 unconnected nets and 0 clearance errors. A simulation of the milled copper found no shorts and no opens.

## Connectors

| Ref | What | Pins / Nano |
|---|---|---|
| J1 | MQ-3 | 5V, GND, DO -> D6 |
| J2 | Turbidity | 5V, GND, DO -> D5 |
| J3 | LDR | 5V, GND, DO -> D4 |
| J4 | DHT11 | 5V, GND, DATA -> D3 |
| J5 | DS18B20 | 5V, GND, DATA -> D2 (4.7k pull-up R1 on board) |
| J6 | RGB beacon | B -> D9, R -> D8, G -> D7 (220R each, R2-R4), and - |
| J7 | Pump driver control | GND, IN2 (= GND), IN1 -> D10 (10k pull-down R7) |
| J8 | Spare | D11, D12, GND |
| J9 | TDS | GND, power <- A0, signal -> A1 |
| J10 | Analog spare | A2-A5 |
| J11 | pH signal | ADIY pin "O" -> 4.7k (R8) -> A6, and GND |
| J12 | AUX 5 V in | screw terminal: + and - (feeds the sensors' 5 V, the pump and the step-up) |
| J13 | Pump power out | + and -, to the Mini L298N |
| J14 | Step-up module | IN+, IN-, OUT+ (9 V), OUT- |
| J15 | pH board power | 9 V and GND |
| J16 | Step-down module | IN+ (9 V), IN-, OUT+ (set to 4.0 V), OUT- |
| J17 | SIM800L | RXD, TXD, GND, VCC (4.0 V; 1000 uF C2 on board) |
| J18 | Raspberry Pi UART | GND (pin 6), TX (pin 8, through the 4.7k/10k divider), RX (pin 10) |

**Power:**
- The sensors' 5 V comes from the AUX charger on J12, not from the Nano.
- The Nano is powered by the Pi's USB.
- All grounds are shared.

**Firmware:** `firmware/aquasentinel_nano/aquasentinel_nano.ino`. Set `#define BOARD_PCB 1` for this board; `0` is the breadboard wiring.

## Folders

- `design/` contains:
  - the KiCad board (`AquaSentinel_Sensor_Hub.kicad_pcb`);
  - the scripts that built it (`build_hub_v3.py`, run with KiCad 10's python);
  - `export_geom.py` and `make_gcode.py` (system python with shapely);
  - the renders and the DRC report.
- `design/gcode/` has the milled files. The origin X0 Y0 is the board's lower-left corner, with the copper side up; Z0 is the copper surface. The files run in this order:
  1. `01` isolation (30 deg x 0.1 V-bit, 0.08 mm)
  2. `02` spot drill
  3. `04` outline score
  4. `03_drill_1.0mm_ALL_103`
  5. `03_drill_PILOTS_1.0mm` (widen by hand: J12 to 1.3 mm, mounting holes to 3.2 mm)
- `design/sender/pcb_sender.py` is the GRBL sender used to mill the board:
  - it has a height map, pause/resume/stop and check mode;
  - run it with `python pcb_sender.py --port COM18 --run FILE.nc`.
- `firmware/` holds the Nano firmware and `wiring_test.py` for the Pi.
- `older_versions/` holds the earlier 145 x 90 and 84 x 84 layouts, which were not milled.

## Machine notes (TTC-450 Pro, GRBL 1.1h)

- **Candle:** Windows Smart App Control blocks Candle on this laptop, so the board was milled with the Python sender.
- **Check mode clears the zero:** leaving GRBL check mode (`$C`) soft-resets the controller and clears the work zero (G54). The sender saves and restores it.
- **Frame check:** always trace the board area at Z 15 with the spindle off before cutting, because the clamps sit at the edges.
- **Homing:** don't home after a controller restart while a job is zeroed.
