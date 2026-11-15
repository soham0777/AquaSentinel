"""AquaSentinel - Raspberry Pi side of the 1:5 live model.

The Arduino Nano on our Sensor Hub board reads every sensor and prints one JSON line per second
over USB. This package reads those lines, decides whether the water is normal, acts (beacon,
pump sample, SMS through the SIM800L) and serves a live dashboard for the booth screen.
"""
__version__ = "1.0.0"
