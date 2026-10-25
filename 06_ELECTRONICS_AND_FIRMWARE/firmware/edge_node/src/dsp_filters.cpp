#include "dsp_filters.h"

float DigitalFilter::computeMedian5(float samples[5]) {
    float sorted[5];
    for (int i = 0; i < 5; i++) sorted[i] = samples[i];

    // Simple 5-element insertion sort
    for (int i = 1; i < 5; i++) {
        float key = sorted[i];
        int j = i - 1;
        while (j >= 0 && sorted[j] > key) {
            sorted[j + 1] = sorted[j];
            j--;
        }
        sorted[j + 1] = key;
    }
    // Return middle element
    return sorted[2];
}

float DigitalFilter::applyEMA(float current_val, float prev_filtered, float alpha) {
    if (prev_filtered <= -999.0f) {
        return current_val; // First initialization
    }
    return (alpha * current_val) + ((1.0f - alpha) * prev_filtered);
}
