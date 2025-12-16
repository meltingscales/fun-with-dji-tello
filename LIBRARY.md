# Tello Library Documentation

This project includes shared utilities to keep the code DRY (Don't Repeat Yourself).

## Files

### `constants.py`
All shared configuration values and constants:
- **Timing**: `CALIBRATION_DELAY` (10s), `TAKEOFF_TIMEOUT` (7s)
- **Battery thresholds**: `CRITICAL_BATTERY`, `LOW_BATTERY`, `WARNING_BATTERY`
- **Temperature thresholds**: `OVERHEAT_TEMP`, `HIGH_TEMP`
- **Flight control**: `DEFAULT_SPEED`, `SQUARE_SIDE_LENGTH`, `ROTATION_ANGLE`
- **Colors**: `COLOR_GREEN`, `COLOR_RED`, etc. (BGR format for OpenCV)
- **Video settings**: Display sizes, FPS calculation interval
- **Face detection**: Scale factors, min size, etc.

### `lib.py`
Shared utility classes and functions:

#### Classes

**`FaceDetector`**
- Face detection using Haar Cascades
- Methods: `detect_faces()`, `draw_faces()`, `toggle()`

**`TelloConnection`**
- `connect_and_start_video()` - Handles connection and 10-second calibration wait
- `check_preflight()` - Battery and temperature safety checks

**`VideoUtils`**
- `create_edge_view()` - Edge detection for low-light visibility
- `add_text_overlay()` - Add text to frames
- `add_text_with_background()` - Add text with background box
- `get_battery_color()` - Get color based on battery level
- `combine_views_horizontal()` - Side-by-side frames
- `combine_views_vertical()` - Stacked frames

**`FlightController`**
- `safe_takeoff()` - Takeoff with error handling and tips
- `safe_land()` - Landing with error handling
- `emergency_land()` - Emergency stop and land

**`FPSCounter`**
- Track and calculate frames per second
- Methods: `update()`, `get_fps()`

#### Functions

**`print_controls(controls_dict)`**
- Pretty-print control schemes
- Example: `print_controls({'W': 'Forward', 'S': 'Back'})`

## Usage Example

```python
from djitellopy import Tello
from lib import TelloConnection, FlightController
from constants import *

tello = Tello()

# Connect and initialize (handles 10s calibration!)
if not TelloConnection.connect_and_start_video(tello):
    exit(1)

# Pre-flight checks
if not TelloConnection.check_preflight(tello):
    exit(1)

# Safe takeoff with error handling
if FlightController.safe_takeoff(tello):
    # Fly!
    time.sleep(3)
    FlightController.safe_land(tello)
```

See `example_using_lib.py` for a complete working example.

## Benefits

### Before (repetitive code):
```python
print("Starting video stream...")
tello.streamon()
print("Waiting for sensors to calibrate (10 seconds)...")
time.sleep(10)
print("Ready to fly!")

battery = tello.get_battery()
if battery < 15:
    print("Battery too low!")
    return False
```

### After (using library):
```python
if not TelloConnection.connect_and_start_video(tello):
    return False

if not TelloConnection.check_preflight(tello):
    return False
```

Much cleaner! 🎉

## Migrating Existing Scripts

To migrate an existing script to use the library:

1. Import from `lib` and `constants`:
   ```python
   from lib import TelloConnection, FlightController, VideoUtils
   from constants import *
   ```

2. Replace connection code with:
   ```python
   TelloConnection.connect_and_start_video(tello)
   ```

3. Replace takeoff with:
   ```python
   FlightController.safe_takeoff(tello)
   ```

4. Replace landing with:
   ```python
   FlightController.safe_land(tello)
   ```

5. Use constants instead of magic numbers:
   ```python
   # Before
   if battery < 15:

   # After
   if battery < LOW_BATTERY:
   ```

## Testing

Run the example script to test the library:
```bash
just example
```
