#!/usr/bin/env python3
"""
Joystick/Controller Remote Control for DJI Tello
Fly the drone using a game controller with live video!

Supports: PS4, Xbox One, and generic controllers

Controls (PS4/Xbox):
  Left Stick Y  - Throttle (up/down)
  Left Stick X  - Yaw (rotate left/right)
  Right Stick Y - Pitch (forward/backward)
  Right Stick X - Roll (left/right)
  Triangle/Y    - Take off
  Cross/A       - Land
  Square/X      - Take photo (placeholder)
  Circle/B      - Toggle face detection
  L1/LB        - Emergency stop

Features:
  - Smooth analog control with deadzone
  - Auto-detects controller type
  - Dual view: Color + Edge detection (for low light)
  - Real-time telemetry display
"""

import cv2
import time
import pygame
import numpy as np
from djitellopy import Tello


class ControllerConfig:
    """Controller button/axis mappings for different controller types"""

    def __init__(self, controller_name=""):
        self.name = controller_name.lower()

        # Default (PS4-style) configuration
        self.deadzone = 0.08

        # Axes (analog sticks)
        self.left_x = 0  # Yaw
        self.left_y = 1  # Throttle
        self.right_x = 2  # Roll
        self.right_y = 3  # Pitch

        # Axis inversions
        self.left_y_reverse = -1
        self.right_y_reverse = -1

        # Buttons
        self.btn_takeoff = 3  # Triangle/Y
        self.btn_land = 1     # Cross/A
        self.btn_photo = 0    # Square/X
        self.btn_toggle = 2   # Circle/B
        self.btn_emergency = 4  # L1/LB

        # Detect controller type and adjust mappings
        if "xbox" in self.name:
            print("Xbox controller detected!")
            self.deadzone = 0.09
            self.btn_takeoff = 14  # Y
            self.btn_land = 11     # A
            self.btn_photo = 13    # X
            self.btn_toggle = 12   # B
            self.btn_emergency = 8  # LB
        elif "ps4" in self.name or "playstation" in self.name:
            print("PS4 controller detected!")
        else:
            print(f"Generic controller detected: {controller_name}")
            print("Using PS4-style button layout")


