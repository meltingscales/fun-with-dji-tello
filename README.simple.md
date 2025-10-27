# Flying Your Tello Drone - Kid's Guide!

Hey there, future pilot! Ready to fly a real drone with code? Let's go!

## What You'll Learn

- How to program a drone to fly by itself
- How to control a drone with your keyboard
- How to fly with a game controller (like PS4 or Xbox!)
- How video streaming works
- How AI can recognize faces (artificial intelligence!)
- Why safety matters when flying

## What You Get

You have **FOUR AWESOME PROGRAMS**:

### Program 1: The Square Dancer
Your drone will fly in a perfect square all by itself while you watch on your screen! It's like watching a flying robot do a dance!

### Program 2: You're The Pilot!
Take control! Fly the drone with your keyboard like playing a video game, but it's REAL!

### Program 3: The AI Face Finder!
Fly the drone AND watch as the computer draws boxes around people's faces it sees! It's like giving your drone super-vision powers! The AI can spot faces in real-time and track them on the screen.

### Program 4: The Game Controller Pro!
Use your PlayStation or Xbox controller to fly the drone! The joysticks control movement smoothly just like in video games. This is the COOLEST way to fly - it feels like you're playing a flight simulator, but the drone actually moves in real life!

## Before You Start - SUPER IMPORTANT!

