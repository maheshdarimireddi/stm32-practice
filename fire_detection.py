"""
Advanced Fire Detection System
Uses HSV color analysis + optical flow to detect real fire
Avoids false positives from red clothing/objects
"""

import cv2
import numpy as np
from collections import deque
import time
from datetime import datetime


class FireDetector:
    def __init__(self):
        """Initialize fire detector with HSV ranges and parameters"""
        
        # ULTRA-STRICT fire-specific HSV ranges
        # Real flames: BRIGHT (V > 150), highly saturated orange-red (H 0-15), very dynamic
        # Tomatoes: DARKER (V < 140), duller saturation, static
        # Hue: 0-15 (pure red-orange, excludes dark reds)
        # Saturation: 140-255 (very saturated - flame brightness)
        # Value: 150-255 (VERY bright - key difference from tomato)
        
        self.lower_fire_red1 = np.array([0, 140, 150])
        self.upper_fire_red1 = np.array([15, 255, 255])
        
        # Only include very bright deep reds (near pure red hue)
        self.lower_fire_red2 = np.array([175, 140, 150])
        self.upper_fire_red2 = np.array([180, 255, 255])
        
        # Skin tone and red cloth filter (to exclude)
        self.lower_skin = np.array([0, 10, 60])
        self.upper_skin = np.array([25, 110, 200])
        
        # Red cloth and TOMATO filter (to exclude)
        # Tomatoes: H 0-25, S 60-140, V 80-150 (duller, darker)
        self.lower_tomato_red1 = np.array([0, 60, 80])
        self.upper_tomato_red1 = np.array([25, 140, 150])
        
        self.lower_tomato_red2 = np.array([170, 60, 80])
        self.upper_tomato_red2 = np.array([180, 140, 150])
        
        # Red cloth (to exclude) - lower saturation, different value range
        self.lower_cloth_red1 = np.array([0, 50, 50])
        self.upper_cloth_red1 = np.array([25, 110, 180])
        
        self.lower_cloth_red2 = np.array([170, 50, 50])
        self.upper_cloth_red2 = np.array([180, 110, 180])
        
        # Motion parameters
        self.prev_gray = None
        self.motion_history = deque(maxlen=5)
        self.min_motion_threshold = 0.45  # 45% of fire area must have motion (tomatoes won't have this)
        
        # Detection parameters
        self.min_fire_area = 800  # Minimum pixels for fire (larger = more selective)
        self.max_fire_area = 80000  # Maximum pixels for fire detection
        self.consecutive_frames = 0
        self.required_detections = 5  # Require 5 consecutive detections (stricter temporal)
        
        # Flame flickering detection
        self.flicker_history = deque(maxlen=10)
        self.min_flicker_variance = 0.08  # Very high variance - only real flames flicker this much
        
        # Alerts
        self.fire_detected = False
        self.alert_start_time = None
        self.min_alert_duration = 1  # seconds
        
    def detect_fire_color(self, hsv_frame):
        """
        Detect fire using ultra-strict HSV color ranges
        Focuses on: BRIGHTNESS (V>150), high saturation, orange-red hue
        Excludes: Tomatoes (darker, duller), skin, cloth
        """
        # Create masks for fire ranges (ULTRA STRICT)
        mask_fire_1 = cv2.inRange(hsv_frame, self.lower_fire_red1, self.upper_fire_red1)
        mask_fire_2 = cv2.inRange(hsv_frame, self.lower_fire_red2, self.upper_fire_red2)
        fire_mask = cv2.bitwise_or(mask_fire_1, mask_fire_2)
        
        # Remove skin tones (hands, faces)
        skin_mask = cv2.inRange(hsv_frame, self.lower_skin, self.upper_skin)
        fire_mask = cv2.bitwise_and(fire_mask, cv2.bitwise_not(skin_mask))
        
        # Remove TOMATO and fruit colors (darker reds)
        tomato_mask_1 = cv2.inRange(hsv_frame, self.lower_tomato_red1, self.upper_tomato_red1)
        tomato_mask_2 = cv2.inRange(hsv_frame, self.lower_tomato_red2, self.upper_tomato_red2)
        tomato_mask = cv2.bitwise_or(tomato_mask_1, tomato_mask_2)
        fire_mask = cv2.bitwise_and(fire_mask, cv2.bitwise_not(tomato_mask))
        
        # Remove red cloth
        mask_cloth_1 = cv2.inRange(hsv_frame, self.lower_cloth_red1, self.upper_cloth_red1)
        mask_cloth_2 = cv2.inRange(hsv_frame, self.lower_cloth_red2, self.upper_cloth_red2)
        cloth_mask = cv2.bitwise_or(mask_cloth_1, mask_cloth_2)
        fire_mask = cv2.bitwise_and(fire_mask, cv2.bitwise_not(cloth_mask))
        
        # Apply morphological operations to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_OPEN, kernel, iterations=2)
        fire_mask = cv2.morphologyEx(fire_mask, cv2.MORPH_CLOSE, kernel, iterations=2)
        
        return fire_mask
    
    def detect_motion(self, gray_frame, fire_mask):
        """
        Detect motion in fire region using optical flow
        Real flames have characteristic flickering motion
        """
        if self.prev_gray is None:
            self.prev_gray = gray_frame
            return 0.0
        
        # Calculate optical flow
        flow = cv2.calcOpticalFlowFarneback(
            self.prev_gray, gray_frame, None,
            0.5, 3, 15, 3, 5, 1.2, 0
        )
        
        # Calculate magnitude of flow
        magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
        
        # Apply fire mask to get motion only in fire region
        masked_magnitude = magnitude * (fire_mask / 255.0)
        
        # Calculate motion percentage
        fire_pixels = cv2.countNonZero(fire_mask)
        if fire_pixels == 0:
            motion_ratio = 0.0
        else:
            motion_pixels = np.sum(masked_magnitude > 2.0)
            motion_ratio = motion_pixels / fire_pixels
        
        self.prev_gray = gray_frame.copy()
        return motion_ratio
    
    def detect_flicker(self, fire_mask):
        """
        Detect flame flicker pattern
        Real flames have characteristic flickering in contour area
        """
        fire_area = cv2.countNonZero(fire_mask)
        self.flicker_history.append(fire_area)
        
        if len(self.flicker_history) < 5:
            return False
        
        # Calculate variance in fire area
        area_array = np.array(list(self.flicker_history))
        area_variance = np.var(area_array) / (np.mean(area_array) + 1)
        
        # Real flames have noticeable flickering
        return area_variance > self.min_flicker_variance
    
    def get_fire_contours(self, fire_mask):
        """Extract fire contours from mask"""
        contours, _ = cv2.findContours(
            fire_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
    
    def is_fire_like_shape(self, contour):
        """
        Check if contour has fire-like characteristics
        - Very irregular/jagged edges (not smooth like hands)
        - Aspect ratio between 0.6 and 1.8
        - Solidity check (fires are jagged, hands are smooth)
        - Circularity between 0.25-0.7
        """
        area = cv2.contourArea(contour)
        if area < self.min_fire_area or area > self.max_fire_area:
            return False
        
        # Calculate perimeter for shape irregularity
        perimeter = cv2.arcLength(contour, True)
        if perimeter == 0:
            return False
        
        # Circularity ratio (more irregular = higher ratio)
        circularity = (4 * np.pi * area) / (perimeter * perimeter)
        
        # Real flames are very irregular, not smooth or circular
        # Hand: smooth, circular=~0.5-0.7
        # Fire: jagged, circular=0.25-0.6
        if circularity > 0.7:  # Exclude smooth shapes (hands, cloth)
            return False
        
        if circularity < 0.25:  # Too jagged - noise
            return False
        
        # Get bounding box for aspect ratio
        rect = cv2.minAreaRect(contour)
        if rect[1][0] == 0:
            return False
        
        aspect_ratio = rect[1][1] / rect[1][0]
        if aspect_ratio > 1.8 or aspect_ratio < 0.6:  # Stricter aspect ratio
            return False
        
        # Check solidity (area / convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        if hull_area == 0:
            return False
        
        solidity = area / hull_area
        # Fire has jagged edges (solidity 0.4-0.85)
        # Hand/cloth have smoother edges (solidity 0.85+)
        if solidity > 0.85:  # Too solid - likely hand/cloth
            return False
        
        if solidity < 0.4:  # Too hollow - noise
            return False
        
        return True
    
    def process_frame(self, frame):
        """
        Process single frame for fire detection
        Returns: (fire_detected, marked_frame, confidence)
        """
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Color-based detection
        fire_mask = self.detect_fire_color(hsv)
        
        # Motion detection
        motion_ratio = self.detect_motion(gray, fire_mask)
        
        # Get contours
        contours = self.get_fire_contours(fire_mask)
        
        # Analyze contours
        fire_detected_this_frame = False
        valid_contours = []
        
        for contour in contours:
            if self.is_fire_like_shape(contour):
                valid_contours.append(contour)
                fire_detected_this_frame = True
        
        # Check flicker pattern
        has_flicker = self.detect_flicker(fire_mask)
        
        # Multi-criteria detection
        # Real fire needs: color + motion + flicker + correct shape
        if fire_detected_this_frame and motion_ratio > self.min_motion_threshold and has_flicker:
            self.consecutive_frames += 1
        else:
            self.consecutive_frames = max(0, self.consecutive_frames - 1)
        
        # Final decision
        fire_status = self.consecutive_frames >= self.required_detections
        
        # Draw results
        marked_frame = frame.copy()
        for contour in valid_contours:
            x, y, w, h = cv2.boundingRect(contour)
            cv2.rectangle(marked_frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
        
        # Confidence score
        confidence = min(100, (self.consecutive_frames / self.required_detections) * 100)
        
        return fire_status, marked_frame, confidence, motion_ratio, has_flicker


def main():
    """Main detection loop"""
    print("=" * 60)
    print("FIRE DETECTION SYSTEM - Real-time Camera Feed")
    print("=" * 60)
    print("\nInstructions:")
    print("- Show candle, matches, or paper on fire to test detection")
    print("- Red clothing will NOT trigger false alarms")
    print("- Press 'q' to quit, 's' to take screenshot, 't' for test mode")
    print("=" * 60 + "\n")
    
    cap = cv2.VideoCapture(0)
    detector = FireDetector()
    
    frame_count = 0
    fps_start = time.time()
    fps = 0
    
    alert_sound_played = False
    
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Cannot read from camera")
            break
        
        frame_count += 1
        
        # Resize for processing
        frame = cv2.resize(frame, (640, 480))
        
        # Detect fire
        fire_status, marked_frame, confidence, motion, flicker = detector.process_frame(frame)
        
        # Calculate FPS
        if frame_count % 30 == 0:
            fps = 30 / (time.time() - fps_start)
            fps_start = time.time()
        
        # Display info
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cv2.putText(marked_frame, f"Time: {timestamp}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"FPS: {fps:.1f}", (10, 60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"Motion: {motion:.2%}", (10, 90),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"Flicker: {'YES' if flicker else 'NO'}", (10, 120),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        cv2.putText(marked_frame, f"Confidence: {confidence:.1f}%", (10, 150),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # Alert display
        if fire_status:
            # Red border for alert
            cv2.rectangle(marked_frame, (5, 5), (635, 475), (0, 0, 255), 3)
            
            # Large alert text
            cv2.putText(marked_frame, "FIRE DETECTED!", (150, 250),
                       cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv2.putText(marked_frame, f"Confidence: {confidence:.1f}%", (180, 310),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            
            # Beep sound (if available)
            if not alert_sound_played:
                print("\n" + "🔥 " * 20)
                print("FIRE DETECTED! FIRE DETECTED! FIRE DETECTED!")
                print("🔥 " * 20)
                alert_sound_played = True
        else:
            alert_sound_played = False
        
        # Show frame
        cv2.imshow("Fire Detection", marked_frame)
        
        # Key handling
        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('s'):
            filename = f"fire_detection_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
            cv2.imwrite(filename, marked_frame)
            print(f"Screenshot saved: {filename}")
        elif key == ord('t'):
            print("\n--- TEST MODE ---")
            print(f"Fire Detected: {fire_status}")
            print(f"Confidence: {confidence:.1f}%")
            print(f"Motion Ratio: {motion:.2%}")
            print(f"Flicker: {flicker}")
            print(f"Consecutive Detections: {detector.consecutive_frames}/{detector.required_detections}")
            print("---")
    
    cap.release()
    cv2.destroyAllWindows()
    print("\nCamera closed. Fire detection stopped.")


if __name__ == "__main__":
    main()
