"""
GREED HOUSE
A short psychological risk / decision-making game made with Pygame.

Main Menu:
    BUILD HOUSE - the core loop:
        1. FARM   - click falling material blocks (BRICK / IRON / GOLD /
                     DIAMOND) to collect them for free, straight
                     into your stockpile. Rarer blocks fall much faster, so
                     they're worth more but harder to catch. The screen shows
                     how many of each material you currently own. Coins AND
                     the material stockpile both reset to 0 (well, coins to
                     the starting amount of 100) at the start of every new
                     round, ready to spend in the Shop.
        2. SHOP   - spend money on a building material (Wood / Brick / Iron / ...),
                     or use whatever you already collected in Farm for free.
                     Better material = lower chance of collapse.
        3. BUILD  - build the house higher and higher.
                     Every floor adds more score, but also more risk.
                     Reaching floor 20 pays a 50 coin bonus, and reaching
                     floor 50 grants a short bonus round of Find Resources
                     without losing your progress (each is one-time per
                     build attempt).
                     You can also open the SHOP again at any time while
                     building, to spend coins earned mid-run without
                     losing your progress.
        4. Decide: STOP now, or BUILD one more floor?

Controls:
    Mouse  - click coins / blocks / buttons
    SPACE  - Build Higher (while playing)
    ENTER  - Stop (while playing)
    S      - Open Shop (while playing)

Run with:
    python main.py
"""

import pygame
import random
import sys
import json
import os

# ============================================================
# BASIC SETUP
# ============================================================

pygame.init()
pygame.font.init()

WIDTH = 1280
HEIGHT = 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("GREED HOUSE")
clock = pygame.time.Clock()

# Fonts
font_small = pygame.font.SysFont("arial", 20)
font_medium = pygame.font.SysFont("arial", 28)
font_large = pygame.font.SysFont("arial", 48)
font_title = pygame.font.SysFont("arial", 64, bold=True)

# ============================================================
# COLORS
# ============================================================

COLOR_BG_MENU = (245, 240, 222)        # cream
COLOR_BG_PLAY = (198, 226, 250)        # light blue sky
COLOR_BG_FARM = (210, 240, 210)        # light green
COLOR_GROUND = (150, 200, 140)

COLOR_WALL_DAMAGED = (200, 150, 120)
COLOR_ROOF = (200, 70, 40)             # dark red/orange
COLOR_WINDOW = (120, 190, 230)         # sky blue
COLOR_DOOR = (90, 55, 30)              # dark brown
COLOR_OUTLINE = (35, 22, 15)           # bold dark outline for emphasis

COLOR_DANGER = (200, 30, 30)
COLOR_SAFE = (40, 140, 70)
COLOR_WARNING = (230, 160, 20)
COLOR_COIN = (235, 190, 50)

COLOR_TEXT = (40, 40, 40)
COLOR_TEXT_LIGHT = (255, 255, 255)
COLOR_CRACK = (70, 60, 55)

COLOR_BUTTON = (250, 250, 250)
COLOR_BUTTON_BORDER = (15, 15, 15)     # bold dark border for emphasis
COLOR_BUTTON_BUILD = (200, 230, 200)
COLOR_BUTTON_STOP = (240, 200, 200)
COLOR_BUTTON_SELECTED = (255, 245, 200)

# ============================================================
# GAME STATES
# ============================================================

STATE_MENU = "MENU"
STATE_FARM = "FARM"
STATE_BONUS_FARM = "BONUS_FARM"
STATE_SHOP = "SHOP"
STATE_PLAYING = "PLAYING"
STATE_STOPPED = "STOPPED"
STATE_COLLAPSED = "COLLAPSED"
STATE_STATISTICS = "STATISTICS"

current_state = STATE_MENU

# ============================================================
# MATERIALS
# ============================================================
# Better material = lower risk_multiplier = safer house.

MATERIALS = {
    "WOOD":    {"label": "WOOD",    "cost": 0,  "risk_multiplier": 1.0,  "color": (196, 154, 108)},
    "BRICK":   {"label": "BRICK",   "cost": 5,  "risk_multiplier": 0.70, "color": (188, 92, 70)},
    "IRON":    {"label": "IRON",    "cost": 15, "risk_multiplier": 0.45, "color": (150, 155, 165)},
    "GOLD":    {"label": "GOLD",    "cost": 25, "risk_multiplier": 0.30, "color": (232, 189, 60)},
    "DIAMOND": {"label": "DIAMOND", "cost": 50, "risk_multiplier": 0.0,  "color": (185, 235, 250)},
}
MATERIAL_ORDER = ["WOOD", "BRICK", "IRON", "GOLD", "DIAMOND"]

# ============================================================
# GAME VARIABLES
# ============================================================

current_floor = 0
best_floor = 0

STARTER_COINS = 100   # what a brand-new save starts with (existing saves are unaffected - load_data overrides this)

coins = STARTER_COINS           # persists across the whole session AND is saved to disk
selected_material = "WOOD"      # the material that will be used to build the NEXT floor
shop_from_playing = False       # True when the Shop was opened mid-build (BUILD HIGHER screen), not from Farm
inventory = {"BRICK": 0, "IRON": 0, "GOLD": 0, "DIAMOND": 0}  # owned stock of each paid material (WOOD is free & unlimited)


shop_message = ""               # feedback text for the shop (e.g. "NOT ENOUGH COINS")
shop_message_timer = 0
shop_message_color = None

cracks = []                     # list of (floor_index, x_offset, y_offset)
close_call_active = False
close_call_timer = 0

floor_materials = []            # material key used to build each floor, in order (for per-block coloring)

milestone_message = ""
milestone_timer = 0

# Big banner shown dead-center of the screen specifically for the floor 20 /
# floor 50 rewards (separate from milestone_message, which stays in the small
# side panel for the "5/10/15..." flavor-text hints).
center_message = ""
center_message_timer = 0

last_round_floor = 0
last_round_result = ""          # "STOPPED" or "COLLAPSED"
last_round_material = "WOOD"

greed_score = 0
greed_label = ""

