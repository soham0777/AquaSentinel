"""pH calibration only. Kept for the old instructions; the full wizard is tools/calibrate.py.

  python3 ~/aquasentinel/tools/calibrate_ph.py      (the service can keep running)
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from calibrate import Source, cal_ph, settings    # noqa: E402

if __name__ == "__main__":
    cal_ph(Source(settings.load()))
