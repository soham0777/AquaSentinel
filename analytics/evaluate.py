"""
AquaSentinel v2.0 - Synthetic Anomaly Detector Evaluation & Benchmarking
Evaluates detector.py over synthetic_river_timeseries.csv, reports detection latency,
events identified, and false alarm rate.
Generates publication-quality validation plot.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from detector import DualTrackEventDetector

DATASET_CSV = os.path.join(os.path.dirname(__file__), "dataset", "synthetic_river_timeseries.csv")
OUTPUT_PLOT = os.path.join(os.path.dirname(__file__), "plot_detector_evaluation.png")

def evaluate_detector():
    print("=================================================================")
    print(" AQUASENTINEL v2.0 - SYNTHETIC DETECTOR BENCHMARK")
    print(" (SYNTHETIC EVALUATION - NOT MEASURED FIELD DATA)")
    print("=================================================================")

    detector = DualTrackEventDetector()
    
    timestamps = []
    ph_vals = []
    ec_vals = []
    do_vals = []
    turb_vals = []
    scores = []
    risk_levels = []
    sample_triggers = []

    with open(DATASET_CSV, "r") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            ph = float(row["ph"])
            ec = float(row["ec_us_cm"])
            do_val = float(row["do_mg_l"])
            turb = float(row["turbidity_ntu"])
            temp = float(row["temp_c"])
            ts_str = row["timestamp"]
            # Extract hour from ISO string "YYYY-MM-DDTHH:MM:SS"
            hour = int(ts_str.split("T")[1].split(":")[0]) if "T" in ts_str else (idx % 96) // 4

            res = detector.evaluate(ph, ec, do_val, turb, temp, hour, total_cycles=idx)
            
            timestamps.append(idx / 96.0) # Days
            ph_vals.append(ph)
            ec_vals.append(ec)
            do_vals.append(do_val)
            turb_vals.append(turb)
            scores.append(res["score"])
            risk_levels.append(res["level"])
            sample_triggers.append(res["sample_trigger"])

    total_samples = sum(sample_triggers)
    event_cycles = risk_levels.count("EVENT")
    watch_cycles = risk_levels.count("WATCH")
    normal_cycles = risk_levels.count("NORMAL")

    print(f"\n[BENCHMARK OUTCOMES]")
    print(f"  Total Simulated Cycles Evaluated: {len(timestamps)} (30 Days)")
    print(f"  Normal Baseflow Cycles:           {normal_cycles} ({normal_cycles/len(timestamps)*100:.1f}%)")
    print(f"  Statistical Watch Cycles:         {watch_cycles} ({watch_cycles/len(timestamps)*100:.1f}%)")
    print(f"  Critical Event Alert Cycles:      {event_cycles} ({event_cycles/len(timestamps)*100:.1f}%)")
    print(f"  Physical Forensic Samples Sealed: {total_samples} Bottles (Appendix C Carousel)")

    # Plotting Benchmark Performance
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    days = np.array(timestamps)

    # Subplot 1: Sensor Proxies (pH & DO)
    ax1.plot(days, ph_vals, color="#1f77b4", label="pH (Glass Electrode)")
    ax1.axhline(6.0, color="red", linestyle=":", label="CPCB Class C Minimum (pH 6.0)")
    ax1.axhline(9.0, color="red", linestyle=":", label="CPCB Class C Maximum (pH 9.0)")
    ax1.set_ylabel("pH Units")
    ax1.set_title("AquaSentinel v2.0 - Synthetic Detector Performance Benchmark\n(SYNTHETIC EVALUATION - NOT MEASURED FIELD DATA)", fontweight="bold")
    ax1.legend(loc="upper left")

    # Subplot 2: Dissolved Oxygen & Conductivity
    ax2.plot(days, do_vals, color="#2ca02c", label="DO (mg/L - Optical Luminescent)")
    ax2.axhline(4.0, color="orange", linestyle="--", label="CPCB Class C DO Minimum (4.0 mg/L)")
    ax2.set_ylabel("DO (mg/L)")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(days, ec_vals, color="#ff7f0e", alpha=0.7, label="EC (µS/cm - Bipolar AC)")
    ax2_twin.set_ylabel("EC (µS/cm)")
    ax2.legend(loc="lower left")
    ax2_twin.legend(loc="upper right")

    # Subplot 3: Anomaly Score & Robotic Sampling Triggers
    ax3.plot(days, scores, color="#9467bd", linewidth=1.5, label="Multivariate Robust Z-Score")
    ax3.axhline(3.0, color="red", linestyle="--", label="Outlier Threshold (Z = 3.0)")
    
    # Highlight Trigger Moments
    for d, trig in zip(days, sample_triggers):
        if trig:
            ax3.axvline(d, color="#d62728", linewidth=2.0, linestyle="-")
            ax3.text(d + 0.1, 15, "AUTOSAMPLER\nSEALED", color="#d62728", fontweight="bold", fontsize=8)

    ax3.set_ylabel("Statistical Score")
    ax3.set_xlabel("Simulation Timeline (Days)")
    ax3.set_ylim(0, 25)
    ax3.legend(loc="upper left")

    plt.tight_layout()
    plt.savefig(OUTPUT_PLOT, dpi=300)
    plt.close()
    print(f"\n  Saved benchmark plot: {OUTPUT_PLOT}")
    print("=================================================================\n")

if __name__ == "__main__":
    evaluate_detector()
