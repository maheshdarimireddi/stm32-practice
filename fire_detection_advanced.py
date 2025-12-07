"""
Fire Detection with Audio Alert
Enhanced version with sound notification
"""

import cv2
import numpy as np
from collections import deque
import time
from datetime import datetime
import winsound  # Windows sound


class FireDetectorWithAlert(FireDetector):
    """Extended fire detector with audio alerts"""
    
    def __init__(self):
        super().__init__()
        self.last_alert_time = 0
        self.alert_cooldown = 2  # seconds between alerts
    
    def play_alert(self):
        """Play alert sound"""
        current_time = time.time()
        if current_time - self.last_alert_time > self.alert_cooldown:
            try:
                # Frequency: 1000Hz, Duration: 500ms
                winsound.Beep(1000, 500)
                self.last_alert_time = current_time
            except Exception as e:
                print(f"Warning: Could not play sound: {e}")


# Copy the FireDetector class from fire_detection.py
class FireDetector:
    def __init__(self):
        """Initialize fire detector with HSV ranges and parameters"""
        
        self.lower_fire_red1 = np.array([0, 100, 100])
        self.upper_fire_red1 = np.array([25, 255, 255])
        
        self.lower_fire_red2 = np.array([170, 100, 100])
        self.upper_fire_red2 = np.array([180, 255, 255])
        
        self.lower_cloth_red1 = np.array([0, 50, 50])
        self.upper_cloth_red1 = np.array([25, 100, 150])
        
        self.lower_cloth_red2 = np.array([170, 50, 50])
        self.upper_cloth_red2 = np.array([180, 100, 150])
        
        self.prev_gray = None
        self.motion_history = deque(maxlen=5)
        self.min_motion_threshold = 0.15
        
        self.min_fire_area = 500
        self.max_fire_area = 100000
        self.consecutive_frames = 0
        self.required_detections = 3
        
        self.flicker_history = deque(maxlen=10)
        self.min_flicker_variance = 0.02
        
        self.fire_detected = False
        self.alert_start_time = None
    
    def detect_fire_color(self, hsv_frame):
        """Detect fire using HSV color ranges"""
        mask_fire_1 = cv2.inRange(hsv_frame, self.lower_fire_red1, self.upper_fire_red1)
        mask_fire_2 = cv2.inRange(hsv_frame, self.lower_fire_red2, self.upper_fire_red2)
        fire_mask = cv2.bitwise_or(mask_fire_1, mask_fire_2)
        
        mask_cloth_1 = cv2.inRange(hsv_frame, self.lower_cloth_red1, self.upper_cloth_red1)
        mask_cloth_2 = cv2.inRange(hsv_frame, self.lower_cloth_red2, self.upper_cloth_red2)
        cloth_mask = cv2.bitwise_or(mask_cloth_1, mask_cloth_2)
        
        fire_mask = cv2.bitwise_and(fire_mask, cv2.bitwise_not(cloth_mask))
        
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        return fire_mask
    
    def detect_motion(self, gray_frame, fire_mask):
        """Detect motion in fire region"""
        if self.prev_gray is None:
            self.prev_gray = gray_frame
            return 0.0
        
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray_frame, None,
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        masked_magnitude = magnitude * (fire_mask / 255.0)
        
        fire_pixels = cv2.countNonZero(fire_mask)
        if fire_pixels == 0:
            motion_ratio = 0.0
        else:
            motion_pixels = np.sum(masked_magnitude > 2.0)
            motion_ratio = motion_pixels / fire_pixels
        
        self.prev_gray = gray_frame.copy()
        return motion_ratio
    
    def detect_flicker(self, fire_mask):
        """Detect flame flicker pattern"""
        fire_area = cv2.countNonZero(fire_mask)
        self.flicker_history.append(fire_area)
        
        if len(self.flicker_history) < 5:
            return False
        
        area_array = np.array(list(self.flicker_history))
        area_variance = np.var(area_array) / (np.mean(area_array) + 1)
        
        return area_variance > self.min_flicker_variance
    
    def get_fire_contours(self, fire_mask):
        """Extract fire contours from mask"""
        contours, _ = cv2.findContours(
            fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
    
    def is_fire_like_shape(self, contour):
        """Check if contour has fire-like characteristics"""
        area = cv2.contourArea(contour)
        if area < self.min_fire_area or area > self.max_fire_area:
            return False
        
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return False
        
        circularity = (4 * np.pi * area) / (perimeter * perimeter)
        
        if circularity > 0.8:
            return False
        
        rect = cv2.minAreaRect(contour)
        if rect[1][0] == 0:
            return False
        
        aspect_ratio = rect[1][1] / rect[1][0]
        if aspect_ratio > 3 or aspect_ratio < 0.3:
            return False
        
        return True
    
    def process_frame(self, frame):
        """Process single frame for fire detection"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        fire_mask = self.detect_fire_color(hsv)
        motion_ratio = self.detect_motion(gray, fire_mask)
        contours = self.get_fire_contours(fire_mask)
        
        fire_detected_this_frame = False
        valid_contours = []
        
        for contour in contours:
            if self.is_fire_like_shape(contour):
                valid_contours.append(contour)
                fire_detected_this_frame = True
        
        has_flicker = self.detect_flicker(fire_mask)
        
        if fire_detected_this_frame and motion_ratio > self.min_motion_threshold and has_flicker:
            self.consecutive_frames += 1
        else:
            self.consecutive_frames = max(0, self.consecutive_frames - 1)
        
        fire_status = self.consecutive_frames >= self.required_detections
        
        marked_frame = frame.copy()
        for contour in valid_contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(marked_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        confidence = min(100, (self.consecutive_frames / self.required_detections) * 100)
        
        return fire_status, marked_frame, confidence, motion_ratio, has_flicker


def main():
    """Main detection loop with audio alerts"""
    print("=" * 60)
    print("FIRE DETECTION SYSTEM - With Audio Alerts")
    print("=" * 60)
    print("\nFeatures:")
    print("✓ Candle/match/paper fire detection")
    print("✓ Red cloth false positive avoidance")
    print("✓ Motion + flicker + color analysis")
    print("✓ Audio alerts on detection")
    print("\nControls:")
    print("- Press 'q' to quit")
    print("- Press 's' to screenshot")
    print("- Press 't' for debug info")
    print("=" * 60 + "\n")
    
    cap = cv2.VideoCapture(0)
    detector = FireDetectorWithAlert()
    
    frame_count = 0
    fps_start = time.time()
    fps = 0
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read from camera")
            break
        
        frame_count += 1
        frame = cv2.resize(frame, (640, 480))
        
        fire_status, marked_frame, confidence, motion, flicker = detector.process_frame(frame)
        
        if frame_count % 30 == 0:
            fps = 30 / (time.time() - fps_start)
            fps_start = time.time()
        
        # Display metrics
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(marked_frame, f"Time: {timestamp}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"FPS: {fps:.1f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"Motion: {motion:.2%}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"Flicker: {'YES' if flicker else 'NO'}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"Conf: {confidence:.1f}%", (10, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        if fire_status:
            cv2.rectangle(marked_frame, (5, 5), (635, 475), (0, 0, 255), 3)
            cv2.putText(marked_frame, "FIRE DETECTED!", (120, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 2.5, (0, 0, 255), 3)
            cv2.putText(marked_frame, f"{confidence:.1f}% Confidence", (140, 320),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 2)
            
            detector.play_alert()
            print(f"[ALERT] Fire detected at {timestamp}")
        
        cv2.imshow("Fire Detection System", marked_frame)
        
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"fire_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(filename, marked_frame)
            print(f"Screenshot: {filename}")
        elif key == ord('t'):
            print(f"\nFire: {fire_status} | Conf: {confidence:.1f}% | Motion: {motion:.2%} | Flicker: {flicker}")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nFire detection stopped.")


if __name__ == "__main__":
    main()
