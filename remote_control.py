#!/usr/bin/env python3
"""
WASD Remote Control for DJI Tello with Continuous Movement
Fly the drone using your keyboard with live video!

Controls:
  WASD - Move forward/left/back/right (hold for continuous movement)
  I/P  - Move up/down (hold for continuous movement)
  Q/E  - Rotate left/right (hold for continuous movement)
  T    - Take off
  L    - Land
  ESC  - Emergency land and quit

Features:
  - Continuous movement while holding keys
  - Dual view: Color + Edge detection (for low light)
  - Real-time velocity display
"""

import cv2
import time
import keyboard
import numpy as np
from djitellopy import Tello


class TelloController:
    def __init__(self):
        self.tello = Tello()
        self.speed = 50  # Speed percentage (0-100)
        self.running = False
        self.in_flight = False

        # Current velocities
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

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
        time.sleep(2)
        return True

    def update_velocities(self):
        """Update velocity values based on currently pressed keys"""
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

        # Check key states and set velocities
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

        # Send RC control command
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

    def emergency_land(self):
        print("Emergency landing!")
        self.tello.send_rc_control(0, 0, 0, 0)
        self.tello.land()
        self.in_flight = False

    def create_edge_view(self, frame):
        """Create edge detection view for low light visibility"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)

        # Apply Canny edge detection
        edges = cv2.Canny(blurred, 50, 150)

        # Convert back to BGR for display
        edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)

        # Make edges more visible (green tint)
        edges_bgr[:, :, 1] = edges  # Green channel

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
        cv2.putText(frame, f"Status: {status}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)

        # Battery
        battery_color = (0, 255, 0) if battery > 30 else (0, 165, 255) if battery > 15 else (0, 0, 255)
        cv2.putText(frame, f"Bat: {battery}%", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, battery_color, 2)

        # Active commands
        active_cmds = self.get_active_commands()
        cmd_color = (0, 255, 0) if active_cmds != "None" else (128, 128, 128)
        cv2.putText(frame, f"Active: {active_cmds}", (10, 90),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, cmd_color, 2)

        # Velocity
        cv2.putText(frame, f"Vel: LR:{self.left_right:+3d} FB:{self.forward_backward:+3d}",
                    (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(frame, f"     UD:{self.up_down:+3d} YAW:{self.yaw:+3d}",
                    (10, 140), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        # View label
        view_label = "EDGE VIEW" if is_edge_view else "COLOR VIEW"
        cv2.putText(frame, view_label, (10, frame.shape[0] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 2)

        return frame

    def run(self):
        """Main control loop"""
        if not self.connect():
            return

        print("\n" + "="*60)
        print("TELLO REMOTE CONTROL - CONTINUOUS MOVEMENT")
        print("="*60)
        print("\nControls (HOLD keys for continuous movement):")
        print("  W/A/S/D - Move forward/left/back/right")
        print("  I/P     - Move up/down")
        print("  Q/E     - Rotate left/right")
        print("  T       - Take off")
        print("  L       - Land")
        print("  ESC     - Emergency land and quit")
        print("\nDual view: Color (left) + Edge detection (right)")
        print("Edge view helps with low-light visibility!")
        print("="*60 + "\n")

        # Set up keyboard hooks for takeoff/land/quit
        keyboard.on_press_key('t', lambda _: self.takeoff() if not self.in_flight else None)
        keyboard.on_press_key('l', lambda _: self.land() if self.in_flight else None)
        keyboard.on_press_key('esc', lambda _: setattr(self, 'running', False))

        self.running = True

        try:
            while self.running:
                # Get video frame
                frame = self.tello.get_frame_read().frame
                if frame is not None:
                    # Resize to standard size
                    frame = cv2.resize(frame, (480, 360))

                    # Create edge detection view
                    edges = self.create_edge_view(frame)

                    # Get battery
                    battery = self.tello.get_battery()

                    # Add overlays
                    frame_with_overlay = self.add_overlay(frame.copy(), battery, False)
                    edges_with_overlay = self.add_overlay(edges.copy(), battery, True)

                    # Combine both views side by side
                    combined = np.hstack([frame_with_overlay, edges_with_overlay])

                    # Display
                    cv2.imshow('Tello Remote Control - Color + Edges', combined)

                # Update velocities continuously
                self.update_velocities()

                # Small delay to prevent CPU overload
                if cv2.waitKey(10) & 0xFF == ord('q'):
                    break

                # Check if ESC was pressed
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

    controller = TelloController()
    controller.run()


if __name__ == "__main__":
    main()
