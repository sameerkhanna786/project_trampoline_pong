# AI Development Guide for Students

This guide explains how to implement `student_ai_choose_move()` clearly and safely while preserving game behavior.

Read setup and Git basics first in `README.md`.

## 1. What you are allowed to change

You should edit:
- `student_ai_choose_move(state)` in `ai_opponents.py`

You should not edit (unless teacher explicitly asks):
- Physics and collision logic in `pong.py`
- Benchmark pass/fail logic
- `ReferenceAI` behavior

## 2. AI API Contract

`student_ai_choose_move(state)` is called every frame.

Input:
- `state`: a `GameState` object.

Output:
- `-1` to move paddle up
- `0` to keep paddle still
- `1` to move paddle down

The game clamps unexpected values, but you should still return exactly `-1`, `0`, or `1`.

## 3. `GameState` Field Reference

Your AI can use:
- `state.my_side`: `"left"` or `"right"`
- `state.window_width`, `state.window_height`
- `state.paddle_height`, `state.paddle_speed`
- `state.my_paddle_x`, `state.my_paddle_y`
- `state.opponent_paddle_x`, `state.opponent_paddle_y`
- `state.ball_x`, `state.ball_y`
- `state.ball_vx`, `state.ball_vy`

Helpful interpretation:
- If your paddle is on the right side, `ball_vx > 0` means the ball is moving toward you.
- If your paddle is on the left side, `ball_vx < 0` means the ball is moving toward you.

## 4. Recommended Milestone Plan

The template in `ai_opponents.py` has two branches with TODO hints.
Work through them in order:

1. Fill in Branch A (ball moving toward you):
- Compare `state.ball_y` to `paddle_center`.
- Return `MOVE_UP` (`-1`) or `MOVE_DOWN` (`1`) to move your paddle toward the ball.
- This alone is enough to start blocking shots.

2. Fill in Branch B (ball moving away):
- Compare `paddle_center` to `screen_center`.
- Move your paddle back toward the center so you are ready for the next rally.

3. Optional enhancements (after passing benchmark):
- Add a dead zone so the paddle does not jitter when it is already close to the target.
- Use `predict_intercept_y(state)` (provided helper) to aim where the ball will arrive instead of where it is now.
- Tune numeric values (dead zone size, switching thresholds) by watching replays.

## 5. Simple Implementation Pattern

Here is a minimal working version that fills in both TODOs:

```python
def student_ai_choose_move(state):
    paddle_center = state.my_paddle_y + state.paddle_height // 2
    screen_center = state.window_height // 2

    if is_ball_moving_toward_me(state):
        # Branch A: move toward the ball
        if state.ball_y < paddle_center:
            return -1   # up
        if state.ball_y > paddle_center:
            return 1    # down
        return 0

    # Branch B: drift back to center
    if paddle_center < screen_center:
        return 1    # down toward center
    if paddle_center > screen_center:
        return -1   # up toward center
    return 0
```

This is enough to beat `ReferenceAI` and pass the benchmark.

## 6. Required Test Workflow

Run these after each major AI change:

```bash
# Human vs your AI
python pong.py --mode human-vs-student

# Visual AI-vs-AI comparison
python pong.py --mode ai-vs-ai --left-ai reference --right-ai student

# Pass/fail benchmark
python pong.py --mode benchmark
```

Recommended consistency check:

```bash
python pong.py --mode benchmark --matches 30 --seed 2026
python pong.py --mode benchmark --matches 30 --seed 3000
```

## 7. Passing Target (Grading)

By default, benchmark pass requires:
- at least 60% decisive-match win rate against `ReferenceAI`
- no runtime errors in `student_ai_choose_move`

Note:
- Draw-only matches do not count in the win-rate denominator.

## 8. Debugging Tips

If your AI behaves strangely:
- verify returned values are only `-1`, `0`, `1`
- print key state values temporarily:
  - `ball_x`, `ball_y`, `ball_vx`, `ball_vy`
  - `my_paddle_y`
- remove debug prints before commit

If benchmark crashes:
- check for division-by-zero and index errors in your code
- make sure all branches in `student_ai_choose_move` return an integer

## 9. Team Collaboration Suggestions

Useful team workflow:
- each student creates a separate feature branch
- each branch implements one strategy variant
- compare branches using benchmark results in PR descriptions

Example branch ideas:
- `feature/student-ai-tracker`
- `feature/student-ai-predictive`
- `feature/student-ai-defensive`

## 10. PR Checklist for AI Work

Before opening PR:
- `student_ai_choose_move` is the only code logic changed (unless assigned otherwise)
- game runs in `human-vs-student` mode
- benchmark command completes
- PR includes:
  - strategy summary
  - benchmark output
  - known limitations
