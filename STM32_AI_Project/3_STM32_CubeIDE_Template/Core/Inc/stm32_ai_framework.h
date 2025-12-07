/*
 * STM32 AI Integration Framework
 * Using TensorFlow Lite for Microcontrollers
 * 
 * This framework provides:
 * - Model initialization
 * - Input preprocessing
 * - Inference execution
 * - Output postprocessing
 */

#ifndef STM32_AI_FRAMEWORK_H
#define STM32_AI_FRAMEWORK_H

#include <stdint.h>
#include <stdlib.h>
#include <string.h>

typedef struct {
    uint8_t* model_data;
    uint32_t model_size;
    float input_buffer[1024];
    float output_buffer[2];
    uint32_t inference_time_ms;
} FireDetectionModel;

// Initialize model
int32_t fire_detection_init(FireDetectionModel* model);

// Preprocessing
void preprocess_image(uint8_t* raw_image, uint32_t raw_size, float* normalized_image);

// Inference
float fire_detection_inference(FireDetectionModel* model);

// Postprocessing
typedef struct {
    int fire_detected;
    float confidence;
    int alert_level;
} DetectionResult;

DetectionResult process_detection_output(FireDetectionModel* model);

#endif // STM32_AI_FRAMEWORK_H
