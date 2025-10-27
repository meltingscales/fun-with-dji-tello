#!/usr/bin/env python3
"""
Square Flight Program for DJI Tello
Makes the drone fly in a square pattern while showing live video!
"""

import cv2
import time
from djitellopy import Tello


def display_message(frame, message, position=(50, 50)):
    """Display a message on the video frame"""
    # Add a black background for better readability
    (text_width, text_height), _ = cv2.getTextSize(
        message, cv2.FONT_HERSHEY_SIMPLEX, 1.2, 3
    )
    cv2.rectangle(
        frame,
        (position[0] - 10, position[1] - text_height - 10),
        (position[0] + text_width + 10, position[1] + 10),
        (0, 0, 0),
        -1
    )
    # Draw the text
    cv2.putText(
        frame,
        message,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        1.2,
        (0, 255, 0),  # Green text
        3
    )


def show_video_with_message(tello, message, duration=2):
    """Show video with a message for a specific duration"""
    print(f"📢 {message}")
    start_time = time.time()

    while time.time() - start_time < duration:
        frame = tello.get_frame_read().frame
        if frame is not None:
            # Resize frame for better display
            frame = cv2.resize(frame, (960, 720))
            display_message(frame, message)

            # Show battery level
            battery = tello.get_battery()
            display_message(frame, f"Battery: {battery}%", (50, 650))

            cv2.imshow('Tello Square Flight', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def main():
    print("🚁 Tello Square Flight Program")
    print("=" * 50)

    # Create Tello object and connect
    tello = Tello()

    print("📡 Connecting to Tello...")
    tello.connect()
    print(f"✅ Connected! Battery: {tello.get_battery()}%")

    # Start video stream
    print("📹 Starting video stream...")
    tello.streamon()
    time.sleep(2)  # Give the stream time to start

    # Create window
    cv2.namedWindow('Tello Square Flight')

    # Show initial message
    show_video_with_message(tello, "Press SPACE to start!", 3)

    # Wait for user to press space
    while True:
        frame = tello.get_frame_read().frame
        if frame is not None:
            frame = cv2.resize(frame, (960, 720))
            display_message(frame, "Press SPACE to start!")
            battery = tello.get_battery()
            display_message(frame, f"Battery: {battery}%", (50, 650))
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
        # Take off
        show_video_with_message(tello, "🚀 Taking off...", 2)
        tello.takeoff()
        show_video_with_message(tello, "✅ In the air!", 2)

        # Fly in a square pattern (50 cm per side)
        # Side 1 - Forward
        show_video_with_message(tello, "➡️ Moving forward...", 1)
        tello.move_forward(50)
        show_video_with_message(tello, "✅ Side 1 done!", 1)

        # Turn 90 degrees
        show_video_with_message(tello, "↩️ Turning right...", 1)
        tello.rotate_clockwise(90)
        time.sleep(1)

        # Side 2 - Forward
        show_video_with_message(tello, "➡️ Moving forward...", 1)
        tello.move_forward(50)
        show_video_with_message(tello, "✅ Side 2 done!", 1)

        # Turn 90 degrees
        show_video_with_message(tello, "↩️ Turning right...", 1)
        tello.rotate_clockwise(90)
        time.sleep(1)

        # Side 3 - Forward
        show_video_with_message(tello, "➡️ Moving forward...", 1)
        tello.move_forward(50)
        show_video_with_message(tello, "✅ Side 3 done!", 1)

        # Turn 90 degrees
        show_video_with_message(tello, "↩️ Turning right...", 1)
        tello.rotate_clockwise(90)
        time.sleep(1)

        # Side 4 - Forward
        show_video_with_message(tello, "➡️ Moving forward...", 1)
        tello.move_forward(50)
        show_video_with_message(tello, "✅ Side 4 done!", 1)

        # Turn to face original direction
        show_video_with_message(tello, "↩️ Turning right...", 1)
        tello.rotate_clockwise(90)
        time.sleep(1)

        # Square complete!
        show_video_with_message(tello, "🎉 Square complete!", 3)

        # Land
        show_video_with_message(tello, "🛬 Landing...", 2)
        tello.land()
        show_video_with_message(tello, "✅ Landed safely!", 2)

    except Exception as e:
        print(f"❌ Error: {e}")
        print("🛬 Emergency landing...")
        tello.land()

    finally:
        # Cleanup
        print("🧹 Cleaning up...")
        time.sleep(2)
        cv2.destroyAllWindows()
        tello.streamoff()
        print("👋 Done! Thanks for flying!")


if __name__ == "__main__":
    main()
