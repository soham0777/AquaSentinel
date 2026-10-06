"""
AquaSentinel v2.0 - Dual-Track Statistical Event Detection Engine (Python Reference)
Bit-for-bit mathematical reference of firmware/edge_node/src/anomaly_engine.cpp
Adheres strictly to Appendix B: Diurnal EWMA Baselines + CPCB Hard Limits.
"""

import math

class DualTrackEventDetector:
    def __init__(self, alpha=1.0/96.0):
        self.alpha = alpha
        
        # 24 Diurnal Bins for pH, DO, Temperature [mu, d]
        self.ph_bins = [[7.50, 0.15] for _ in range(24)]
        self.do_bins = [[6.50, 0.40] for _ in range(24)]
        self.temp_bins = [[24.0, 1.00] for _ in range(24)]
        
        # Single baselines for EC and Turbidity
        self.ec_baseline = [450.0, 35.0]
        self.turb_baseline = [12.0, 3.0]
        
        # History & State
        self.outlier_history = 0 # 3-cycle bitmask
        self.normal_consecutive = 0
        self.current_risk = "NORMAL"
        self.prev_reading = None

        # Floors
        self.floors = {
            "ph": 0.05,
            "ec": 10.0,
            "do": 0.20,
            "turb": 2.0
        }

    def _compute_z(self, val, mu, d, floor_val):
        robust_s = max(1.4826 * d, floor_val)
        return abs(val - mu) / robust_s

    def evaluate(self, ph, ec, do_val, turb, temp, hour_of_day, total_cycles=700):
        """
        Evaluates a single 15-minute sensor acquisition cycle.
        Returns dict: {'level': str, 'score': float, 'flags': int, 'reason': str, 'sample_trigger': bool}
        """
        hour = int(hour_of_day) % 24
        
        # 1. CPCB Designated Best Use Class C Hard Limit Tripwires
        if ph < 6.0 or ph > 9.0:
            self.current_risk = "EVENT"
            self.normal_consecutive = 0
            return {
                "level": "EVENT",
                "score": 99.0,
                "flags": 0x01,
                "reason": f"HARD_LIMIT: pH={ph:.2f} out of bounds [6.0, 9.0]",
                "sample_trigger": True
            }
        if do_val < 4.0:
            self.current_risk = "EVENT"
            self.normal_consecutive = 0
            return {
                "level": "EVENT",
                "score": 99.0,
                "flags": 0x04,
                "reason": f"HARD_LIMIT: Hypoxia DO={do_val:.2f} mg/L < 4.0 mg/L",
                "sample_trigger": True
            }
        if ec > 2250.0:
            self.current_risk = "EVENT"
            self.normal_consecutive = 0
            return {
                "level": "EVENT",
                "score": 99.0,
                "flags": 0x02,
                "reason": f"HARD_LIMIT: Effluent Spike EC={ec:.1f} uS/cm > 2250 uS/cm",
                "sample_trigger": True
            }

        # 2. Compute Robust Diurnal Z-Scores
        z_ph = self._compute_z(ph, self.ph_bins[hour][0], self.ph_bins[hour][1], self.floors["ph"])
        z_ec = self._compute_z(ec, self.ec_baseline[0], self.ec_baseline[1], self.floors["ec"])
        z_do = self._compute_z(do_val, self.do_bins[hour][0], self.do_bins[hour][1], self.floors["do"])
        z_turb = self._compute_z(turb, self.turb_baseline[0], self.turb_baseline[1], self.floors["turb"])

        flags = 0
        if z_ph > 3.0: flags |= 0x01
        if z_ec > 3.0: flags |= 0x02
        if z_do > 3.0: flags |= 0x04
        if z_turb > 3.0: flags |= 0x08

        max_z = max(z_ph, z_ec, z_do, z_turb)

        # 3. Learning Period Check (First 7 days = 672 cycles)
        if total_cycles < 672:
            self._update_baselines(ph, ec, do_val, turb, hour)
            return {
                "level": "NORMAL",
                "score": max_z,
                "flags": 0,
                "reason": f"LEARNING_PERIOD: Baseline learning ({total_cycles}/672)",
                "sample_trigger": False
            }

        # 4. Persistence Window Logic (>= 2 outliers in last 3 cycles = EVENT)
        is_outlier = (flags != 0)
        self.outlier_history = ((self.outlier_history << 1) | (1 if is_outlier else 0)) & 0x07
        
        outlier_count = bin(self.outlier_history).count("1")

        if outlier_count >= 2:
            trigger = (self.current_risk != "EVENT")
            self.current_risk = "EVENT"
            self.normal_consecutive = 0
            res = {
                "level": "EVENT",
                "score": max_z,
                "flags": flags,
                "reason": f"STAT_EVENT: Persistent anomaly (Z_max={max_z:.2f}, flags=0x{flags:02X})",
                "sample_trigger": trigger
            }
        elif outlier_count == 1:
            self.current_risk = "WATCH"
            self.normal_consecutive = 0
            res = {
                "level": "WATCH",
                "score": max_z,
                "flags": flags,
                "reason": f"STAT_WATCH: Single outlier (Z_max={max_z:.2f})",
                "sample_trigger": False
            }
        else:
            self.normal_consecutive += 1
            if self.normal_consecutive >= 4:
                self.current_risk = "NORMAL"
            
            # Update EWMA baselines ONLY during normal conditions
            if self.current_risk == "NORMAL":
                self._update_baselines(ph, ec, do_val, turb, hour)

            res = {
                "level": self.current_risk,
                "score": max_z,
                "flags": 0,
                "reason": f"NORMAL: Within diurnal bounds (Z_max={max_z:.2f})",
                "sample_trigger": False
            }

        self.prev_reading = (ph, ec, do_val, turb)
        return res

    def _update_baselines(self, ph, ec, do_val, turb, hour):
        # Update pH
        self.ph_bins[hour][0] += self.alpha * (ph - self.ph_bins[hour][0])
        self.ph_bins[hour][1] += self.alpha * (abs(ph - self.ph_bins[hour][0]) - self.ph_bins[hour][1])
        # Update EC
        self.ec_baseline[0] += self.alpha * (ec - self.ec_baseline[0])
        self.ec_baseline[1] += self.alpha * (abs(ec - self.ec_baseline[0]) - self.ec_baseline[1])
        # Update DO
        self.do_bins[hour][0] += self.alpha * (do_val - self.do_bins[hour][0])
        self.do_bins[hour][1] += self.alpha * (abs(do_val - self.do_bins[hour][0]) - self.do_bins[hour][1])
        # Update Turbidity
        self.turb_baseline[0] += self.alpha * (turb - self.turb_baseline[0])
        self.turb_baseline[1] += self.alpha * (abs(turb - self.turb_baseline[0]) - self.turb_baseline[1])
