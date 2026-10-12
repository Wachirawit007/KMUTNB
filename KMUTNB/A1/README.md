# GREED HOUSE

A short 2D psychological decision-making game built with Python and Pygame.

**"How high will you go?"**

## Genre

Psychological Risk / Decision Making / Greed Test

The game is not really about building a house. It is about testing one simple
question, over and over: *should I stop now, or should I take one more risk?*

## Project Info

- **Project Name:** GREED HOUSE
- **Python Version:** 3.12.x
- **Pygame Version:** 2.6.0
- **Engine:** Pygame only (no Unity / Unreal / Godot / Tkinter)
- **Graphics:** 100% drawn with `pygame.draw` — no external image assets required

## Installation

1. Make sure Python 3.12 is installed.
2. (Recommended) Create a virtual environment:

   ```
   python -m venv .venv
   .venv\Scripts\activate      # Windows
   ```

3. Install dependencies:

   ```
   pip install -r requirements.txt
   ```

## Running

```
python main.py
```

## Controls

| Action        | Mouse           | Keyboard |
|---------------|-----------------|----------|
| Build Higher  | Click button    | SPACE    |
| Stop          | Click button    | ENTER    |
| Menu buttons  | Click           | -        |

The window can be resized; the house scales to keep the UI fixed in place.

## Game Rules

1. You start with a 1-floor house.
2. Each round, choose **BUILD HIGHER** or **STOP**.
3. Building adds one floor and increases your risk of collapse. The higher
   the house, the more dangerous it becomes.
4. If you **STOP**, your score for the round is the number of floors built.
5. If the house **collapses**, your score for the round is 0 — no matter how
   high you had gone.
6. Before each round you may pick a personal goal (10 / 20 / 30 / 50 floors,
   or "I don't know"). Reaching your goal offers a choice: **STOP** or
   **GO BEYOND**.
7. Your best floor count is tracked across the whole session, along with
   other statistics (total attempts, collapses, stops, etc.).
8. At the end of each round you receive a **Game Greed Score (0–100)** —
   this is just a fun in-game result, not a real psychological diagnosis.

## File Structure

```
GREED_HOUSE/
│
├── main.py
├── requirements.txt
└── README.md
```

Everything lives in `main.py`, organized into clearly named functions
(drawing functions, game logic functions, event handling, and screen
functions) rather than spread across many files or classes.
