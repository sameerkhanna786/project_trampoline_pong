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
    
    Return -1 (up), 0 (stay), or 1 (down).
    """

    paddle_center = state.my_paddle_y + state.paddle_height // 2
    screen_center = state.window_height // 2

    if is_ball_moving_toward_me(state):

        if state.ball_y < paddle_center:
            return -1
        elif state.ball_y > paddle_center:
            return 1
        else:
            return 0

    else:
        if paddle_center < screen_center:
            return 1
        elif paddle_center > screen_center:
            return -1
        else:
            return 0
    paddle_center = state.my_paddle_y + state.paddle_height // 2
    screen_center = state.window_height // 2

    # Branch A: ball is moving toward you.
    # This is the most important branch — you need to defend!
    if is_ball_moving_toward_me(state):
        # TODO: Move your paddle toward the ball to block it.
        #   Hint: compare state.ball_y to paddle_center.
        return MOVE_STAY

    # Branch B: ball is moving away from you.
    # Good time to reposition so you are ready for the next rally.
    # TODO: Move your paddle back toward the center of the screen.
    #   Hint: compare paddle_center to screen_center.
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
