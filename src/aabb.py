import pygame as pg


# Intervals
def intervals_overlap(a1: int, b1: int, a2: int, b2: int) -> bool:
    return a1 <= b2 and a2 <= b1


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
# TODO
