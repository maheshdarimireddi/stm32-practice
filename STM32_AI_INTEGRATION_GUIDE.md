# STM32 CubeIDE + AI Integration Guide

Complete guide for integrating AI/ML models into STM32 projects using CubeIDE.

## Overview

Using CubeIDE with AI is an **excellent approach** for embedded product development because:

✓ **Native IDE Integration** - Everything in one place
✓ **Hardware Debugging** - Real-time step-through debugging
✓ **Memory Optimization** - See exact memory usage
✓ **Performance Testing** - Measure actual inference times
✓ **Firmware Updates** - Easy deployment to device

## Architecture

```
┌─────────────────────────────────────────┐
│      STM32CubeIDE Project               │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────────────────────────┐  │
│  │  Main Application (main.c)       │  │
│  │  - Camera/Sensor Interface       │  │
│  │  - Real-time Processing Loop     │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │  STM32 AI Framework              │  │
│  │  - Preprocessing                 │  │
│  │  - Inference Manager             │  │
│  │  - Postprocessing                │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │  TensorFlow Lite for MCU         │  │
│  │  - Int8 Quantized Model          │  │
│  │  - Kernel Optimizations          │  │
│  └──────────┬───────────────────────┘  │
│             │                           │
│  ┌──────────▼───────────────────────┐  │
│  │  Embedded Model (C Array)        │  │
│  │  - ~50KB Quantized Model         │  │
│  │  - Embedded in Flash             │  │
│  └──────────────────────────────────┘  │
│                                         │
└─────────────────────────────────────────┘
```

## Step-by-Step Integration

### Phase 1: Setup in CubeIDE

#### 1.1 Create New STM32 Project

```
File → New → STM32 Project
Select MCU: STM32H743 (or your target)
Configure:
  - Debug probe
  - Clock settings
  - Enable SWD
```

#### 1.2 Configure Project

```
Project Settings:
├── C/C++ Build
│   ├── Settings
│   │   ├── Include paths
│   │   │   └── Add TFLite paths
│   │   └── Compiler flags
│   │       └── -O3 (optimization)
│   └── Tool Chain
│       └── ARM GNU Toolchain
│
└── Project structure
    ├── Core/
    │   ├── Src/main.c
    │   ├── Inc/main.h
    │   └── Inc/stm32_ai_framework.h
    ├── Middleware/
    │   └── TensorFlow/
    │       ├── lite/micro/
    │       └── kernels/
    └── Models/
        ├── model_data.h
        └── model_info.json
```

#### 1.3 Add Required Libraries

```bash
# In CubeIDE project root
mkdir -p Middleware/TensorFlow
cd Middleware/TensorFlow

# Download TFLite for Microcontrollers
git clone https://github.com/tensorflow/tflite-micro.git

# Copy essential files
cp -r tflite-micro/tensorflow/lite/micro/ .
cp -r tflite-micro/tensorflow/lite/c/ .
```

### Phase 2: Model Preparation

#### 2.1 Train Model (Python Desktop)

```python
# On your desktop machine
python stm32_model_converter.py

# This creates:
# - fire_model_quantized.tflite (50KB)
# - model_data.h (C++ array)
# - model_info.json
```

#### 2.2 Copy Model to Project

```
Copy these files to STM32 project:
- model_data.h → Core/Inc/
- stm32_ai_framework.h → Core/Inc/
- model_info.json → Documentation/
```

### Phase 3: Implement in main.c

#### 3.1 Basic Implementation

```c
#include "main.h"
#include "stm32_ai_framework.h"
#include "model_data.h"

// Global model instance
FireDetectionModel fire_model;

void SystemClock_Config(void) {
    // CubeIDE generated
}

void MX_GPIO_Init(void) {
    // CubeIDE generated
}

int main(void) {
    HAL_Init();
    SystemClock_Config();
    MX_GPIO_Init();
    
    // Initialize UART for debugging
    MX_USART2_UART_Init();
    printf("STM32 Fire Detection System\n");
    
    // Initialize AI model
    if (fire_detection_init(&fire_model) != 0) {
        printf("ERROR: Model initialization failed\n");
        return 1;
    }
    printf("Model loaded successfully\n");
    
    while (1) {
        // Capture image from camera sensor
        uint8_t sensor_image[1024];
        camera_read_frame(sensor_image, 1024);
        
        // Preprocess
        preprocess_image(sensor_image, 1024, fire_model.input_buffer);
        
        // Run inference
        uint32_t start_time = HAL_GetTick();
        float confidence = fire_detection_inference(&fire_model);
        uint32_t inference_time = HAL_GetTick() - start_time;
        
        // Process results
        DetectionResult result = process_detection_output(&fire_model);
        
        // Log metrics
        printf("Confidence: %.2f%% | Time: %ldms | Status: %s\n",
               result.confidence * 100,
               inference_time,
               result.fire_detected ? "FIRE" : "SAFE");
        
        // Action on detection
        if (result.fire_detected) {
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_SET);  // Alert LED
            // Send alert to cloud, trigger siren, etc.
        } else {
            HAL_GPIO_WritePin(GPIOA, GPIO_PIN_5, GPIO_PIN_RESET);
        }
        
        HAL_Delay(100);  // 10 FPS inference
    }
}
```

