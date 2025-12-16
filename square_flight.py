#!/usr/bin/env python3
"""
Square Flight Program for DJI Tello
Makes the drone fly in a square pattern while showing live video!
"""

import cv2
import time
from djitellopy import Tello
from lib import TelloConnection, FlightController, VideoUtils
from constants import *


def show_video_with_message(tello, message, duration=2):
    """Show video with a message for a specific duration"""
    print(f"📢 {message}")
    start_time = time.time()

    while time.time() - start_time < duration:
        frame = tello.get_frame_read().frame
        if frame is not None:
            # Resize frame for better display
            frame = cv2.resize(frame, (960, 720))

            # Add message with background
            VideoUtils.add_text_with_background(frame, message, (50, 50))

            # Show battery level
            battery = tello.get_battery()
            battery_color = VideoUtils.get_battery_color(battery)
            VideoUtils.add_text_with_background(
                frame, f"Battery: {battery}%", (50, 650),
                font_scale=1.0, text_color=battery_color
            )

            cv2.imshow('Tello Square Flight', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main():
    print("🚁 Tello Square Flight Program")
    print("=" * 50)

    # Create Tello object
    tello = Tello()

    # Connect and start video stream with proper calibration
    if not TelloConnection.connect_and_start_video(tello):
        return

    # Create window
    cv2.namedWindow('Tello Square Flight')

    # Show initial message
    show_video_with_message(tello, "Press SPACE to start!", 3)

    # Wait for user to press space
    while True:
        frame = tello.get_frame_read().frame
        if frame is not None:
            frame = cv2.resize(frame, (960, 720))
            VideoUtils.add_text_with_background(frame, "Press SPACE to start!", (50, 50))

            battery = tello.get_battery()
            battery_color = VideoUtils.get_battery_color(battery)
            VideoUtils.add_text_with_background(
                frame, f"Battery: {battery}%", (50, 650),
                font_scale=1.0, text_color=battery_color
            )
            cv2.imshow('Tello Square Flight', frame)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(' '):  # Space bar
            break
        elif key == ord('q'):
            print("❌ Cancelled by user")
            cv2.destroyAllWindows()
            tello.streamoff()
            return

    try:
        # Pre-flight safety checks
        if not TelloConnection.check_preflight(tello):
            raise Exception("Pre-flight checks failed")

        # Take off
        show_video_with_message(tello, "🚀 Taking off...", 2)
        if not FlightController.safe_takeoff(tello):
            raise Exception("Takeoff failed")
        show_video_with_message(tello, "✅ In the air!", 2)

        # Fly in a square pattern
        for side in range(4):
            # Forward movement
            show_video_with_message(tello, f"➡️ Moving forward (Side {side + 1})...", 1)
            tello.move_forward(SQUARE_SIDE_LENGTH)
            show_video_with_message(tello, f"✅ Side {side + 1} done!", 1)

            # Turn 90 degrees (except after last side)
            if side < 3:
                show_video_with_message(tello, "↩️ Turning right...", 1)
                tello.rotate_clockwise(ROTATION_ANGLE)
                time.sleep(1)

        # Final turn to face original direction
        show_video_with_message(tello, "↩️ Turning right...", 1)
        tello.rotate_clockwise(ROTATION_ANGLE)
        time.sleep(1)

        # Square complete!
        show_video_with_message(tello, "🎉 Square complete!", 3)

        # Land
        show_video_with_message(tello, "🛬 Landing...", 2)
        FlightController.safe_land(tello)
        show_video_with_message(tello, "✅ Landed safely!", 2)

    except Exception as e:
        print(f"❌ Error: {e}")
        FlightController.emergency_land(tello)

    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        time.sleep(2)
        cv2.destroyAllWindows()
        tello.streamoff()
        print("👋 Done! Thanks for flying!")


if __name__ == "__main__":
    main()
