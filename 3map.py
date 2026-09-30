import csv
import math
import glob
import os

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation


# ============================================
# SETTINGS
# ============================================

SCAN_FOLDER = "scans"

SENSOR_SPACING = 6.0

TOP_Z = 6.0
MIDDLE_Z = 0.0
BOTTOM_Z = -6.0


# Time between scans in milliseconds
ANIMATION_DELAY = 1000


# ============================================
# FIND SCANS
# ============================================

files = sorted(
    glob.glob(
        os.path.join(
            SCAN_FOLDER,
            "scan_*.csv"
        )
    )
)

if not files:
    print("No scan CSV files found.")
    exit()

print("Found", len(files), "scans")


# ============================================
# FUNCTION TO LOAD ONE SCAN
# ============================================

def load_scan(filename):

    points_x = []
    points_y = []
    points_z = []

    with open(filename, "r") as file:

        reader = csv.DictReader(file)

        for row in reader:

            try:
                pan = float(row["pan"])

                top = float(row["top"])
                middle = float(row["middle"])
                bottom = float(row["bottom"])

            except (ValueError, KeyError):
                continue


            angle = math.radians(pan)


            # -------------------------------
            # TOP
            # -------------------------------

            if top > 0:

                x = top * math.sin(angle)
                y = top * math.cos(angle)
                z = TOP_Z

                points_x.append(x)
                points_y.append(y)
                points_z.append(z)


            # -------------------------------
            # MIDDLE
            # -------------------------------

            if middle > 0:

                x = middle * math.sin(angle)
                y = middle * math.cos(angle)
                z = MIDDLE_Z

                points_x.append(x)
                points_y.append(y)
                points_z.append(z)


            # -------------------------------
            # BOTTOM
            # -------------------------------

            if bottom > 0:

                x = bottom * math.sin(angle)
                y = bottom * math.cos(angle)
                z = BOTTOM_Z

                points_x.append(x)
                points_y.append(y)
                points_z.append(z)


    return points_x, points_y, points_z


# ============================================
# CREATE FIGURE
# ============================================

fig = plt.figure(figsize=(10, 8))

ax = fig.add_subplot(
    111,
    projection="3d"
)


# ============================================
# ANIMATION
# ============================================

def update(frame):

    ax.clear()

    filename = files[frame]

    x, y, z = load_scan(filename)


    # Plot current scan

    ax.scatter(
        x,
        y,
        z,
        s=20
    )


    # -------------------------------
    # AXES
    # -------------------------------

    ax.set_xlabel("X (cm)")
    ax.set_ylabel("Y (cm)")
    ax.set_zlabel("Z (cm)")


    # -------------------------------
    # TITLE
    # -------------------------------

    ax.set_title(
        f"3D Ultrasonic Scan\n"
        f"Time Step: {frame + 1} / {len(files)}\n"
        f"{os.path.basename(filename)}"
    )


    # -------------------------------
    # KEEP SAME SCALE
    # -------------------------------

    ax.set_xlim(-250, 250)
    ax.set_ylim(0, 250)
    ax.set_zlim(-20, 20)


# ============================================
# START ANIMATION
# ============================================

animation = FuncAnimation(
    fig,
    update,
    frames=len(files),
    interval=ANIMATION_DELAY,
    repeat=True
)


plt.show()