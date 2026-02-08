"""Simple Pong game with optional AI opponent.

Controls:
- Left paddle: W (up), S (down)
- Right paddle (PVP mode only): Up arrow, Down arrow
"""

import argparse
import os
import random
import warnings

from ai_opponents import GameState, create_ai, normalize_move

# Hide the pygame startup banner in terminal output.
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")

# pygame 2.6 imports pkg_resources internally, which triggers a deprecation
# warning on newer setuptools versions. Suppress that single warning.
warnings.filterwarnings(
    "ignore",
    message=r"pkg_resources is deprecated as an API.*",
    category=UserWarning,
    module=r"pygame\.pkgdata",
)

import pygame

# Window and game settings
WIDTH = 800
HEIGHT = 500
FPS = 60
WIN_SCORE = 7
DEFAULT_MAX_MATCH_FRAMES = FPS * 45
BENCHMARK_MAX_BALL_X_SPEED = 20
BENCHMARK_MAX_BALL_Y_SPEED = 14

# Paddle settings
PADDLE_WIDTH = 12
PADDLE_HEIGHT = 90
PADDLE_SPEED = 6

# Ball settings
BALL_SIZE = 14
BALL_START_SPEED = 5
BALL_MAX_Y_SPEED = 7

# Colors (R, G, B)
BLACK = (20, 20, 20)
WHITE = (245, 245, 245)
AI_CHOICES = ["tracking", "reference", "random", "student"]


def parse_args() -> argparse.Namespace:
    """Parse command-line options."""
    parser = argparse.ArgumentParser(description="Simple Pong")
    parser.add_argument(
        "--mode",
        choices=["pvp", "human-vs-ai", "human-vs-student", "ai-vs-ai", "benchmark"],
        default="human-vs-ai",
        help=(
            "pvp = 2 players, human-vs-ai = left human vs right AI, "
            "human-vs-student = left human vs StudentAI, "
            "ai-vs-ai = watch AIs compete, benchmark = pass/fail test"
        ),
    )
    parser.add_argument(
        "--opponent",
        choices=AI_CHOICES,
        default="tracking",
        help="AI strategy for the right paddle in human-vs-ai mode",
    )
    parser.add_argument(
        "--left-ai",
        choices=AI_CHOICES,
        default="reference",
        help="Left AI in ai-vs-ai mode",
    )
    parser.add_argument(
        "--right-ai",
        choices=AI_CHOICES,
        default="student",
        help="Right AI in ai-vs-ai mode",
    )
    parser.add_argument(
        "--matches",
        type=int,
        default=25,
        help="Number of matches for benchmark mode",
    )
    parser.add_argument(
        "--pass-win-rate",
        type=float,
        default=0.60,
        help="StudentAI required decisive-match win rate to pass benchmark mode",
    )
    parser.add_argument(
        "--max-match-frames",
        type=int,
        default=DEFAULT_MAX_MATCH_FRAMES,
        help="Frame limit for each ai-vs-ai benchmark match",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=2026,
        help="Base random seed for benchmark mode",
    )
    return parser.parse_args()


def clamp_paddle(paddle_rect: pygame.Rect) -> None:
    """Keep a paddle inside the window."""
    if paddle_rect.top < 0:
        paddle_rect.top = 0
    if paddle_rect.bottom > HEIGHT:
        paddle_rect.bottom = HEIGHT


def reset_ball(ball_rect: pygame.Rect) -> tuple[int, int]:
    """Move ball to center and return a fresh velocity."""
    ball_rect.center = (WIDTH // 2, HEIGHT // 2)
    x_direction = random.choice([-1, 1])
    y_direction = random.choice([-1, 1])
    vx = BALL_START_SPEED * x_direction
    vy = BALL_START_SPEED * y_direction
    return vx, vy


def move_paddles(
    keys: pygame.key.ScancodeWrapper,
    left_paddle: pygame.Rect,
    right_paddle: pygame.Rect,
) -> None:
    """Read keyboard input and move paddles."""
    if keys[pygame.K_w]:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s]:
        left_paddle.y += PADDLE_SPEED
    if keys[pygame.K_UP]:
        right_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_DOWN]:
        right_paddle.y += PADDLE_SPEED

    clamp_paddle(left_paddle)
    clamp_paddle(right_paddle)


