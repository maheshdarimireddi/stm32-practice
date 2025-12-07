# STM32 AI Project - Main README

## Project Overview

Complete AI/ML integration framework for STM32 microcontrollers with fire detection as the demonstration use case.

**Folder Structure**:
```
STM32_AI_Project/
├── 1_Documentation/              ← Read first
│   └── STM32_AI_INTEGRATION_GUIDE.md
├── 2_Desktop_Tools/              ← Develop & test here
│   ├── stm32_model_converter.py
│   ├── stm32_ai_testing.py
│   ├── requirements.txt
│   └── README.md
└── 3_STM32_CubeIDE_Template/     ← Deploy to hardware
    ├── Core/
    │   ├── Inc/
    │   └── Src/
    ├── Models/
    ├── Middleware/
    └── README.md
```

## Quick Start

### For Desktop Development & Testing

1. **Setup Python environment**:
   ```bash
   cd 2_Desktop_Tools
   python -m venv env
   source env/bin/activate  # Windows: env\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Convert your trained model**:
   ```bash
   python stm32_model_converter.py --input fire_detection_model.h5 --output Models/
   ```

3. **Test on desktop**:
   ```bash
   python stm32_ai_testing.py --model Models/model.tflite --samples 100
   ```

4. **View generated C code**:
   - `Models/model_data.h` - Contains quantized weights as C array

### For STM32 Hardware Deployment

1. **Read integration guide**:
   - Open `1_Documentation/STM32_AI_INTEGRATION_GUIDE.md`

2. **Create CubeIDE project**:
   - Use `3_STM32_CubeIDE_Template/` as reference

3. **Copy template files**:
   - Core/Inc files → Your Project/Core/Inc
   - Core/Src files → Your Project/Core/Src
   - Generated `model_data.h` → Your Project/Core/Inc

4. **Configure & compile**:
   - Add include paths
   - Add model file to project
   - Compile and debug

## File Organization

### 1_Documentation/
**Comprehensive integration guide** covering:
- Architecture overview
- System design patterns
- File organization in CubeIDE
- Step-by-step integration
- Debugging tips
- Performance optimization

**Read this first** for understanding the full workflow.

### 2_Desktop_Tools/
**Python utilities for model development**:

#### stm32_model_converter.py
- Loads Keras `.h5` models
- Converts to TensorFlow Lite
- Quantizes to int8 (4x size reduction)
- Generates C++ headers with model weights
- Outputs: `model.tflite`, `model_data.h`, metadata

#### stm32_ai_testing.py
- Simulates STM32 inference on desktop
- Generates synthetic test data
- Calculates accuracy metrics
- Profiles performance
- Estimates memory usage

#### requirements.txt
Dependencies:
- TensorFlow 2.12+ (model conversion)
- NumPy (numerical computing)
- OpenCV (image processing for testing)

### 3_STM32_CubeIDE_Template/
**Ready-to-use STM32 project template**:

#### Core/Inc/
- `stm32_ai_framework.h` - Main inference framework with structs and declarations
- `model_data.h` - Generated model weights (from Desktop Tools)
- `main.h` - Project-specific headers

#### Core/Src/
- `main.c` - Complete firmware template with main loop
- `ai_inference.c` - Inference implementation (preprocessing, model run, postprocessing)
- `stm32fxxx_it.c` - Interrupt handlers

#### Models/
- `model.tflite` - Copy generated model here
- `model_info.json` - Model metadata

#### Middleware/
- `tensorflow_lite/` - TFLite library (download separately)

## Workflow: Desktop → Hardware

```
┌─────────────────┐
│  Train Model    │
│  (TensorFlow)   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  2_Desktop_Tools/           │
│  stm32_model_converter.py   │  ← Convert & Quantize
│  Outputs: model_data.h      │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────┐
│  2_Desktop_Tools/           │
│  stm32_ai_testing.py        │  ← Test & Validate
│  Outputs: accuracy metrics  │
└────────┬────────────────────┘
         │ (If tests pass)
         ▼
┌──────────────────────────────────────┐
│  3_STM32_CubeIDE_Template/           │
│  Copy files to CubeIDE project       │
│  - model_data.h → Core/Inc/          │
│  - model.tflite → Models/            │
│  - ai_inference.c → Core/Src/        │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  STM32CubeIDE                        │
│  - Configure compiler paths          │
│  - Add TFLite library                │
│  - Compile & Flash                   │
│  - Debug on hardware                 │
└──────────────────────────────────────┘
```

## Technical Details

### Model Conversion
```python
# Input: fire_detection_model.h5 (trained Keras model)
# Process:
#   1. Load Keras model
#   2. Convert to TensorFlow Lite
#   3. Quantize to int8 (reduces size 4x)
#   4. Generate C++ header array
# Output: model_data.h (~50KB)
```

### Hardware Target
- **MCU**: STM32H743 (recommended)
  - 480 MHz Cortex-M7
  - 2MB Flash, 1MB RAM
  - Adequate for fire detection model
  
### Performance Budget
```
Input Preprocessing:   10ms
Model Inference:       35ms
Output Postprocessing: 5ms
Sensor I/O:           5ms
─────────────────────────
Total Cycle Time:     55ms ≈ 18 FPS
```

### Model Size
```
Quantized Model:  48 KB
Runtime Memory:   50 KB
Buffers:          100 KB
─────────────────────────
Total:           ~200 KB (well under 2MB limit)
```

## Use Cases

1. **Fire Detection**: Real-time flame detection with minimal false positives
2. **Sensor Fusion**: Integrate multiple sensors with AI inference
3. **Edge Computing**: Run ML models directly on embedded devices
4. **Low Power**: Optimized for battery-powered applications

## Support & Troubleshooting

### Common Issues

**Model too large for STM32**:
- Solution: Use provided quantization (int8)
- Typically reduces size 4x without accuracy loss

**Poor accuracy on hardware**:
- Solution: Run desktop tests before deployment
- Validate preprocessing matches training data

**Compilation errors**:
- Solution: Check include paths, verify TFLite library added

### Getting Help

1. Check relevant README files in each folder
2. Review STM32_AI_INTEGRATION_GUIDE.md
3. Consult C code comments for implementation details

## Next Steps

1. **Immediate**: Read `1_Documentation/STM32_AI_INTEGRATION_GUIDE.md`
2. **Short-term**: Run desktop tools to convert and test your model
3. **Medium-term**: Create CubeIDE project using template
4. **Final**: Deploy to hardware and iterate

## Files Generated During Development

The following files are automatically generated:

```
After Model Conversion:
  Models/
    ├── model.tflite          (30-50 KB)
    ├── model_data.h          (auto-generated C header)
    └── model_info.json       (metadata)

In CubeIDE Project:
  Core/Inc/
    └── model_data.h          (copy of generated file)
  
  Models/
    └── model.tflite          (copy of converted model)
```

## Version Info

- **Framework**: STM32 AI Framework v1.0
- **TensorFlow Lite**: v2.12+
- **STM32CubeIDE**: v1.14+
- **Target MCUs**: STM32H7, STM32F7 series
- **Python**: 3.8+

## License

This framework is provided as-is for educational and commercial use.