# --- Farm mini-game state ("FIND RESOURCES": click falling material blocks
# and coins) ---
# Clicking a material block adds ONE unit of that material straight to the
# stockpile - easy/common materials fall more often AND more slowly than
# rare/hard ones, in this order from easiest to hardest:
# BRICK, IRON, GOLD, DIAMOND.
# Clicking a falling COIN instead adds its random value (20-40) straight to
# your coin total - the bigger the coin's value, the faster it falls, so
# high-value coins are worth grabbing but harder to catch in time.
FARM_DURATION_SECONDS = 15
FARM_MATERIAL_ORDER = ["BRICK", "IRON", "GOLD", "DIAMOND"]
FARM_MATERIAL_WEIGHTS = [50, 30, 15, 5]      # easy -> hard, must line up with FARM_MATERIAL_ORDER
FARM_MATERIAL_SPEEDS = {                     # (min, max) fall speed - rarer blocks fall faster
    "BRICK":   (5.0, 7.0),
    "IRON":    (6.5, 9.0),
    "GOLD":    (8.5, 11.5),
    "DIAMOND": (11.0, 15.0),
}

FARM_COIN_SPAWN_CHANCE = 0.3    # chance a spawn is a coin instead of a material block
FARM_COIN_MIN_VALUE = 20
FARM_COIN_MAX_VALUE = 40
FARM_COIN_SPEED_MIN = 5.0        # a value-1 coin falls about this fast...
FARM_COIN_SPEED_MAX = 16.0       # ...and a value-30 coin falls about this fast


def coin_speed_for_value(value):
    """Higher-value coins fall faster - scales linearly across the value range."""
    span = FARM_COIN_MAX_VALUE - FARM_COIN_MIN_VALUE
    ratio = (value - FARM_COIN_MIN_VALUE) / span if span > 0 else 0
    return FARM_COIN_SPEED_MIN + ratio * (FARM_COIN_SPEED_MAX - FARM_COIN_SPEED_MIN)


# Bonus round of Find Resources that can trigger mid-build (see FLOOR_MILESTONES
# below) - same falling-block gameplay, just shorter, and it hands control
# back to BUILD HIGHER afterwards instead of going to the Shop.
BONUS_FARM_DURATION_SECONDS = 6

# Floor milestones for a single build attempt (reset in reset_game()):
# EVERY FLOOR_MILESTONE_COINS_FLOOR floors (20, 40, 60, ...) pays a flat coin
# bonus - this one repeats for as long as you keep climbing. Reaching floor
# 50 (FLOOR_MILESTONE_BONUS_FARM_FLOOR) still grants a one-time bonus round
# of the Find Resources mini-game.
FLOOR_MILESTONE_COINS_FLOOR = 20
FLOOR_MILESTONE_COINS_AMOUNT = 125
FLOOR_MILESTONE_BONUS_FARM_FLOOR = 50

milestone_50_awarded = False    # reset per build attempt in reset_game()

farm_time_left = 0              # frames remaining
farm_coins = []                 # list of dicts: x, y, speed, size, and either
                                 # "material" (BRICK/IRON/GOLD/DIAMOND) or
                                 # "is_coin"+"value" (20-40) for falling coins
farm_spawn_cooldown = 0

# Statistics (persist for the whole session, saved to disk)
stats = {
    "best_floor": 0,
    "highest_attempt": 0,
    "total_attempts": 0,
    "total_collapses": 0,
    "total_stops": 0,
    "total_floors_built": 0,
    "total_coins_earned": 0,
}

# Buttons store their rects so handle_events can check clicks against them.
buttons = {}

# ============================================================
# SAVE / LOAD (fixes progress resetting every time the game is launched)
# ============================================================
# Everything above was already kept in memory correctly for the length of
# one run of the program - the actual reset players noticed happens because
# nothing was ever written to disk, so coins/stats/best_floor all went
# back to 0 the next time the game was started. This writes them to a small
# JSON save file next to the script and loads them back on launch.

SAVE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "greed_house_save.json")


def save_data():
    """Write coins, inventory, best_floor and stats to disk so they survive restarts."""
    data = {
        "coins": coins,
        "inventory": inventory,
        "best_floor": best_floor,
        "stats": stats,
    }
    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f)
    except OSError:
        pass  # if the disk write fails, just keep playing with in-memory progress


def load_data():
    """Load coins, inventory, best_floor and stats from disk, if a save file exists."""
    global coins, best_floor

    if not os.path.exists(SAVE_FILE):
        return
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError):
        return

    coins = data.get("coins", coins)
    best_floor = data.get("best_floor", best_floor)
    loaded_inventory = data.get("inventory", {})
    for key in inventory:
        if key in loaded_inventory:
            inventory[key] = loaded_inventory[key]
    loaded_stats = data.get("stats", {})
    for key in stats:
        if key in loaded_stats:
            stats[key] = loaded_stats[key]


# ============================================================
# DRAWING: HOUSE PARTS
# ============================================================

def draw_roof(surface, x, y, width, color=COLOR_ROOF):
    """Draw a triangular roof. (x, y) is the bottom-left corner of the roof."""
    top_point = (x + width / 2, y - width * 0.35)
    left_point = (x, y)
    right_point = (x + width, y)
    pygame.draw.polygon(surface, color, [top_point, left_point, right_point])
    pygame.draw.polygon(surface, COLOR_OUTLINE, [top_point, left_point, right_point], 2)


def draw_ceiling(surface, x, y, width):
    """Draw a thin ceiling/floor divider line between two floors."""
    pygame.draw.rect(surface, COLOR_OUTLINE, (x, y, width, 4))


def draw_wall(surface, x, y, width, height, wall_color, damaged=False):
    """Draw the wall of one floor (a simple rectangle) using the chosen material color."""
    color = COLOR_WALL_DAMAGED if damaged else wall_color
    pygame.draw.rect(surface, color, (x, y, width, height))
    pygame.draw.rect(surface, COLOR_OUTLINE, (x, y, width, height), 2)


def draw_floor(surface, x, y, width):
    """Draw the floor line at the bottom of one level."""
    pygame.draw.rect(surface, COLOR_OUTLINE, (x, y, width, 4))


def draw_window(surface, x, y, size=18):
    """Draw a small square window with a cross frame."""
    rect = pygame.Rect(x, y, size, size)
    pygame.draw.rect(surface, COLOR_WINDOW, rect)
    pygame.draw.rect(surface, COLOR_OUTLINE, rect, 2)
    pygame.draw.line(surface, COLOR_OUTLINE, (x + size / 2, y), (x + size / 2, y + size), 1)
    pygame.draw.line(surface, COLOR_OUTLINE, (x, y + size / 2), (x + size, y + size / 2), 1)


