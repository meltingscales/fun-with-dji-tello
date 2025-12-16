#!/usr/bin/env python3
"""
Shared utility functions and classes for DJI Tello drone control programs
"""

import cv2
import time
import numpy as np
from djitellopy import Tello
from constants import *


class FaceDetector:
    """Lightweight face detection using OpenCV's Haar Cascades"""

    def __init__(self, enabled=True):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            print("Warning: Could not load face detection model!")
            self.available = False
        else:
            self.available = True
            print("Face detection model loaded successfully!")

        self.enabled = enabled
        self.face_count = 0

    def detect_faces(self, frame):
        """Detect faces in the frame"""
        if not self.available or not self.enabled:
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=FACE_DETECTION_SCALE_FACTOR,
            minNeighbors=FACE_DETECTION_MIN_NEIGHBORS,
            minSize=FACE_DETECTION_MIN_SIZE
        )
        return faces

    def draw_faces(self, frame, faces):
        """Draw boxes around detected faces"""
        self.face_count = len(faces)

        for i, (x, y, w, h) in enumerate(faces):
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), COLOR_GREEN, 3)

            # Add label
            label = f"Face #{i + 1}"
            cv2.rectangle(frame, (x, y - 25), (x + 100, y), COLOR_GREEN, -1)
            cv2.putText(frame, label, (x + 2, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, COLOR_BLACK, 2)

        return frame

    def toggle(self):
        """Toggle face detection on/off"""
        self.enabled = not self.enabled
        return self.enabled


class TelloConnection:
    """Helper class for connecting to Tello with proper initialization"""

    @staticmethod
    def connect_and_start_video(tello: Tello, min_battery=CRITICAL_BATTERY):
        """
        Connect to Tello and start video stream with proper calibration delay

        Args:
            tello: Tello instance
            min_battery: Minimum battery percentage required (default: 10%)

        Returns:
            bool: True if successful, False otherwise
        """
        print("Connecting to Tello...")
        tello.connect()

        battery = tello.get_battery()
        print(f"Connected! Battery: {battery}%")

        if battery < min_battery:
            print(f"ERROR: Battery is critically low ({battery}%)!")
            print(f"Minimum required: {min_battery}%")
            return False

        if battery < LOW_BATTERY:
            print(f"WARNING: Battery is low ({battery}%). Charge soon!")

        print("Starting video stream...")
        tello.streamon()

        print(f"Waiting for sensors to calibrate ({CALIBRATION_DELAY} seconds)...")
        time.sleep(CALIBRATION_DELAY)

        print("Ready to fly!")
        return True

    @staticmethod
    def check_preflight(tello: Tello, verbose=True):
        """
        Show pre-flight checklist (SDK handles hardware safety)

        Args:
            tello: Tello instance
            verbose: Print detailed information

        Returns:
            bool: Always True (let SDK handle hardware checks)
        """
        if verbose:
            battery = tello.get_battery()

            print("\n" + "="*50)
            print("PRE-FLIGHT CHECKLIST:")
            print("="*50)
            print(f"✓ Battery: {battery}%")
            print("✓ Ensure drone is on a FLAT surface")
            print("✓ Ensure good lighting (not too dark)")
            print("✓ Remove any obstacles within 2 meters")
            print("="*50)

        return True


class VideoUtils:
    """Utility functions for video processing and display"""

    @staticmethod
    def create_edge_view(frame):
        """Create edge detection view for low light visibility"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges_bgr[:, :, 1] = edges  # Green channel for visibility
        return edges_bgr

    @staticmethod
    def add_text_overlay(frame, text, position=(10, 30),
                        font_scale=0.6, color=COLOR_GREEN, thickness=2):
        """Add text overlay to frame"""
        cv2.putText(frame, text, position,
                   cv2.FONT_HERSHEY_SIMPLEX, font_scale, color, thickness)
        return frame

    @staticmethod
    def add_text_with_background(frame, text, position=(10, 30),
                                 font_scale=1.2, text_color=COLOR_GREEN,
                                 bg_color=COLOR_BLACK, thickness=3):
        """Add text with black background for better readability"""
        (text_width, text_height), _ = cv2.getTextSize(
            text, cv2.FONT_HERSHEY_SIMPLEX, font_scale, thickness
        )

        # Draw background rectangle
        x, y = position
        cv2.rectangle(
            frame,
            (x - 10, y - text_height - 10),
            (x + text_width + 10, y + 10),
            bg_color,
            -1
        )

        # Draw text
        cv2.putText(
            frame, text, position,
            cv2.FONT_HERSHEY_SIMPLEX, font_scale, text_color, thickness
        )
        return frame

    @staticmethod
    def get_battery_color(battery):
        """Get appropriate color for battery display based on level"""
        if battery > WARNING_BATTERY:
            return COLOR_GREEN
        elif battery > LOW_BATTERY:
            return COLOR_ORANGE
        else:
            return COLOR_RED

    @staticmethod
    def combine_views_horizontal(left, right):
        """Combine two frames side by side"""
        return np.hstack([left, right])

    @staticmethod
    def combine_views_vertical(top, bottom):
        """Combine two frames vertically"""
        return np.vstack([top, bottom])


class FlightController:
    """Common flight control operations"""

    @staticmethod
    def safe_takeoff(tello: Tello, verbose=True):
        """
        Attempt takeoff with error handling

        Args:
            tello: Tello instance
            verbose: Print status messages

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if verbose:
                print(f"\n🚀 Taking off (may take up to {TAKEOFF_TIMEOUT} seconds)...")

            tello.takeoff()

            if verbose:
                print("✓ Successfully in the air!")

            return True

        except Exception as e:
            if verbose:
                print(f"\n✗ TAKEOFF FAILED: {e}")
                print("\nTroubleshooting tips:")
                print("  1. Place drone on a flat, non-reflective surface")
                print("  2. Ensure room has good lighting")
                print("  3. Move away from metal objects/surfaces")
                print("  4. Check propellers are not obstructed")
                print("  5. Try power cycling the drone")
                print("  6. Ensure propeller guards (if any) are properly attached")

            return False

    @staticmethod
    def safe_land(tello: Tello, verbose=True):
        """
        Attempt landing with error handling

        Args:
            tello: Tello instance
            verbose: Print status messages

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if verbose:
                print("\n🛬 Landing...")

            # Stop all movement first
            tello.send_rc_control(0, 0, 0, 0)
            time.sleep(0.5)

            tello.land()

            if verbose:
                print("✓ Landed safely!")

            return True

        except Exception as e:
            if verbose:
                print(f"\n✗ LANDING FAILED: {e}")
                print("Note: Drone may have landed anyway")

            return False

    @staticmethod
    def emergency_land(tello: Tello):
        """Emergency landing - stop everything and land immediately"""
        print("\n⚠️  EMERGENCY LANDING!")
        try:
            tello.send_rc_control(0, 0, 0, 0)
            tello.land()
            print("✓ Emergency landing complete")
        except Exception as e:
            print(f"✗ Emergency landing failed: {e}")
            print("Manual intervention may be required!")


class FPSCounter:
    """Track and calculate frames per second"""

    def __init__(self, calc_interval=FPS_CALC_INTERVAL):
        self.calc_interval = calc_interval
        self.frame_count = 0
        self.start_time = time.time()
        self.fps = 0.0

    def update(self):
        """Update frame count and calculate FPS if interval reached"""
        self.frame_count += 1

        if self.frame_count >= self.calc_interval:
            elapsed = time.time() - self.start_time
            self.fps = self.frame_count / elapsed
            self.frame_count = 0
            self.start_time = time.time()

        return self.fps

    def get_fps(self):
        """Get current FPS value"""
        return self.fps


def print_controls(controls_dict):
    """
    Print formatted controls list

    Args:
        controls_dict: Dictionary of {key: description}
    """
    print("\n" + "="*60)
    print("CONTROLS:")
    print("="*60)

    max_key_len = max(len(k) for k in controls_dict.keys())

    for key, description in controls_dict.items():
        print(f"  {key:<{max_key_len}} - {description}")

    print("="*60 + "\n")
