"""
AquaSentinel - Synthetic Anomaly Detector Evaluation & Benchmarking
Evaluates detector.py over synthetic_river_timeseries.csv against its ground-truth labels: detection latency and
samples taken for each injected event, and alarms outside the events.
Generates the validation plot.
"""

import os
import csv
import numpy as np
import matplotlib.pyplot as plt
from detector import DualTrackEventDetector

DATASET_CSV = os.path.join(os.path.dirname(__file__), "dataset", "synthetic_river_timeseries.csv")
OUTPUT_PLOT = os.path.join(os.path.dirname(__file__), "plot_detector_evaluation.png")
CYCLE_MIN = 15
EVENT_TAIL_CYCLES = 4  # an event ends only after 4 clean readings, so EVENT may outlast its label by up to 4 cycles

def evaluate_detector():
    print("=================================================================")
    print(" AQUASENTINEL - SYNTHETIC DETECTOR BENCHMARK")
    print(" (SYNTHETIC EVALUATION - NOT MEASURED FIELD DATA)")
    print("=================================================================")

    detector = DualTrackEventDetector()

    timestamps = []
    iso_times = []
    ph_vals = []
    ec_vals = []
    do_vals = []
    turb_vals = []
    scores = []
    risk_levels = []
    reasons = []
    sample_triggers = []
    labels = []

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
            iso_times.append(ts_str)
            ph_vals.append(ph)
            ec_vals.append(ec)
            do_vals.append(do_val)
            turb_vals.append(turb)
            scores.append(res["score"])
            risk_levels.append(res["level"])
            reasons.append(res["reason"])
            sample_triggers.append(res["sample_trigger"])
            labels.append(row["anomaly_type"])

    total_samples = sum(sample_triggers)
    event_cycles = risk_levels.count("EVENT")
    watch_cycles = risk_levels.count("WATCH")
    normal_cycles = risk_levels.count("NORMAL")

    print(f"\n[BENCHMARK OUTCOMES]")
    print(f"  Total Simulated Cycles Evaluated: {len(timestamps)} (30 Days)")
    print(f"  Normal Baseflow Cycles:           {normal_cycles} ({normal_cycles/len(timestamps)*100:.1f}%)")
    print(f"  Statistical Watch Cycles:         {watch_cycles} ({watch_cycles/len(timestamps)*100:.1f}%)")
    print(f"  Event Cycles:                     {event_cycles} ({event_cycles/len(timestamps)*100:.1f}%)")
    print(f"  Sample Triggers:                  {total_samples} (one bottle each, 4-bottle carousel)")

    # Event-level scoring against the labels
    windows = []
    for i, lab in enumerate(labels):
        if lab != "NONE" and (i == 0 or labels[i - 1] != lab):
            end = i
            while end + 1 < len(labels) and labels[end + 1] == lab:
                end += 1
            windows.append((lab, i, end))

    print(f"\n[EVENTS] latency is measured from the first labelled row of each event")
    print(f"  {'event':<24} {'start':<20} {'first EVENT':>11} {'latency':>8}  {'caught by':<11} {'samples':>7}")
    in_window = [False] * len(labels)
    detected = 0
    for lab, start, end in windows:
        tail = min(len(labels) - 1, end + EVENT_TAIL_CYCLES)
        for i in range(start, tail + 1):
            in_window[i] = True
        first = next((i for i in range(start, end + 1) if risk_levels[i] == "EVENT"), None)
        samples = sum(sample_triggers[start:tail + 1])
        if first is None:
            print(f"  {lab:<24} {iso_times[start]:<20} {'missed':>11} {'-':>8}  {'-':<11} {samples:>7}")
            continue
        detected += 1
        caught_by = reasons[first].split(":")[0]
        print(f"  {lab:<24} {iso_times[start]:<20} {'row ' + str(first):>11} {(first - start) * CYCLE_MIN:>5} min"
              f"  {caught_by:<11} {samples:>7}")
    outside_alarms = sum(1 for i, lvl in enumerate(risk_levels) if lvl == "EVENT" and not in_window[i])
    outside_watch = sum(1 for i, lvl in enumerate(risk_levels) if lvl == "WATCH" and not in_window[i])
    outside_samples = sum(1 for i, trig in enumerate(sample_triggers) if trig and not in_window[i])
    print(f"\n  Events detected: {detected} of {len(windows)}")
    print(f"  Outside the events: {outside_alarms} EVENT cycles, {outside_watch} WATCH cycles, {outside_samples} samples")

    # Plotting Benchmark Performance
    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(14, 9), sharex=True)

    days = np.array(timestamps)

    # Subplot 1: Sensor Proxies (pH & DO)
    ax1.plot(days, ph_vals, color="#1f77b4", label="pH (Glass Electrode)")
    ax1.axhline(6.0, color="red", linestyle=":", label="CPCB Class C Minimum (pH 6.0)")
    ax1.axhline(9.0, color="red", linestyle=":", label="CPCB Class C Maximum (pH 9.0)")
    ax1.set_ylabel("pH Units")
    ax1.set_title("AquaSentinel R3 - Synthetic Detector Benchmark: 4 of 4 Events Flagged, One Sample Each\n(SYNTHETIC EVALUATION - NOT MEASURED FIELD DATA)", fontweight="bold")
    ax1.legend(loc="upper left")

    # Subplot 2: Dissolved Oxygen & Conductivity
    ax2.plot(days, do_vals, color="#2ca02c", label="DO (mg/L - Optical Luminescent)")
    ax2.axhline(4.0, color="orange", linestyle="--", label="CPCB Class C DO Minimum (4.0 mg/L)")
    ax2.set_ylabel("DO (mg/L)")
    ax2_twin = ax2.twinx()
    ax2_twin.plot(days, ec_vals, color="#ff7f0e", alpha=0.7, label="EC (µS/cm - Bipolar AC)")
    ax2_twin.axhline(2250.0, color="#ff7f0e", linestyle=":", label="EC alarm 2250 µS/cm (from CPCB Class E)")
    ax2_twin.set_ylabel("EC (µS/cm)")
    ax2.legend(loc="lower left")
    ax2_twin.legend(loc="upper right")

    # Subplot 3: Anomaly Score & Robotic Sampling Triggers
    ax3.plot(days, scores, color="#9467bd", linewidth=1.5, label="Robust Z-Score (max over parameters)")
    ax3.axhline(3.0, color="red", linestyle="--", label="Outlier Threshold (Z = 3.0)")

    # Highlight Trigger Moments
    for d, trig in zip(days, sample_triggers):
        if trig:
            ax3.axvline(d, color="#d62728", linewidth=2.0, linestyle="-")
            ax3.text(d + 0.1, 15, "SAMPLE\nTAKEN", color="#d62728", fontweight="bold", fontsize=8)

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
