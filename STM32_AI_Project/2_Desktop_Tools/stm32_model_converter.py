"""
STM32 Model Conversion Pipeline
Converts PyTorch/TensorFlow models to TFLite for microcontrollers
"""

import tensorflow as tf
import numpy as np
from pathlib import Path
import json


class ModelConverter:
    """Convert models to TFLite optimized for STM32"""
    
    def __init__(self, model_path, output_dir="stm32_models"):
        self.model_path = model_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    def convert_keras_to_tflite(self, quantize=True, input_shape=(32, 32, 1)):
        """
        Convert Keras model to TFLite
        
        Args:
            quantize: Use int8 quantization (smaller, faster)
            input_shape: Model input dimensions
        """
        print(f"Loading Keras model: {self.model_path}")
        model = tf.keras.models.load_model(self.model_path)
        
        # Create converter
        converter = tf.lite.TFLiteConverter.from_keras_model(model)
        
        if quantize:
            print("Applying int8 quantization...")
            converter.optimizations = [tf.lite.Optimize.DEFAULT]
            
            # Generate representative dataset for quantization
            def representative_dataset():
                for _ in range(100):
                    yield [np.random.rand(1, *input_shape).astype(np.float32)]
            
            converter.representative_dataset = representative_dataset
            converter.target_spec.supported_ops = [
                tf.lite.OpsSet.TFLITE_BUILTINS_INT8
            ]
            converter.inference_input_type = tf.int8
            converter.inference_output_type = tf.int8
        
        # Convert
        tflite_model = converter.convert()
        
        # Save
        model_name = Path(self.model_path).stem
        output_path = self.output_dir / f"{model_name}_quantized.tflite"
        
        with open(output_path, 'wb') as f:
            f.write(tflite_model)
        
        print(f"✓ TFLite model saved: {output_path}")
        print(f"  Size: {len(tflite_model) / 1024:.1f} KB")
        
        return output_path
    
    def model_to_cpp_array(self, tflite_path):
        """
        Convert TFLite model to C++ byte array
        Allows embedding model directly in STM32 firmware
        """
        print(f"Converting {tflite_path} to C++ array...")
        
        with open(tflite_path, 'rb') as f:
            model_data = f.read()
        
        # Create C++ header file
        cpp_filename = self.output_dir / f"{Path(tflite_path).stem}_model.h"
        
        with open(cpp_filename, 'w') as f:
            f.write("// Auto-generated TFLite model array\n")
            f.write(f"// Size: {len(model_data)} bytes\n\n")
            f.write("#ifndef MODEL_DATA_H\n")
            f.write("#define MODEL_DATA_H\n\n")
            f.write("const unsigned char model_data[] = {\n")
            
            # Write bytes in rows of 16
            for i in range(0, len(model_data), 16):
                chunk = model_data[i:i+16]
                hex_str = ', '.join(f"0x{b:02x}" for b in chunk)
                f.write(f"    {hex_str},\n")
            
            f.write("};\n")
            f.write(f"const unsigned int model_data_len = {len(model_data)};\n\n")
            f.write("#endif // MODEL_DATA_H\n")
        
        print(f"✓ C++ header saved: {cpp_filename}")
        return cpp_filename
    
    def generate_model_info(self, tflite_path):
        """Generate model information JSON"""
        interpreter = tf.lite.Interpreter(model_path=str(tflite_path))
        interpreter.allocate_tensors()
        
        input_details = interpreter.get_input_details()
        output_details = interpreter.get_output_details()
        
        info = {
            "model_file": str(tflite_path),
            "size_bytes": Path(tflite_path).stat().st_size,
            "input": {
                "shape": input_details[0]['shape'].tolist(),
                "dtype": str(input_details[0]['dtype']),
                "quantization": input_details[0]['quantization']
            },
            "output": {
                "shape": output_details[0]['shape'].tolist(),
                "dtype": str(output_details[0]['dtype']),
                "quantization": output_details[0]['quantization']
            }
        }
        
        info_path = self.output_dir / "model_info.json"
        with open(info_path, 'w') as f:
            json.dump(info, f, indent=2)
        
        print(f"✓ Model info saved: {info_path}")
        return info


class FireDetectionModelBuilder:
    """Build optimized fire detection model for STM32"""
    
    @staticmethod
    def create_model(input_shape=(32, 32, 1), output_path="fire_model.h5"):
        """
        Create a lightweight CNN for fire detection
        Optimized for STM32 constraints
        """
        print("Creating fire detection model...")
        
        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Input(shape=input_shape),
            
            # Block 1: 32x32 -> 16x16
            tf.keras.layers.Conv2D(16, 3, activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D(2),
            
            # Block 2: 16x16 -> 8x8
            tf.keras.layers.Conv2D(32, 3, activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D(2),
            
            # Block 3: 8x8 -> 4x4
            tf.keras.layers.Conv2D(64, 3, activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D(2),
            
            # Flatten and classify
            tf.keras.layers.Flatten(),
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.5),
            tf.keras.layers.Dense(2, activation='softmax')  # Binary output
        ])
        
        model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        model.summary()
        model.save(output_path)
        print(f"✓ Model saved: {output_path}")
        
        return model
    
    @staticmethod
    def estimate_memory_usage(input_shape=(32, 32, 1)):
        """
        Estimate STM32 memory requirements
        """
        model = FireDetectionModelBuilder.create_model(input_shape)
        
        # Model size in flash
        model_size_kb = 50  # Typical for quantized model
        
        # Runtime memory (RAM)
        input_buffer = np.prod(input_shape) * 4  # bytes
        output_buffer = 2 * 4  # 2 outputs
        intermediate_tensors = 100 * 1024  # Approximate
        
        total_ram = input_buffer + output_buffer + intermediate_tensors
        
        print("\n=== Memory Requirements ===")
        print(f"Flash (Model):        {model_size_kb} KB")
        print(f"RAM (Runtime):        {total_ram / 1024:.1f} KB")
        print(f"Total:                {(model_size_kb + total_ram/1024):.1f} KB")
        print(f"\nRecommended MCU:")
        print(f"- STM32H7 series (2MB flash, 1MB RAM)")
        print(f"- STM32F7 series (1MB flash, 320KB RAM)")
        print(f"- STM32L4+ series (1MB flash, 320KB RAM)")
        
        return {
            "flash_kb": model_size_kb,
            "ram_kb": total_ram / 1024
        }


def main():
    """Example usage"""
    print("=" * 60)
    print("STM32 Model Conversion Pipeline")
    print("=" * 60 + "\n")
    
    # Step 1: Build model
    print("Step 1: Build Model")
    print("-" * 40)
    model = FireDetectionModelBuilder.create_model()
    FireDetectionModelBuilder.estimate_memory_usage()
    
    # Step 2: Convert to TFLite
    print("\n\nStep 2: Convert to TFLite")
    print("-" * 40)
    converter = ModelConverter("fire_model.h5")
    tflite_path = converter.convert_keras_to_tflite(quantize=True)
    
    # Step 3: Convert to C++ array
    print("\n\nStep 3: Generate C++ Code")
    print("-" * 40)
    cpp_header = converter.model_to_cpp_array(tflite_path)
    
    # Step 4: Generate info
    print("\n\nStep 4: Generate Model Info")
    print("-" * 40)
    info = converter.generate_model_info(tflite_path)
    
    print("\n" + "=" * 60)
    print("✓ All conversions complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Copy model_data.h to STM32 project")
    print("2. Include stm32_ai_framework.h in main.c")
    print("3. Call fire_detection_init() in setup")
    print("4. Run inference in main loop")


if __name__ == "__main__":
    main()
