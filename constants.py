#!/usr/bin/env python3
"""
Shared constants for DJI Tello drone control programs
"""

# Timing constants (in seconds)
CALIBRATION_DELAY = 10  # Critical: Sensors need 10 seconds to calibrate after streamon()
TAKEOFF_TIMEOUT = 7     # Takeoff command can take up to 7 seconds
COMMAND_DELAY = 0.01    # Delay between RC control commands (10ms)

# Battery thresholds (percentage)
CRITICAL_BATTERY = 10   # Below this = refuse to fly
LOW_BATTERY = 15        # Below this = warn user
WARNING_BATTERY = 30    # Yellow warning color threshold

# Temperature thresholds (Celsius)
OVERHEAT_TEMP = 80      # Above this = refuse to fly
HIGH_TEMP = 70          # Above this = warn user

# Flight control
DEFAULT_SPEED = 50      # Default movement speed (0-100)
SQUARE_SIDE_LENGTH = 50 # Side length for square flight (cm)
ROTATION_ANGLE = 90     # Rotation angle for square flight (degrees)

# Network
TELLO_IP = '192.168.10.1'
TELLO_PORT = 8889

# Video display
DEFAULT_WINDOW_WIDTH = 640
DEFAULT_WINDOW_HEIGHT = 480
FPS_CALC_INTERVAL = 20  # Calculate FPS every N frames

# Face detection
FACE_DETECTION_SCALE_FACTOR = 1.1
FACE_DETECTION_MIN_NEIGHBORS = 5
FACE_DETECTION_MIN_SIZE = (30, 30)

# Controller settings
CONTROLLER_DEADZONE = 0.08  # Joystick deadzone to prevent drift
XBOX_DEADZONE = 0.09

# Colors (BGR format for OpenCV)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (0, 0, 255)
COLOR_YELLOW = (0, 255, 255)
COLOR_ORANGE = (0, 165, 255)
COLOR_WHITE = (255, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_BLACK = (0, 0, 0)
