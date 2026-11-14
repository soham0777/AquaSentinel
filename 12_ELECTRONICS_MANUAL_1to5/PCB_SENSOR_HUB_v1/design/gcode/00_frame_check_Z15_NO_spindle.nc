( AquaSentinel Sensor Hub v1.2 - 00 FRAME CHECK - spindle stays OFF )
( traces the 104 x 72 board outline at Z 15 so you can see it stays on the copper and clear of the clamps )
( origin X0 Y0 = lower-left corner of the 104 x 72 BOARD, Z0 = copper surface )
G21 G90 G94
G17
M5
G0 Z15.00
G1 X0 Y0 F800
G4 P2
G1 X104 Y0 F800
G4 P2
G1 X104 Y72 F800
G4 P2
G1 X0 Y72 F800
G4 P2
G1 X0 Y0 F800
G4 P1
M30
