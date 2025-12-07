# Desktop Tools README

## Overview

This folder contains Python tools for:
- **Model Conversion**: Keras → TensorFlow Lite → C++ embedded format
- **Desktop Testing**: Validate models before hardware deployment
- **Performance Analysis**: Profile inference speed, memory usage

## Files

### stm32_model_converter.py
Converts trained Keras fire detection models to STM32-compatible format:
- Loads `.h5` model files
- Quantizes to int8 (reduce size 4x)
- Generates C header arrays
- Estimates memory footprint

**Usage**:
```python
converter = ModelConverter("fire_detection_model.h5", "output/")
converter.convert_to_tflite(quantize=True, int8=True)
converter.generate_c_header()
```

### stm32_ai_testing.py
Desktop simulator and testing framework:
- Generates synthetic test images (fire/no-fire)
- Simulates STM32 inference
- Calculates accuracy metrics
- Profiles inference timing

**Usage**:
```python
simulator = STM32Simulator("model.tflite")
suite = TestSuite(simulator)
suite.run_comprehensive_tests(100)
suite.print_report()
```

## Workflow

1. **Setup Python Environment**:
   ```bash
   python -m venv stm32_ai_env
   source stm32_ai_env/bin/activate  # or stm32_ai_env\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Convert Your Model**:
   ```bash
   python stm32_model_converter.py --input fire_detection_model.h5 --output Models/
   ```

3. **Test on Desktop**:
   ```bash
   python stm32_ai_testing.py --model Models/model.tflite --samples 100
   ```

4. **Copy to CubeIDE**:
   - Copy generated `model_data.h` to `Core/Inc/`
   - Copy `model.tflite` to project's Models folder
   - Compile and deploy

## Expected Outputs

### After Model Conversion
- `model.tflite` (30-50KB quantized)
- `model_data.h` (C++ header with weights as array)
- `model_info.json` (metadata)

### After Testing
```
Fire Detection Model Test Report
==================================
Accuracy:   94.2%
Precision:  92.1%
Recall:     96.3%
F1-Score:   94.1%

Inference Statistics:
  Average:  35.4 ms
  Min:      32.1 ms
  Max:      41.2 ms

Memory Footprint:
  Model:    48.2 KB
  Runtime:  ~50 KB
  Total:    ~100 KB
```

## Troubleshooting

**Model too large for MCU**:
- Check estimated memory in test output
- STM32H743: 2MB flash (model ~500KB max recommended)
- STM32H733: 1MB flash (model ~200KB max recommended)

**Poor accuracy on hardware**:
- Run desktop test suite first
- Check quantization settings
- Verify preprocessing matches deployment

**Slow inference**:
- Profile with timing stats
- Reduce model complexity
- Enable HW acceleration if available

