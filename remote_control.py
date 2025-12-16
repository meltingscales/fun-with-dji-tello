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
from djitellopy import Tello
from lib import TelloConnection, FlightController, VideoUtils, print_controls
from constants import *


class TelloController:
    def __init__(self):
        self.tello = Tello()
        self.speed = DEFAULT_SPEED
        self.running = False
        self.in_flight = False

        # Current velocities
        self.left_right = 0
        self.forward_backward = 0
        self.up_down = 0
        self.yaw = 0

    def connect(self):
        """Connect to the Tello drone"""
        return TelloConnection.connect_and_start_video(tello=self.tello)

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
            if FlightController.safe_takeoff(self.tello):
                self.in_flight = True

    def land(self):
        if self.in_flight:
            if FlightController.safe_land(self.tello):
                self.in_flight = False

    def emergency_land(self):
        FlightController.emergency_land(self.tello)
        self.in_flight = False

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
        VideoUtils.add_text_overlay(frame, f"Status: {status}", (10, 30),
                                    font_scale=0.6, color=status_color)

        # Battery
        battery_color = VideoUtils.get_battery_color(battery)
        VideoUtils.add_text_overlay(frame, f"Bat: {battery}%", (10, 60),
                                    font_scale=0.5, color=battery_color)

        # Active commands
        active_cmds = self.get_active_commands()
        cmd_color = COLOR_GREEN if active_cmds != "None" else COLOR_GRAY
        VideoUtils.add_text_overlay(frame, f"Active: {active_cmds}", (10, 90),
                                    font_scale=0.5, color=cmd_color)

        # Velocity
        VideoUtils.add_text_overlay(
            frame, f"Vel: LR:{self.left_right:+3d} FB:{self.forward_backward:+3d}",
            (10, 120), font_scale=0.4, color=COLOR_WHITE, thickness=1
        )
        VideoUtils.add_text_overlay(
            frame, f"     UD:{self.up_down:+3d} YAW:{self.yaw:+3d}",
            (10, 140), font_scale=0.4, color=COLOR_WHITE, thickness=1
        )

        # View label
        view_label = "EDGE VIEW" if is_edge_view else "COLOR VIEW"
        VideoUtils.add_text_overlay(frame, view_label, (10, frame.shape[0] - 10),
                                    font_scale=0.5, color=COLOR_YELLOW)

        return frame

    def run(self):
        """Main control loop"""
        if not self.connect():
            return

        print("\n" + "="*60)
        print("TELLO REMOTE CONTROL - CONTINUOUS MOVEMENT")
        print("="*60)

        # Print controls using library function
        print_controls({
            'W/A/S/D': 'Move forward/left/back/right (HOLD)',
            'I/P': 'Move up/down (HOLD)',
            'Q/E': 'Rotate left/right (HOLD)',
            'T': 'Take off',
            'L': 'Land',
            'ESC': 'Emergency land and quit'
        })

        print("Dual view: Color (left) + Edge detection (right)")
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

                    # Create edge detection view using library
                    edges = VideoUtils.create_edge_view(frame)

                    # Get battery
                    battery = self.tello.get_battery()

                    # Add overlays
                    frame_with_overlay = self.add_overlay(frame.copy(), battery, False)
                    edges_with_overlay = self.add_overlay(edges.copy(), battery, True)

                    # Combine both views side by side using library
                    combined = VideoUtils.combine_views_horizontal(
                        frame_with_overlay, edges_with_overlay
                    )

                    # Display
                    cv2.imshow('Tello Remote Control - Color + Edges', combined)

                # Update velocities continuously
                self.update_velocities()

                # Small delay to prevent CPU overload (ESC only for quit - Q is for rotation!)
                cv2.waitKey(10)

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
