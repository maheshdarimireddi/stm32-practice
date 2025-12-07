"""
Fire Detection Calibration Tool
Test different colors, adjust sensitivity, and fine-tune detection
"""

import cv2
import numpy as np
from collections import deque


class FireDetectionCalibrator:
    """Calibration tool for fire detection"""
    
    def __init__(self):
        self.mode = 'color'  # 'color', 'hsv', 'motion'
        
        # HSV range sliders
        self.h_min = 0
        self.h_max = 25
        self.s_min = 100
        self.s_max = 255
        self.v_min = 100
        self.v_max = 255
        
        self.prev_gray = None
        self.motion_threshold = 2.0
        
    def create_trackbars(self, window_name):
        """Create adjustment trackbars"""
        cv2.createTrackbar('H Min', window_name, self.h_min, 180, self.on_trackbar)
        cv2.createTrackbar('H Max', window_name, self.h_max, 180, self.on_trackbar)
        cv2.createTrackbar('S Min', window_name, self.s_min, 255, self.on_trackbar)
        cv2.createTrackbar('S Max', window_name, self.s_max, 255, self.on_trackbar)
        cv2.createTrackbar('V Min', window_name, self.v_min, 255, self.on_trackbar)
        cv2.createTrackbar('V Max', window_name, self.v_max, 255, self.on_trackbar)
    
    def on_trackbar(self, x):
        """Trackbar callback"""
        pass
    
    def get_trackbar_values(self, window_name):
        """Get current trackbar values"""
        self.h_min = cv2.getTrackbarPos('H Min', window_name)
        self.h_max = cv2.getTrackbarPos('H Max', window_name)
        self.s_min = cv2.getTrackbarPos('S Min', window_name)
        self.s_max = cv2.getTrackbarPos('S Max', window_name)
        self.v_min = cv2.getTrackbarPos('V Min', window_name)
        self.v_max = cv2.getTrackbarPos('V Max', window_name)
    
    def detect_color_range(self, hsv_frame):
        """Detect with custom HSV range"""
        lower = np.array([self.h_min, self.s_min, self.v_min])
        upper = np.array([self.h_max, self.s_max, self.v_max])
        mask = cv2.inRange(hsv_frame, lower, upper)
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=1)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=1)
        
        return mask
    
    def detect_motion(self, gray_frame):
        """Detect motion between frames"""
        if self.prev_gray is None:
            self.prev_gray = gray_frame.copy()
            return None
        
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray_frame, None,
            pyr_scale=0.5, levels=3, winsize=15,
            iterations=3, n8=False, poly_n=5, poly_sigma=1.2, flags=0
        )
        
        magnitude, _ = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        motion_mask = (magnitude > self.motion_threshold).astype(np.uint8) * 255
        
        self.prev_gray = gray_frame.copy()
        return motion_mask


def calibration_mode():
    """HSV calibration tool"""
    print("=" * 60)
    print("FIRE DETECTION CALIBRATOR")
    print("=" * 60)
    print("\nCalibration Mode - Adjust HSV sliders to find fire colors")
    print("\nDefault ranges:")
    print("- H (Hue): 0-25 (red-orange) and 170-180 (deep red)")
    print("- S (Saturation): 100-255 (bright colors)")
    print("- V (Value): 100-255 (high brightness)")
    print("\nInstructions:")
    print("1. Show objects under camera (fire, red cloth, etc.)")
    print("2. Adjust sliders to isolate target color")
    print("3. Note values that work best")
    print("4. Press 's' to save settings")
    print("5. Press 'q' to quit")
    print("=" * 60 + "\n")
    
    cap = cv2.VideoCapture(0)
    calibrator = FireDetectionCalibrator()
    window_name = "Calibrator"
    
    cv2.namedWindow(window_name)
    calibrator.create_trackbars(window_name)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        calibrator.get_trackbar_values(window_name)
        mask = calibrator.detect_color_range(hsv)
        
        # Show original and mask side by side
        result = np.hstack([frame, cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)])
        
        # Add text info
        text = f"H:{calibrator.h_min}-{calibrator.h_max} S:{calibrator.s_min}-{calibrator.s_max} V:{calibrator.v_min}-{calibrator.v_max}"
        cv2.putText(result, text, (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        pixels = cv2.countNonZero(mask)
        cv2.putText(result, f"Detected pixels: {pixels}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        
        cv2.imshow(window_name, result)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            print(f"\nSettings to use in fire_detection.py:")
            print(f"self.h_min = {calibrator.h_min}")
            print(f"self.h_max = {calibrator.h_max}")
            print(f"self.s_min = {calibrator.s_min}")
            print(f"self.s_max = {calibrator.s_max}")
            print(f"self.v_min = {calibrator.v_min}")
            print(f"self.v_max = {calibrator.v_max}\n")
    
    cap.release()
    cv2.destroyAllWindows()


def test_colors_mode():
    """Test specific colors"""
    print("=" * 60)
    print("COLOR TEST MODE")
    print("=" * 60)
    print("\nThis mode helps identify if your camera sees colors correctly")
    print("Press 'q' to quit\n")
    
    cap = cv2.VideoCapture(0)
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame = cv2.resize(frame, (640, 480))
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Show different color masks
        masks = {
            'Red': (cv2.inRange(hsv, np.array([0, 100, 100]), np.array([30, 255, 255])),
                   'Red range'),
            'Orange': (cv2.inRange(hsv, np.array([10, 100, 100]), np.array([25, 255, 255])),
                      'Orange range'),
            'Yellow': (cv2.inRange(hsv, np.array([20, 100, 100]), np.array([35, 255, 255])),
                      'Yellow range'),
        }
        
        cv2.imshow('Original', frame)
        
        for name, (mask, label) in masks.items():
            display = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
            cv2.putText(display, label, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.imshow(name, display)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()


def main_menu():
    """Main menu"""
    while True:
        print("\n" + "=" * 60)
        print("FIRE DETECTION SYSTEM - TOOLS")
        print("=" * 60)
        print("\n1. Calibrate HSV ranges (interactive)")
        print("2. Test color detection")
        print("3. Run real-time detection (fire_detection.py)")
        print("4. Exit")
        print("\nChoice: ", end="")
        
        choice = input().strip()
        
        if choice == '1':
            calibration_mode()
        elif choice == '2':
            test_colors_mode()
        elif choice == '3':
            print("\nRunning fire_detection.py...")
            import subprocess
            try:
                subprocess.run(['python', 'fire_detection.py'])
            except Exception as e:
                print(f"Error: {e}")
        elif choice == '4':
            print("Goodbye!")
            break
        else:
            print("Invalid choice")


if __name__ == "__main__":
    main_menu()
