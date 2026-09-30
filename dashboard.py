import serial
import math
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import matplotlib.gridspec as gridspec
import time
import collections

# ============================================
# SETTINGS
# ============================================
PORT = "COM3"
BAUD_RATE = 9600

# ============================================
# CONNECT TO ARDUINO
# ============================================
print(f"Connecting to Edge Radar on {PORT}...")
try:
    # Very short timeout for low-latency realtime reads
    ser = serial.Serial(PORT, BAUD_RATE, timeout=0.01)
    print("Connected!")
except Exception as e:
    print("Could not open serial port:", e)
    exit()

# ============================================
# DASHBOARD SETUP
# ============================================
# Use a sleek dark theme for the command center look
plt.style.use('dark_background')
fig = plt.figure(figsize=(14, 8))
fig.canvas.manager.set_window_title('Context-Aware Edge Radar Dashboard')

# Split screen into Left (Map) and Right (Analytics)
gs = gridspec.GridSpec(2, 2, width_ratios=[1.5, 1])

# --------------------------------------------
# Panel 1: Top-Down Map
# --------------------------------------------
ax_map = fig.add_subplot(gs[:, 0])
ax_map.set_title("Spatial Dwell-Time Analytics (Bird's Eye View)", fontsize=14, weight='bold')
ax_map.set_xlim(-250, 250)
ax_map.set_ylim(0, 250)
ax_map.set_aspect('equal') # Prevents stretching
ax_map.grid(True, alpha=0.2, linestyle='--')
ax_map.set_xlabel("X (cm)")
ax_map.set_ylabel("Y (cm)")

# Draw the radar origin
ax_map.plot(0, 0, marker='o', color='white', markersize=10, label="Radar Agent")

# Scatter arrays for the 3 sensors
scatter_top = ax_map.scatter([], [], c='#ff4444', s=60, label='Top Sensor', alpha=0.7, edgecolors='none')
scatter_mid = ax_map.scatter([], [], c='#44ff44', s=60, label='Mid Sensor', alpha=0.7, edgecolors='none')
scatter_bot = ax_map.scatter([], [], c='#4444ff', s=60, label='Bot Sensor', alpha=0.7, edgecolors='none')
ax_map.legend(loc='upper right')

# --------------------------------------------
# Panel 2: State Machine
# --------------------------------------------
ax_state = fig.add_subplot(gs[0, 1])
ax_state.axis('off')
ax_state.set_title("Edge Agent Pipeline Status", fontsize=12, color='gray')

state_text = ax_state.text(0.5, 0.6, "INITIALIZING...", 
                           fontsize=26, ha='center', va='center', weight='bold')
sub_text = ax_state.text(0.5, 0.4, "Waiting for spatial lock...", 
                         fontsize=12, ha='center', va='center', color='lightgray')

# --------------------------------------------
# Panel 3: Vital Signs (Simulated DSP Phase)
# --------------------------------------------
ax_vitals = fig.add_subplot(gs[1, 1])
ax_vitals.set_title("Phase Unwrapping: Cardiopulmonary Vitals", fontsize=12, color='gray')
ax_vitals.set_xlim(0, 100)
ax_vitals.set_ylim(-2, 2)
ax_vitals.grid(True, alpha=0.2, linestyle='--')
ax_vitals.set_xticks([]) # Hide X axis ticks for clean scrolling effect
ax_vitals.set_ylabel("Amplitude")

line_vitals, = ax_vitals.plot([], [], c='#00ffff', lw=2)

# ============================================
# DATA STORAGE & LOGIC
# ============================================
points_top = {'x': [], 'y': []}
points_mid = {'x': [], 'y': []}
points_bot = {'x': [], 'y': []}

# For state machine intent detection
history_distances = collections.deque(maxlen=30)
current_state = "INITIALIZING"

# For vitals simulation
vitals_data = collections.deque([0]*100, maxlen=100)
t_vitals = 0.0

previous_pan = -1

