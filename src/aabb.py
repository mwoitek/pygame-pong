from math import isclose
from typing import Protocol

type Number = int | float

INFINITY = float("inf")


class RectLike(Protocol):
    x: Number
    y: Number
    width: Number
    height: Number


class IntIndexable(Protocol):
    def __getitem__(self, index: int) -> Number: ...


def ge(
    a: Number,
    b: Number,
    /,
    *,
    rel_tol: float = 1e-05,
    abs_tol: float = 1e-08,
) -> bool:
    return a > b or isclose(a, b, rel_tol=rel_tol, abs_tol=abs_tol)


# Ordinary AABB


def intervals_overlap(
    a1: Number,
    b1: Number,
    a2: Number,
    b2: Number,
) -> bool:
    return ge(min(b1, b2), max(a1, a2))


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
            return -INFINITY, INFINITY
        return None
    t1 = (a2 - b1) / v
    t2 = (b2 - a1) / v
    if t1 < t2:
        return t1, t2
    return t2, t1


def sweep(
    r1: RectLike,
    r2: RectLike,
    v1: IntIndexable,
    v2: IntIndexable,
    dt: float,
) -> tuple[float, int, int] | None:
    res_x = sweep_axis(r1.x, r1.x + r1.width, r2.x, r2.x + r2.width, v1[0], v2[0])
    if res_x is None:
        return None
    res_y = sweep_axis(r1.y, r1.y + r1.height, r2.y, r2.y + r2.height, v1[1], v2[1])
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
        normal_x = 1 if v1[0] < v2[0] else -1
    else:
        normal_y = 1 if v1[1] < v2[1] else -1
    return entry_time, normal_x, normal_y
