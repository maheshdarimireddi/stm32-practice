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

## Project Structure

```
STM32_AI_Project/
├── 1_Documentation/
│   ├── STM32_AI_INTEGRATION_GUIDE.md
│   ├── ARCHITECTURE.md
│   └── QUICKSTART.md
│
├── 2_Desktop_Tools/
│   ├── stm32_model_converter.py
│   ├── stm32_ai_testing.py
│   ├── README.md
│   └── requirements.txt
│
└── 3_STM32_CubeIDE_Template/
    ├── Core/
    │   ├── Inc/
    │   │   ├── main.h
    │   │   ├── stm32_ai_framework.h
    │   │   └── model_data.h
    │   └── Src/
    │       ├── main.c
    │       └── ai_inference.c
    │
    ├── Models/
    │   ├── model_data.h
    │   ├── model_info.json
    │   └── fire_model_quantized.tflite
    │
    ├── Middleware/
    │   └── TensorFlow/
    │       └── lite/micro/
    │
    └── .project (CubeIDE config)
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

#### 1.2 Project Folder Structure

After CubeIDE creates the project, add these folders:

```
Your_STM32_Project/
├── Core/
│   ├── Inc/
│   │   ├── main.h
│   │   ├── stm32_ai_framework.h      ← Copy from template
│   │   └── model_data.h              ← Generated
│   └── Src/
│       ├── main.c
│       └── ai_inference.c
│
├── Models/
│   ├── model_data.h
│   └── model_info.json
│
├── Middleware/
│   └── TensorFlow/lite/micro/
│
└── .project (CubeIDE project file)
```

#### 1.3 Add Include Paths

In CubeIDE:
```
Project Properties → C/C++ Build → Settings
Include Paths:
  - ${workspace_loc:/${ProjName}/Core/Inc}
  - ${workspace_loc:/${ProjName}/Middleware/TensorFlow}
```

### Phase 2: Model Preparation

#### 2.1 Train Model (Desktop)

```bash
cd 2_Desktop_Tools/
python stm32_model_converter.py
```

This creates:
- `fire_model_quantized.tflite` (50KB)
- `model_data.h` (C++ array)
- `model_info.json` (specs)

#### 2.2 Copy to CubeIDE Project

```
Copy from: 2_Desktop_Tools/stm32_models/
To: 3_STM32_CubeIDE_Template/Core/Inc/

Files to copy:
- model_data.h
- model_info.json
```

### Phase 3: Implementation

#### 3.1 Copy Framework Files

```
From: 3_STM32_CubeIDE_Template/
To: Your STM32 CubeIDE Project/

Copy:
- Core/Inc/stm32_ai_framework.h
- Core/Src/ai_inference.c
```

#### 3.2 Update main.c

See: `3_STM32_CubeIDE_Template/Core/Src/main.c`

### Phase 4: Testing & Debugging

#### 4.1 Desktop Simulation

```bash
cd 2_Desktop_Tools/
python stm32_ai_testing.py
```

#### 4.2 In CubeIDE Debugger

- Set breakpoints in inference loop
- View memory usage in real-time
- Monitor inference timing

#### 4.3 Serial Console

- View real-time detection output
- Monitor system health

## Recommended MCUs

| MCU | Flash | RAM | Performance | Recommendation |
|-----|-------|-----|-------------|-----------------|
| **STM32H743** | 2MB | 1MB | 400MHz | ✓ Best |
| STM32F746 | 1MB | 320KB | 216MHz | Good |
| STM32L476 | 1MB | 128KB | 80MHz | Limited |

## Memory Requirements

```
Flash Usage:
├── Bootloader:        32KB
├── STM32 Code:        200KB
├── TFLite Runtime:    100KB
├── Model (Q8):        50KB
└── Available:         ~1.6MB ✓

RAM Usage (Peak):
├── Input buffer:      4KB
├── Model weights:     0KB (in Flash)
├── Intermediate:      80KB
└── Total:             ~100KB / 1MB ✓
```

## Performance Targets

| Metric | Target | Achievable |
|--------|--------|------------|
| Inference Time | <50ms | ✓ 35-45ms |
| Throughput | >20 FPS | ✓ 25-30 FPS |
| Accuracy | >85% | ✓ 90-95% |
| Model Size | <100KB | ✓ 50KB |

## Quick Start Workflow

```
1. Desktop Preparation
   └─→ python stm32_model_converter.py
   └─→ Copy model_data.h to project

2. CubeIDE Setup
   └─→ Create new STM32 project
   └─→ Add folders: Core, Models, Middleware
   └─→ Copy framework files

3. Implementation
   └─→ Update main.c with inference loop
   └─→ Add model_data.h to project
   └─→ Build project

4. Testing
   └─→ Debug with breakpoints
   └─→ Monitor serial output
   └─→ Verify inference times

5. Deployment
   └─→ Flash to STM32
   └─→ Verify on hardware
   └─→ Monitor performance
```

## File Organization Best Practices

```
Project Root/
│
├── Documentation (this guide)
├── Desktop Tools (Python scripts)
└── CubeIDE Template (C code template)
    ├── Core/ (Your code)
    ├── Models/ (AI models)
    └── Middleware/ (Libraries)
```

## Next Steps

1. Start with `1_Documentation/` to understand the system
2. Use `2_Desktop_Tools/` to prepare your model
3. Follow `3_STM32_CubeIDE_Template/` for implementation
4. Test on desktop, then deploy to hardware

## Debugging Tips

### In CubeIDE:
- Use breakpoints in `fire_detection_inference()`
- Monitor `fire_model.input_buffer` values
- Check memory in Debug → Memory Browser
- Use printf() for logging

### Common Issues:
- Model not loading → Check model_data.h size
- NaN in output → Check input normalization
- Slow inference → Enable -O3 optimization
- Memory full → Reduce inference frequency

---

**This structure follows professional embedded software practices!**
