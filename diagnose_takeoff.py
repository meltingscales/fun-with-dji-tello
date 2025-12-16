#!/usr/bin/env python3
"""
Tello Takeoff Diagnostic Tool
Helps identify why takeoff is failing
"""

import cv2
import time
from djitellopy import Tello


def check_sensor_readings(tello):
    """Check all available sensor readings"""
    print("\n" + "="*60)
    print("SENSOR READINGS:")
    print("="*60)

    try:
        battery = tello.get_battery()
        print(f"✓ Battery: {battery}%")
        if battery < 15:
            print("  ⚠️  WARNING: Battery too low for safe flight!")
            return False
    except Exception as e:
        print(f"✗ Battery check failed: {e}")
        return False

    try:
        temp = tello.get_temperature()
        print(f"✓ Temperature: {temp}°C")
        if temp > 80:
            print("  ⚠️  WARNING: Drone is overheating! Let it cool down.")
            return False
        elif temp > 70:
            print("  ⚠️  WARNING: Temperature is high. Consider cooling.")
    except Exception as e:
        print(f"✗ Temperature check failed: {e}")

    try:
        height = tello.get_height()
        print(f"✓ Current height: {height} cm")
    except Exception as e:
        print(f"✗ Height check failed: {e}")

    try:
        barometer = tello.get_barometer()
        print(f"✓ Barometer: {barometer} cm")
    except Exception as e:
        print(f"✗ Barometer check failed: {e}")

    try:
        flight_time = tello.get_flight_time()
        print(f"✓ Flight time: {flight_time}s")
    except Exception as e:
        print(f"✗ Flight time check failed: {e}")

    return True


