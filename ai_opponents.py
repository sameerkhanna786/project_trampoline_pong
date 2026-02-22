"""AI scaffolding for Pong.

Students should edit student_ai_choose_move() to implement their own AI.
"""

import random
from collections import namedtuple

MOVE_UP = -1
MOVE_STAY = 0
MOVE_DOWN = 1

# GameState holds a snapshot of one frame from a paddle's perspective.
#
# Available fields:
#   state.window_width      - width of the game window in pixels
#   state.window_height     - height of the game window in pixels
#   state.paddle_height     - height of each paddle in pixels
#   state.paddle_speed      - pixels a paddle moves per frame
#   state.my_side           - "left" or "right"
#   state.my_paddle_x       - x position of your paddle
#   state.my_paddle_y       - y position of your paddle (top edge)
#   state.opponent_paddle_x - x position of opponent paddle
#   state.opponent_paddle_y - y position of opponent paddle (top edge)
#   state.ball_x            - x position of ball center
#   state.ball_y            - y position of ball center
#   state.ball_vx           - horizontal ball speed (positive = moving right)
#   state.ball_vy           - vertical ball speed (positive = moving down)
GameState = namedtuple("GameState", [
    "window_width", "window_height", "paddle_height", "paddle_speed",
    "my_side", "my_paddle_x", "my_paddle_y",
    "opponent_paddle_x", "opponent_paddle_y",
    "ball_x", "ball_y", "ball_vx", "ball_vy",
])


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def is_ball_moving_toward_me(state):
    if state.my_side == "right":
        return state.ball_vx > 0
    return state.ball_vx < 0


def reflect_y(y_value, height):
    """Reflect a y value inside [0, height] as if bouncing on top/bottom walls."""
    if height <= 0:
        return 0.0
    period = 2 * height
    reflected = y_value % period
    if reflected > height:
        reflected = period - reflected
    return reflected


def predict_intercept_y(state):
    """Estimate where the ball will cross this paddle's x coordinate."""
    if state.ball_vx == 0:
        return float(state.ball_y)
    steps = (state.my_paddle_x - state.ball_x) / state.ball_vx
    if steps < 0:
        return float(state.ball_y)
    predicted_y = state.ball_y + state.ball_vy * steps
    return reflect_y(predicted_y, state.window_height)


# ===== YOUR CODE: Edit the function below ===================================

def student_ai_choose_move(state):
    """Starter strategy for students.

    Edit this function to implement your own AI.
    Return -1 (up), 0 (stay), or 1 (down).
    """
    paddle_center = state.my_paddle_y + state.paddle_height // 2
    screen_center = state.window_height // 2

    # Branch A: wall safety branch.
    # If your paddle is pinned against a wall, move away from that wall first.

    if state.my_paddle_y <= 0:
        # TODO: Your paddle is bumping into the top wall; what should you do?
        return MOVE_STAY
    if state.my_paddle_y + state.paddle_height >= state.window_height:
        # TODO: Your paddle is bumping into the bottom wall; what should you do?
        return MOVE_STAY

    # Branch B: ball is moving toward you.
    # Usually this is the most important branch for defense.
    if is_ball_moving_toward_me(state):
        # If ball is close, use current ball_y for a quick reaction.
        horizontal_distance = abs(state.my_paddle_x - state.ball_x)
        if horizontal_distance < 120:
            target_y = state.ball_y
        else:
            # If ball is far, use predicted intercept.
            # Try changing this to state.ball_y if prediction feels too hard.
            target_y = predict_intercept_y(state)

        # Smaller dead zone when ball is fast -> react more aggressively.
        if abs(state.ball_vy) >= 6:
            dead_zone = 8
        else:
            dead_zone = 14

        # Movement decision for the "ball coming at me" branch.
        if target_y < paddle_center - dead_zone:
            # TODO: Your paddle is too low to catch the ball; what should you do?
            return MOVE_UP
        if target_y > paddle_center + dead_zone:
            # TODO: Your paddle is too high to catch the ball; what should you do?
            return MOVE_DOWN
        return MOVE_STAY

    # Branch C: ball is moving away from you.
    # Reposition toward center so you are ready for the next rally.
    if paddle_center < screen_center - 12:
        # TODO: Your paddle is higher than the center of your board; what should you do?
        return MOVE_DOWN
    if paddle_center > screen_center + 12:
        # TODO: Your paddle is lower than the center of your board; what should you do?
        return MOVE_UP

    # Branch D: neutral fallback.
    # If no branch strongly suggests moving, hold still.
    return MOVE_STAY


# ===== DO NOT EDIT BELOW THIS LINE ==========================================

def tracking_ai_choose_move(state):
    """Baseline opponent that tracks the ball with simple rules."""
    paddle_center = state.my_paddle_y + state.paddle_height // 2
    target_y = state.ball_y

    # When ball moves away, drift back toward center.
    if not is_ball_moving_toward_me(state):
        target_y = state.window_height // 2

    dead_zone = 8
    if target_y < paddle_center - dead_zone:
        return MOVE_UP
    if target_y > paddle_center + dead_zone:
        return MOVE_DOWN
    return MOVE_STAY


def random_ai_choose_move(state):
    """Very weak opponent useful for first tests."""
    return random.choice([MOVE_UP, MOVE_STAY, MOVE_DOWN])


def make_reference_ai():
    """Create a ReferenceAI function (intentionally weak baseline for benchmarking).

    Returns a choose_move function that keeps internal state via closure.
    """
    hold_frames = 0
    last_move = MOVE_STAY

    def choose_move(state):
        nonlocal hold_frames, last_move

        # Larger reaction delay keeps this baseline intentionally easy to beat.
        if hold_frames > 0:
            hold_frames -= 1
            return last_move

        paddle_center = state.my_paddle_y + state.paddle_height // 2

        if is_ball_moving_toward_me(state):
            # Track current ball position instead of predicted intercept.
            target_y = state.ball_y
        else:
            # Slowly drift to center when ball is moving away.
            target_y = state.window_height // 2

        dead_zone = 24
        if target_y < paddle_center - dead_zone:
            last_move = MOVE_UP
        elif target_y > paddle_center + dead_zone:
            last_move = MOVE_DOWN
        else:
            last_move = MOVE_STAY

        # Periodic mistakes make this AI less consistent.
        if random.random() < 0.18:
            last_move = random.choice([MOVE_UP, MOVE_STAY, MOVE_DOWN])

        hold_frames = random.randint(2, 4)
        return last_move

    return choose_move


def normalize_move(move):
    """Coerce any integer move into -1, 0, or 1."""
    if move < 0:
        return MOVE_UP
    if move > 0:
        return MOVE_DOWN
    return MOVE_STAY


def create_ai(name):
    """Return (choose_move_function, display_name) for the given AI name."""
    key = name.strip().lower()
    if key == "tracking":
        return tracking_ai_choose_move, "TrackingAI"
    if key == "reference":
        return make_reference_ai(), "ReferenceAI"
    if key == "random":
        return random_ai_choose_move, "RandomAI"
    if key == "student":
        return student_ai_choose_move, "StudentAI"
    raise ValueError("Unknown AI. Choose from: tracking, reference, random, student")