def move_left_paddle(keys: pygame.key.ScancodeWrapper, left_paddle: pygame.Rect) -> None:
    """Move only the left paddle from keyboard input."""
    if keys[pygame.K_w]:
        left_paddle.y -= PADDLE_SPEED
    if keys[pygame.K_s]:
        left_paddle.y += PADDLE_SPEED
    clamp_paddle(left_paddle)


def move_right_paddle_with_ai(right_paddle: pygame.Rect, ai_move: int) -> None:
    """Apply AI move to the right paddle.

    ai_move values:
    -1 = up, 0 = stay, 1 = down
    """
    right_paddle.y += normalize_move(ai_move) * PADDLE_SPEED
    clamp_paddle(right_paddle)


def move_left_paddle_with_ai(left_paddle: pygame.Rect, ai_move: int) -> None:
    """Apply AI move to the left paddle."""
    left_paddle.y += normalize_move(ai_move) * PADDLE_SPEED
    clamp_paddle(left_paddle)


def build_ai_state(
    side: str,
    my_paddle: pygame.Rect,
    opponent_paddle: pygame.Rect,
    ball_rect: pygame.Rect,
    ball_vx: int,
    ball_vy: int,
) -> GameState:
    """Create the state object passed to an AI controller."""
    if side not in {"left", "right"}:
        raise ValueError("side must be 'left' or 'right'")

    return GameState(
        window_width=WIDTH,
        window_height=HEIGHT,
        paddle_height=PADDLE_HEIGHT,
        paddle_speed=PADDLE_SPEED,
        my_side=side,
        my_paddle_x=my_paddle.x,
        my_paddle_y=my_paddle.y,
        opponent_paddle_x=opponent_paddle.x,
        opponent_paddle_y=opponent_paddle.y,
        ball_x=ball_rect.centerx,
        ball_y=ball_rect.centery,
        ball_vx=ball_vx,
        ball_vy=ball_vy,
    )


def bounce_off_paddle(ball_rect: pygame.Rect, paddle_rect: pygame.Rect, vx: int, vy: int) -> tuple[int, int]:
    """Bounce ball from a paddle and adjust vertical speed based on hit location."""
    # Flip horizontal direction.
    vx = -vx

    # Hitting near paddle edges changes Y speed more than center hits.
    relative_hit = (ball_rect.centery - paddle_rect.centery) / (PADDLE_HEIGHT / 2)
    vy += int(relative_hit * 3)

    # Keep Y speed in a useful range.
    if vy > BALL_MAX_Y_SPEED:
        vy = BALL_MAX_Y_SPEED
    if vy < -BALL_MAX_Y_SPEED:
        vy = -BALL_MAX_Y_SPEED

    return vx, vy


def update_ball(
    ball_rect: pygame.Rect,
    left_paddle: pygame.Rect,
    right_paddle: pygame.Rect,
    vx: int,
    vy: int,
    left_score: int,
    right_score: int,
) -> tuple[int, int, int, int]:
    """Move ball, handle collisions, and update score."""
    ball_rect.x += vx
    ball_rect.y += vy

    # Bounce off top/bottom walls.
    if ball_rect.top <= 0 or ball_rect.bottom >= HEIGHT:
        vy = -vy

    # Paddle collisions.
    if ball_rect.colliderect(left_paddle) and vx < 0:
        ball_rect.left = left_paddle.right
        vx, vy = bounce_off_paddle(ball_rect, left_paddle, vx, vy)
    elif ball_rect.colliderect(right_paddle) and vx > 0:
        ball_rect.right = right_paddle.left
        vx, vy = bounce_off_paddle(ball_rect, right_paddle, vx, vy)

    # Scoring.
    if ball_rect.left <= 0:
        right_score += 1
        vx, vy = reset_ball(ball_rect)
    elif ball_rect.right >= WIDTH:
        left_score += 1
        vx, vy = reset_ball(ball_rect)

    return vx, vy, left_score, right_score