### Safety First!
- Find a big open space (your living room works if it's big enough!)
- Move stuff out of the way - at least 6 feet of space around you
- NO pets or little siblings nearby
- Don't fly near breakable things (like that expensive vase!)
- Keep the drone where you can see it
- If something goes wrong, press `ESC` to land immediately!

### Get Your Drone Ready
1. Charge your Tello drone (the light should be green)
2. Turn it on (press the button on the side)
3. Wait for the light to blink yellow
4. On your computer, connect to the Tello's WiFi
   - Look for a network called `TELLO-XXXXXX` (X's are numbers)
   - Connect to it (no password needed!)

## How To Fly - The Easy Way

### Step 1: Open Your Terminal
- On Mac: Find "Terminal" in Applications
- On Windows: Find "Command Prompt" or "PowerShell"
- On Linux: You probably already know! 😄

### Step 2: Go To The Right Folder
```bash
cd fun-with-dji-tello
```

### Step 3: Install Everything
This gets the drone software ready:
```bash
uv sync
```

### Step 4: Pick Your Program!

#### Option A: Watch The Square Dance
```bash
just square
```

What happens:
1. A window opens showing what the drone sees
2. Press `SPACE` when you're ready
3. The drone takes off (cool, right?)
4. It flies in a square - watch the screen to see which side it's on!
5. It lands by itself when done

**Your job:** Just watch and enjoy! The drone does everything automatically.

#### Option B: Be The Pilot
```bash
just remote
```

What happens:
1. A window opens with the drone's camera view
2. You'll see controls on the screen
3. Press `T` to take off
4. Use these keys to fly:
   - `W` = Forward (↑)
   - `S` = Backward (↓)
   - `A` = Left (←)
   - `D` = Right (→)
   - `I` = Up ⬆️
   - `P` = Down ⬇️
   - `Q` = Spin left 🔄
   - `E` = Spin right 🔁
   - `L` = Land
   - `ESC` = EMERGENCY STOP!

**Your job:** Fly the drone! Try making shapes, flying around obstacles (safely!), or just cruising around.

#### Option C: AI Face Detective Mode!
```bash
just faces
```

What happens:
1. Everything from Option B, PLUS...
2. The AI starts looking for faces automatically!
3. When it sees a face, it draws a green box around it
4. You can see how many faces it found (it counts them!)
5. Press `F` to turn face detection on or off whenever you want

**Your job:** Fly around and see if the drone can spot faces! Try:
- Having a friend stand somewhere and see if the drone can find them
- Turning face detection off (`F`) and on again
- Counting how many faces it can detect at once
- Learning how AI "sees" the world!

**Cool fact:** The drone uses the same kind of technology that cameras use to focus on faces, or that helps cars detect pedestrians!

#### Option D: Game Controller Mode!
```bash
just controller
```

**First:** Plug in your PS4, Xbox, or USB game controller before running this!

What happens:
1. The program detects your controller automatically
2. The joysticks control the drone smoothly - just like a video game!
3. Left stick moves up/down and spins, right stick moves forward/back/left/right
4. Press Triangle (PS4) or Y (Xbox) to take off
5. Press Cross (PS4) or A (Xbox) to land
6. Press Circle (PS4) or B (Xbox) to turn on face detection!
7. EMERGENCY: Press L1 (PS4) or LB (Xbox) to stop everything NOW

**Your job:** This is the PRO way to fly! Try:
- Making smooth circles (easier with joysticks than keyboard!)
- Flying backwards while spinning (feels like a movie!)
- Combining forward movement with rotation for cool maneuvers
- Using the analog sticks to control speed (push harder = go faster!)

**Why it's awesome:**
- Your thumbs control everything - no need to take your eyes off the screen!
- Smooth analog control means you can go slow OR fast
- Feels just like playing a flight game, but it's REAL!
- The joysticks have "dead zones" so tiny movements don't make the drone drift

**Controller tips:**
- Start with small stick movements until you get the hang of it
- The drone responds to HOW MUCH you push the stick (not just which direction)
- If your controller isn't working, make sure it's plugged in BEFORE you start the program

## Tips For New Pilots

### Starting Out
1. **Start with the square program** - Watch how the drone moves
2. **Then try keyboard control** - But start slow!
3. **Try face detection mode** - See AI in action!
4. **Level up to game controller** - This is the ultimate flying experience!
5. **Practice taking off and landing** - That's the hardest part
6. **Try small movements first** - Don't press keys/move sticks too fast!

### Getting Good
- The drone moves about 1 foot (30cm) each time you press a movement key
- Wait for one movement to finish before starting another
- Keep track of where the drone is facing (it turns when you use Q/E)
- Watch the battery meter - land when it gets low!

### If Something Goes Wrong
- **Drone flying weird?** → Press `ESC` to land now
- **Video frozen?** → The drone is still flying! Press `ESC` to land
- **Lost control?** → Press `ESC` to land
- **Not responding?** → Turn off the drone and restart everything

## Cool Things To Try

Once you're comfortable flying:

1. **Fly a circle** - Keep pressing right and forward at the same time
2. **Take a tour** - Fly around your room and look at things from above
3. **Play follow the leader** - Have a friend walk around while you follow with the drone
4. **Create patterns** - Try triangles, zigzags, or your initials!
5. **Obstacle course** - Set up safe obstacles and fly around them
6. **Face finder challenge** - Use face detection mode and see how many people the drone can spot!
7. **Hide and seek** - Have friends hide around corners and use the drone to find them (AI mode on!)
8. **Compare modes** - Fly with face detection OFF, then turn it ON - see the difference in FPS (speed)!
9. **Controller combo moves** - With a game controller, try flying forward while spinning in a circle!
10. **Speed control challenge** - Practice using different stick pressures to fly at different speeds
11. **Precision landing** - Use the controller to land on a specific spot (like a piece of paper)

## Understanding The Code (For Curious Minds!)

Want to know how it works?

### The Square Program
```python
tello.takeoff()        # Go up!
tello.move_forward(50) # Fly forward 50cm
tello.rotate_clockwise(90)  # Turn right
# ...repeat for each side of the square
tello.land()           # Come back down
```

It's like giving your drone a list of instructions: "Take off, go forward, turn, go forward, turn..." and so on!

### The Remote Control
```python
if key == 'w':         # Did they press W?
    tello.move_forward(30)  # Then move forward!
```

It's always watching for your key presses and telling the drone what to do!

### The Face Detection AI
```python
faces = face_cascade.detectMultiScale(frame)  # Find faces!
for (x, y, w, h) in faces:
    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)  # Draw green box!
```

The AI looks at each video frame and tries to find patterns that look like faces. When it finds one, it draws a box around it! It's like the computer learned what faces look like and can spot them super fast!

### The Controller Program
```python
left_x = joystick.get_axis(0)  # Read left stick X position
yaw = int(left_x * 100)        # Convert to drone speed (-100 to 100)
tello.send_rc_control(roll, pitch, throttle, yaw)  # Send to drone!
```

The controller program reads your joystick positions 30+ times per second! It converts the stick position (how far you push it) into a speed value, then continuously tells the drone to move at that speed. That's why it feels so smooth - it's like the drone is reading your mind through the controller!

## Troubleshooting (When Stuff Doesn't Work)

### "I don't see any video!"
- Is your computer connected to the Tello's WiFi? Check!
- Wait a few seconds - the video takes time to start
- Try turning the drone off and on again

### "The drone won't take off!"
- Is the battery charged? (Should be green light)
- Is it on a flat surface?
- Battery too low? (Needs to be over 10%)

### "The keys aren't doing anything!"
- Click on the video window first (make sure it's selected)
- Did you take off first? Press `T`!
- Are you pressing the right keys?

### "It's going crazy!"
- PRESS `ESC` RIGHT NOW to land!
- Make sure you have enough space
- Check that nothing is blocking the drone

### "Face detection isn't working!"
- Make sure you pressed `F` to turn it on
- The AI works best with good lighting (turn on some lights!)
- Faces need to be facing the camera (not turned away)
- Try getting closer - the face needs to be big enough to detect
- If the video is too slow, the AI might be working hard - this is normal!

### "My controller isn't working!"
- Is it plugged in? Check the USB cable!
- Plug it in BEFORE you start the program
- Try a different USB port
- Make sure the controller is charged (for wireless controllers)
- The program shows which controller it detected - check if it's the right one
- Try pressing buttons - you should see them light up on the controller

### "The drone is flying crazy with the controller!"
- Are you moving the sticks too much? Start gentle!
- The joysticks are super sensitive - small movements = small speed
- Let go of the sticks and they should center (drone stops)
- If it drifts when sticks are centered, the program has "deadzone" to help
- Practice hovering first (take off, then don't touch the sticks!)

## Want To Learn More?

### Modify The Code!
- Can you make the square bigger? (Hint: change the numbers in `square_flight.py`)
- Can you make it do a triangle instead?
- Can you add more messages on the screen?
- Can you change the color of the face detection boxes? (Hint: look for `(0, 255, 0)`)
- Can you adjust the controller sensitivity? (Hint: look for "deadzone" in the controller program)
- Can you make the drone respond faster/slower to controller inputs?

### Learn About Drones!
- How do drones stay in the air? (It's all about the spinning propellers!)
- What's a gyroscope? (It helps the drone know which way is up!)
- How does the camera work? (It sends video over WiFi!)

### Learn About AI!
- How does the computer recognize faces? (It looks for patterns like eyes, nose, mouth!)
- What's machine learning? (Teaching computers to learn from examples!)
- Why does face detection need good lighting? (The AI needs to see clearly!)
- Could you train the AI to detect other things? (Yes! Dogs, cats, cars - anything!)

### Learn About Controllers!
- How do analog sticks work? (They measure how far you push in each direction!)
- What's a deadzone? (A small area where tiny movements are ignored to prevent drift!)
- Why do game controllers feel smooth? (They send position updates many times per second!)
- How does the program know which button you pressed? (Each button has a number ID!)
- Can any USB controller work? (Most of them! The program detects what's connected!)

## Most Important Rules

1. **Always fly safely** - No people or pets nearby
2. **Watch the battery** - Land before it gets too low
3. **Stay in control** - If you're not sure, land!
4. **Have fun** - That's what this is all about!
5. **Learn and experiment** - Try new things (safely!)

## Ready To Fly?

You're all set! Remember:
- Start with the square program to watch how it works
- Then try keyboard control when you're ready
- Try the AI face detection mode to see computer vision in action!
- Level up to game controller for the ultimate flying experience!
- Always fly safely
- Have an adult nearby when you're learning
- HAVE FUN!

---

Questions? Problems? Cool discoveries? Share them with your friends, teachers, or coding group!

**Now go fly that drone!** 🚁✨

P.S. - Once you get really good, you can even modify the code to make the drone do whatever you want! The sky's the limit! (Well, actually the ceiling is the limit indoors, but you get the idea! 😄)
