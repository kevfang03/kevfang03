"""How all-time contributions turn into towers on the skyline.

Every few contributions add a floor to the tower under construction. When a
tower reaches full height it stays on the skyline for good, crowned with your
monogram, and the crane moves to the next empty lot.
"""

from __future__ import annotations

TOWER_FLOORS = 22
CONTRIBUTIONS_PER_FLOOR = 8
# (x, width) of each building lot on the skyline, filled in this order.
LOTS = ((36, 16), (176, 12), (77, 8))


def tower_progress(total_contributions: int) -> tuple[int, int]:
    """Return (finished towers, floors built on the current one)."""
    per_tower = TOWER_FLOORS * CONTRIBUTIONS_PER_FLOOR
    done = min(max(0, total_contributions) // per_tower, len(LOTS))
    if done == len(LOTS):
        return done, 0
    return done, (total_contributions % per_tower) // CONTRIBUTIONS_PER_FLOOR
