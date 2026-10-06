"""
AquaSentinel v2.0 - 1-D River Advection-Dispersion Transport Modeling Engine
Simulates lotic downstream propagation of chemical/effluent plumes along the
Godavari River corridor from Kopargaon Bridge Outfall to Puntamba (~19 km straight-line reach).

Calculates longitudinal dispersion coefficient D_L using both:
1. Fischer (1975): D_L = 0.011 * (U^2 * W^2) / (H * u*)
2. Kashefipour & Falconer (2002): D_L = [10.612 * (U/u*) + 2.0] * U * H * (W/H)^0.65
Removes arbitrary mathematical clamps and displays travel time uncertainty bands.
"""

import math
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

class LoticTransportModel:
    def __init__(self, stream_velocity=0.60, river_width=50.0, mean_depth=1.80, bed_slope=0.00035, k_decay=5e-6):
        """
        stream_velocity: mean stream velocity U (m/s)
        river_width: W (m)
        mean_depth: H (m)
        bed_slope: S (dimensionless hydraulic slope)
        k_decay: first-order reaction/decay rate (1/s)
        """
        self.U = stream_velocity
        self.W = river_width
        self.H = mean_depth
        self.S = bed_slope
        self.A = self.W * self.H  # Cross-sectional area (m^2)
        self.k = k_decay
        
        # Shear velocity u* = sqrt(g * H * S)
        g = 9.80665
        self.u_star = math.sqrt(g * self.H * self.S)

        # 1. Fischer (1975) Longitudinal Dispersion Coefficient (m^2/s)
        self.D_L_fischer = 0.011 * ((self.U ** 2) * (self.W ** 2)) / (self.H * self.u_star)

        # 2. Kashefipour & Falconer (2002) Longitudinal Dispersion Coefficient (m^2/s)
        # D_L = [10.612 * (U/u*) + 2.0] * U * H * (W/H)^0.65
        self.D_L_kashefipour = (10.612 * (self.U / self.u_star) + 2.0) * self.U * self.H * ((self.W / self.H) ** 0.65)

        # Mean representative D_L for simulation
        self.D_L_mean = (self.D_L_fischer + self.D_L_kashefipour) / 2.0

    def impulse_concentration(self, x, t, mass_kg=500.0, D_L=None):
        """
        Analytical solution for 1-D advection-dispersion equation:
        C(x,t) = (M / (A * sqrt(4 * pi * D_L * t))) * exp(- (x - U*t)^2 / (4 * D_L * t) - k*t)
        Returns concentration in mg/L (g/m^3).
        """
        if t <= 0:
            return 0.0
        d_val = D_L if D_L is not None else self.D_L_mean
        denom = self.A * math.sqrt(4.0 * math.pi * d_val * t)
        if denom == 0:
            return 0.0
        diff = x - self.U * t
        exponent = - (diff ** 2) / (4.0 * d_val * t) - self.k * t
        if exponent < -50.0:
            return 0.0
        return (mass_kg * 1000.0 / denom) * math.exp(exponent)

