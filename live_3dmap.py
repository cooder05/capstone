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
    ser = serial.Serial(PORT, BAUD_RATE, timeout=0.05)
    print("Connected!")
except Exception as e:
    print("Could not open serial port:", e)
    exit()

# ============================================
# CREATE FIGURE
# ============================================
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# ============================================
# DATA STORAGE
# ============================================
points_x = []
points_y = []
points_z = []

previous_pan = -1

# ============================================
# READ AND PARSE SERIAL
# ============================================
def read_serial():
    global points_x, points_y, points_z, previous_pan
    
    # Read as much as is available in the buffer
    while ser.in_waiting:
        line = ser.readline().decode("utf-8", errors="ignore").strip()
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
            
        # Clear points when starting a new scan (pan wraps back to 0)
        if pan < previous_pan or (pan == 0 and previous_pan != 0):
            points_x.clear()
            points_y.clear()
            points_z.clear()
            
        previous_pan = pan
            
        angle = math.radians(pan)
        
        # TOP SENSOR
        if top > 0:
            points_x.append(top * math.sin(angle))
            points_y.append(top * math.cos(angle))
            points_z.append(TOP_Z)
            
        # MIDDLE SENSOR
        if middle > 0:
            points_x.append(middle * math.sin(angle))
            points_y.append(middle * math.cos(angle))
            points_z.append(MIDDLE_Z)
            
        # BOTTOM SENSOR
        if bottom > 0:
            points_x.append(bottom * math.sin(angle))
            points_y.append(bottom * math.cos(angle))
            points_z.append(BOTTOM_Z)


# ============================================
# ANIMATION LOOP
# ============================================
def update(frame):
    # Fetch new data
    read_serial()
    
    # Redraw
    ax.clear()
    
    if points_x:
        ax.scatter(points_x, points_y, points_z, s=20)
        
    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel("Z (cm)")
    ax.set_title("Live 3D Ultrasonic Scan")
    
    # Keep constant scale (matches 3map.py bounds)
    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 250)
    ax.set_zlim(-20, 20)

# 50ms interval = ~20 FPS refresh
animation = FuncAnimation(
    fig, 
    update, 
    interval=50, 
    cache_frame_data=False
)

try:
    plt.show()
finally:
    ser.close()
    print("Serial connection closed.")
