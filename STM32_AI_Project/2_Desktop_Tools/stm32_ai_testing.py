"""
STM32 AI Testing Framework
Simulate STM32 inference and validate model on desktop
"""

import numpy as np
import cv2
from pathlib import Path
import json
import time


class STM32Simulator:
    """Simulate STM32 AI inference on desktop"""
    
    def __init__(self, model_path):
        self.model_path = model_path
        self.inference_count = 0
        self.total_inference_time = 0
    
    def load_model(self):
        """Load TFLite model"""
        import tensorflow as tf
        self.interpreter = tf.lite.Interpreter(model_path=str(self.model_path))
        self.interpreter.allocate_tensors()
        
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()
        
        print(f"✓ Model loaded: {self.model_path}")
        print(f"  Input shape: {self.input_details[0]['shape']}")
        print(f"  Output shape: {self.output_details[0]['shape']}")
    
    def preprocess_image(self, image_path, target_size=(32, 32)):
        """Preprocess image for model"""
        img = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
        if img is None:
            raise ValueError(f"Cannot load image: {image_path}")
        
        # Resize to target
        img = cv2.resize(img, target_size)
        
        # Normalize
        img = img.astype(np.float32) / 255.0
        
        # Add batch dimension
        img = np.expand_dims(img, axis=0)
        if len(img.shape) == 3:
            img = np.expand_dims(img, axis=-1)
        
        return img
    
    def infer(self, image_path, confidence_threshold=0.7):
        """Run inference"""
        start_time = time.time()
        
        # Preprocess
        input_data = self.preprocess_image(image_path)
        
        # Set input
        self.interpreter.set_tensor(
            self.input_details[0]['index'], 
            input_data.astype(self.input_details[0]['dtype'])
        )
        
        # Invoke
        self.interpreter.invoke()
        
        # Get output
        output_data = self.interpreter.get_tensor(
            self.output_details[0]['index']
        )
        
        inference_time = (time.time() - start_time) * 1000  # ms
        
        # Process results
        probabilities = output_data[0]
        fire_prob = probabilities[1]  # Fire class
        
        self.inference_count += 1
        self.total_inference_time += inference_time
        
        result = {
            'fire_detected': fire_prob > confidence_threshold,
            'fire_probability': float(fire_prob),
            'inference_time_ms': inference_time,
            'confidence': float(fire_prob)
        }
        
        return result
    
    def get_stats(self):
        """Get inference statistics"""
        avg_time = self.total_inference_time / max(1, self.inference_count)
        
        return {
            'total_inferences': self.inference_count,
            'avg_inference_time_ms': avg_time,
            'throughput_fps': 1000 / avg_time if avg_time > 0 else 0
        }


