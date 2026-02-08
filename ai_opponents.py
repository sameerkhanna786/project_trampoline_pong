"""AI scaffolding for Pong.

Students should primarily edit StudentAI.choose_move().
"""

from dataclasses import dataclass
import random

MOVE_UP = -1
MOVE_STAY = 0
MOVE_DOWN = 1


def normalize_move(move: int) -> int:
    """Coerce any integer move into -1, 0, or 1."""
    if move < 0:
        return MOVE_UP
    if move > 0:
        return MOVE_DOWN
    return MOVE_STAY


@dataclass(frozen=True)
class GameState:
    """Snapshot of one frame from a paddle's perspective."""

    window_width: int
    window_height: int
    paddle_height: int
    paddle_speed: int
    my_side: str  # "left" or "right"
    my_paddle_x: int
    my_paddle_y: int
    opponent_paddle_x: int
    opponent_paddle_y: int
    ball_x: int
    ball_y: int
    ball_vx: int
    ball_vy: int


def _is_ball_moving_toward_me(state: GameState) -> bool:
    if state.my_side == "right":
        return state.ball_vx > 0
    return state.ball_vx < 0


def _reflect_y(y_value: float, height: int) -> float:
    """Reflect a y value inside [0, height] as if bouncing on top/bottom walls."""
    if height <= 0:
        return 0.0
    period = 2 * height
    reflected = y_value % period
    if reflected > height:
        reflected = period - reflected
    return reflected


def _predict_intercept_y(state: GameState) -> float:
    """Estimate where the ball will cross this paddle's x coordinate."""
    if state.ball_vx == 0:
        return float(state.ball_y)
    steps = (state.my_paddle_x - state.ball_x) / state.ball_vx
    if steps < 0:
        return float(state.ball_y)
    predicted_y = state.ball_y + state.ball_vy * steps
    return _reflect_y(predicted_y, state.window_height)


class PongAI:
    """Base class for all AI strategies."""

    name = "PongAI"

    def choose_move(self, state: GameState) -> int:
        # Default behavior: do nothing.
        _ = state
        return MOVE_STAY


class TrackingAI(PongAI):
    """Baseline opponent that tracks the ball with simple rules."""

    name = "TrackingAI"

    def choose_move(self, state: GameState) -> int:
        paddle_center = state.my_paddle_y + state.paddle_height // 2
        target_y = state.ball_y

        # When ball moves away, drift back toward center.
        if not _is_ball_moving_toward_me(state):
            target_y = state.window_height // 2

        dead_zone = 8
        if target_y < paddle_center - dead_zone:
            return MOVE_UP
        if target_y > paddle_center + dead_zone:
            return MOVE_DOWN
        return MOVE_STAY


class ReferenceAI(PongAI):
    """Target AI students should try to beat."""

    name = "ReferenceAI"

    def __init__(self) -> None:
        self._hold_frames = 0
        self._last_move = MOVE_STAY

    def choose_move(self, state: GameState) -> int:
        # Small reaction delay keeps this AI strong but beatable.
        if self._hold_frames > 0:
            self._hold_frames -= 1
            return self._last_move

        paddle_center = state.my_paddle_y + state.paddle_height // 2

        if _is_ball_moving_toward_me(state):
            target_y = _predict_intercept_y(state)
            opponent_center = state.opponent_paddle_y + state.paddle_height // 2
            # Small aim bias tries to send returns away from the opponent center.
            if opponent_center < state.window_height // 2:
                target_y += 10
            else:
                target_y -= 10
            if random.random() < 0.06:
                self._last_move = MOVE_STAY
                self._hold_frames = 1
                return self._last_move
        else:
            target_y = state.window_height // 2

        dead_zone = 8
        if target_y < paddle_center - dead_zone:
            self._last_move = MOVE_UP
        elif target_y > paddle_center + dead_zone:
            self._last_move = MOVE_DOWN
        else:
            self._last_move = MOVE_STAY

        self._hold_frames = 1
        return self._last_move


class RandomAI(PongAI):
    """Very weak opponent useful for first tests."""

    name = "RandomAI"

    def choose_move(self, state: GameState) -> int:
        _ = state
        return random.choice([MOVE_UP, MOVE_STAY, MOVE_DOWN])


class StudentAI(PongAI):
    """Starter strategy for students.

    Edit choose_move() to implement your own AI.
    """

    name = "StudentAI"

    def choose_move(self, state: GameState) -> int:
        # TODO(student): replace this with your own strategy.
        # Suggested steps:
        # 1) Track ball only when it is moving toward your paddle.
        # 2) Predict where the ball will be when it reaches your x position.
        # 3) Add a small dead zone to avoid jittering.
        paddle_center = state.my_paddle_y + state.paddle_height // 2

        if state.ball_y < paddle_center - 12:
            return MOVE_UP
        if state.ball_y > paddle_center + 12:
            return MOVE_DOWN
        return MOVE_STAY


def create_ai(name: str) -> PongAI:
    """Factory for named AI strategies."""
    key = name.strip().lower()
    if key == "tracking":
        return TrackingAI()
    if key == "reference":
        return ReferenceAI()
    if key == "random":
        return RandomAI()
    if key == "student":
        return StudentAI()
    raise ValueError("Unknown AI. Choose from: tracking, reference, random, student")