def test_video_stream(tello):
    """Test if video stream is working and show a preview"""
    print("\n" + "="*60)
    print("TESTING VIDEO STREAM:")
    print("="*60)
    print("Starting video stream...")

    try:
        tello.streamon()
        print("✓ Stream command sent successfully")

        print("\nWaiting for sensors to calibrate (10 seconds)...")
        for i in range(10, 0, -1):
            print(f"  {i} seconds remaining...", end='\r')
            time.sleep(1)
        print("\n✓ Calibration wait complete")

        # Try to get a frame
        print("\nAttempting to capture video frame...")
        for attempt in range(5):
            frame = tello.get_frame_read().frame
            if frame is not None:
                print(f"✓ Video frame captured (attempt {attempt + 1})")

                # Show the frame
                frame = cv2.resize(frame, (640, 480))

                # Add diagnostic overlay
                cv2.putText(frame, "TELLO DIAGNOSTIC VIEW", (10, 30),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                cv2.putText(frame, "Check if image is clear", (10, 60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                cv2.putText(frame, "Look for obstacles below drone", (10, 85),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
                cv2.putText(frame, "Press any key to continue...", (10, 450),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

                cv2.imshow('Tello Diagnostic - Video Check', frame)
                print("\nShowing video preview. Press any key to continue...")
                cv2.waitKey(0)
                cv2.destroyAllWindows()
                return True
            else:
                print(f"  ✗ Attempt {attempt + 1} failed, retrying...")
                time.sleep(1)

        print("✗ Failed to capture video frame after 5 attempts")
        return False

    except Exception as e:
        print(f"✗ Video stream error: {e}")
        return False


def test_surface_detection(tello):
    """Test if the drone can see the surface below it"""
    print("\n" + "="*60)
    print("SURFACE DETECTION TEST:")
    print("="*60)

    print("\nCapturing downward view...")
    try:
        frame = tello.get_frame_read().frame
        if frame is not None:
            # The camera points forward, but we can check lighting
            frame = cv2.resize(frame, (640, 480))
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            avg_brightness = gray.mean()

            print(f"✓ Average brightness: {avg_brightness:.1f}/255")

            if avg_brightness < 30:
                print("  ⚠️  WARNING: Environment is very dark!")
                print("     The Tello needs good lighting for its optical sensors.")
            elif avg_brightness < 60:
                print("  ⚠️  WARNING: Environment is dim. More light recommended.")
            else:
                print("  ✓ Lighting appears adequate")

            # Show the frame
            cv2.putText(frame, f"Brightness: {avg_brightness:.1f}/255", (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            cv2.putText(frame, "Press any key to continue...", (10, 450),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            cv2.imshow('Tello Diagnostic - Lighting Check', frame)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

            return avg_brightness >= 30
        else:
            print("✗ Could not capture frame")
            return False
    except Exception as e:
        print(f"✗ Surface detection error: {e}")
        return False


def attempt_takeoff_with_diagnostics(tello):
    """Attempt takeoff with detailed diagnostics"""
    print("\n" + "="*60)
    print("TAKEOFF ATTEMPT:")
    print("="*60)

    print("\nPRE-FLIGHT CHECKLIST:")
    print("  ✓ Drone on flat, non-reflective surface?")
    print("  ✓ Good lighting in room?")
    print("  ✓ No obstacles within 2 meters?")
    print("  ✓ Propellers spin freely?")
    print("  ✓ Propeller guards secure (if installed)?")
    print("\nPress ENTER to attempt takeoff, or Ctrl+C to cancel...")
    input()

    try:
        print("\n🚀 Sending takeoff command...")
        print("(This may take up to 7 seconds to complete)")

        start_time = time.time()
        tello.takeoff()
        elapsed = time.time() - start_time

        print(f"✓ TAKEOFF SUCCESSFUL! (took {elapsed:.1f} seconds)")

        # Show success in video
        time.sleep(2)
        frame = tello.get_frame_read().frame
        if frame is not None:
            frame = cv2.resize(frame, (640, 480))
            cv2.putText(frame, "TAKEOFF SUCCESSFUL!", (50, 240),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
            cv2.imshow('Tello Diagnostic - Success!', frame)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()

        print("\n🛬 Landing drone...")
        tello.land()
        print("✓ Landed successfully")
        return True

    except Exception as e:
        print(f"\n✗ TAKEOFF FAILED: {e}")
        print("\nPOSSIBLE CAUSES:")
        print("  1. Surface is too reflective (try matte surface)")
        print("  2. Surface has patterns that confuse optical sensors")
        print("  3. Room is too dark")
        print("  4. Drone is overheating")
        print("  5. IMU needs calibration (use official Tello app)")
        print("  6. Drone needs firmware update (use official Tello app)")
        print("  7. Hardware issue with motors or sensors")

        # Try to capture error state
        try:
            frame = tello.get_frame_read().frame
            if frame is not None:
                frame = cv2.resize(frame, (640, 480))
                cv2.putText(frame, "TAKEOFF FAILED", (50, 240),
                           cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 0, 255), 3)
                cv2.putText(frame, "See console for details", (50, 280),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
                cv2.imshow('Tello Diagnostic - Error', frame)
                cv2.waitKey(5000)
                cv2.destroyAllWindows()
        except:
            pass

        return False


def main():
    print("="*60)
    print("TELLO TAKEOFF DIAGNOSTIC TOOL")
    print("="*60)
    print("\nThis tool will help diagnose why your Tello won't take off.")
    print("Make sure your Tello is:")
    print("  - Powered on")
    print("  - Connected to your computer via WiFi")
    print("  - Placed on a flat surface")

    print("\nConnecting to Tello...")
    tello = Tello()

    try:
        tello.connect()
        print("✓ Connected to Tello!")

        # Run diagnostics
        if not check_sensor_readings(tello):
            print("\n⚠️  Sensor check failed. Cannot proceed safely.")
            return

        if not test_video_stream(tello):
            print("\n⚠️  Video stream failed. This may indicate a connectivity issue.")
            print("Try restarting the drone and reconnecting.")
            return

        if not test_surface_detection(tello):
            print("\n⚠️  Lighting may be insufficient.")

        # Attempt takeoff
        success = attempt_takeoff_with_diagnostics(tello)

        if success:
            print("\n" + "="*60)
            print("✓✓✓ DIAGNOSIS COMPLETE - DRONE IS WORKING! ✓✓✓")
            print("="*60)
            print("\nYour drone should now work with the square flight program.")
        else:
            print("\n" + "="*60)
            print("DIAGNOSIS COMPLETE - ISSUE FOUND")
            print("="*60)
            print("\nRECOMMENDED ACTIONS:")
            print("1. Open the official Tello app on your phone")
            print("2. Calibrate the IMU (Settings > Calibrate IMU)")
            print("3. Update firmware if available")
            print("4. Try flying manually in the app first")
            print("5. If still failing, check for hardware issues")

    except Exception as e:
        print(f"\n✗ Connection failed: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Make sure Tello is powered on")
        print("2. Connect to Tello WiFi network (TELLO-XXXXXX)")
        print("3. Disable other WiFi/network connections")
        print("4. Try restarting the Tello")

    finally:
        print("\n🧹 Cleaning up...")
        try:
            tello.streamoff()
        except:
            pass
        cv2.destroyAllWindows()
        print("Done!")


if __name__ == "__main__":
    main()
