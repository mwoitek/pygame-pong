from typing import Protocol

type Number = int | float


class RectLike(Protocol):
    x: Number
    y: Number
    width: Number
    height: Number


# Ordinary AABB


def intervals_overlap(
    a1: Number,
    b1: Number,
    a2: Number,
    b2: Number,
) -> bool:
    return max(a1, a2) <= min(b1, b2)


def rectangles_overlap(r1: RectLike, r2: RectLike) -> bool:
    return intervals_overlap(
        r1.x,
        r1.x + r1.width,
        r2.x,
        r2.x + r2.width,
    ) and intervals_overlap(
        r1.y,
        r1.y + r1.height,
        r2.y,
        r2.y + r2.height,
    )
