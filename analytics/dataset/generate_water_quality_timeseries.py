"""
AquaSentinel - Lotic Water Quality Timeseries & Pollution Event Generator
Simulates realistic 15-minute multi-parameter sensor observations for a Maharashtra River (e.g. Godavari/Mula-Mutha).
Includes baseline diurnal dynamics, hydrological variations, and four distinct episodic pollution events.
"""

import math
import os
import random
import csv
from datetime import datetime, timedelta

def generate_dataset(output_path, days=30):
    random.seed(42)
    start_time = datetime(2026, 3, 1, 0, 0, 0)
    total_steps = days * 24 * 4  # 15-minute intervals -> 96 steps/day
    
    rows = []
    header = [
        "timestamp", "step_index", "ph", "turbidity_ntu", "temp_c", 
        "ec_us_cm", "do_mg_l", "depth_m", "flow_velocity_m_s",
        "event_label", "is_anomaly", "anomaly_type"
    ]
    rows.append(header)
    
    # Baseline parameters
    base_temp = 24.0
    base_ph = 7.45
    base_ec = 310.0
    base_do = 7.2
    base_turb = 8.5
    base_depth = 1.65
    base_velocity = 0.72

    for step in range(total_steps):
        current_time = start_time + timedelta(minutes=15 * step)
        hour = current_time.hour + current_time.minute / 60.0
        day = step // 96
        
        # Diurnal solar cycle (peaks around 14:00)
        diurnal_solar = math.sin((hour - 8.0) * math.pi / 12.0)
        
        # Natural baseline variations
        temp = base_temp + 3.2 * diurnal_solar + random.gauss(0, 0.25)
        # Dissolved oxygen peaks with afternoon photosynthesis and drops at night
        do = base_do + 1.2 * diurnal_solar + random.gauss(0, 0.18)
        # pH has mild diurnal shift due to carbonate-bicarbonate equilibrium
        ph = base_ph + 0.15 * diurnal_solar + random.gauss(0, 0.05)
        # Electrical conductivity and turbidity baseline
        ec = base_ec + random.gauss(0, 8.0)
        turb = max(1.0, base_turb + random.gauss(0, 1.2))
        depth = base_depth + 0.15 * math.sin(step * 2 * math.pi / 384) + random.gauss(0, 0.02)
        velocity = base_velocity + 0.08 * (depth - base_depth) + random.gauss(0, 0.015)

        is_anomaly = 0
        event_label = "NORMAL"
        anomaly_type = "NONE"

        # --- EPISODIC POLLUTION EVENTS ---
        # Event 1: Industrial Acid Washout (Day 5, 02:00 - 05:00, Steps 488 - 500)
        if 488 <= step <= 500:
            is_anomaly = 1
            event_label = "CONTAMINATION"
            anomaly_type = "INDUSTRIAL_ACID_DUMP"
            intensity = math.sin((step - 488) * math.pi / 12)
            ph -= 3.4 * intensity                  # pH plunges to ~4.0
            ec += 1550.0 * intensity              # EC surges to ~1850 uS/cm
            turb += 65.0 * intensity              # Turbidity rises
            do -= 1.8 * intensity

        # Event 2: Raw Municipal Sewage Overflow (Day 12, 19:30 - 23:30, Steps 1230 - 1246)
        elif 1230 <= step <= 1246:
            is_anomaly = 1
            event_label = "CONTAMINATION"
            anomaly_type = "RAW_SEWAGE_OVERFLOW"
            intensity = math.sin((step - 1230) * math.pi / 16)
            do -= 5.1 * intensity                  # Severe hypoxia: DO crashes to ~1.9 mg/L
            turb += 175.0 * intensity             # Turbidity spikes >180 NTU
            ec += 520.0 * intensity               # Microbial/organic ions elevate EC
            ph -= 0.6 * intensity

        # Event 3: Chemical Salt / Factory Effluent (Day 20, 11:00 - 14:00, Steps 1964 - 1976)
        elif 1964 <= step <= 1976:
            is_anomaly = 1
            event_label = "CONTAMINATION"
            anomaly_type = "CHEMICAL_SALT_SPILL"
            intensity = math.sin((step - 1964) * math.pi / 12)
            ec += 2100.0 * intensity              # Massive ionic surge >2400 uS/cm
            ph += 1.4 * intensity                 # Alkaline shift to ~8.9
            turb += 40.0 * intensity

        # Event 4: Flash Heavy Silt / Runoff (Day 26, 07:00 - 12:00, Steps 2524 - 2544)
        elif 2524 <= step <= 2544:
            is_anomaly = 1
            event_label = "CONTAMINATION"
            anomaly_type = "HEAVY_SILT_SURGE"
            intensity = math.sin((step - 2524) * math.pi / 20)
            turb += 290.0 * intensity             # Turbidity spikes to ~300 NTU
            depth += 0.45 * intensity             # Water level rises
            velocity += 0.28 * intensity          # River flow accelerates
            ec -= 60.0 * intensity                # Dilution effect reduces EC slightly
            do -= 1.2 * intensity

        row = [
            current_time.isoformat(),
            step,
            round(ph, 3),
            round(turb, 2),
            round(temp, 2),
            round(ec, 1),
            round(do, 2),
            round(depth, 3),
            round(velocity, 3),
            event_label,
            is_anomaly,
            anomaly_type
        ]
        rows.append(row)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(rows)
        
    print(f"Generated {len(rows)-1} timeseries steps at {output_path}")

if __name__ == "__main__":
    out_csv = os.path.join(os.path.dirname(os.path.abspath(__file__)), "synthetic_river_timeseries.csv")
    generate_dataset(out_csv, days=30)
