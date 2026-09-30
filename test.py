import pygame
import serial
import math
import time

# ==========================================
# SETTINGS
# ==========================================

PORT = "COM3"
BAUD_RATE = 115200

MAX_DISTANCE = 250       # Maximum distance in cm

WIDTH = 1000
HEIGHT = 700

CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT - 70

RADAR_RADIUS = 550

# ==========================================
# SERIAL CONNECTION
# ==========================================

print("Connecting to Arduino...")

ser = serial.Serial(
    PORT,
    BAUD_RATE,
    timeout=0.1
)

time.sleep(2)

print("Connected!")

# ==========================================
# PYGAME SETUP
# ==========================================

pygame.init()

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT)
)

pygame.display.set_caption(
    "Ultrasonic Radar"
)

clock = pygame.time.Clock()

# Fonts
font = pygame.font.SysFont(
    "Arial",
    20
)

small_font = pygame.font.SysFont(
    "Arial",
    16
)

# ==========================================
# COLORS
# ==========================================

BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 80, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)

# ==========================================
# RADAR DATA
# ==========================================

current_angle = 90
current_distance = -1

# Store latest distance for every angle
distances = {}

# ==========================================
# FUNCTIONS
# ==========================================

def polar_to_screen(angle, distance):

    # Convert angle to radians
    theta = math.radians(angle)

    # Scale distance to radar radius
    r = (distance / MAX_DISTANCE) * RADAR_RADIUS

    # 0 degrees = right
    # 90 degrees = up

    x = CENTER_X + r * math.cos(theta)

    y = CENTER_Y - r * math.sin(theta)

    return int(x), int(y)


def draw_radar():

    # ======================================
    # RADAR ARCS
    # ======================================

    for distance in range(50, MAX_DISTANCE + 1, 50):

        radius = int(
            (distance / MAX_DISTANCE)
            * RADAR_RADIUS
        )

        rect = pygame.Rect(
            CENTER_X - radius,
            CENTER_Y - radius,
            radius * 2,
            radius * 2
        )

        # Draw only the upper semicircle
        pygame.draw.arc(
            screen,
            DARK_GREEN,
            rect,
            math.pi,
            2 * math.pi,
            1
        )

        # Distance label

        label = small_font.render(
            f"{distance} cm",
            True,
            GREEN
        )

        screen.blit(
            label,
            (
                CENTER_X + 5,
                CENTER_Y - radius - 18
            )
        )

    # ======================================
    # ANGLE LINES
    # ======================================

    for angle in range(0, 181, 30):

        x, y = polar_to_screen(
            angle,
            MAX_DISTANCE
        )

        pygame.draw.line(
            screen,
            DARK_GREEN,
            (CENTER_X, CENTER_Y),
            (x, y),
            1
        )

        # Angle label

        label = small_font.render(
            f"{angle}°",
            True,
            GREEN
        )

        screen.blit(
            label,
            (
                x - 10,
                y - 10
            )
        )

    # ======================================
    # BASE LINE
    # ======================================

    pygame.draw.line(
        screen,
        GREEN,
        (CENTER_X - RADAR_RADIUS, CENTER_Y),
        (CENTER_X + RADAR_RADIUS, CENTER_Y),
        2
    )


def draw_sweep():

    x, y = polar_to_screen(
        current_angle,
        MAX_DISTANCE
    )

    pygame.draw.line(
        screen,
        GREEN,
        (CENTER_X, CENTER_Y),
        (x, y),
        3
    )


def draw_objects():

    for angle, distance in distances.items():

        if distance <= 0:
            continue

        if distance > MAX_DISTANCE:
            continue

        x, y = polar_to_screen(
            angle,
            distance
        )

        pygame.draw.circle(
            screen,
            RED,
            (x, y),
            6
        )


def draw_information():

    title = font.render(
        "ULTRASONIC RADAR",
        True,
        GREEN
    )

    screen.blit(
        title,
        (20, 20)
    )

    angle_text = font.render(
        f"Angle: {current_angle:.0f}°",
        True,
        WHITE
    )

    screen.blit(
        angle_text,
        (20, 55)
    )

    if current_distance > 0:

        distance_text = font.render(
            f"Distance: {current_distance:.1f} cm",
            True,
            WHITE
        )

    else:

        distance_text = font.render(
            "Distance: --",
            True,
            WHITE
        )

    screen.blit(
        distance_text,
        (20, 85)
    )


# ==========================================
# MAIN LOOP
# ==========================================

running = True

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
        # READ SERIAL DATA
        # ==================================

        while ser.in_waiting:

            line = ser.readline().decode(
                "utf-8",
                errors="ignore"
            ).strip()

            if not line:
                continue

            try:

                angle, distance = map(
                    float,
                    line.split(",")
                )

                current_angle = angle
                current_distance = distance

                # Store latest measurement
                distances[int(angle)] = distance

            except ValueError:

                pass

        # ==================================
        # DRAW
        # ==================================

        screen.fill(BLACK)

        draw_radar()

        draw_objects()

        draw_sweep()

        draw_information()

        # ==================================
        # UPDATE SCREEN
        # ==================================

        pygame.display.flip()

        clock.tick(60)

finally:

    ser.close()

    pygame.quit()

    print("Radar stopped.")