def draw_door(surface, x, y, width=28, height=42):
    """Draw the front door (only used on the ground floor)."""
    rect = pygame.Rect(x, y, width, height)
    pygame.draw.rect(surface, COLOR_DOOR, rect)
    pygame.draw.rect(surface, COLOR_OUTLINE, rect, 2)
    pygame.draw.circle(surface, (230, 220, 180), (x + width - 6, y + height // 2), 2)


def draw_house_damage(surface, floors, base_x, base_y, floor_width, floor_height, scale, tilt_offset):
    """
    Draw extra visual feedback that shows how dangerous the house has become.
    This does not affect gameplay, it is only visual feedback for the player.
    """
    if floors >= 16:
        top_y = base_y - floors * floor_height * scale - 40 * scale
        warn_text = font_medium.render("!", True, COLOR_WARNING)
        surface.blit(warn_text, (base_x + floor_width * scale / 2 - 5, top_y))

    for crack in cracks:
        floor_index, offset_x, offset_y = crack
        crack_y = base_y - floor_index * floor_height * scale
        crack_x = base_x + offset_x * scale + tilt_offset(floor_index)
        p1 = (crack_x, crack_y - offset_y * scale)
        p2 = (crack_x + 8 * scale, crack_y - offset_y * scale + 10 * scale)
        p3 = (crack_x - 4 * scale, crack_y - offset_y * scale + 20 * scale)
        pygame.draw.lines(surface, COLOR_CRACK, False, [p1, p2, p3], 2)


def draw_house(surface, floors, area_top, area_bottom, area_center_x, floor_colors, default_color):
    """
    Draw the whole house made of `floors` levels, a roof on top,
    and a door on the ground floor.

    Each floor is colored using the material it was actually built with
    (floor_colors[floor_index]) so you can see, block by block, what you
    used to build that level - not just whatever material is selected now.
    `default_color` is used as a fallback for any floor missing an entry
    (shouldn't normally happen, just a safety net).

    The house always fits inside the vertical space between
    area_top and area_bottom, using the loop below (no if/elif chain
    for each possible floor count).
    """
    floor_width = 200
    floor_height = 46
    roof_height_extra = floor_width * 0.35

    total_height = floors * floor_height + roof_height_extra
    available_height = area_bottom - area_top

    scale = 1.0
    if total_height > available_height:
        scale = available_height / total_height
    scale = max(scale, 0.12)

    scaled_floor_width = floor_width * scale
    scaled_floor_height = floor_height * scale

    base_x = area_center_x - scaled_floor_width / 2
    base_y = area_bottom  # ground line, house grows upward from here

    def tilt_offset(floor_index):
        if floors <= 5:
            return 0
        lean_strength = min((floors - 5) * 0.6, 18)
        return (floor_index / max(floors, 1)) * lean_strength

    for floor_index in range(floors):
        y = base_y - (floor_index + 1) * scaled_floor_height
        x = base_x + tilt_offset(floor_index)

        damaged = floors >= 11
        wall_color = floor_colors[floor_index] if floor_index < len(floor_colors) else default_color
        draw_wall(surface, x, y, scaled_floor_width, scaled_floor_height, wall_color, damaged)
        draw_ceiling(surface, x, y, scaled_floor_width)
        draw_floor(surface, x, y + scaled_floor_height - 2, scaled_floor_width)

        window_size = max(10, int(16 * scale))
        draw_window(
            surface,
            x + scaled_floor_width / 2 - window_size / 2,
            y + scaled_floor_height / 2 - window_size / 2,
            window_size,
        )

        if floor_index == 0:
            door_w = max(10, int(26 * scale))
            door_h = max(14, int(38 * scale))
            draw_door(
                surface,
                x + scaled_floor_width / 2 - door_w / 2,
                y + scaled_floor_height - door_h,
                door_w,
                door_h,
            )

    roof_x = base_x + tilt_offset(floors)
    roof_y = base_y - floors * scaled_floor_height
    draw_roof(surface, roof_x, roof_y, scaled_floor_width)

    draw_house_damage(surface, floors, base_x, base_y, floor_width, floor_height, scale, tilt_offset)


# ============================================================
# DRAWING: UI HELPERS
# ============================================================

def draw_background(surface, color):
    surface.fill(color)


def draw_button(surface, rect, text, color=COLOR_BUTTON, text_color=COLOR_TEXT, font=font_medium, border_color=COLOR_BUTTON_BORDER):
    pygame.draw.rect(surface, color, rect, border_radius=8)
    pygame.draw.rect(surface, border_color, rect, 5, border_radius=8)
    label = font.render(text, True, text_color)
    label_rect = label.get_rect(center=rect.center)
    surface.blit(label, label_rect)


def draw_text_center(surface, text, y, font=font_medium, color=COLOR_TEXT):
    label = font.render(text, True, color)
    rect = label.get_rect(center=(WIDTH / 2, y))
    surface.blit(label, rect)


def draw_ui(surface):
    """Draw the fixed UI (does not move with the camera/scale)."""
    draw_text_center(surface, "GREED HOUSE", 40, font_large)
    draw_text_center(
        surface,
        f"EVERY {FLOOR_MILESTONE_COINS_FLOOR} FLOORS: +{FLOOR_MILESTONE_COINS_AMOUNT} COINS   |   "
        f"EVERY {FLOOR_MILESTONE_BONUS_FARM_FLOOR} FLOORS: BONUS FIND RESOURCES",
        75,
        font_small,
        COLOR_TEXT,
    )
    floor_text = font_medium.render(f"CURRENT FLOOR: {current_floor}", True, COLOR_TEXT)
    surface.blit(floor_text, (30, 100))
    best_text = font_medium.render(f"BEST: {best_floor}", True, COLOR_TEXT)
    surface.blit(best_text, (30, 130))
    material_text = font_small.render(f"MATERIAL: {MATERIALS[selected_material]['label']}", True, COLOR_TEXT)
    surface.blit(material_text, (30, 160))
    coins_text = font_small.render(f"COINS: {coins}", True, COLOR_TEXT)
    surface.blit(coins_text, (30, 185))

    # Attention-grabbing messages sit in a side panel (right side) so they
    # never cover the house in the middle of the screen.
    side_x = WIDTH - 260
    side_y = 100

    if milestone_timer > 0 and milestone_message:
        panel_rect = pygame.Rect(side_x - 10, side_y - 10, 250, 50)
        pygame.draw.rect(surface, COLOR_BUTTON, panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_WARNING, panel_rect, 4, border_radius=8)
        msg_text = font_small.render(milestone_message, True, COLOR_WARNING)
        surface.blit(msg_text, (side_x, side_y))
        side_y += 60

    if close_call_active:
        panel_rect = pygame.Rect(side_x - 10, side_y - 10, 250, 50)
        pygame.draw.rect(surface, COLOR_BUTTON, panel_rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_DANGER, panel_rect, 4, border_radius=8)
        warn_text = font_small.render("\u26A0 CLOSE CALL", True, COLOR_DANGER)
        surface.blit(warn_text, (side_x, side_y))


def draw_center_message(surface):
    """Big banner dead-center of the screen announcing a floor 20 / floor 50 reward."""
    if center_message_timer <= 0 or not center_message:
        return
    panel_width = min(WIDTH - 80, 700)
    panel_rect = pygame.Rect(0, 0, panel_width, 80)
    panel_rect.center = (WIDTH / 2, HEIGHT / 2)
    pygame.draw.rect(surface, COLOR_BUTTON, panel_rect, border_radius=12)
    pygame.draw.rect(surface, COLOR_WARNING, panel_rect, 5, border_radius=12)
    draw_text_center(surface, center_message, panel_rect.centery, font_medium, COLOR_DANGER)


def draw_material_selector(surface):
    """Let the player pick which owned material builds the next floor.

    Shown during PLAYING so material choice can change floor by floor -
    each button shows how much of that material is left, and that number
    drops as it gets used to build.
    """
    x = 30
    y = 235
    w, h = 95, 55
    gap = 10

    for key in MATERIAL_ORDER:
        rect = pygame.Rect(x, y, w, h)
        is_selected = (selected_material == key)
        owned = None if key == "WOOD" else inventory.get(key, 0)
        available = key == "WOOD" or (owned or 0) > 0

        color = COLOR_BUTTON_SELECTED if is_selected else (COLOR_BUTTON if available else (210, 210, 210))
        border_color = COLOR_SAFE if is_selected else COLOR_BUTTON_BORDER

        pygame.draw.rect(surface, color, rect, border_radius=6)
        pygame.draw.rect(surface, border_color, rect, 3, border_radius=6)

        name_text = font_small.render(MATERIALS[key]["label"], True, COLOR_TEXT)
        surface.blit(name_text, (rect.x + 8, rect.y + 6))

        owned_str = "\u221E" if key == "WOOD" else str(owned)  # infinity symbol for wood
        owned_text = font_small.render(f"x{owned_str}", True, COLOR_TEXT)
        surface.blit(owned_text, (rect.x + 8, rect.y + 28))

        buttons[f"mat_{key.lower()}"] = rect
        x += w + gap


# ============================================================
# GAME LOGIC
# ============================================================

def calculate_risk(floors):
    """Return the probability (0.0 - 0.90) that the house collapses at this floor count.

    The chosen material lowers this risk (better material = safer).
    """
    base_risk = 0.018 + (floors * 0.007)   # slightly gentler than before - houses are a bit sturdier now
    if base_risk > 0.90:
        base_risk = 0.90
    multiplier = MATERIALS[selected_material]["risk_multiplier"]
    risk = base_risk * multiplier
    return min(risk, 0.90)


def check_collapse(floors):
    """Roll the dice to see if the house collapses at this floor count."""
    risk = calculate_risk(floors)
    return random.random() < risk


def get_milestone_message(floors):
    messages = {
        5: "You're doing fine.",
        10: "Still going?",
        15: "Are you sure?",
        20: "One more?",
        25: "You could stop now.",
        30: "How high do you want to go?",
    }
    if floors in messages:
        return messages[floors]
    if floors > 30 and floors % 5 == 0:
        return "How high do you want to go?"
    return ""


def show_shop_message(text, color=COLOR_DANGER):
    """Pop up a short feedback message in the shop (e.g. why a buy click did nothing)."""
    global shop_message, shop_message_timer, shop_message_color
    shop_message = text
    shop_message_color = color
    shop_message_timer = FPS * 2


def add_crack():
    """Add a small random crack mark somewhere on the current house."""
    floor_index = random.randint(0, max(current_floor - 1, 0))
    offset_x = random.randint(20, 160)
    offset_y = random.randint(5, 35)
    cracks.append((floor_index, offset_x, offset_y))


def reset_game():
    """Start a brand new building attempt (called when leaving the shop)."""
    global current_floor, cracks, close_call_active, close_call_timer
    global milestone_message, milestone_timer, floor_materials
    global milestone_50_awarded
    global center_message, center_message_timer

    current_floor = 0
    cracks = []
    close_call_active = False
    close_call_timer = 0
    milestone_message = ""
    milestone_timer = 0
    floor_materials = []
    milestone_50_awarded = False
    center_message = ""
    center_message_timer = 0


def clear_broken_house():
    """Wipe the fallen house's blocks/cracks after the player has seen them on
    the COLLAPSED screen (called right when they leave that screen, so the
    reset is a visible beat rather than an invisible wipe)."""
    global cracks, floor_materials
    cracks = []
    floor_materials = []


def enter_farm():
    """Reset and start the coin-farming mini-game.

    This is also the start of a brand new Build House round, so both coins
    AND the material stockpile (inventory) reset back to their starting
    amounts here - every round starts from scratch (0 of each material),
    nothing carries over from a previous round or a previous session.
    """
    global farm_time_left, farm_coins, farm_spawn_cooldown, current_state, coins

    coins = STARTER_COINS
    for key in inventory:
        inventory[key] = 0
    farm_time_left = FARM_DURATION_SECONDS * FPS
    farm_coins = []
    farm_spawn_cooldown = 0
    current_state = STATE_FARM
    save_data()


def trigger_bonus_farm():
    """Start a short bonus round of Find Resources mid-build (see FLOOR_MILESTONE_BONUS_FARM_FLOOR).

    Unlike enter_farm(), this does NOT reset coins and hands control back to
    BUILD HIGHER (not the Shop) once time runs out, so the current house is
    never lost.
    """
    global farm_time_left, farm_coins, farm_spawn_cooldown, current_state

    farm_time_left = BONUS_FARM_DURATION_SECONDS * FPS
    farm_coins = []
    farm_spawn_cooldown = 0
    current_state = STATE_BONUS_FARM


def enter_shop():
    """Enter the shop from the Farm phase (before a build attempt has started)."""
    global current_state, shop_from_playing
    shop_from_playing = False
    current_state = STATE_SHOP


def enter_shop_from_playing():
    """Open the shop mid-build, without resetting or losing the current house."""
    global current_state, shop_from_playing
    shop_from_playing = True
    current_state = STATE_SHOP


def select_material(material_key):
    """Pick which owned material will be used to build the next floor(s)."""
    global selected_material

    if material_key == "WOOD" or inventory.get(material_key, 0) > 0:
        selected_material = material_key
    else:
        show_shop_message(f"YOU DON'T OWN ANY {MATERIALS[material_key]['label']} YET")


def buy_material(material_key):
    """Buy one more unit of a material and add it to the stockpile.

    Buying no longer costs you your only shot per visit - you can buy as many
    times, and as many different materials, as you can afford. Every branch
    leaves a short on-screen message so a click that can't succeed (not
    enough coins) is clearly explained instead of feeling unresponsive.
    """
    global coins

    if material_key == "WOOD":
        return  # wood is free and unlimited, nothing to buy

    cost = MATERIALS[material_key]["cost"]

    if coins < cost:
        show_shop_message(f"NOT ENOUGH COINS (NEED {cost})")
        return

    coins -= cost
    inventory[material_key] = inventory.get(material_key, 0) + 1
    show_shop_message(
        f"BOUGHT 1 {MATERIALS[material_key]['label']} (OWNED: {inventory[material_key]})",
        COLOR_SAFE,
    )
    save_data()


def update_farm():
    """Spawn and move falling material blocks (and coins) during the FARM /
    BONUS_FARM states.

    Each spawn rolls a material block (BRICK/IRON/GOLD/DIAMOND, weighted from
    easy/common to hard/rare via FARM_MATERIAL_WEIGHTS, falling at a speed
    from FARM_MATERIAL_SPEEDS - rarer blocks fall faster) or, with
    FARM_COIN_SPAWN_CHANCE probability, a coin worth a random amount between
    FARM_COIN_MIN_VALUE and FARM_COIN_MAX_VALUE - the higher its value, the
    faster it falls (see coin_speed_for_value).

    When time runs out: the normal FARM round moves on to the Shop, while a
    BONUS_FARM round (triggered mid-build, see FLOOR_MILESTONE_BONUS_FARM_FLOOR)
    hands control straight back to BUILD HIGHER instead.
    """
    global farm_time_left, farm_spawn_cooldown, current_state

    farm_time_left -= 1
    if farm_time_left <= 0:
        if current_state == STATE_BONUS_FARM:
            current_state = STATE_PLAYING
        else:
            enter_shop()
        return

    farm_spawn_cooldown -= 1
    if farm_spawn_cooldown <= 0:
        if random.random() < FARM_COIN_SPAWN_CHANCE:
            value = random.randint(FARM_COIN_MIN_VALUE, FARM_COIN_MAX_VALUE)
            farm_coins.append({
                "x": random.randint(60, WIDTH - 60),
                "y": -20,
                "speed": coin_speed_for_value(value),
                "size": 30,
                "is_coin": True,
                "value": value,
            })
        else:
            material = random.choices(FARM_MATERIAL_ORDER, weights=FARM_MATERIAL_WEIGHTS, k=1)[0]
            speed_min, speed_max = FARM_MATERIAL_SPEEDS[material]
            farm_coins.append({
                "x": random.randint(60, WIDTH - 60),
                "y": -20,
                "speed": random.uniform(speed_min, speed_max),
                "size": 32,
                "material": material,
            })
        farm_spawn_cooldown = random.randint(10, 22)

    for block in farm_coins[:]:
        block["y"] += block["speed"]
        if block["y"] > HEIGHT + 30:
            farm_coins.remove(block)


def collect_coin_at(pos):
    """Check if a click position hits a falling block; if it's a material
    block, add that material to the stockpile - if it's a coin, add its
    value straight to the coin total."""
    global coins

    for block in farm_coins[:]:
        half = block["size"] / 2
        if (block["x"] - half - 10 <= pos[0] <= block["x"] + half + 10 and
                block["y"] - half - 10 <= pos[1] <= block["y"] + half + 10):
            farm_coins.remove(block)
            if block.get("is_coin"):
                value = block.get("value", 0)
                coins += value
                stats["total_coins_earned"] += value
            else:
                material = block.get("material", "BRICK")
                inventory[material] = inventory.get(material, 0) + 1
            break


def build_higher():
    """Handle the BUILD HIGHER action during PLAYING state.

    Whichever material is currently selected gets used (and consumed by 1)
    to build this floor. If that was the last unit owned, the player is
    automatically switched to WOOD (always available) so they're never
    stuck, and a message explains what happened.
    """
    global current_floor, close_call_active, close_call_timer
    global milestone_message, milestone_timer, selected_material, coins
    global milestone_50_awarded
    global center_message, center_message_timer

    material_used = selected_material
    current_floor += 1
    stats["total_floors_built"] += 1
    if current_floor > stats["highest_attempt"]:
        stats["highest_attempt"] = current_floor

    floor_materials.append(material_used)  # remember what this specific floor was built with

    if material_used != "WOOD":
        inventory[material_used] = max(0, inventory.get(material_used, 0) - 1)
        save_data()

    if check_collapse(current_floor):
        collapse_game()
        return

    close_call_chance = min(0.05 + current_floor * 0.01, 0.35)
    if random.random() < close_call_chance:
        close_call_active = True
        close_call_timer = FPS * 2
        add_crack()
    else:
        close_call_active = False

    ran_out = material_used != "WOOD" and inventory.get(material_used, 0) <= 0
    if ran_out:
        selected_material = "WOOD"
        milestone_message = f"OUT OF {MATERIALS[material_used]['label']}! SWITCHED TO WOOD"
        milestone_timer = FPS * 3
    else:
        message = get_milestone_message(current_floor)
        if message:
            milestone_message = message
            milestone_timer = FPS * 3

    # EVERY FLOOR_MILESTONE_COINS_FLOOR floors (20, 40, 60, ...) pays a flat
    # coin bonus - repeats for the whole build attempt. Floor 50 still grants
    # a one-time bonus Find Resources round (flag reset in reset_game()).
    if current_floor > 0 and current_floor % FLOOR_MILESTONE_COINS_FLOOR == 0:
        coins += FLOOR_MILESTONE_COINS_AMOUNT
        stats["total_coins_earned"] += FLOOR_MILESTONE_COINS_AMOUNT
        save_data()
        center_message = f"FLOOR {current_floor}! YOU GOT +{FLOOR_MILESTONE_COINS_AMOUNT} COINS"
        center_message_timer = FPS * 3

    if current_floor == FLOOR_MILESTONE_BONUS_FARM_FLOOR and not milestone_50_awarded:
        milestone_50_awarded = True
        center_message = f"FLOOR {FLOOR_MILESTONE_BONUS_FARM_FLOOR}! YOU GOT A FIND RESOURCES BONUS ROUND"
        center_message_timer = FPS * 3
        trigger_bonus_farm()


def compute_greed_score(collapsed):
    """Work out a simple, in-game-only 'greed score' for the round that just ended."""
    score = min(current_floor * 2, 60)
    if not collapsed:
        score += 10  # bonus for stopping in time instead of losing it all
    if selected_material == "WOOD" and current_floor >= 10:
        score += 10  # went high without ever upgrading materials
    score = max(0, min(score, 100))

    if score <= 20:
        label = "CAREFUL"
    elif score <= 40:
        label = "CAUTIOUS"
    elif score <= 60:
        label = "RISK TAKER"
    elif score <= 80:
        label = "GREEDY"
    else:
        label = "EXTREMELY GREEDY"

    return score, label


def stop_game():
    """Handle the player choosing to STOP."""
    global current_state, best_floor, last_round_floor, last_round_result
    global greed_score, greed_label, last_round_material

    stats["total_attempts"] += 1
    stats["total_stops"] += 1

    if current_floor > best_floor:
        best_floor = current_floor
        stats["best_floor"] = best_floor

    last_round_floor = current_floor
    last_round_result = "STOPPED"
    last_round_material = selected_material
    greed_score, greed_label = compute_greed_score(collapsed=False)
    current_state = STATE_STOPPED
    save_data()


def collapse_game():
    """Handle the house collapsing."""
    global current_state, last_round_floor, last_round_result
    global greed_score, greed_label, last_round_material

    stats["total_attempts"] += 1
    stats["total_collapses"] += 1

    last_round_floor = current_floor
    last_round_result = "COLLAPSED"
    last_round_material = selected_material
    greed_score, greed_label = compute_greed_score(collapsed=True)
    current_state = STATE_COLLAPSED
    save_data()

    # NOTE: the house blocks (floor_materials/cracks) are deliberately kept
    # as-is here so the COLLAPSED screen can render the broken house exactly
    # as it fell. They only get cleared once the player leaves this screen
    # (see the STATE_COLLAPSED "try_again" handling below), so the reset is
    # something the player actually sees happen, not an invisible wipe.


# ============================================================
# EVENT HANDLING
# ============================================================

def point_in_rect(pos, rect):
    return rect.collidepoint(pos)


def handle_events():
    global current_state, WIDTH, HEIGHT, screen

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            save_data()
            pygame.quit()
            sys.exit()

        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)

        if event.type == pygame.KEYDOWN:
            if current_state == STATE_PLAYING:
                if event.key == pygame.K_SPACE:
                    build_higher()
                elif event.key == pygame.K_RETURN:
                    stop_game()
                elif event.key == pygame.K_s:
                    enter_shop_from_playing()

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos

            if current_state == STATE_MENU:
                if point_in_rect(pos, buttons.get("build_house", pygame.Rect(0, 0, 0, 0))):
                    enter_farm()
                elif point_in_rect(pos, buttons.get("statistics", pygame.Rect(0, 0, 0, 0))):
                    current_state = STATE_STATISTICS
                elif point_in_rect(pos, buttons.get("quit", pygame.Rect(0, 0, 0, 0))):
                    save_data()
                    pygame.quit()
                    sys.exit()

            elif current_state in (STATE_FARM, STATE_BONUS_FARM):
                collect_coin_at(pos)

            elif current_state == STATE_SHOP:
                if point_in_rect(pos, buttons.get("build_btn", pygame.Rect(0, 0, 0, 0))):
                    if shop_from_playing:
                        current_state = STATE_PLAYING
                    else:
                        reset_game()
                        current_state = STATE_PLAYING
                else:
                    for key in MATERIAL_ORDER:
                        buy_rect = buttons.get(f"{key.lower()}_buy_btn")
                        card_rect = buttons.get(f"{key.lower()}_card")
                        if buy_rect is not None and point_in_rect(pos, buy_rect):
                            buy_material(key)
                            break
                        elif card_rect is not None and point_in_rect(pos, card_rect):
                            select_material(key)
                            break

            elif current_state == STATE_PLAYING:
                if point_in_rect(pos, buttons.get("build", pygame.Rect(0, 0, 0, 0))):
                    build_higher()
                elif point_in_rect(pos, buttons.get("stop", pygame.Rect(0, 0, 0, 0))):
                    stop_game()
                elif point_in_rect(pos, buttons.get("shop_mid_build", pygame.Rect(0, 0, 0, 0))):
                    enter_shop_from_playing()
                else:
                    for key in MATERIAL_ORDER:
                        mat_rect = buttons.get(f"mat_{key.lower()}")
                        if mat_rect is not None and point_in_rect(pos, mat_rect):
                            select_material(key)
                            break

            elif current_state == STATE_STOPPED:
                if point_in_rect(pos, buttons.get("play_again", pygame.Rect(0, 0, 0, 0))):
                    enter_farm()
                elif point_in_rect(pos, buttons.get("main_menu", pygame.Rect(0, 0, 0, 0))):
                    current_state = STATE_MENU

            elif current_state == STATE_COLLAPSED:
                if point_in_rect(pos, buttons.get("try_again", pygame.Rect(0, 0, 0, 0))):
                    clear_broken_house()
                    enter_farm()

            elif current_state == STATE_STATISTICS:
                if point_in_rect(pos, buttons.get("back", pygame.Rect(0, 0, 0, 0))):
                    current_state = STATE_MENU


# ============================================================
# UPDATE
# ============================================================

def update_game():
    global milestone_timer, close_call_timer, close_call_active, shop_message_timer
    global center_message_timer

    if current_state in (STATE_FARM, STATE_BONUS_FARM):
        update_farm()

    if milestone_timer > 0:
        milestone_timer -= 1

    if center_message_timer > 0:
        center_message_timer -= 1

    if close_call_timer > 0:
        close_call_timer -= 1
        if close_call_timer == 0:
            close_call_active = False

    if shop_message_timer > 0:
        shop_message_timer -= 1


# ============================================================
# SCREENS
# ============================================================

def show_main_menu(surface):
    draw_background(surface, COLOR_BG_MENU)
    draw_text_center(surface, "GREED HOUSE", 140, font_title)
    draw_text_center(surface, "HOW HIGH CAN YOU GO?", 210, font_medium)

    center_x = WIDTH / 2
    build_house_rect = pygame.Rect(0, 0, 260, 60)
    build_house_rect.center = (center_x, 320)
    stats_rect = pygame.Rect(0, 0, 260, 60)
    stats_rect.center = (center_x, 400)
    quit_rect = pygame.Rect(0, 0, 260, 60)
    quit_rect.center = (center_x, 480)

    buttons["build_house"] = build_house_rect
    buttons["statistics"] = stats_rect
    buttons["quit"] = quit_rect

    draw_button(surface, build_house_rect, "BUILD HOUSE")
    draw_button(surface, stats_rect, "STATISTICS")
    draw_button(surface, quit_rect, "QUIT")


def draw_farm_inventory(surface, y):
    """Show how many of each material the player currently owns, in one line."""
    parts = [f"{key}: {inventory.get(key, 0)}" for key in FARM_MATERIAL_ORDER]
    draw_text_center(surface, "OWNED - " + "   ".join(parts), y, font_small, COLOR_TEXT)


def show_farm(surface, bonus=False):
    draw_background(surface, COLOR_BG_FARM)
    title = "BONUS FIND RESOURCES!" if bonus else "FIND RESOURCES"
    draw_text_center(surface, title, 60, font_large, COLOR_WARNING if bonus else COLOR_TEXT)
    draw_text_center(surface, "Click blocks to collect BRICK / IRON / GOLD / DIAMOND, or grab falling COINS", 105, font_small)

    seconds_left = max(0, farm_time_left // FPS + 1)
    draw_text_center(surface, f"TIME: {seconds_left}", 150, font_medium, COLOR_WARNING)
    if bonus:
        draw_text_center(surface, f"FLOOR: {current_floor}   COINS: {coins}", 190, font_medium, COLOR_TEXT)
    else:
        draw_text_center(surface, f"COINS: {coins}", 190, font_medium, COLOR_TEXT)

    draw_farm_inventory(surface, 220)

    for block in farm_coins:
        cx, cy = int(block["x"]), int(block["y"])
        half = block["size"] / 2

        if block.get("is_coin"):
            # Coins are drawn as circles so they read differently from the
            # square material blocks, with their value shown on top.
            pygame.draw.circle(surface, COLOR_COIN, (cx, cy), half)
            pygame.draw.circle(surface, COLOR_OUTLINE, (cx, cy), half, 3)
            label_text = font_small.render(str(block.get("value", 0)), True, COLOR_OUTLINE)
            label_rect = label_text.get_rect(center=(cx, cy))
            surface.blit(label_text, label_rect)
            continue

        material = block.get("material", "BRICK")
        rect = pygame.Rect(cx - half, cy - half, block["size"], block["size"])
        pygame.draw.rect(surface, MATERIALS[material]["color"], rect)
        pygame.draw.rect(surface, COLOR_OUTLINE, rect, 3)

        # Show which material it is so players can see what they're going for before clicking.
        label_text = font_small.render(MATERIALS[material]["label"][0], True, COLOR_OUTLINE)
        label_rect = label_text.get_rect(center=(cx, cy))
        surface.blit(label_text, label_rect)

    if bonus:
        draw_center_message(surface)


def show_shop(surface):
    draw_background(surface, COLOR_BG_MENU)
    draw_text_center(surface, "STOCK UP ON MATERIALS", 80, font_large)
    draw_text_center(surface, f"COINS: {coins}", 125, font_medium, COLOR_WARNING)
    draw_text_center(surface, "Click a card to select it - click BUY to add to your stockpile", 152, font_small)

    if shop_message_timer > 0 and shop_message:
        draw_text_center(surface, shop_message, 175, font_small, shop_message_color or COLOR_DANGER)

    center_x = WIDTH / 2
    card_width, card_height = 200, 230
    spacing = 20
    total_width = card_width * len(MATERIAL_ORDER) + spacing * (len(MATERIAL_ORDER) - 1)
    start_x = center_x - total_width / 2
    cards_top = 210

    descriptions = {
        "WOOD": ["FREE & UNLIMITED", "Normal risk"],
        "BRICK": ["COST 5 EACH", "Safer (-30% risk)"],
        "IRON": ["COST 15 EACH", "Safer (-55% risk)"],
        "GOLD": ["COST 25 EACH", "Safer (-70% risk)"],
        "DIAMOND": ["COST 50 EACH", "Safest (-100% risk)"],
    }

    for i, key in enumerate(MATERIAL_ORDER):
        rect = pygame.Rect(start_x + i * (card_width + spacing), cards_top, card_width, card_height)
        is_selected = (selected_material == key)
        owned = None if key == "WOOD" else inventory.get(key, 0)
        can_select = key == "WOOD" or (owned or 0) > 0
        can_afford = key == "WOOD" or coins >= MATERIALS[key]["cost"]

        border_color = COLOR_SAFE if is_selected else COLOR_BUTTON_BORDER
        card_color = COLOR_BUTTON_SELECTED if is_selected else COLOR_BUTTON
        if not is_selected and not can_select:
            card_color = (225, 225, 225)  # visibly greyed out - you don't own any of this yet

        pygame.draw.rect(surface, card_color, rect, border_radius=10)
        pygame.draw.rect(surface, border_color, rect, 5, border_radius=10)

        # Little material color swatch
        swatch_rect = pygame.Rect(0, 0, 50, 50)
        swatch_rect.center = (rect.centerx, rect.top + 38)
        pygame.draw.rect(surface, MATERIALS[key]["color"], swatch_rect)
        pygame.draw.rect(surface, COLOR_OUTLINE, swatch_rect, 2)

        name_text = font_medium.render(MATERIALS[key]["label"], True, COLOR_TEXT)
        name_rect = name_text.get_rect(center=(rect.centerx, rect.top + 78))
        surface.blit(name_text, name_rect)

        line_y = rect.top + 102
        for line in descriptions[key]:
            line_text = font_small.render(line, True, COLOR_TEXT)
            line_rect = line_text.get_rect(center=(rect.centerx, line_y))
            surface.blit(line_text, line_rect)
            line_y += 20

        # Shows how much of this material is currently in stock - decreases as it's used to build.
        owned_str = "UNLIMITED" if key == "WOOD" else f"OWNED: {owned}"
        owned_color = COLOR_SAFE if is_selected else COLOR_TEXT
        owned_text = font_small.render(owned_str, True, owned_color)
        owned_rect = owned_text.get_rect(center=(rect.centerx, line_y + 8))
        surface.blit(owned_text, owned_rect)

        # The whole card selects this material (if owned, or always for WOOD).
        buttons[f"{key.lower()}_card"] = rect

        if key != "WOOD":
            buy_rect = pygame.Rect(0, 0, 130, 34)
            buy_rect.center = (rect.centerx, rect.bottom - 24)
            buy_color = COLOR_BUTTON_BUILD if can_afford else (200, 200, 200)
            draw_button(surface, buy_rect, "BUY +1", buy_color, font=font_small)
            buttons[f"{key.lower()}_buy_btn"] = buy_rect

    build_rect = pygame.Rect(0, 0, 260, 60)
    build_rect.center = (center_x, cards_top + card_height + 70)
    buttons["build_btn"] = build_rect
    if shop_from_playing:
        draw_button(surface, build_rect, "BACK TO BUILDING", COLOR_BUTTON_BUILD)
    else:
        draw_button(surface, build_rect, "START BUILDING", COLOR_BUTTON_BUILD)


def show_playing(surface):
    draw_background(surface, COLOR_BG_PLAY)

    ground_y = HEIGHT - 100
    pygame.draw.rect(surface, COLOR_GROUND, (0, ground_y, WIDTH, HEIGHT - ground_y))

    area_top = 305  # moved down from 180 to make room for the material selector below
    area_bottom = ground_y
    # Each floor keeps the color of whatever material actually built it,
    # instead of the whole house repainting to the currently selected one.
    floor_colors = [MATERIALS[m]["color"] for m in floor_materials]
    default_color = MATERIALS[selected_material]["color"]
    draw_house(surface, current_floor, area_top, area_bottom, WIDTH / 2, floor_colors, default_color)

    draw_ui(surface)
    draw_material_selector(surface)
    draw_center_message(surface)

    build_rect = pygame.Rect(0, 0, 260, 60)
    build_rect.center = (WIDTH / 2 - 150, HEIGHT - 50)
    stop_rect = pygame.Rect(0, 0, 260, 60)
    stop_rect.center = (WIDTH / 2 + 150, HEIGHT - 50)

    buttons["build"] = build_rect
    buttons["stop"] = stop_rect

    draw_button(surface, build_rect, "BUILD HIGHER", COLOR_BUTTON_BUILD)
    pygame.draw.rect(surface, COLOR_BUTTON_STOP, stop_rect, border_radius=8)
    pygame.draw.rect(surface, COLOR_BUTTON_BORDER, stop_rect, 5, border_radius=8)
    stop_label = font_medium.render("STOP", True, COLOR_TEXT)
    stop_label_rect = stop_label.get_rect(center=(stop_rect.centerx, stop_rect.centery - 12))
    surface.blit(stop_label, stop_label_rect)
    stop_bonus_label = font_small.render("(+Point 10)", True, COLOR_TEXT)
    stop_bonus_rect = stop_bonus_label.get_rect(center=(stop_rect.centerx, stop_rect.centery + 14))
    surface.blit(stop_bonus_label, stop_bonus_rect)

    shop_rect = pygame.Rect(0, 0, 140, 45)
    shop_rect.center = (WIDTH - 100, 50)
    buttons["shop_mid_build"] = shop_rect
    draw_button(surface, shop_rect, "SHOP", COLOR_BUTTON_SELECTED, font=font_small)


def show_result_screen(surface, title, title_color, lines, y_offset=0, draw_bg=True):
    if draw_bg:
        draw_background(surface, COLOR_BG_MENU)
    draw_text_center(surface, title, 120 + y_offset, font_large, title_color)

    y = 190 + y_offset
    for line in lines:
        draw_text_center(surface, line, y, font_medium)
        y += 38

    center_x = WIDTH / 2
    if current_state == STATE_STOPPED:
        again_rect = pygame.Rect(0, 0, 240, 55)
        again_rect.center = (center_x - 140, y + 40)
        menu_rect = pygame.Rect(0, 0, 240, 55)
        menu_rect.center = (center_x + 140, y + 40)
        buttons["play_again"] = again_rect
        buttons["main_menu"] = menu_rect
        draw_button(surface, again_rect, "PLAY AGAIN")
        draw_button(surface, menu_rect, "MAIN MENU")
    else:
        try_rect = pygame.Rect(0, 0, 240, 55)
        try_rect.center = (center_x, y + 40)
        buttons["try_again"] = try_rect
        draw_button(surface, try_rect, "TRY AGAIN")


def show_stopped(surface):
    lines = [
        "YOU STOPPED",
        f"FINAL FLOOR: {last_round_floor}",
        f"SCORE: {greed_score} ({greed_label})",
        "( +10 Points)",
    ]
    show_result_screen(surface, "YOU STOPPED", COLOR_SAFE, lines)


def show_collapsed(surface):
    draw_background(surface, COLOR_BG_MENU)

    # Show the house exactly as it fell (still using the blocks/cracks from
    # the run that just ended - clear_broken_house() only wipes them once the
    # player leaves this screen) so the reset is something they actually see,
    # not an invisible wipe.
    house_top = 20
    house_bottom = 235
    floor_colors = [MATERIALS[m]["color"] for m in floor_materials]
    default_color = MATERIALS[last_round_material]["color"]
    draw_house(surface, last_round_floor, house_top, house_bottom, WIDTH / 2, floor_colors, default_color)

    lines = [
        "THE HOUSE COLLAPSED",
        f"FINAL FLOOR: {last_round_floor}",
        f"SCORE: {greed_score} ({greed_label})",
    ]
    show_result_screen(surface, "THE HOUSE COLLAPSED", COLOR_DANGER, lines, y_offset=170, draw_bg=False)


def show_statistics(surface):
    draw_background(surface, COLOR_BG_MENU)
    draw_text_center(surface, "STATISTICS", 100, font_large)

    lines = [
        f"BEST FLOOR       {stats['best_floor']}",
        f"TOTAL ATTEMPTS   {stats['total_attempts']}",
        f"COLLAPSES        {stats['total_collapses']}",
        f"STOPS            {stats['total_stops']}",
        f"TOTAL FLOORS     {stats['total_floors_built']}",
        f"COINS EARNED     {stats['total_coins_earned']}",
    ]
    y = 200
    for line in lines:
        draw_text_center(surface, line, y, font_medium)
        y += 45

    back_rect = pygame.Rect(0, 0, 200, 55)
    back_rect.center = (WIDTH / 2, y + 40)
    buttons["back"] = back_rect
    draw_button(surface, back_rect, "BACK")


# ============================================================
# MAIN DRAW DISPATCH
# ============================================================

def draw_game():
    if current_state == STATE_MENU:
        show_main_menu(screen)
    elif current_state == STATE_FARM:
        show_farm(screen)
    elif current_state == STATE_BONUS_FARM:
        show_farm(screen, bonus=True)
    elif current_state == STATE_SHOP:
        show_shop(screen)
    elif current_state == STATE_PLAYING:
        show_playing(screen)
    elif current_state == STATE_STOPPED:
        show_stopped(screen)
    elif current_state == STATE_COLLAPSED:
        show_collapsed(screen)
    elif current_state == STATE_STATISTICS:
        show_statistics(screen)

    pygame.display.flip()


# ============================================================
# MAIN LOOP
# ============================================================

def main():
    load_data()  # bring back coins/best_floor/stats from the last time the game was played
    while True:
        handle_events()
        update_game()
        draw_game()
        clock.tick(FPS)


if __name__ == "__main__":
    main()