def simulate_plume_transport():
    print("=================================================================")
    print(" AQUASENTINEL v2.0 - LOTIC ADVECTION-DISPERSION MODEL")
    print(" Reach: Kopargaon Bridge Outfall -> Puntamba Corridor (~19 km)")
    print(" (SCENARIO, NOT A FORECAST - THEORETICAL 1-D SIMULATION)")
    print("=================================================================")

    # Model baseline across Godavari reach
    model = LoticTransportModel(stream_velocity=0.60, river_width=50.0, mean_depth=1.80)
    print(f"\n[HYDRODYNAMIC PARAMETERS]")
    print(f"  Stream Flow Velocity (U):         {model.U:.2f} m/s ({model.U*3.6:.2f} km/h)")
    print(f"  River Channel Width (W):          {model.W:.1f} m")
    print(f"  Mean Hydraulic Depth (H):         {model.H:.2f} m")
    print(f"  Shear Velocity (u*):              {model.u_star:.4f} m/s")
    print(f"  D_L (Fischer 1975 Model):         {model.D_L_fischer:.2f} m^2/s")
    print(f"  D_L (Kashefipour & Falconer 2002): {model.D_L_kashefipour:.2f} m^2/s")
    print(f"  D_L Mean Modeling Baseline:       {model.D_L_mean:.2f} m^2/s")

    # Downstream Receptors along the Godavari River reach:
    # 1. Local Agricultural Lift Scheme (4.5 km)
    # 2. Intermediate Rural Intake (11.0 km)
    # 3. Puntamba Riverbank Ghats & Lift (19.0 km straight-line distance; river sinuosity ~1.2 => ~22.8 km channel length)
    receptors = [
        ("Downstream Lift Scheme", 4500),
        ("Intermediate Rural Intake", 11000),
        ("Puntamba Riverbank Ghats", 19000)
    ]

    time_hours = np.linspace(0.1, 16.0, 500)
    time_sec = time_hours * 3600.0
    mass_kg = 500.0 # 500 kg chemical effluent shock load

    plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    colors = ["#1f77b4", "#ff7f0e", "#2ca02c"]

    # Left Subplot: Breakthrough Concentration Curves at Receptors
    for (name, dist), col in zip(receptors, colors):
        c_fischer = [model.impulse_concentration(dist, t, mass_kg, model.D_L_fischer) for t in time_sec]
        c_kashef = [model.impulse_concentration(dist, t, mass_kg, model.D_L_kashefipour) for t in time_sec]
        c_mean = [model.impulse_concentration(dist, t, mass_kg, model.D_L_mean) for t in time_sec]

        # Find peak arrival time
        peak_idx = np.argmax(c_mean)
        peak_hr = time_hours[peak_idx]
        peak_c = c_mean[peak_idx]

        ax1.plot(time_hours, c_mean, color=col, linewidth=2.0, label=f"{name} ({dist/1000:.1f} km, Peak: {peak_hr:.1f}h)")
        ax1.fill_between(time_hours, c_fischer, c_kashef, color=col, alpha=0.15)
        ax1.plot(peak_hr, peak_c, marker='o', color=col)

    ax1.set_xlabel("Time Elapsed Since Outfall Pulse (Hours)")
    ax1.set_ylabel("Contaminant Concentration (mg/L)")
    ax1.set_title("Plume Breakthrough Concentration Curves\n(Band shows Fischer 1975 vs Kashefipour 2002 D_L range)", fontweight="bold")
    ax1.set_xlim(0, 16)
    ax1.legend(loc="upper right")

    # Right Subplot: Travel Time Uncertainty Band (U = 0.2 to 1.0 m/s)
    dist_km = np.linspace(1.0, 25.0, 100)
    dist_m = dist_km * 1000.0

    t_slow_hr = (dist_m / 0.20) / 3600.0 # 0.2 m/s dry-season low flow
    t_fast_hr = (dist_m / 1.00) / 3600.0 # 1.0 m/s monsoon flow
    t_nom_hr = (dist_m / 0.60) / 3600.0  # 0.6 m/s nominal flow

    ax2.plot(dist_km, t_nom_hr, color="#d62728", linewidth=2.0, label="Nominal Flow (U = 0.60 m/s)")
    ax2.fill_between(dist_km, t_fast_hr, t_slow_hr, color="#d62728", alpha=0.20, label="Flow Velocity Band (0.2 - 1.0 m/s)")
    
    # Highlight Puntamba Reach
    puntamba_dist = 19.0
    puntamba_nom_hr = (puntamba_dist * 1000.0 / 0.60) / 3600.0
    ax2.axvline(puntamba_dist, color="purple", linestyle="--", label=f"Puntamba Ghats ({puntamba_dist} km)")
    ax2.text(puntamba_dist + 0.5, 10, f"Puntamba Arrival Window:\n{puntamba_dist*1000/1.0/3600:.1f}h to {puntamba_dist*1000/0.2/3600:.1f}h\n(Nominal: ~{puntamba_nom_hr:.1f}h)", 
             color="purple", fontweight="bold", fontsize=9)

    ax2.set_xlabel("Downstream Distance from Kopargaon Station (km)")
    ax2.set_ylabel("Plume Arrival Travel Time (Hours)")
    ax2.set_title("Downstream Plume Travel Scenario\n(Theoretical Advection-Dispersion Simulation, Not a Forecast)", fontweight="bold")
    ax2.set_xlim(0, 25)
    ax2.set_ylim(0, 35)
    ax2.legend(loc="upper left")

    plt.tight_layout()
    plot_path = os.path.join(os.path.dirname(__file__), "advection_dispersion_breakthrough_curves.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"\n  Saved updated breakthrough curves: {plot_path}")
    print("=================================================================\n")

if __name__ == "__main__":
    simulate_plume_transport()
