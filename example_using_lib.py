#!/usr/bin/env python3
"""
Example: Simple Tello flight using the shared library
This demonstrates how much cleaner the code is with lib.py and constants.py
"""

import cv2
import time
from djitellopy import Tello
from lib import (
    TelloConnection,
    FlightController,
    VideoUtils,
    FPSCounter,
    print_controls
)
from constants import *


def main():
    print("🚁 Tello Flight Example (using lib.py)")
    print("="*50)

    # Create Tello instance
    tello = Tello()

    # Connect and start video stream (handles all the initialization!)
    if not TelloConnection.connect_and_start_video(tello):
        print("Failed to connect. Exiting.")
        return

    # Pre-flight safety checks
    if not TelloConnection.check_preflight(tello):
        print("Pre-flight checks failed. Exiting.")
        tello.streamoff()
        return

    # Create FPS counter
    fps_counter = FPSCounter()

    # Show controls
    print_controls({
        'SPACE': 'Take off',
        'L': 'Land',
        'Q': 'Quit'
    })

    # Create window
    cv2.namedWindow('Tello Example')

    in_flight = False

    try:
        print("\nPress SPACE to take off...")

        while True:
            # Get frame
            frame = tello.get_frame_read().frame
            if frame is not None:
                # Resize
                frame = cv2.resize(frame, (DEFAULT_WINDOW_WIDTH, DEFAULT_WINDOW_HEIGHT))

                # Get telemetry
                battery = tello.get_battery()
                fps_counter.update()

                # Add status overlay
                status = "FLYING" if in_flight else "ON GROUND"
                status_color = COLOR_GREEN if in_flight else COLOR_RED

                VideoUtils.add_text_overlay(
                    frame, f"Status: {status}", (10, 30),
                    color=status_color
                )

                VideoUtils.add_text_overlay(
                    frame, f"Battery: {battery}%", (10, 60),
                    color=VideoUtils.get_battery_color(battery)
                )

                VideoUtils.add_text_overlay(
                    frame, f"FPS: {fps_counter.get_fps():.1f}", (10, 90),
                    color=COLOR_WHITE
                )

                # Show frame
                cv2.imshow('Tello Example', frame)

            # Handle keyboard input
            key = cv2.waitKey(1) & 0xFF

            if key == ord(' '):  # Space - takeoff
                if not in_flight:
                    if FlightController.safe_takeoff(tello):
                        in_flight = True
                        time.sleep(2)  # Hover for 2 seconds

            elif key == ord('l'):  # L - land
                if in_flight:
                    if FlightController.safe_land(tello):
                        in_flight = False

            elif key == ord('q'):  # Q - quit
                print("\nQuitting...")
                break

    except KeyboardInterrupt:
        print("\nKeyboard interrupt!")

    except Exception as e:
        print(f"\nError: {e}")

    finally:
        # Cleanup
        print("Cleaning up...")
        if in_flight:
            FlightController.emergency_land(tello)

        cv2.destroyAllWindows()
        tello.streamoff()
        print("Done!")


if __name__ == "__main__":
    main()
