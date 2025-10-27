# DJI Tello Drone Programs

Four fun Python programs for flying your DJI Tello drone with live video!

## Programs

### 1. Square Flight Demo (`square_flight.py`)
Watch your drone fly in a perfect square pattern while seeing live video with on-screen instructions. Great for demonstrations and learning!

**Features:**
- Autonomous square flight pattern
- Live video feed with status overlay
- On-screen step-by-step instructions
- Battery level monitoring
- Safe landing on completion

### 2. Remote Control (`remote_control.py`)
Fly your Tello drone using your keyboard with live video feedback!

**Controls:**
- `W/A/S/D` - Move forward/left/back/right
- `I/P` - Move up/down
- `Q/E` - Rotate left/right
- `T` - Take off
- `L` - Land
- `ESC` - Emergency land and quit

**Features:**
- Real-time keyboard control
- Live video with control overlay
- Battery monitoring
- Flight status display
- Emergency landing capability

### 3. Remote Control with Facial Recognition (`remote_control_facial_recognition.py`)
Fly your drone with keyboard controls while the AI automatically detects and highlights faces in the video feed!

**Controls:** (same as Remote Control, plus:)
- `F` - Toggle face detection on/off

**Features:**
- All features from Remote Control program
- Real-time face detection using OpenCV's Haar Cascades
- Green bounding boxes around detected faces
- Face counter showing number of faces detected
- Lightweight ML model optimized for real-time performance
- Toggle detection on/off during flight
- FPS (frames per second) display

**Perfect for:**
- Learning about computer vision and AI
- Following people or pets safely
- Search and rescue demonstrations
- Understanding how drones can "see"

### 4. Controller/Joystick Remote Control (`remote_control_joystick.py`)
Fly your drone with a game controller for the most natural flying experience!

**Supported Controllers:**
- PlayStation 4 (PS4) DualShock
- Xbox One controller
- Generic USB game controllers

**Controls:**
- **Left Stick Y** - Throttle (up/down)
- **Left Stick X** - Yaw (rotate)
- **Right Stick Y** - Pitch (forward/backward)
- **Right Stick X** - Roll (left/right)
- **Triangle/Y** - Take off
- **Cross/A** - Land
- **Circle/B** - Toggle face detection
- **L1/LB** - Emergency stop

**Features:**
- Smooth analog control with automatic deadzone
- Auto-detects controller type (PS4/Xbox/Generic)
- Dual view: Color + Edge detection
- Real-time telemetry (roll, pitch, yaw, throttle)
- Optional face detection
- FPS display
- Continuous movement based on stick position

**Perfect for:**
- The most intuitive drone control experience
- Smooth, precise movements
- Gamers who want to fly like a video game
- Advanced flight maneuvers

## Requirements

- DJI Tello or Tello EDU drone
- Python 3.8+
- uv (Python package manager)
- just (command runner) - optional but recommended

## Quick Start

### 1. Setup

Make sure your Tello drone is:
- Fully charged (at least 50% battery recommended)
- Powered on
- Connected to your computer via WiFi

The Tello creates its own WiFi network called `TELLO-XXXXXX`. Connect to it before running the programs.

### 2. Install Dependencies

```bash
# Install with uv
uv sync

# Or if you prefer pip
pip install djitellopy opencv-python pillow
```

### 3. Run Programs

**Using just (recommended):**
```bash
# Square flight demo
just square

# Remote control
just remote

# Remote control with face detection
just faces

# Controller/joystick control
just controller

# Test connection
just test-connection

# Check battery
just battery
```

**Or run directly:**
```bash
# Square flight demo
uv run python square_flight.py

# Remote control
uv run python remote_control.py

# Remote control with facial recognition
uv run python remote_control_facial_recognition.py

# Controller/joystick control
uv run python remote_control_joystick.py
```

## Safety Tips

- Always fly in an open area with at least 2m clearance on all sides
- Keep the drone in your line of sight
- Don't fly near people, animals, or fragile objects
- Check battery level before flying (should be >20%)
- Have a clear flight path with no obstacles
- Be ready to use emergency landing (ESC key) if needed
- Don't fly outdoors in windy conditions (Tello is a small drone)

## Troubleshooting

**Video not showing?**
- Make sure you're connected to the Tello's WiFi network
- Try updating the Tello firmware via the official Tello app
- Wait a few seconds after starting - video stream needs time to initialize

**Drone not responding?**
- Check WiFi connection to `TELLO-XXXXXX`
- Restart the drone
- Make sure battery is charged (>10%)
- Try the connection test: `just test-connection`

**Controls not working in remote control mode?**
- Make sure the video window is selected (click on it)
- Check that the drone has taken off first (press `T`)
- Verify you're pressing the correct keys

**Drone won't take off?**
- Check battery level (must be >10%, recommended >20%)
- Make sure the drone is on a flat surface
- Check that propellers are properly attached
- Restart the drone and try again

## Educational Use

These programs are designed for kids ages 10-15 to learn about:
- Drone programming
- Computer vision and AI (live video and face detection)
- Machine learning in action (facial recognition)
- Coordinate systems and geometry (square pattern)
- User input handling (keyboard controls)
- Safety and responsible flying
- Real-world applications of robotics and AI

For a kid-friendly guide, see [README.simple.md](README.simple.md)!

## Technical Details

**Built with:**
- Python 3.12
- [DJITelloPy](https://github.com/damiafuentes/DJITelloPy) - Tello drone library
- OpenCV - Video display and image processing
- Pillow - Image handling
- uv - Fast Python package manager

## License

MIT License - Feel free to modify and share!

## Resources

- [DJITelloPy Documentation](https://djitellopy.readthedocs.io/)
- [Tello SDK](https://dl-cdn.ryzerobotics.com/downloads/Tello/Tello%20SDK%202.0%20User%20Guide.pdf)
- [Official Tello App](https://www.ryzerobotics.com/tello/downloads)

## Have Fun! 🚁

Remember: Practice makes perfect! Start with the square flight demo to see how the drone moves, then try remote control when you're ready to fly it yourself.

Always fly safely and responsibly!