class FaceDetector:
    """Lightweight face detection using OpenCV's Haar Cascades"""

    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        self.enabled = False  # Off by default for performance
        self.face_count = 0

    def detect_faces(self, frame):
        if not self.enabled:
            return []
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        return faces

    def draw_faces(self, frame, faces):
        self.face_count = len(faces)
        for i, (x, y, w, h) in enumerate(faces):
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
            label = f"Face #{i + 1}"
            cv2.rectangle(frame, (x, y - 25), (x + 100, y), (0, 255, 0), -1)
            cv2.putText(frame, label, (x + 2, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)
        return frame


class TelloJoystickController:
    def __init__(self):
        self.tello = Tello()
        self.running = False
        self.in_flight = False
        self.face_detector = FaceDetector()

        # Velocities (-100 to 100)
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

        # FPS tracking
        self.fps_start = time.time()
        self.fps_counter = 0
        self.fps = 0

        # Initialize pygame and joystick
        pygame.init()
        pygame.joystick.init()

        if pygame.joystick.get_count() == 0:
            raise Exception("No joystick/controller detected! Please connect a controller.")

        self.joystick = pygame.joystick.Joystick(0)
        self.joystick.init()
        self.config = ControllerConfig(self.joystick.get_name())

        print(f"\nController: {self.joystick.get_name()}")
        print(f"Axes: {self.joystick.get_numaxes()}")
        print(f"Buttons: {self.joystick.get_numbuttons()}")

    def connect(self):
        """Connect to the Tello drone"""
        print("\nConnecting to Tello...")
        self.tello.connect()
        battery = self.tello.get_battery()
        print(f"Connected! Battery: {battery}%")

        if battery < 10:
            print("WARNING: Battery is very low! Charge before flying.")
            return False

        print("Starting video stream...")
        self.tello.streamon()
        time.sleep(2)
        return True

    def apply_deadzone(self, value):
        """Apply deadzone to prevent drift"""
        if abs(value) < self.config.deadzone:
            return 0.0
        return value

    def update_velocities(self):
        """Update velocities from joystick axes"""
        # Get axis values and apply deadzone
        left_x = self.apply_deadzone(self.joystick.get_axis(self.config.left_x))
        left_y = self.apply_deadzone(self.joystick.get_axis(self.config.left_y))
        right_x = self.apply_deadzone(self.joystick.get_axis(self.config.right_x))
        right_y = self.apply_deadzone(self.joystick.get_axis(self.config.right_y))

        # Convert to velocity commands (-100 to 100)
        self.yaw = int(left_x * 100)
        self.up_down = int(left_y * self.config.left_y_reverse * 100)
        self.left_right = int(right_x * 100)
        self.forward_backward = int(right_y * self.config.right_y_reverse * 100)

        # Send RC control if flying
        if self.in_flight:
            self.tello.send_rc_control(
                self.left_right,
                self.forward_backward,
                self.up_down,
                self.yaw
            )

    def takeoff(self):
        if not self.in_flight:
            print("Taking off...")
            self.tello.takeoff()
            self.in_flight = True
            print("In the air!")

    def land(self):
        if self.in_flight:
            print("Landing...")
            self.tello.send_rc_control(0, 0, 0, 0)
            self.tello.land()
            self.in_flight = False
            print("Landed!")

    def emergency_stop(self):
        print("EMERGENCY STOP!")
        self.tello.send_rc_control(0, 0, 0, 0)
        self.tello.emergency()
        self.in_flight = False

    def toggle_face_detection(self):
        self.face_detector.enabled = not self.face_detector.enabled
        status = "ON" if self.face_detector.enabled else "OFF"
        print(f"Face detection: {status}")

    def create_edge_view(self, frame):
        """Create edge detection view for low light visibility"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
        edges_bgr[:, :, 1] = edges
        return edges_bgr

    def add_overlay(self, frame, battery=0, is_edge_view=False):
        """Add telemetry overlay to frame"""
        # Flight status
        status = "FLYING" if self.in_flight else "ON GROUND"
        color = (0, 255, 0) if self.in_flight else (0, 0, 255)
        cv2.putText(frame, f"Status: {status}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Battery
        battery_color = (0, 255, 0) if battery > 30 else (0, 165, 255) if battery > 15 else (0, 0, 255)
        cv2.putText(frame, f"Battery: {battery}%", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, battery_color, 2)

        # Face detection
        if not is_edge_view and self.face_detector.enabled:
            cv2.putText(frame, f"Faces: {self.face_detector.face_count}",
                        (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 2)

        # Controller input
        cv2.putText(frame, f"Roll:{self.left_right:+4d} Pitch:{self.forward_backward:+4d}",
                    (10, 100), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        cv2.putText(frame, f"Thro:{self.up_down:+4d} Yaw:{self.yaw:+4d}",
                    (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        # FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        # View label
        view_label = "EDGE VIEW" if is_edge_view else "COLOR VIEW"
        cv2.putText(frame, view_label, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 2)

        # Controller name
        cv2.putText(frame, self.config.name[:20], (frame.shape[1] - 200, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (150, 150, 150), 1)

        return frame

    def run(self):
        """Main control loop"""
        if not self.connect():
            return

        print("\n" + "="*70)
        print("TELLO JOYSTICK/CONTROLLER CONTROL")
        print("="*70)
        print(f"\nUsing controller: {self.joystick.get_name()}")
        print("\nControls:")
        print("  Left Stick  - Throttle (Y) / Yaw (X)")
        print("  Right Stick - Pitch (Y) / Roll (X)")
        print("  Triangle/Y  - Take off")
        print("  Cross/A     - Land")
        print("  Circle/B    - Toggle face detection")
        print("  L1/LB       - EMERGENCY STOP")
        print("\nDual view: Color (top) + Edge detection (bottom)")
        print("="*70 + "\n")

        self.running = True

        try:
            while self.running:
                # Process pygame events
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.running = False

                    elif event.type == pygame.JOYBUTTONDOWN:
                        if event.button == self.config.btn_takeoff:
                            self.takeoff()
                        elif event.button == self.config.btn_land:
                            self.land()
                        elif event.button == self.config.btn_toggle:
                            self.toggle_face_detection()
                        elif event.button == self.config.btn_emergency:
                            self.emergency_stop()
                            self.running = False

                # Update velocities from joystick
                self.update_velocities()

                # Get video frame
                frame = self.tello.get_frame_read().frame
                if frame is not None:
                    frame = cv2.resize(frame, (640, 480))

                    # Face detection
                    faces = self.face_detector.detect_faces(frame)
                    if len(faces) > 0 and self.face_detector.enabled:
                        frame = self.face_detector.draw_faces(frame, faces)

                    # Create edge view
                    edges = self.create_edge_view(frame)

                    # Get battery
                    battery = self.tello.get_battery()

                    # Calculate FPS
                    self.fps_counter += 1
                    if self.fps_counter >= 20:
                        self.fps = self.fps_counter / (time.time() - self.fps_start)
                        self.fps_start = time.time()
                        self.fps_counter = 0

                    # Add overlays
                    frame_with_overlay = self.add_overlay(frame.copy(), battery, False)
                    edges_with_overlay = self.add_overlay(edges.copy(), battery, True)

                    # Combine views vertically
                    combined = np.vstack([frame_with_overlay, edges_with_overlay])

                    # Display
                    cv2.imshow('Tello Joystick Control - Color + Edges', combined)

                # Check for quit
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.running = False

        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected!")
            if self.in_flight:
                self.land()

        except Exception as e:
            print(f"\nError: {e}")
            if self.in_flight:
                self.land()

        finally:
            print("Cleaning up...")
            if self.in_flight:
                self.land()
            pygame.quit()
            cv2.destroyAllWindows()
            self.tello.streamoff()
            print("Done! Thanks for flying!")


def main():
    print("\n" + "="*70)
    print("TELLO JOYSTICK/CONTROLLER CONTROL")
    print("="*70)
    print("\nPlease connect your game controller before starting.")
    print("Supported: PS4, Xbox One, and generic USB controllers")
    print("\nChecking for controller...")

    try:
        controller = TelloJoystickController()
        controller.run()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("- Make sure your controller is connected")
        print("- Try disconnecting and reconnecting it")
        print("- Check that your controller is recognized by your OS")


if __name__ == "__main__":
    main()
