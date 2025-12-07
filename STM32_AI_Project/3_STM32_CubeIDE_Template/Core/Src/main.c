/*
 * STM32 Fire Detection - Main Application
 * Template for STM32CubeIDE project
 */

#include "main.h"
#include "stm32_ai_framework.h"
#include "model_data.h"

// Global model instance
FireDetectionModel fire_model;

void SystemClock_Config(void) {
    // CubeIDE generated clock configuration
}

void MX_GPIO_Init(void) {
    // CubeIDE generated GPIO initialization
    // Configure LED on GPIO_PIN_5 for fire alert
    GPIO_InitTypeDef GPIO_InitStruct = {0};
    
    __HAL_RCC_GPIOA_CLK_ENABLE();
    
    GPIO_InitStruct.Pin = GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_LOW;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
}

void MX_USART2_UART_Init(void) {
    // CubeIDE generated UART initialization
    // For serial debugging and output
}

/**
 * Main application loop
 */
int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    MX_USART2_UART_Init();
    
    printf("=== STM32 Fire Detection System ===\n");
    printf("Initializing AI model...\n");
    
    // Initialize AI model
    if (fire_detection_init(&fire_model) != 0) {
        printf("ERROR: Model initialization failed\n");
        return 1;
    }
    printf("✓ Model loaded successfully\n");
    
    uint32_t frame_count = 0;
    uint32_t detections = 0;
    
    while (1) {
        // Capture image from camera sensor
        // This is a placeholder - implement with your camera driver
        uint8_t sensor_image[1024];
        // camera_read_frame(sensor_image, 1024);
        
        // For demo: generate synthetic frame
        for (int i = 0; i < 1024; i++) {
            sensor_image[i] = (frame_count % 256);
        }
        
        // Preprocess image
        preprocess_image(sensor_image, 1024, fire_model.input_buffer);
        
        // Run inference
        uint32_t start_time = HAL_GetTick();
        float confidence = fire_detection_inference(&fire_model);
        fire_model.inference_time_ms = HAL_GetTick() - start_time;
        
        // Process results
        DetectionResult result = process_detection_output(&fire_model);
        
        // Log metrics
        printf("[%lu] Confidence: %.2f%% | Time: %ldms | Status: %s\n",
               frame_count,
               result.confidence * 100,
               fire_model.inference_time_ms,
               result.fire_detected ? "FIRE" : "SAFE");
        
        // Action on fire detection
        if (result.fire_detected) {
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);  // Turn on alert LED
            detections++;
            printf("  ⚠ FIRE ALERT (Total: %lu)\n", detections);
            
            // Additional actions:
            // - Trigger siren/buzzer
            // - Send alert to cloud
            // - Log to SD card
            // - Activate suppression system
        } else {
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);  // Turn off alert LED
        }
        
        frame_count++;
        
        // Run inference at 10 FPS (100ms interval)
        HAL_Delay(100);
        
        // Safety check: reset watchdog
        // HAL_IWDG_Refresh(&hiwdg);
    }
}

/**
 * Error handler
 */
void Error_Handler(void) {
    printf("ERROR: System error occurred\n");
    while (1) {
        // Blink LED to indicate error
        HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
        HAL_Delay(200);
    }
}

/**
 * Printf redirection (for debugging)
 */
int _write(int file, char *ptr, int len) {
    HAL_UART_Transmit(&huart2, (uint8_t*)ptr, len, 0xFFFFFFFF);
    return len;
}
