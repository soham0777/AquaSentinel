"""
AquaSentinel - Multi-Parameter Proxy Anomaly Detection Training & Weight Exporter
Trains multivariate statistical anomaly detection on lotic water-quality timeseries.
Computes baseline feature vectors (mean, standard deviation, covariance) and exports
C++ header weights for real-time edge execution on the ESP32 microcontroller.
"""

import os
import csv
import math
import numpy as np

def train_and_export(csv_path, header_out_path):
    # Read timeseries
    normal_samples = []
    anomaly_samples = []
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # 6 physical indicators: pH, Turbidity, Temp, EC, DO, Depth
            feats = [
                float(row["ph"]),
                float(row["turbidity_ntu"]),
                float(row["temp_c"]),
                float(row["ec_us_cm"]),
                float(row["do_mg_l"]),
                float(row["depth_m"])
            ]
            if int(row["is_anomaly"]) == 0:
                normal_samples.append(feats)
            else:
                anomaly_samples.append(feats)

    X_norm = np.array(normal_samples)
    X_anom = np.array(anomaly_samples)
    
    # Baseline statistical moments
    means = np.mean(X_norm, axis=0)
    stds = np.std(X_norm, axis=0)
    cov = np.cov(X_norm, rowvar=False)
    
    # Regularized inverse covariance for Mahalanobis distance
    reg_cov = cov + np.eye(6) * 1e-4
    inv_cov = np.linalg.inv(reg_cov)

    print(f"Trained on {len(X_norm)} normal baseline epochs.")
    print("Baseline Means (pH, Turb, Temp, EC, DO, Depth):", np.round(means, 3))
    print("Baseline Stds: ", np.round(stds, 3))

    # Evaluate detection performance
    def compute_anomaly_score(x):
        diff = x - means
        # Mahalanobis distance: sqrt( (x-u)^T * InvCov * (x-u) )
        m_dist = math.sqrt(np.dot(np.dot(diff, inv_cov), diff))
        return m_dist

    norm_scores = [compute_anomaly_score(x) for x in X_norm]
    anom_scores = [compute_anomaly_score(x) for x in X_anom]

    # Threshold chosen at 99.5th percentile of normal
    threshold = float(np.percentile(norm_scores, 99.5))
    true_positives = sum(1 for s in anom_scores if s >= threshold)
    false_positives = sum(1 for s in norm_scores if s >= threshold)
    sensitivity = true_positives / len(anom_scores)
    fp_rate = false_positives / len(norm_scores)

    print(f"Optimized Anomaly Threshold: {threshold:.3f}")
    print(f"Detection Sensitivity (Recall): {sensitivity*100:.1f}%")
    print(f"False Positive Rate: {fp_rate*100:.2f}%")

    # Export C++ Header
    os.makedirs(os.path.dirname(header_out_path), exist_ok=True)
    with open(header_out_path, 'w') as f:
        f.write("/**\n")
        f.write(" * AquaSentinel ESP32 Edge Firmware - Exported Anomaly Weights\n")
        f.write(" * Multi-Parameter Lotic Proxy Anomaly Engine\n")
        f.write(" * Automatically generated from validated Maharashtra river timeseries.\n")
        f.write(" */\n\n")
        f.write("#ifndef EXPORTED_ANOMALY_WEIGHTS_H\n")
        f.write("#define EXPORTED_ANOMALY_WEIGHTS_H\n\n")
        f.write("#define NUM_FEATURES 6\n\n")
        f.write(f"// Anomaly score threshold (Mahalanobis distance metric)\n")
        f.write(f"const float ANOMALY_THRESHOLD = {threshold:.4f}f;\n\n")
        
        # Means
        f.write("// Feature baseline means: [pH, Turbidity (NTU), Temp (C), EC (uS/cm), DO (mg/L), Depth (m)]\n")
        f.write("const float BASELINE_MEANS[NUM_FEATURES] = {\n    ")
        f.write(", ".join(f"{m:.4f}f" for m in means))
        f.write("\n};\n\n")

        # Stds
        f.write("// Feature standard deviations\n")
        f.write("const float BASELINE_STDS[NUM_FEATURES] = {\n    ")
        f.write(", ".join(f"{s:.4f}f" for s in stds))
        f.write("\n};\n\n")

        # Inverse Covariance Matrix
        f.write("// Inverse Covariance Matrix (6x6) for Edge Mahalanobis Distance computation\n")
        f.write("const float INV_COVARIANCE[NUM_FEATURES][NUM_FEATURES] = {\n")
        for i in range(6):
            row_str = ", ".join(f"{inv_cov[i][j]:.6f}f" for j in range(6))
            f.write(f"    {{{row_str}}}" + (",\n" if i < 5 else "\n"))
        f.write("};\n\n")

        # Rate of change critical thresholds (per 15-minute cycle)
        f.write("// Maximum allowable 15-minute rate-of-change gradients before immediate emergency alert\n")
        f.write("const float CRITICAL_GRADIENT_PH   = 0.80f;   // delta pH / 15min\n")
        f.write("const float CRITICAL_GRADIENT_TURB = 40.0f;   // delta NTU / 15min\n")
        f.write("const float CRITICAL_GRADIENT_EC   = 250.0f;  // delta uS/cm / 15min\n")
        f.write("const float CRITICAL_GRADIENT_DO   = 2.0f;    // negative delta DO / 15min\n\n")

        f.write("#endif // EXPORTED_ANOMALY_WEIGHTS_H\n")

    print(f"Exported C++ edge weights header to {header_out_path}")

if __name__ == "__main__":
    csv_in = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dataset", "synthetic_river_timeseries.csv")
    h_out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "firmware", "edge_node", "include", "exported_anomaly_weights.h")
    train_and_export(csv_in, h_out)
