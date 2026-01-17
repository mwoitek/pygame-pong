from enum import IntEnum

import pygame as pg

WINDOW_WIDTH = 12 * 67
WINDOW_HEIGHT = 12 * 51
ARENA_BORDER_WIDTH = 12

DARK_BLUE = pg.Color(32, 32, 96)


class Arena:
    def __init__(
        self,
        border_width: int,
        gap_length: int,
        border_color: pg.typing.ColorLike = "white",
    ) -> None:
        self.border_width = border_width
        self.gap_length = gap_length
        self.border_color = border_color
        self.vertical_surf = self._get_vertical_surface()
        self.horizontal_surf = self._get_horizontal_surface()
        self.vertical_rects = self._get_vertical_rectangles()
        self.horizontal_rects = self._get_horizontal_rectangles()
        self.surf = self._get_surface()

    def _get_vertical_surface(self) -> pg.Surface:
        width = self.border_width
        height = (WINDOW_HEIGHT - self.gap_length) // 2
        surf = pg.Surface((width, height))
        surf.fill(self.border_color)
        return surf

    def _get_horizontal_surface(self) -> pg.Surface:
        width = WINDOW_WIDTH - 2 * self.border_width
        height = self.border_width
        surf = pg.Surface((width, height))
        surf.fill(self.border_color)
        return surf

    def _get_vertical_rectangles(self) -> list[pg.Rect]:
        x = WINDOW_WIDTH - self.border_width
        y = self.vertical_surf.height + self.gap_length
        positions = [
            (0, 0),
            (0, y),
            (x, 0),
            (x, y),
        ]
        return [self.vertical_surf.get_rect(topleft=topleft) for topleft in positions]

    def _get_horizontal_rectangles(self) -> list[pg.Rect]:
        positions = [
            (self.border_width, 0),
            (self.border_width, WINDOW_HEIGHT - self.border_width),
        ]
        return [self.horizontal_surf.get_rect(topleft=topleft) for topleft in positions]

    def _get_surface(self) -> pg.Surface:
        surf = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        for rect in self.vertical_rects:
            surf.blit(self.vertical_surf, rect)
        for rect in self.horizontal_rects:
            surf.blit(self.horizontal_surf, rect)
        return surf

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self.surf)


class Divider:
    def __init__(
        self,
        square_side: int,
        gap_length: int | None = None,
        color: pg.typing.ColorLike = "white",
    ) -> None:
        self.square_side = square_side
        self.gap_length = gap_length if gap_length is not None else square_side
        self.color = color
        self.rects = self._get_rectangles()
        self.surf = self._get_surface()

    def _get_rectangles(self) -> list[pg.Rect]:
        rects: list[pg.Rect] = []
        delta_y = self.gap_length + self.square_side
        num_rects = (WINDOW_HEIGHT - 2 * ARENA_BORDER_WIDTH + self.gap_length) // delta_y
        for i in range(num_rects):
            rect = pg.Rect(0, i * delta_y, self.square_side, self.square_side)
            rects.append(rect)
        return rects

    def _get_surface(self) -> pg.Surface:
        square = pg.Surface((self.square_side, self.square_side))
        square.fill(self.color)
        last_rect = self.rects[-1]
        surf = pg.Surface((self.square_side, last_rect.y + last_rect.height))
        for rect in self.rects:
            surf.blit(square, rect)
        return surf

    def render(self, screen: pg.Surface) -> None:
        screen.blit(
            self.surf,
            ((WINDOW_WIDTH - self.square_side) // 2, ARENA_BORDER_WIDTH),
        )


class Action(IntEnum):
    MOVE_DOWN = 0
    MOVE_UP = 1


class ActionBuffer:
    def __init__(self) -> None:
        self.values = [False for _ in range(len(Action))]

    def __getitem__(self, action: Action) -> bool:
        return self.values[action.value]

    def __setitem__(self, action: Action, value: bool) -> None:
        self.values[action.value] = value


class Paddle:
    def __init__(
        self,
        x: float,
        y: float,
        width: float,
        height: float,
        velocity: float,
    ) -> None:
        self.rect = pg.FRect(x, y, width, height)
        self.velocity = velocity
        self.max_y = WINDOW_HEIGHT - ARENA_BORDER_WIDTH - height

    def update(self, action_buffer: ActionBuffer, dt: float) -> None:
        y = self.rect.y
        if action_buffer[Action.MOVE_DOWN]:
            y += self.velocity * dt
            y = min(y, self.max_y)
            action_buffer[Action.MOVE_DOWN] = False
        if action_buffer[Action.MOVE_UP]:
            y -= self.velocity * dt
            y = max(y, ARENA_BORDER_WIDTH)
            action_buffer[Action.MOVE_UP] = False
        self.rect.y = y


pg.init()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Pong")

arena = Arena(
    border_width=ARENA_BORDER_WIDTH,
    gap_length=12 * 30,
    border_color=DARK_BLUE,
)
divider = Divider(square_side=4, color=DARK_BLUE)
action_buffers = [ActionBuffer(), ActionBuffer()]

is_running = True
while is_running:
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                is_running = False
            case _:
                pass
    # update
    screen.fill("black")
    arena.render(screen)
    divider.render(screen)
    pg.display.flip()

pg.quit()
