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
import numpy as np
from djitellopy import Tello


class FaceDetector:
    """Lightweight face detection using OpenCV's Haar Cascades"""

    def __init__(self):
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        if self.face_cascade.empty():
            print("Warning: Could not load face detection model!")
            self.available = False
        else:
            self.available = True
            print("Face detection model loaded successfully!")

        self.enabled = True
        self.face_count = 0

    def detect_faces(self, frame):
        """Detect faces in the frame"""
        if not self.available or not self.enabled:
            return []

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        return faces

    def draw_faces(self, frame, faces):
        """Draw boxes around detected faces"""
        self.face_count = len(faces)

        for i, (x, y, w, h) in enumerate(faces):
            # Draw rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            # Add label
            label = f"Face #{i + 1}"
            cv2.rectangle(frame, (x, y - 25), (x + 100, y), (0, 255, 0), -1)
            cv2.putText(frame, label, (x + 2, y - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 2)

        return frame


class TelloFaceController:
    def __init__(self):
        self.tello = Tello()
        self.face_detector = FaceDetector()
        self.speed = 50
        self.running = False
        self.in_flight = False

        # Current velocities
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

        # FPS tracking
        self.fps_start = time.time()
        self.fps_counter = 0
        self.fps = 0

    def connect(self):
        """Connect to the Tello drone"""
        print("Connecting to Tello...")
        self.tello.connect()
        battery = self.tello.get_battery()
        print(f"Connected! Battery: {battery}%")

        if battery < 10:
            print("WARNING: Battery is very low! Charge before flying.")
            return False

        print("Starting video stream...")
        self.tello.streamon()
        print("Waiting for sensors to calibrate (this takes ~5 seconds)...")
        time.sleep(5)  # Increased delay for sensor calibration
        print("Ready to fly!")
        return True

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
            print("\n" + "="*50)
            print("TAKEOFF CHECKLIST:")
            print("="*50)
            print("✓ Ensure drone is on a FLAT surface")
            print("✓ Ensure good lighting (not too dark)")
            print("✓ Remove any obstacles around drone")
            print("✓ Keep away from metal surfaces")
            print("✓ Propeller guards (if any) are secure")
            print("="*50)
            print("\nAttempting takeoff in 2 seconds...")
            time.sleep(2)

            try:
                print("Sending takeoff command...")
                self.tello.takeoff()
                self.in_flight = True
                print("✓ Successfully in the air!")
            except Exception as e:
                print(f"\n✗ TAKEOFF FAILED: {e}")
                print("\nTroubleshooting tips:")
                print("  1. Place drone on a flat, non-reflective surface")
                print("  2. Ensure room has good lighting")
                print("  3. Move away from metal objects/surfaces")
                print("  4. Check propellers are not obstructed")
                print("  5. Try power cycling the drone")
                print("  6. Ensure propeller guards (if any) are properly attached")
                self.in_flight = False

    def land(self):
        if self.in_flight:
            print("Landing...")
            self.tello.send_rc_control(0, 0, 0, 0)
            self.tello.land()
            self.in_flight = False
            print("Landed!")

    def emergency_land(self):
        print("Emergency landing!")
        self.tello.send_rc_control(0, 0, 0, 0)
        self.tello.land()
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
        edges_bgr[:, :, 1] = edges  # Green channel for visibility
        return edges_bgr

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
        color = (0, 255, 0) if self.in_flight else (0, 0, 255)
        cv2.putText(frame, f"Status: {status}", (10, 25),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Battery
        battery_color = (0, 255, 0) if battery > 30 else (0, 165, 255) if battery > 15 else (0, 0, 255)
        cv2.putText(frame, f"Bat: {battery}%", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, battery_color, 2)

        # Face detection status
        if not is_edge_view:
            face_status = "ON" if self.face_detector.enabled else "OFF"
            face_color = (0, 255, 0) if self.face_detector.enabled else (128, 128, 128)
            cv2.putText(frame, f"Faces: {face_status} ({self.face_detector.face_count})",
                        (10, 75), cv2.FONT_HERSHEY_SIMPLEX, 0.45, face_color, 2)

        # Active commands
        active_cmds = self.get_active_commands()
        cmd_color = (0, 255, 0) if active_cmds != "None" else (128, 128, 128)
        cv2.putText(frame, f"Active: {active_cmds}", (10, 100),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, cmd_color, 1)

        # Velocity and FPS
        cv2.putText(frame, f"FPS: {self.fps:.1f}", (10, 120),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)
        cv2.putText(frame, f"Vel: {self.left_right:+3d},{self.forward_backward:+3d},{self.up_down:+3d},{self.yaw:+3d}",
                    (10, 135), cv2.FONT_HERSHEY_SIMPLEX, 0.35, (200, 200, 200), 1)

        # View label
        view_label = "EDGE VIEW" if is_edge_view else "COLOR VIEW"
        cv2.putText(frame, view_label, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 0), 2)

        return frame

    def run(self):
        """Main control loop with face detection"""
        if not self.connect():
            return

        print("\n" + "="*70)
        print("TELLO REMOTE CONTROL WITH FACE RECOGNITION")
        print("="*70)
        print("\nControls (HOLD keys for continuous movement):")
        print("  W/A/S/D - Move forward/left/back/right")
        print("  I/P     - Move up/down")
        print("  Q/E     - Rotate left/right")
        print("  T       - Take off")
        print("  L       - Land")
        print("  F       - Toggle face detection on/off")
        print("  ESC     - Emergency land and quit")
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
                    frame = cv2.resize(frame, (640, 480))

                    # Detect and draw faces on color view
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

                    # Combine views vertically (stacked)
                    combined = np.vstack([frame_with_overlay, edges_with_overlay])

                    # Display
                    cv2.imshow('Tello Face Recognition - Color + Edges', combined)

                # Update velocities
                self.update_velocities()

                # Small delay
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

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
