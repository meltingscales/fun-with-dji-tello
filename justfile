# DJI Tello Drone Programs
# Run with: just <command>

# Show available commands
default:
    @just --list

# Run the square flight demo
square:
    @echo "🚁 Starting Square Flight Demo..."
    @echo "Make sure your Tello is powered on and connected!"
    uv run python square_flight.py

# Run the remote control program
remote:
    @echo "🎮 Starting Remote Control..."
    @echo "Make sure your Tello is powered on and connected!"
    uv run python remote_control.py

# Run the remote control with facial recognition
faces:
    @echo "👤 Starting Remote Control with Face Detection..."
    @echo "Make sure your Tello is powered on and connected!"
    uv run python remote_control_facial_recognition.py

# Run the controller/joystick remote control
controller:
    @echo "🎮 Starting Controller/Joystick Control..."
    @echo "Make sure your Tello is powered on and connected!"
    @echo "Connect your PS4/Xbox/USB controller before starting!"
    uv run python remote_control_joystick.py

# Install dependencies
install:
    @echo "📦 Installing dependencies..."
    uv sync

# Check battery level (requires tello to be on)
battery:
    @echo "🔋 Checking battery..."
    @uv run python -c "from djitellopy import Tello; t = Tello(); t.connect(); print(f'Battery: {t.get_battery()}%')"

# Run a quick connection test
test-connection:
    @echo "📡 Testing connection to Tello..."
    @uv run python -c "from djitellopy import Tello; t = Tello(); t.connect(); print('✅ Connected!'); print(f'Battery: {t.get_battery()}%'); print(f'Temperature: {t.get_temperature()}°C')"

# Diagnose takeoff issues
diagnose:
    @echo "🔍 Running Takeoff Diagnostics..."
    @echo "This will help identify why takeoff is failing"
    uv run python diagnose_takeoff.py

# Run example using the shared library
example:
    @echo "📚 Running Library Example..."
    @echo "This demonstrates using lib.py and constants.py"
    uv run python example_using_lib.py

# Clean up Python cache files
clean:
    @echo "🧹 Cleaning up..."
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
    @echo "✅ Clean!"
