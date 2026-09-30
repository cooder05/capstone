import serial
import math
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# ============================================
# SETTINGS
# ============================================
PORT = "COM3"
BAUD_RATE = 9600

TOP_Z = 6.0
MIDDLE_Z = 0.0
BOTTOM_Z = -6.0

# ============================================
# CONNECT TO ARDUINO
# ============================================
print(f"Connecting to Arduino on {PORT}...")
try:
    ser = serial.Serial(PORT, BAUD_RATE, timeout=0.01) # Reduced timeout for lower latency
    print("Connected!")
except Exception as e:
    print("Could not open serial port:", e)
    exit()

# ============================================
# CREATE FIGURE
# ============================================
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# Force the 3D plot to be a perfect cube
ax.set_box_aspect((1, 1, 1))

ax.set_xlabel("X (cm)")
ax.set_ylabel("Y (cm)")
ax.set_zlabel("Z (cm)")
ax.set_title("Live 3D Ultrasonic Scan")

# Set static bounds (Matches 3map.py)
ax.set_xlim(-250, 250)
ax.set_ylim(0, 250)
ax.set_zlim(-20, 20)

# Create 3 separate scatter objects with different colors for each sensor
scatter_top = ax.scatter([], [], [], c='r', s=20, label='Top Sensor')
scatter_mid = ax.scatter([], [], [], c='g', s=20, label='Middle Sensor')
scatter_bot = ax.scatter([], [], [], c='b', s=20, label='Bottom Sensor')
ax.legend()

# ============================================
# DATA STORAGE
# ============================================
points_top = {'x': [], 'y': [], 'z': []}
points_mid = {'x': [], 'y': [], 'z': []}
points_bot = {'x': [], 'y': [], 'z': []}

previous_pan = -1

# ============================================
# READ AND PARSE SERIAL
# ============================================
def read_serial():
    global previous_pan
    
    # Read all available lines rapidly
    lines = ser.readlines()
    if not lines:
        return
        
    for raw_line in lines:
        line = raw_line.decode("utf-8", errors="ignore").strip()
        if not line:
            continue
            
        parts = line.split(",")
        if len(parts) != 4:
            continue
            
        try:
            pan = int(parts[0])
            top = int(parts[1])
            middle = int(parts[2])
            bottom = int(parts[3])
        except ValueError:
            continue
            
        # Clear points when starting a new scan (pan sweeps back)
        if pan < previous_pan or (pan == 0 and previous_pan != 0):
            for pts in [points_top, points_mid, points_bot]:
                pts['x'].clear()
                pts['y'].clear()
                pts['z'].clear()
                
        previous_pan = pan
        angle = math.radians(pan)
        
        # TOP SENSOR
        if top > 0:
            points_top['x'].append(top * math.sin(angle))
            points_top['y'].append(top * math.cos(angle))
            points_top['z'].append(TOP_Z)
            
        # MIDDLE SENSOR
        if middle > 0:
            points_mid['x'].append(middle * math.sin(angle))
            points_mid['y'].append(middle * math.cos(angle))
            points_mid['z'].append(MIDDLE_Z)
            
        # BOTTOM SENSOR
        if bottom > 0:
            points_bot['x'].append(bottom * math.sin(angle))
            points_bot['y'].append(bottom * math.cos(angle))
            points_bot['z'].append(BOTTOM_Z)


# ============================================
# ANIMATION LOOP
# ============================================
def update(frame):
    read_serial()
    
    # Update scatter plots data directly instead of clearing the whole axes.
    # This massively reduces latency and prevents flickering.
    
    if points_top['x']:
        scatter_top._offsets3d = (points_top['x'], points_top['y'], points_top['z'])
    else:
        scatter_top._offsets3d = ([], [], [])
        
    if points_mid['x']:
        scatter_mid._offsets3d = (points_mid['x'], points_mid['y'], points_mid['z'])
    else:
        scatter_mid._offsets3d = ([], [], [])
        
    if points_bot['x']:
        scatter_bot._offsets3d = (points_bot['x'], points_bot['y'], points_bot['z'])
    else:
        scatter_bot._offsets3d = ([], [], [])
        
    return scatter_top, scatter_mid, scatter_bot

# 10ms interval for lower latency and smoother updates
animation = FuncAnimation(
    fig, 
    update, 
    interval=10, 
    cache_frame_data=False
)

try:
    plt.show()
finally:
    ser.close()
    print("Serial connection closed.")
