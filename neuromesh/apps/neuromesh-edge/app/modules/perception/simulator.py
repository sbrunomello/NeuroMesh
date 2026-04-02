from __future__ import annotations

import random


def next_motion_state(current_moving: bool) -> tuple[bool, float, float]:
    interval_jitter = random.uniform(-0.2, 0.3)
    moving = current_moving
    if random.random() < 0.35:
        moving = not moving
    confidence = round(random.uniform(0.5, 0.99) if moving else random.uniform(0.01, 0.4), 2)
    return moving, confidence, interval_jitter
