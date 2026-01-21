import math
from collections.abc import Iterable, Iterator

import pygame as pg

type Number = int | float
type Rect = pg.Rect | pg.FRect


def isclose(
    a: Number,
    b: Number,
    /,
    *,
    rel_tol: float = 1e-05,
    abs_tol: float = 1e-08,
) -> bool:
    return math.isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


def ge(a: Number, b: Number) -> bool:
    return a > b or isclose(a, b)


# Ordinary AABB
def intervals_overlap(
    a1: Number,
    b1: Number,
    a2: Number,
    b2: Number,
) -> bool:
    return ge(min(b1, b2), max(a1, a2))


def rectangles_overlap(r1: Rect, r2: Rect) -> bool:
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


# Swept AABB
def sweep_axis(
    a1: Number,
    b1: Number,
    a2: Number,
    b2: Number,
    v1: Number,
    v2: Number,
) -> tuple[float, float] | None:
    v = v1 - v2
    if isclose(v, 0):
        if intervals_overlap(a1, b1, a2, b2):
            return -math.inf, math.inf
        return None
    t1 = (a2 - b1) / v
    t2 = (b2 - a1) / v
    if t1 < t2:
        return t1, t2
    return t2, t1


def sweep(
    r1: Rect,
    r2: Rect,
    v1: pg.Vector2,
    v2: pg.Vector2,
    dt: float,
) -> tuple[float, int, int] | None:
    res_x = sweep_axis(r1.x, r1.x + r1.width, r2.x, r2.x + r2.width, v1.x, v2.x)
    if res_x is None:
        return None
    res_y = sweep_axis(r1.y, r1.y + r1.height, r2.y, r2.y + r2.height, v1.y, v2.y)
    if res_y is None:
        return None
    x_entry_time, x_exit_time = res_x
    y_entry_time, y_exit_time = res_y
    entry_time = max(x_entry_time, y_entry_time)
    exit_time = min(x_exit_time, y_exit_time)
    if entry_time > exit_time or entry_time < 0 or exit_time > dt:
        return None
    normal_x, normal_y = 0, 0
    if ge(x_entry_time, y_entry_time):
        normal_x = 1 if v1.x < v2.x else -1
    else:
        normal_y = 1 if v1.y < v2.y else -1
    return entry_time, normal_x, normal_y


# Dealing with multiple collisions
def swept_bounding_box(r: Rect, v: pg.Vector2, dt: float) -> pg.FRect:
    x1, x2 = r.x, r.x + r.width
    y1, y2 = r.y, r.y + r.height
    delta = v * dt
    x_min = min(x1, x1 + delta.x)
    x_max = max(x2, x2 + delta.x)
    y_min = min(y1, y1 + delta.y)
    y_max = max(y2, y2 + delta.y)
    width = x_max - x_min
    height = y_max - y_min
    return pg.FRect(x_min, y_min, width, height)


def filter_rectangles(
    rs: Iterable[Rect],
    r: Rect,
    v: pg.Vector2,
    dt: float,
) -> Iterator[Rect]:
    bbox = swept_bounding_box(r, v, dt)
    return (t for t in rs if rectangles_overlap(t, bbox))
