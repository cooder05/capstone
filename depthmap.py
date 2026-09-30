import pygame
import serial
import time
import os


# ==========================================
# SETTINGS
# ==========================================

PORT = "COM3"
BAUD_RATE = 115200

PAN_MIN = 0
PAN_MAX = 100

TILT_MIN = 0
TILT_MAX = 100

PAN_STEP = 4
TILT_STEP = 4

MAX_DISTANCE = 250

WIDTH = 1000
HEIGHT = 750


# ==========================================
# SAVE SETTINGS
# ==========================================

SAVE_FOLDER = "depth_maps"

os.makedirs(SAVE_FOLDER, exist_ok=True)

scan_number = 1


# ==========================================
# SERIAL
# ==========================================

print("Connecting...")

ser = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=0.1
)

time.sleep(2)

print("Connected!")


# ==========================================
# PYGAME
# ==========================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Ultrasonic Depth Map"
)

clock = pygame.time.Clock()

font = pygame.font.SysFont(
    "Arial",
    20
)

small_font = pygame.font.SysFont(
    "Arial",
    15
)


# ==========================================
# DEPTH MAP SIZE
# ==========================================

pan_count = (
    (PAN_MAX - PAN_MIN) // PAN_STEP
) + 1

tilt_count = (
    (TILT_MAX - TILT_MIN) // TILT_STEP
) + 1

print("Pan positions :", pan_count)
print("Tilt positions:", tilt_count)
print("Total points  :", pan_count * tilt_count)


# ==========================================
# CREATE DEPTH MAP
# ==========================================

def create_depth_map():

    return [
        [-1 for _ in range(pan_count)]
        for _ in range(tilt_count)
    ]


depth_map = create_depth_map()


# ==========================================
# DISPLAY AREA
# ==========================================

MAP_X = 100
MAP_Y = 100

MAP_WIDTH = 800
MAP_HEIGHT = 500

CELL_WIDTH = MAP_WIDTH / pan_count
CELL_HEIGHT = MAP_HEIGHT / tilt_count


# ==========================================
# DISTANCE → COLOR
# ==========================================

def depth_color(distance):

    if distance <= 0:
        return (20, 20, 20)

    distance = min(
        distance,
        MAX_DISTANCE
    )

    brightness = int(
        255 -
        (distance / MAX_DISTANCE) * 220
    )

    return (
        brightness,
        brightness,
        brightness
    )


# ==========================================
# DRAW DEPTH MAP
# ==========================================

def draw_depth_map():

    for tilt_index in range(tilt_count):

        for pan_index in range(pan_count):

            distance = depth_map[
                tilt_index
            ][
                pan_index
            ]

            color = depth_color(distance)

            x = MAP_X + (
                pan_index * CELL_WIDTH
            )

            y = MAP_Y + (
                tilt_index * CELL_HEIGHT
            )

            rect = pygame.Rect(
                int(x),
                int(y),
                int(CELL_WIDTH) + 1,
                int(CELL_HEIGHT) + 1
            )

            pygame.draw.rect(
                screen,
                color,
                rect
            )


# ==========================================
# SAVE DEPTH MAP
# ==========================================

def save_depth_map():

    global scan_number

    image = pygame.Surface(
        (MAP_WIDTH, MAP_HEIGHT)
    )

    image.fill(
        (20, 20, 20)
    )

    for tilt_index in range(tilt_count):

        for pan_index in range(pan_count):

            distance = depth_map[
                tilt_index
            ][
                pan_index
            ]

            color = depth_color(distance)

            x = int(
                pan_index * CELL_WIDTH
            )

            y = int(
                tilt_index * CELL_HEIGHT
            )

            width = int(
                CELL_WIDTH
            ) + 1

            height = int(
                CELL_HEIGHT
            ) + 1

            pygame.draw.rect(
                image,
                color,
                (
                    x,
                    y,
                    width,
                    height
                )
            )

    filename = os.path.join(
        SAVE_FOLDER,
        f"depth_map_{scan_number:03d}.png"
    )

    pygame.image.save(
        image,
        filename
    )

    print()
    print("==============================")
    print(f"SCAN {scan_number} COMPLETE")
    print(f"Saved: {filename}")
    print("==============================")
    print()

    scan_number += 1


# ==========================================
# MAIN LOOP
# ==========================================

running = True

current_pan = PAN_MIN
current_tilt = TILT_MIN
current_distance = 0

previous_tilt = TILT_MIN


try:

    while running:

        # ==================================
        # EVENTS
        # ==================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    running = False


        # ==================================
        # READ SERIAL
        # ==================================

        while ser.in_waiting:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            try:

                pan, tilt, distance = map(
                    float,
                    line.split(",")
                )

                pan = int(pan)
                tilt = int(tilt)

                current_pan = pan
                current_tilt = tilt
                current_distance = distance


                # ==================================
                # STORE MEASUREMENT
                # ==================================

                pan_index = round(
                    (pan - PAN_MIN)
                    / PAN_STEP
                )

                tilt_index = round(
                    (tilt - TILT_MIN)
                    / TILT_STEP
                )

                if (
                    0 <= pan_index < pan_count
                    and
                    0 <= tilt_index < tilt_count
                ):

                    depth_map[
                        tilt_index
                    ][
                        pan_index
                    ] = distance


                # ==================================
                # NEW TILT ROW
                # ==================================

                if tilt != previous_tilt:

                    # A new scan starts when
                    # Arduino returns from
                    # tilt 100 back to tilt 0.
                    if (
                        previous_tilt == TILT_MAX
                        and
                        tilt == TILT_MIN
                    ):

                        save_depth_map()

                        depth_map = (
                            create_depth_map()
                        )

                    previous_tilt = tilt


            except ValueError:

                pass


        # ==================================
        # DRAW
        # ==================================

        screen.fill(
            (10, 10, 10)
        )

        title = font.render(
            "ULTRASONIC DEPTH MAP",
            True,
            (255, 255, 255)
        )

        screen.blit(
            title,
            (20, 20)
        )


        # ==================================
        # DRAW MAP
        # ==================================

        draw_depth_map()


        # ==================================
        # CURRENT POSITION
        # ==================================

        pan_index = round(
            (current_pan - PAN_MIN)
            / PAN_STEP
        )

        tilt_index = round(
            (current_tilt - TILT_MIN)
            / TILT_STEP
        )

        if (
            0 <= pan_index < pan_count
            and
            0 <= tilt_index < tilt_count
        ):

            x = MAP_X + (
                pan_index * CELL_WIDTH
            )

            y = MAP_Y + (
                tilt_index * CELL_HEIGHT
            )

            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (
                    int(x),
                    int(y)
                ),
                5
            )


        # ==================================
        # INFORMATION
        # ==================================

        info = font.render(
            f"Pan: {current_pan}°    "
            f"Tilt: {current_tilt}°    "
            f"Distance: "
            f"{current_distance:.1f} cm",
            True,
            (255, 255, 255)
        )

        screen.blit(
            info,
            (20, 650)
        )


        save_info = small_font.render(
            f"Saved scans: "
            f"{scan_number - 1}",
            True,
            (180, 180, 180)
        )

        screen.blit(
            save_info,
            (20, 680)
        )


        # ==================================
        # UPDATE
        # ==================================

        pygame.display.flip()

        clock.tick(60)


finally:

    ser.close()

    pygame.quit()

    print("Radar stopped.")