def draw_scene(
    screen: pygame.Surface,
    font: pygame.font.Font,
    small_font: pygame.font.Font,
    left_paddle: pygame.Rect,
    right_paddle: pygame.Rect,
    ball_rect: pygame.Rect,
    left_score: int,
    right_score: int,
    status_text: str = "",
) -> None:
    """Draw all visible game elements."""
    screen.fill(BLACK)

    # Center line
    pygame.draw.line(screen, WHITE, (WIDTH // 2, 0), (WIDTH // 2, HEIGHT), 2)

    # Paddles and ball
    pygame.draw.rect(screen, WHITE, left_paddle)
    pygame.draw.rect(screen, WHITE, right_paddle)
    pygame.draw.rect(screen, WHITE, ball_rect)

    # Score text
    score_text = font.render(f"{left_score} : {right_score}", True, WHITE)
    score_rect = score_text.get_rect(center=(WIDTH // 2, 35))
    screen.blit(score_text, score_rect)

    if status_text:
        mode_text = small_font.render(status_text, True, WHITE)
        screen.blit(mode_text, (16, 12))

    pygame.display.flip()


def show_message(screen: pygame.Surface, font: pygame.font.Font, text: str, milliseconds: int = 1800) -> None:
    """Display a center message for a short moment."""
    screen.fill(BLACK)
    message = font.render(text, True, WHITE)
    message_rect = message.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    screen.blit(message, message_rect)
    pygame.display.flip()
    pygame.time.wait(milliseconds)


def create_match_objects() -> tuple[pygame.Rect, pygame.Rect, pygame.Rect, int, int]:
    """Create paddles, ball, and initial ball velocity."""
    left_paddle = pygame.Rect(30, HEIGHT // 2 - PADDLE_HEIGHT // 2, PADDLE_WIDTH, PADDLE_HEIGHT)
    right_paddle = pygame.Rect(
        WIDTH - 30 - PADDLE_WIDTH,
        HEIGHT // 2 - PADDLE_HEIGHT // 2,
        PADDLE_WIDTH,
        PADDLE_HEIGHT,
    )
    ball_rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
    vx, vy = reset_ball(ball_rect)
    return left_paddle, right_paddle, ball_rect, vx, vy


def run_single_ai_match(left_ai_name: str, right_ai_name: str, max_frames: int) -> tuple[str, int, int, str]:
    """Run one headless AI-vs-AI match and return winner and score.

    winner: "left", "right", or "draw"
    reason: "score", "frame_limit", "left_ai_error", "right_ai_error"
    """
    left_ai = create_ai(left_ai_name)
    right_ai = create_ai(right_ai_name)
    left_paddle, right_paddle, ball_rect, vx, vy = create_match_objects()

    left_score = 0
    right_score = 0
    frame_count = 0

    while left_score < WIN_SCORE and right_score < WIN_SCORE and frame_count < max_frames:
        left_state = build_ai_state("left", left_paddle, right_paddle, ball_rect, vx, vy)
        right_state = build_ai_state("right", right_paddle, left_paddle, ball_rect, vx, vy)

        try:
            left_move = normalize_move(left_ai.choose_move(left_state))
        except Exception:
            return "right", left_score, right_score, "left_ai_error"

        try:
            right_move = normalize_move(right_ai.choose_move(right_state))
        except Exception:
            return "left", left_score, right_score, "right_ai_error"

        move_left_paddle_with_ai(left_paddle, left_move)
        move_right_paddle_with_ai(right_paddle, right_move)

        prev_left_score = left_score
        prev_right_score = right_score
        prev_vx = vx

        vx, vy, left_score, right_score = update_ball(
            ball_rect, left_paddle, right_paddle, vx, vy, left_score, right_score
        )

        # Benchmark-only rally acceleration to avoid endless 0-0 loops.
        scored = left_score != prev_left_score or right_score != prev_right_score
        paddle_hit = not scored and prev_vx * vx < 0
        if paddle_hit:
            if abs(vx) < BENCHMARK_MAX_BALL_X_SPEED:
                vx += 1 if vx > 0 else -1
            if vy != 0 and abs(vy) < BENCHMARK_MAX_BALL_Y_SPEED:
                vy += 1 if vy > 0 else -1

        frame_count += 1

    if left_score > right_score:
        return "left", left_score, right_score, "score"
    if right_score > left_score:
        return "right", left_score, right_score, "score"
    return "draw", left_score, right_score, "frame_limit"


def run_benchmark(args: argparse.Namespace) -> int:
    """Benchmark StudentAI against ReferenceAI and print pass/fail."""
    matches = max(1, args.matches)
    max_frames = max(60, args.max_match_frames)
    pass_win_rate = min(max(args.pass_win_rate, 0.0), 1.0)
    minimum_decisive = max(5, matches // 4)

    student_wins = 0
    reference_wins = 0
    draws = 0
    student_errors = 0

    for match_index in range(matches):
        random.seed(args.seed + match_index)
        winner, left_score, right_score, reason = run_single_ai_match("reference", "student", max_frames)

        if winner == "right":
            student_wins += 1
        elif winner == "left":
            reference_wins += 1
        else:
            draws += 1

        if reason == "right_ai_error":
            student_errors += 1

        print(
            f"Match {match_index + 1:02d}: "
            f"ReferenceAI {left_score} - {right_score} StudentAI "
            f"({reason})"
        )

    decisive_matches = student_wins + reference_wins
    decisive_win_rate = student_wins / decisive_matches if decisive_matches > 0 else 0.0
    passed = (
        decisive_matches >= minimum_decisive
        and decisive_win_rate >= pass_win_rate
        and student_errors == 0
    )

    print("\nBenchmark Summary")
    print("-----------------")
    print(f"StudentAI wins:   {student_wins}")
    print(f"ReferenceAI wins: {reference_wins}")
    print(f"Draws:            {draws}")
    print(f"Decisive matches: {decisive_matches} (minimum required: {minimum_decisive})")
    print(f"Student decisive win rate: {decisive_win_rate:.2%}")
    print(f"Required rate:            {pass_win_rate:.2%}")
    if student_errors > 0:
        print(f"Student AI errors: {student_errors} (auto-fail)")
    print(f"Result: {'PASS' if passed else 'FAIL'}")

    return 0 if passed else 1


def run_interactive_mode(args: argparse.Namespace) -> None:
    pygame.init()
    pygame.display.set_caption("Simple Pong")

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 40)
    small_font = pygame.font.SysFont("consolas", 22)

    left_paddle, right_paddle, ball_rect, vx, vy = create_match_objects()

    left_score = 0
    right_score = 0
    running = True

    left_ai = None
    right_ai = None
    status_text = "Mode: PVP"

    if args.mode == "pvp":
        status_text = "Mode: PVP (2 players)"
    elif args.mode == "human-vs-ai":
        right_ai = create_ai(args.opponent)
        status_text = f"Mode: Human vs {right_ai.name}"
    elif args.mode == "human-vs-student":
        right_ai = create_ai("student")
        status_text = "Mode: Human vs StudentAI"
    elif args.mode == "ai-vs-ai":
        left_ai = create_ai(args.left_ai)
        right_ai = create_ai(args.right_ai)
        status_text = f"Mode: {left_ai.name} vs {right_ai.name}"

    show_message(screen, font, "Pong - First to 7")

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        keys = pygame.key.get_pressed()
        if args.mode == "pvp":
            move_paddles(keys, left_paddle, right_paddle)
        elif args.mode in {"human-vs-ai", "human-vs-student"}:
            move_left_paddle(keys, left_paddle)
            right_state = build_ai_state("right", right_paddle, left_paddle, ball_rect, vx, vy)
            right_move = normalize_move(right_ai.choose_move(right_state))
            move_right_paddle_with_ai(right_paddle, right_move)
        elif args.mode == "ai-vs-ai":
            left_state = build_ai_state("left", left_paddle, right_paddle, ball_rect, vx, vy)
            right_state = build_ai_state("right", right_paddle, left_paddle, ball_rect, vx, vy)
            left_move = normalize_move(left_ai.choose_move(left_state))
            right_move = normalize_move(right_ai.choose_move(right_state))
            move_left_paddle_with_ai(left_paddle, left_move)
            move_right_paddle_with_ai(right_paddle, right_move)

        vx, vy, left_score, right_score = update_ball(
            ball_rect, left_paddle, right_paddle, vx, vy, left_score, right_score
        )
        draw_scene(
            screen,
            font,
            small_font,
            left_paddle,
            right_paddle,
            ball_rect,
            left_score,
            right_score,
            status_text,
        )

        if left_score >= WIN_SCORE or right_score >= WIN_SCORE:
            if args.mode == "pvp":
                winner = "Left Player Wins!" if left_score > right_score else "Right Player Wins!"
            elif args.mode in {"human-vs-ai", "human-vs-student"}:
                winner = "You Win!" if left_score > right_score else f"{right_ai.name} Wins!"
            else:
                winner = f"{left_ai.name} Wins!" if left_score > right_score else f"{right_ai.name} Wins!"
            show_message(screen, font, winner)
            left_score = 0
            right_score = 0
            left_paddle.centery = HEIGHT // 2
            right_paddle.centery = HEIGHT // 2
            vx, vy = reset_ball(ball_rect)
            show_message(screen, font, "New Match")

        clock.tick(FPS)

    pygame.quit()


def main() -> int:
    args = parse_args()

    if args.mode == "benchmark":
        return run_benchmark(args)

    run_interactive_mode(args)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