class TestSuite:
    """Comprehensive test suite for fire detection"""
    
    def __init__(self, model_path, test_data_dir="test_images"):
        self.simulator = STM32Simulator(model_path)
        self.simulator.load_model()
        self.test_data_dir = Path(test_data_dir)
        self.results = {
            'true_positive': 0,
            'true_negative': 0,
            'false_positive': 0,
            'false_negative': 0
        }
    
    def create_test_data(self):
        """Generate synthetic test images"""
        print("Generating synthetic test data...")
        self.test_data_dir.mkdir(exist_ok=True)
        
        # Fire images (synthetic bright patterns)
        for i in range(10):
            img = np.zeros((32, 32), dtype=np.uint8)
            # Simulate flame (bright center with noise)
            y, x = np.ogrid[:32, :32]
            mask = ((x - 16)**2 + (y - 16)**2) <= 64
            img[mask] = np.random.randint(200, 256, size=np.sum(mask))
            
            # Add flickering effect
            noise = np.random.randint(0, 50, (32, 32))
            img = np.clip(img + noise, 0, 255).astype(np.uint8)
            
            cv2.imwrite(str(self.test_data_dir / f"fire_{i}.jpg"), img)
        
        # Non-fire images (dark patterns)
        for i in range(10):
            img = np.random.randint(0, 100, (32, 32), dtype=np.uint8)
            cv2.imwrite(str(self.test_data_dir / f"no_fire_{i}.jpg"), img)
        
        print(f"✓ Generated test data in {self.test_data_dir}")
    
    def run_test(self, image_path, ground_truth):
        """Run single test"""
        result = self.simulator.infer(image_path)
        
        # Update confusion matrix
        predicted = result['fire_detected']
        
        if predicted == 1 and ground_truth == 1:
            self.results['true_positive'] += 1
            status = "✓ TP"
        elif predicted == 0 and ground_truth == 0:
            self.results['true_negative'] += 1
            status = "✓ TN"
        elif predicted == 1 and ground_truth == 0:
            self.results['false_positive'] += 1
            status = "✗ FP"
        else:
            self.results['false_negative'] += 1
            status = "✗ FN"
        
        print(f"{status} | {image_path.name:20} | "
              f"Confidence: {result['confidence']:.2%} | "
              f"Time: {result['inference_time_ms']:.1f}ms")
        
        return result
    
    def run_all_tests(self):
        """Run full test suite"""
        print("\n" + "=" * 80)
        print("Running Test Suite")
        print("=" * 80 + "\n")
        
        # Test fire images
        print("Fire Detection Tests:")
        print("-" * 80)
        fire_images = sorted(self.test_data_dir.glob("fire_*.jpg"))
        for img_path in fire_images:
            self.run_test(img_path, ground_truth=1)
        
        # Test non-fire images
        print("\nNo-Fire Detection Tests:")
        print("-" * 80)
        no_fire_images = sorted(self.test_data_dir.glob("no_fire_*.jpg"))
        for img_path in no_fire_images:
            self.run_test(img_path, ground_truth=0)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        tp = self.results['true_positive']
        tn = self.results['true_negative']
        fp = self.results['false_positive']
        fn = self.results['false_negative']
        
        total = tp + tn + fp + fn
        
        # Calculate metrics
        accuracy = (tp + tn) / total if total > 0 else 0
        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
        
        print("\n" + "=" * 80)
        print("Test Results Summary")
        print("=" * 80)
        print(f"\nConfusion Matrix:")
        print(f"  True Positive (TP):  {tp:3d}")
        print(f"  True Negative (TN):  {tn:3d}")
        print(f"  False Positive (FP): {fp:3d}")
        print(f"  False Negative (FN): {fn:3d}")
        print(f"\nMetrics:")
        print(f"  Accuracy:   {accuracy:.2%}")
        print(f"  Precision:  {precision:.2%}")
        print(f"  Recall:     {recall:.2%}")
        print(f"  F1-Score:   {f1:.2%}")
        
        stats = self.simulator.get_stats()
        print(f"\nPerformance:")
        print(f"  Total Inferences:       {stats['total_inferences']}")
        print(f"  Avg Inference Time:     {stats['avg_inference_time_ms']:.2f}ms")
        print(f"  Throughput:             {stats['throughput_fps']:.1f} FPS")
        
        # Memory estimate
        print(f"\nSTM32 Suitability:")
        if stats['avg_inference_time_ms'] < 50 and accuracy > 0.85:
            print(f"  ✓ EXCELLENT for STM32H7/F7")
        elif stats['avg_inference_time_ms'] < 100 and accuracy > 0.80:
            print(f"  ✓ GOOD for STM32H7/F7")
        else:
            print(f"  ⚠ May need optimization")
        
        print("=" * 80)


def main():
    """Run testing pipeline"""
    print("\n" + "=" * 80)
    print("STM32 AI Testing Framework")
    print("=" * 80 + "\n")
    
    # Check if model exists
    model_path = Path("stm32_models/fire_model_quantized.tflite")
    
    if not model_path.exists():
        print(f"Warning: Model not found at {model_path}")
        print("Run stm32_model_converter.py first")
        return
    
    # Create test suite
    test_suite = TestSuite(str(model_path))
    
    # Generate test data
    test_suite.create_test_data()
    
    # Run tests
    test_suite.run_all_tests()


if __name__ == "__main__":
    main()