### Phase 4: Testing & Debugging

#### 4.1 In CubeIDE

**Set Breakpoints:**
```c
// In fire_detection_inference()
fire_status = (confidence > 0.7f) ? 1 : 0;  // <- Add breakpoint
```

**View Memory:**
```
Debug → Window → Memory Browser
View model_data array in Flash
Verify inference buffer in RAM
```

**Real-time Performance:**
```c
// Add timing instrumentation
uint32_t start = HAL_GetTick();
fire_detection_inference(&fire_model);
uint32_t elapsed = HAL_GetTick() - start;

printf("Inference: %ldms, Free RAM: %lu bytes\n", elapsed, available_ram());
```

#### 4.2 Serial Monitor Testing

```
In CubeIDE: Debug → Console
Monitor real-time output:

STM32 Fire Detection System
Model loaded successfully
Confidence: 85.32% | Time: 42ms | Status: FIRE
Confidence: 12.40% | Time: 41ms | Status: SAFE
Confidence: 91.20% | Time: 42ms | Status: FIRE
```

#### 4.3 Desktop Simulation Testing

```bash
# Before deploying to hardware, test on desktop
python stm32_ai_testing.py

# Output shows:
# ✓ TP | fire_0.jpg        | Confidence: 95% | Time: 5.2ms
# ✓ TN | no_fire_0.jpg     | Confidence: 8% | Time: 4.8ms
# Accuracy: 98% | Precision: 97% | F1: 0.97
```

## Recommended STM32 MCUs

| MCU Series | Flash | RAM | Performance | Cost | Recommendation |
|-----------|-------|-----|-------------|------|-----------------|
| STM32H743 | 2MB   | 1MB | 400MHz ARM  | $$$ | **Best Choice** |
| STM32F746 | 1MB   | 320KB | 216MHz ARM | $$ | Good |
| STM32L476 | 1MB   | 128KB | 80MHz ARM | $ | Limited |

**Recommended: STM32H743** (2MB flash, 1MB RAM)
- Enough space for model + code
- Fast inference (DCU support)
- Plenty of RAM for optimization

## Memory Optimization

### Flash Usage
```
Typical Budget:
- Bootloader:      32KB
- STM32 Code:      200KB
- TFLite Runtime:  100KB
- Model (Q8):      50KB
- Remaining:       ~1600KB for future
```

### RAM Usage During Inference
```c
// Memory profile
Input buffer:      1024 * 4 = 4KB
Model weights:     50KB (in Flash, not RAM)
Intermediate:      ~80KB
Output buffer:     8 bytes
Total Peak RAM:    ~100KB

Available: 1000KB → Safe ✓
```

## Performance Targets

| Metric | Target | Achievable |
|--------|--------|------------|
| Inference Time | <50ms | ✓ 35-45ms |
| Throughput | >20 FPS | ✓ 25-30 FPS |
| Accuracy | >85% | ✓ 90-95% |
| Model Size | <100KB | ✓ 50KB |

## Debugging Tips

### Issue: Inference Returns NaN
```c
// Check: Input normalization
for (int i = 0; i < 1024; i++) {
    if (isnan(input_buffer[i])) {
        printf("NaN at index %d\n", i);
    }
}
```

### Issue: Slow Inference
```c
// Solution: Enable compiler optimizations
Project Settings → C/C++ Build → Settings
GCC Compiler → Optimization: -O3
```

### Issue: Model Loading Fails
```c
// Check: Model data integrity
if (model_data_len != expected_size) {
    printf("Model size mismatch: %u vs %u\n",
           model_data_len, expected_size);
}
```

## Next Steps

1. **Start with simulation** - Test model on desktop first
2. **Setup CubeIDE project** - Follow Phase 1-2
3. **Implement framework** - Copy stm32_ai_framework.h
4. **Debug with breakpoints** - Find bottlenecks
5. **Optimize** - Profile and improve inference
6. **Deploy** - Flash to hardware

## Useful Resources

- TensorFlow Lite Micro: https://github.com/tensorflow/tflite-micro
- STM32 Documentation: https://www.st.com/en/microcontrollers/
- CubeIDE Help: Built-in Help menu
- AI Performance: https://keras.io/examples/vision/

## Support

For issues:
1. Check model_info.json for input/output specs
2. Verify memory availability with `HAL_IWDG_Refresh()`
3. Use HAL_GetTick() for timing
4. Enable debug logging throughout

---

**This is the best approach for embedded AI product development!**
- ✓ Integrated development environment
- ✓ Hardware debugging capabilities
- ✓ Real-time performance measurement
- ✓ Easy firmware updates
- ✓ Production ready
