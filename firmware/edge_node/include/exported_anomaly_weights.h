/**
 * AquaSentinel ESP32 Edge Firmware - Exported Anomaly Weights
 * Multi-Parameter Lotic Proxy Anomaly Engine
 * Automatically generated from validated Maharashtra river timeseries.
 */

#ifndef EXPORTED_ANOMALY_WEIGHTS_H
#define EXPORTED_ANOMALY_WEIGHTS_H

#define NUM_FEATURES 6

// Anomaly score threshold (Mahalanobis distance metric)
const float ANOMALY_THRESHOLD = 4.0112f;

// Feature baseline means: [pH, Turbidity (NTU), Temp (C), EC (uS/cm), DO (mg/L), Depth (m)]
const float BASELINE_MEANS[NUM_FEATURES] = {
    7.4483f, 8.5175f, 23.9945f, 309.9400f, 7.2036f, 1.6554f
};

// Feature standard deviations
const float BASELINE_STDS[NUM_FEATURES] = {
    0.1179f, 1.2116f, 2.2720f, 8.0385f, 0.8647f, 0.1067f
};

// Inverse Covariance Matrix (6x6) for Edge Mahalanobis Distance computation
const float INV_COVARIANCE[NUM_FEATURES][NUM_FEATURES] = {
    {358.399281f, 0.007302f, -14.320815f, -0.011622f, -6.395325f, -3.560067f},
    {0.007302f, 0.685029f, 0.092617f, -0.005414f, -0.232191f, -0.015499f},
    {-14.320815f, 0.092617f, 4.317576f, -0.007287f, -9.321887f, -0.615997f},
    {-0.011622f, -0.005414f, -0.007287f, 0.015549f, 0.017738f, -0.038198f},
    {-6.395325f, -0.232191f, -9.321887f, 0.017738f, 25.942374f, 1.854393f},
    {-3.560067f, -0.015499f, -0.615997f, -0.038198f, 1.854393f, 87.292854f}
};

// Maximum allowable 15-minute rate-of-change gradients before immediate emergency alert
const float CRITICAL_GRADIENT_PH   = 0.80f;   // delta pH / 15min
const float CRITICAL_GRADIENT_TURB = 40.0f;   // delta NTU / 15min
const float CRITICAL_GRADIENT_EC   = 250.0f;  // delta uS/cm / 15min
const float CRITICAL_GRADIENT_DO   = 2.0f;    // negative delta DO / 15min

#endif // EXPORTED_ANOMALY_WEIGHTS_H
