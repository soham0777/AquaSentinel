#ifndef DSP_FILTERS_H
#define DSP_FILTERS_H

#include <Arduino.h>

class DigitalFilter {
public:
    // Computes the median of an array of 5 samples to reject random bubble / eddy outliers
    static float computeMedian5(float samples[5]);

    // Exponential Moving Average (EMA) to smooth turbulent wave ripples
    static float applyEMA(float current_val, float prev_filtered, float alpha = 0.25f);
};

#endif // DSP_FILTERS_H
