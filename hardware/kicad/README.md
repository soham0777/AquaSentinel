# hardware/kicad

[`AquaSentinel_Mainboard.kicad_sch`](AquaSentinel_Mainboard.kicad_sch) is currently a **text description** of the intended
mainboard (comment lines: ESP32, RS485, power gating, modem, microSD, beacon, pump drivers). It contains **no symbols, wires or
nets**, so KiCad cannot show a drawn schematic and there is no PCB yet. Treat it as design notes, not as a schematic.

To do before any board is ordered: draw the real schematic in KiCad, and verify the P-MOSFET gate-voltage rating against the
datasheet (the note says VGS ±20 V for the AO3401A; the datasheet value must be checked, it may be ±12 V).