# ============================================
# EDGE PROCESSING PIPELINE
# ============================================
def process_state_machine():
    global current_state
    
    if len(history_distances) < 15:
        return
        
    # Only consider valid ranges for variance calculation
    valid_dists = [d for d in history_distances if 0 < d < 250]
    
    if len(valid_dists) > 10:
        variance = np.var(valid_dists)
        
        # If variance is low, subject is stationary (dwelling)
        if variance < 20:
            if current_state != "STATIONARY":
                current_state = "STATIONARY"
                state_text.set_color('#44ff44') # Green
                state_text.set_text("STATIONARY")
                sub_text.set_text("DSP Shift: Extracting Vitals from locked bin")
        else:
            if current_state != "TRANSITORY":
                current_state = "TRANSITORY"
                state_text.set_color('#ffaa00') # Orange
                state_text.set_text("TRANSITORY")
                sub_text.set_text("Macro-mobility spatial tracking active")
                
def read_serial():
    global previous_pan
    
    lines = ser.readlines()
    if not lines:
        return
        
    for raw_line in lines:
        line = raw_line.decode("utf-8", errors="ignore").strip()
        if not line: continue
            
        parts = line.split(",")
        if len(parts) != 4: continue
            
        try:
            pan, top, middle, bottom = map(int, parts)
        except ValueError:
            continue
            
        # Add to history for intent tracking (using middle sensor as center of mass proxy)
        if middle > 0:
            history_distances.append(middle)
            
        # Clear points when starting a new scan (sweep reset)
        if pan < previous_pan or (pan == 0 and previous_pan != 0):
            for pts in [points_top, points_mid, points_bot]:
                pts['x'].clear()
                pts['y'].clear()
                
        previous_pan = pan
        angle = math.radians(pan)
        
        if top > 0:
            points_top['x'].append(top * math.sin(angle))
            points_top['y'].append(top * math.cos(angle))
            
        if middle > 0:
            points_mid['x'].append(middle * math.sin(angle))
            points_mid['y'].append(middle * math.cos(angle))
            
        if bottom > 0:
            points_bot['x'].append(bottom * math.sin(angle))
            points_bot['y'].append(bottom * math.cos(angle))


def update(frame):
    global t_vitals
    
    # 1. Edge Ingestion & Intent Processing
    read_serial()
    process_state_machine()
    
    # 2. Update Spatial Analytics Panel
    if points_top['x']:
        scatter_top.set_offsets(np.c_[points_top['x'], points_top['y']])
    else:
        scatter_top.set_offsets(np.empty((0, 2)))
        
    if points_mid['x']:
        scatter_mid.set_offsets(np.c_[points_mid['x'], points_mid['y']])
    else:
        scatter_mid.set_offsets(np.empty((0, 2)))
        
    if points_bot['x']:
        scatter_bot.set_offsets(np.c_[points_bot['x'], points_bot['y']])
    else:
        scatter_bot.set_offsets(np.empty((0, 2)))
        
    # 3. Update Dynamic DSP / Vital Signs Panel
    if current_state == "STATIONARY":
        t_vitals += 0.1
        # Synthesize a cardiopulmonary signal:
        # High freq (heart rate) + low freq (respiration) + mmWave noise profile
        heart_rate_wave = 0.3 * math.sin(t_vitals * 6)  # ~90 BPM
        respiration_wave = 1.0 * math.sin(t_vitals * 1.2) # ~17 breaths/min
        noise = np.random.normal(0, 0.05)
        vitals_data.append(heart_rate_wave + respiration_wave + noise)
        
        line_vitals.set_color('#00ffff') # Cyan
    else:
        # Flatline / Searching for stationary target
        vitals_data.append(np.random.normal(0, 0.05))
        line_vitals.set_color('#555555') # Dark gray
        
    line_vitals.set_data(range(100), list(vitals_data))
    
    return scatter_top, scatter_mid, scatter_bot, state_text, sub_text, line_vitals

# Run at ~30 FPS for smooth waveform rendering
animation = FuncAnimation(fig, update, interval=33, blit=False, cache_frame_data=False)
plt.tight_layout()

try:
    plt.show()
finally:
    ser.close()
    print("Edge Agent disconnected.")
