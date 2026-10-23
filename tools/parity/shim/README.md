# shim

Minimal stand-ins for the Arduino `Arduino.h` and `Preferences.h` headers, so the unmodified firmware decision code (`firmware/edge_node/src/anomaly_engine.cpp`, `autosampler.cpp`) compiles with a normal C++ compiler on a PC. Used only by `tools/parity/`.
