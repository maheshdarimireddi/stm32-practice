# CubeIDE Template README

## Overview

This folder contains the STM32CubeIDE template structure for integrating AI inference.

## Folder Structure

```
3_STM32_CubeIDE_Template/
├── Core/
│   ├── Inc/                    # Header files
│   │   ├── stm32_ai_framework.h    # Main AI framework
│   │   ├── model_data.h             # Quantized model weights
│   │   └── main.h               # Project headers
│   └── Src/                    # Implementation files
│       ├── main.c                  # Main firmware
│       ├── ai_inference.c          # Inference implementation
│       └── stm32fxxx_it.c      # Interrupt handlers
├── Models/                     # Pre-trained models
│   └── model.tflite            # Quantized model (from Desktop Tools)
└── Middleware/                 # TensorFlow Lite for Microcontrollers
    └── tensorflow_lite/        # TFLite library files
```

## Integration Steps

### 1. Create CubeIDE Project

- **MCU Selection**: STM32H743 (2MB flash, 1MB RAM) recommended
- **Features Enable**:
  - UART for debugging
  - GPIO for fire alerts (optional)
  - SPI/I2C for sensor interface (optional)

### 2. Copy Template Files

```bash
# From 3_STM32_CubeIDE_Template to your CubeIDE project:
cp Core/Inc/stm32_ai_framework.h        -> YourProject/Core/Inc/
cp Core/Inc/model_data.h                -> YourProject/Core/Inc/
cp Core/Src/ai_inference.c              -> YourProject/Core/Src/
cp Core/Src/main.c                      -> YourProject/Core/Src/  # Merge with existing
cp Models/model.tflite                  -> YourProject/Models/
```

### 3. Add TensorFlow Lite Library

Download: https://github.com/tensorflow/tflite-micro

```bash
# Extract to:
# YourProject/Middleware/tensorflow_lite/
```

### 4. Configure Compiler Settings

**Include Paths**:
```
Core/Inc
Middleware/tensorflow_lite/
Middleware/tensorflow_lite/tensorflow/lite/micro/
```

**Compiler Flags** (STM32H743):
```
-mcpu=cortex-m7 -mthumb -mfpu=fpv5-sp-d16 -mfloat-abi=hard
```

### 5. Implement Sensor Interface

Modify `main.c` to read from your fire detection sensor:

```c
// In main loop
uint8_t sensor_data[1024];  // Raw sensor data
float inference_result;

// Read sensor data
sensor_read(sensor_data, 1024);

// Preprocess
preprocess_image(sensor_data, 1024, model.input_buffer);

// Run inference
inference_result = fire_detection_inference(&model);

// Process output
result = process_detection_output(&model);

// Alert if fire detected
if (result.fire_detected) {
    alert_fire();
}
```

### 6. Debug & Test

- Use breakpoints in `ai_inference.c`
- Monitor UART output for inference times
- Validate accuracy on test data before deployment

## Key Files

| File | Purpose | Size |
|------|---------|------|
| `stm32_ai_framework.h` | Framework definitions | ~2KB |
| `model_data.h` | Quantized weights | ~50KB |
| `ai_inference.c` | Inference engine | ~5KB |
| `main.c` | Firmware template | ~4KB |
| `model.tflite` | TFLite binary | 30-50KB |

**Total Flash Estimated**: ~150-200KB

## Performance

### STM32H743 Specs
- **CPU**: 480 MHz Cortex-M7
- **Flash**: 2MB
- **RAM**: 1MB
- **Inference Time**: 30-50ms (depends on model size)

### Expected Performance
```
Model Inference:  35ms
Sensor Read:      5ms
Preprocessing:    10ms
Postprocessing:   2ms
Total Cycle:      52ms ≈ 19 FPS
```

## Troubleshooting

### Compilation Errors

**Error**: `undefined reference to 'tensorflow'`
- Solution: Add TFLite library to linker
- Check Include Paths in project settings

**Error**: `model_data.h not found`
- Solution: Run `stm32_model_converter.py` to generate file
- Place in `Core/Inc/`

### Runtime Issues

**Fire always detected**:
- Check confidence threshold in `process_detection_output()`
- Validate model quantization in Desktop Tools

**Slow inference**:
- Profile with HAL timer
- Consider reducing model size
- Check compiler optimization levels (-O2)

### Memory Issues

**Out of RAM**:
- Reduce input buffer size
- Use smaller model
- Check for memory leaks

## Next Steps

1. Download fire detection model from Desktop Tools
2. Convert with `stm32_model_converter.py`
3. Copy files following Integration Steps
4. Compile and test
5. Deploy to hardware

