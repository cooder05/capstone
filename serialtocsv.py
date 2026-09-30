import serial
import csv
import os
import time


# =====================================
# SERIAL SETTINGS
# =====================================

PORT = "COM3"
BAUD_RATE = 9600


# =====================================
# SAVE SETTINGS
# =====================================

SAVE_FOLDER = "scans"

os.makedirs(
    SAVE_FOLDER,
    exist_ok=True
)


# =====================================
# CONNECT TO ARDUINO
# =====================================

ser = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=1
)

# Give Arduino time to reset
time.sleep(2)

print("--------------------------------")
print("Connected to Arduino")
print("Port:", PORT)
print("Baud rate:", BAUD_RATE)
print("Waiting for data...")
print("--------------------------------")


# =====================================
# SCAN VARIABLES
# =====================================

current_scan = []

scan_number = 15

reached_max = False


# =====================================
# MAIN LOOP
# =====================================

try:

    while True:

        # Read one line from Arduino
        line = ser.readline().decode(
            "utf-8",
            errors="ignore"
        ).strip()


        # Nothing received
        if not line:
            continue


        # =================================
        # PRINT SERIAL OUTPUT
        # =================================

        print("Arduino:", line)


        # =================================
        # PARSE DATA
        # =================================

        parts = line.split(",")


        # Expected:
        # pan,top,middle,bottom

        if len(parts) != 4:
            print("Invalid data:", line)
            continue


        try:

            pan = int(parts[0])
            top = int(parts[1])
            middle = int(parts[2])
            bottom = int(parts[3])

        except ValueError:

            print("Invalid numbers:", line)
            continue


        # =================================
        # START OF 0 → 100 SCAN
        # =================================

        if pan == 0 and not reached_max:

            current_scan = []

            current_scan.append([
                pan,
                top,
                middle,
                bottom
            ])

            continue


        # =================================
        # NORMAL DATA
        # =================================

        current_scan.append([
            pan,
            top,
            middle,
            bottom
        ])


        # =================================
        # REACHED 100°
        # =================================

        if pan == 100:

            reached_max = True

            print("Reached 100°")


        # =================================
        # REACHED 0° AGAIN
        # =================================

        elif pan == 0 and reached_max:

            filename = os.path.join(
                SAVE_FOLDER,
                f"scan_{scan_number:03d}.csv"
            )


            # =================================
            # SAVE CSV
            # =================================

            with open(
                filename,
                "w",
                newline=""
            ) as file:

                writer = csv.writer(file)

                writer.writerow([
                    "pan",
                    "top",
                    "middle",
                    "bottom"
                ])

                writer.writerows(
                    current_scan
                )


            print()
            print("--------------------------------")
            print("SCAN COMPLETE")
            print("Saved:", filename)
            print(
                "Measurements:",
                len(current_scan)
            )
            print("--------------------------------")
            print()


            # Next scan
            scan_number += 1

            current_scan = []

            reached_max = False


except KeyboardInterrupt:

    print()
    print("Stopping...")


finally:

    ser.close()

    print("Serial connection closed.")