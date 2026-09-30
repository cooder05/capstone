# Ultrasonic Radar Capstone

This project provides various visualizations for an Arduino-based ultrasonic or LiDAR scanner over a serial connection. 

## Hardware Setup
Ensure your Arduino is connected and mapped to **`COM3`** before running any scripts. 
*(If your port is different, you will need to update the `PORT` variable at the top of the scripts).*

## How to Run

1. **Live 2D Radar** 
   A classic sweeping 2D radar visualization.
   ```bash
   python test.py
   ```

2. **Live 2D Depth Map**
   A real-time grayscale depth map for a pan-and-tilt scanner setup.
   ```bash
   python depthmap.py
   ```

3. **Record 3D Scans**
   Logs data from a 3-sensor setup into CSV files inside the `scans/` folder.
   ```bash
   python serialtocsv.py
   ```

4. **View Recorded 3D Scans**
   Animates the saved 3D point cloud scans.
   ```bash
   python 3map.py
   ```

5. **Live 3D Map**
   Visualizes the 3-sensor setup in real-time on a 3D scatter plot.
   ```bash
   python live_3dmap.py
   ```
