#!/usr/bin/env python3
"""
WASD Remote Control with Facial Recognition for DJI Tello
Fly the drone using your keyboard with live video and face detection!

Controls:
  WASD - Move forward/left/back/right (hold for continuous movement)
  I/P  - Move up/down (hold for continuous movement)
  Q/E  - Rotate left/right (hold for continuous movement)
  T    - Take off
  L    - Land
  F    - Toggle face detection on/off
  ESC  - Emergency land and quit

Features:
  - Continuous movement while holding keys
  - Real-time face detection with bounding boxes
  - Dual view: Color + Edge detection (for low light)
  - Real-time velocity and FPS display
"""

import cv2
import time
import keyboard
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


class TelloFaceController:
    def __init__(self):
        self.tello = Tello()
        self.face_detector = FaceDetector(enabled=True)
        self.speed = DEFAULT_SPEED
        self.running = False
        self.in_flight = False

        # Current velocities
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

        # FPS tracking
        self.fps_counter = FPSCounter()

    def connect(self):
        """Connect to the Tello drone"""
        return TelloConnection.connect_and_start_video(tello=self.tello)

    def update_velocities(self):
        """Update velocity values based on currently pressed keys"""
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

        if keyboard.is_pressed('w'):
            self.forward_backward = self.speed
        if keyboard.is_pressed('s'):
            self.forward_backward = -self.speed
        if keyboard.is_pressed('a'):
            self.left_right = -self.speed
        if keyboard.is_pressed('d'):
            self.left_right = self.speed
        if keyboard.is_pressed('i'):
            self.up_down = self.speed
        if keyboard.is_pressed('p'):
            self.up_down = -self.speed
        if keyboard.is_pressed('q'):
            self.yaw = -self.speed
        if keyboard.is_pressed('e'):
            self.yaw = self.speed

        if self.in_flight:
            self.tello.send_rc_control(
                self.left_right, self.forward_backward, self.up_down, self.yaw
            )

    def takeoff(self):
        if not self.in_flight:
            # Use library's pre-flight check
            if not TelloConnection.check_preflight(self.tello):
                return

            if FlightController.safe_takeoff(self.tello):
                self.in_flight = True

    def land(self):
        if self.in_flight:
            if FlightController.safe_land(self.tello):
                self.in_flight = False

    def emergency_land(self):
        FlightController.emergency_land(self.tello)
        self.in_flight = False

    def toggle_face_detection(self):
        enabled = self.face_detector.toggle()
        status = "ON" if enabled else "OFF"
        print(f"Face detection: {status}")

    def get_active_commands(self):
        """Get string of currently active commands"""
        commands = []
        if keyboard.is_pressed('w'):
            commands.append('FWD')
        if keyboard.is_pressed('s'):
            commands.append('BACK')
        if keyboard.is_pressed('a'):
            commands.append('LEFT')
        if keyboard.is_pressed('d'):
            commands.append('RIGHT')
        if keyboard.is_pressed('i'):
            commands.append('UP')
        if keyboard.is_pressed('p'):
            commands.append('DOWN')
        if keyboard.is_pressed('q'):
            commands.append('ROT-L')
        if keyboard.is_pressed('e'):
            commands.append('ROT-R')
        return " + ".join(commands) if commands else "None"

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

        # Face detection status
        if not is_edge_view:
            face_status = "ON" if self.face_detector.enabled else "OFF"
            face_color = COLOR_GREEN if self.face_detector.enabled else COLOR_GRAY
            VideoUtils.add_text_overlay(
                frame, f"Faces: {face_status} ({self.face_detector.face_count})",
                (10, 75), font_scale=0.45, color=face_color
            )

        # Active commands
        active_cmds = self.get_active_commands()
        cmd_color = COLOR_GREEN if active_cmds != "None" else COLOR_GRAY
        VideoUtils.add_text_overlay(frame, f"Active: {active_cmds}", (10, 100),
                                    font_scale=0.4, color=cmd_color, thickness=1)

        # Velocity and FPS
        VideoUtils.add_text_overlay(
            frame, f"FPS: {self.fps_counter.get_fps():.1f}", (10, 120),
            font_scale=0.35, color=COLOR_WHITE, thickness=1
        )
        VideoUtils.add_text_overlay(
            frame,
            f"Vel: {self.left_right:+3d},{self.forward_backward:+3d},{self.up_down:+3d},{self.yaw:+3d}",
            (10, 135), font_scale=0.35, color=COLOR_WHITE, thickness=1
        )

        # View label
        view_label = "EDGE VIEW" if is_edge_view else "COLOR VIEW"
        VideoUtils.add_text_overlay(frame, view_label, (10, frame.shape[0] - 10),
                                    font_scale=0.45, color=COLOR_YELLOW)

        return frame

    def run(self):
        """Main control loop with face detection"""
        if not self.connect():
            return

        print("\n" + "="*70)
        print("TELLO REMOTE CONTROL WITH FACE RECOGNITION")
        print("="*70)

        # Print controls using library function
        print_controls({
            'W/A/S/D': 'Move forward/left/back/right (HOLD)',
            'I/P': 'Move up/down (HOLD)',
            'Q/E': 'Rotate left/right (HOLD)',
            'T': 'Take off',
            'L': 'Land',
            'F': 'Toggle face detection on/off',
            'ESC': 'Emergency land and quit'
        })

        print("\nDual view: Color (top) + Edge detection (bottom)")
        print("Edge view helps with low-light visibility!")
        print("="*70 + "\n")

        # Set up keyboard hooks
        keyboard.on_press_key('t', lambda _: self.takeoff() if not self.in_flight else None)
        keyboard.on_press_key('l', lambda _: self.land() if self.in_flight else None)
        keyboard.on_press_key('f', lambda _: self.toggle_face_detection())
        keyboard.on_press_key('esc', lambda _: setattr(self, 'running', False))

        self.running = True

        try:
            while self.running:
                frame = self.tello.get_frame_read().frame
                if frame is not None:
                    # Resize
                    frame = cv2.resize(frame, (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT))

                    # Detect and draw faces on color view using library
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

                    # Combine views vertically (stacked) using library
                    combined = VideoUtils.combine_views_vertical(
                        frame_with_overlay, edges_with_overlay
                    )

                    # Display
                    cv2.imshow('Tello Face Recognition - Color + Edges', combined)

                # Update velocities
                self.update_velocities()

                # Small delay (ESC only for quit - Q is for rotation!)
                cv2.waitKey(10)

                if keyboard.is_pressed('esc'):
                    print("\nESC pressed - Shutting down...")
                    if self.in_flight:
                        self.emergency_land()
                    break

        except KeyboardInterrupt:
            print("\nKeyboard interrupt detected!")
            if self.in_flight:
                self.emergency_land()

        except Exception as e:
            print(f"\nError: {e}")
            if self.in_flight:
                self.emergency_land()

        finally:
            print("Cleaning up...")
            if self.in_flight:
                self.land()
            keyboard.unhook_all()
            cv2.destroyAllWindows()
            self.tello.streamoff()
            print("Done! Thanks for flying!")


def main():
    print("\nNOTE: This program requires keyboard access.")
    print("On Linux, you may need to run with sudo.")
    print("Starting in 2 seconds...\n")
    time.sleep(2)

    controller = TelloFaceController()
    controller.run()


if __name__ == "__main__":
    main()
