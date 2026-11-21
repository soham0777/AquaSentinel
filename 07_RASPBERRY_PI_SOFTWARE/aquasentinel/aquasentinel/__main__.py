"""Start AquaSentinel:   python3 -m aquasentinel            (real Nano)
                         python3 -m aquasentinel --simulate (no hardware, plays the six booth waters)"""
import argparse

from . import __version__, settings
from .core import Station
from .web import serve


def main():
    ap = argparse.ArgumentParser(description="AquaSentinel Raspberry Pi station")
    ap.add_argument("--simulate", action="store_true", help="run without hardware")
    ap.add_argument("--port", type=int, help="dashboard port (default from config.json)")
    a = ap.parse_args()
    cfg = settings.load()
    st = Station(cfg, simulate=a.simulate)
    st.log(f"AquaSentinel {__version__} starting" + (" in SIMULATION mode" if a.simulate else ""))
    st.start()
    serve(st, a.port or cfg.get("web_port", 8080))


if __name__ == "__main__":
    main()
