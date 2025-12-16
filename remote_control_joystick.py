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
from djitellopy import Tello
from lib import (
    TelloConnection,
    FlightController,
    VideoUtils,
    FaceDetector,
    FPSCounter,
    print_controls
)
from constants import *


class ControllerConfig:
    """Controller button/axis mappings for different controller types"""

    def __init__(self, controller_name=""):
        self.name = controller_name.lower()

        # Default (PS4-style) configuration
        self.deadzone = CONTROLLER_DEADZONE

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
            self.deadzone = XBOX_DEADZONE
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


class TelloJoystickController:
    def __init__(self):
        self.tello = Tello()
        self.running = False
        self.in_flight = False
        self.face_detector = FaceDetector(enabled=False)  # Off by default for performance

        # Velocities (-100 to 100)
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

        # FPS tracking
        self.fps_counter = FPSCounter()

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
        return TelloConnection.connect_and_start_video(tello=self.tello)

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
            if FlightController.safe_takeoff(self.tello):
                self.in_flight = True

    def land(self):
        if self.in_flight:
            if FlightController.safe_land(self.tello):
                self.in_flight = False

    def emergency_stop(self):
        FlightController.emergency_land(self.tello)
        self.in_flight = False

    def toggle_face_detection(self):
        enabled = self.face_detector.toggle()
        status = "ON" if enabled else "OFF"
        print(f"Face detection: {status}")

    def add_overlay(self, frame, battery=0, is_edge_view=False):
        """Add overlay information to frame"""
        # Flight status
        status = "FLYING" if self.in_flight else "ON GROUND"
        status_color = COLOR_GREEN if self.in_flight else COLOR_RED
        VideoUtils.add_text_overlay(frame, f"Status: {status}", (10, 25),
                                    font_scale=0.5, color=status_color)

        # Battery
        battery_color = VideoUtils.get_battery_color(battery)
        VideoUtils.add_text_overlay(frame, f"Bat: {battery}%", (10, 50),
                                    font_scale=0.45, color=battery_color)

        # Face detection (color view only)
        if not is_edge_view:
            face_status = "ON" if self.face_detector.enabled else "OFF"
            face_color = COLOR_GREEN if self.face_detector.enabled else COLOR_GRAY
            VideoUtils.add_text_overlay(
                frame, f"Faces: {face_status} ({self.face_detector.face_count})",
                (10, 75), font_scale=0.4, color=face_color, thickness=1
            )

        # Stick positions
        VideoUtils.add_text_overlay(
            frame, f"LR:{self.left_right:+4d} FB:{self.forward_backward:+4d}",
            (10, 100), font_scale=0.4, color=COLOR_WHITE, thickness=1
        )
        VideoUtils.add_text_overlay(
            frame, f"UD:{self.up_down:+4d} YAW:{self.yaw:+4d}",
            (10, 120), font_scale=0.4, color=COLOR_WHITE, thickness=1
        )

        # FPS
        VideoUtils.add_text_overlay(
            frame, f"FPS: {self.fps_counter.get_fps():.1f}",
            (10, 140), font_scale=0.35, color=COLOR_WHITE, thickness=1
        )

        # View label
        view_label = "EDGE VIEW" if is_edge_view else "COLOR VIEW"
        VideoUtils.add_text_overlay(frame, view_label, (10, frame.shape[0] - 10),
                                    font_scale=0.45, color=COLOR_YELLOW)

        return frame

    def run(self):
        """Main control loop"""
        if not self.connect():
            return

        print("\n" + "="*70)
        print("TELLO JOYSTICK/CONTROLLER CONTROL")
        print("="*70)
        print(f"\nUsing controller: {self.joystick.get_name()}")

        # Print controls using library function
        print_controls({
            'Left Stick': 'Throttle (Y) / Yaw (X)',
            'Right Stick': 'Pitch (Y) / Roll (X)',
            'Triangle/Y': 'Take off',
            'Cross/A': 'Land',
            'Circle/B': 'Toggle face detection',
            'L1/LB': 'EMERGENCY STOP'
        })

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
                    frame = cv2.resize(frame, (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT))

                    # Face detection using library
                    faces = self.face_detector.detect_faces(frame)
                    if len(faces) > 0 and self.face_detector.enabled:
                        frame = self.face_detector.draw_faces(frame, faces)

                    # Create edge view using library
                    edges = VideoUtils.create_edge_view(frame)

                    # Get battery
                    battery = self.tello.get_battery()

                    # Calculate FPS
                    self.fps_counter.update()

                    # Add overlays
                    frame_with_overlay = self.add_overlay(frame.copy(), battery, False)
                    edges_with_overlay = self.add_overlay(edges.copy(), battery, True)

                    # Combine views vertically using library
                    combined = VideoUtils.combine_views_vertical(
                        frame_with_overlay, edges_with_overlay
                    )

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
    print("\nMake sure your controller is connected before starting!")
    print("Starting in 2 seconds...\n")
    time.sleep(2)

    try:
        controller = TelloJoystickController()
        controller.run()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nTroubleshooting:")
        print("  1. Make sure your controller is connected")
        print("  2. Check if the controller is detected by your system")
        print("  3. Try reconnecting the controller")


if __name__ == "__main__":
    main()
