import pygame as pg


# Intervals
def intervals_overlap(a1: int, b1: int, a2: int, b2: int) -> bool:
    return a1 < b2 and a2 < b1


def overlap_length(a1: int, b1: int, a2: int, b2: int) -> int:
    return min(b1, b2) - max(a1, a2)


# Detection
def rectangles_overlap(r1: pg.Rect, r2: pg.Rect) -> bool:
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


# Resolution
def get_displacement(r1: pg.Rect, r2: pg.Rect, v1x: int, v1y: int) -> tuple[int, int]:
    dx, dy = 0, 0
    ox = overlap_length(r1.x, r1.x + r1.width, r2.x, r2.x + r2.width)
    oy = overlap_length(r1.y, r1.y + r1.height, r2.y, r2.y + r2.height)
    if ox < oy:
        dx = r2.x + r2.width - r1.x if v1x < 0 else r2.x - r1.x - r1.width
    elif oy < ox:
        dy = r2.y + r2.height - r1.y if v1y < 0 else r2.y - r1.y - r1.height
    else:
        old_x, old_y = r1.x - v1x, r1.y - v1y
        ox = overlap_length(old_x, old_x + r1.width, r2.x, r2.x + r2.width)
        oy = overlap_length(old_y, old_y + r1.height, r2.y, r2.y + r2.height)
        if ox < oy:
            dx = r2.x + r2.width - r1.x if v1x < 0 else r2.x - r1.x - r1.width
        else:
            dy = r2.y + r2.height - r1.y if v1y < 0 else r2.y - r1.y - r1.height
    return dx, dy
