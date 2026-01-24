import random
from enum import IntEnum
from typing import Literal, cast

import pygame as pg

import aabb

type Side = Literal["left", "right"]

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pong"
BORDER_WIDTH = 10

PADDLE_WIDTH = 8
PADDLE_HEIGHT = 96
PADDLE_VELOCITY = 6

BALL_SIZE = 10
BALL_VELOCITY = 6

CYAN = pg.Color(91, 200, 175)
DARK_BLUE = pg.Color(32, 32, 96)
FUCHSIA = pg.Color(176, 48, 176)

FPS = 60
FIXED_DT_US = 1_000_000 // FPS
FIXED_DT_REM = 1_000_000 % FPS

random.seed(a=60693174)


class Arena:
    def __init__(self, /, *, color: pg.typing.ColorLike = "white") -> None:
        self._vertical_rects = self._get_vertical_rectangles()
        self._horizontal_rects = self._get_horizontal_rectangles()
        self.rects = self._vertical_rects + self._horizontal_rects
        self._surf = self._get_surface(color)

    def _get_vertical_rectangles(self) -> list[pg.Rect]:
        positions = [(0, 0), (0, 500), (790, 0), (790, 500)]
        size = (10, 100)
        return [pg.Rect(position, size) for position in positions]

    def _get_horizontal_rectangles(self) -> list[pg.Rect]:
        positions = [(10, 0), (10, 590)]
        size = (780, 10)
        return [pg.Rect(position, size) for position in positions]

    def _get_vertical_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface(self._vertical_rects[0].size)
        surf.fill(color)
        return surf

    def _get_horizontal_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface(self._horizontal_rects[0].size)
        surf.fill(color)
        return surf

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        vertical_surf = self._get_vertical_surface(color)
        horizontal_surf = self._get_horizontal_surface(color)
        blit_sequence = [(vertical_surf, rect) for rect in self._vertical_rects]
        blit_sequence += [(horizontal_surf, rect) for rect in self._horizontal_rects]
        surf.blits(blit_sequence, doreturn=0)
        return surf

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf)


class Divider:
    def __init__(self, /, *, color: pg.typing.ColorLike = "white") -> None:
        self._surf = self._get_surface(color)
        self._pos = (398, 10)

    def _get_rectangles(self) -> list[pg.Rect]:
        return [pg.Rect(0, i * 8, 4, 4) for i in range(73)]

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        square = pg.Surface((4, 4))
        square.fill(color)
        surf = pg.Surface((4, 580))
        blit_sequence = [(square, rect) for rect in self._get_rectangles()]
        surf.blits(blit_sequence, doreturn=0)
        return surf

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self._pos)


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
    def __init__(self, /, *, side: Side, color: pg.typing.ColorLike = "white") -> None:
        self._init_pos = (12 if side == "left" else 780, 252)
        self.rect = pg.Rect(self._init_pos, (PADDLE_WIDTH, PADDLE_HEIGHT))
        self._surf = self._get_surface(color)

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface(self.rect.size)
        surf.fill(color)
        return surf

    def update(self, action_buffer: ActionBuffer) -> None:
        if action_buffer[Action.MOVE_DOWN]:
            self.rect.y = min(self.rect.y + PADDLE_VELOCITY, 492)
            action_buffer[Action.MOVE_DOWN] = False
        if action_buffer[Action.MOVE_UP]:
            self.rect.y = max(self.rect.y - PADDLE_VELOCITY, 12)
            action_buffer[Action.MOVE_UP] = False

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self.rect)


class Ball:
    def __init__(self, /, *, color: pg.typing.ColorLike = "white") -> None:
        self.rect = pg.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        side = cast("Side", random.choice(["left", "right"]))
        self._set_random_position(side)
        # TODO: randomize
        self._vel_x = BALL_VELOCITY
        self._vel_y = BALL_VELOCITY
        self._surf = self._get_surface(color)

    def _set_random_position(self, side: Side) -> None:
        if side == "left":
            x_min, x_max = 370, 400
        else:
            x_min, x_max = 401, 431
        y_min, y_max = 60, 541
        self.rect.centerx = random.randrange(x_min, x_max)
        self.rect.centery = random.randrange(y_min, y_max)

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface(self.rect.size)
        surf.fill(color)
        return surf

    def update(self, rects: list[pg.Rect]) -> None:
        hit = False
        for collider in (r for r in rects if aabb.rectangles_overlap(self.rect, r)):
            hit = True
            dx, dy = aabb.get_displacement(self.rect, collider, self._vel_x, self._vel_y)
            if dx != 0:
                self.rect.x += dx
                self._vel_x *= -1
            else:
                self.rect.y += dy
                self._vel_y *= -1
        if hit:
            return
        self.rect.x += self._vel_x
        self.rect.y += self._vel_y

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self.rect)


PLAYER_KEYBINDINGS = [
    {
        Action.MOVE_DOWN: pg.K_w,
        Action.MOVE_UP: pg.K_e,
    },
    {
        Action.MOVE_DOWN: pg.K_i,
        Action.MOVE_UP: pg.K_o,
    },
]


class Game:
    def __init__(
        self,
        /,
        *,
        arena: Arena,
        divider: Divider,
        paddle_left: Paddle,
        paddle_right: Paddle,
        ball: Ball,
    ) -> None:
        self.is_running = False
        self.arena = arena
        self.divider = divider
        self.paddle_left = paddle_left
        self.paddle_right = paddle_right
        self.ball = ball
        self._action_buffers = [ActionBuffer() for _ in range(len(PLAYER_KEYBINDINGS))]
        self._rects = [*arena.rects, paddle_left.rect, paddle_right.rect]

    def run(self) -> None:
        pg.init()
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(WINDOW_TITLE)
        time_acc = 0
        time_err = 0
        clock = pg.time.Clock()
        self.is_running = True
        while self.is_running:
            for event in pg.event.get():
                self.handle_event(event)
            self.get_actions()
            time_acc += clock.tick() * 1_000  # TODO: enforce max value
            if time_acc >= FIXED_DT_US:
                self.update()
                time_acc -= FIXED_DT_US
                time_err += FIXED_DT_REM
                if time_err >= FPS:
                    time_acc -= 1
                    time_err -= FPS
            self.render()
        pg.quit()

    def handle_event(self, event: pg.event.Event) -> None:
        match event.type:
            case pg.QUIT:
                self.is_running = False
            case _:
                pass

    def get_actions(self) -> None:
        keys = pg.key.get_pressed()
        for action_buffer, bindings in zip(self._action_buffers, PLAYER_KEYBINDINGS, strict=True):
            for action, key in bindings.items():
                if keys[key]:
                    action_buffer[action] = True

    def update(self) -> None:
        self.paddle_left.update(self._action_buffers[0])
        self.paddle_right.update(self._action_buffers[1])
        self.ball.update(self._rects)

    def render(self) -> None:
        self.screen.fill("black")
        self.arena.render(self.screen)
        self.divider.render(self.screen)
        self.paddle_left.render(self.screen)
        self.paddle_right.render(self.screen)
        self.ball.render(self.screen)
        pg.display.flip()


if __name__ == "__main__":
    game = Game(
        arena=Arena(color=DARK_BLUE),
        divider=Divider(color=DARK_BLUE),
        paddle_left=Paddle(side="left", color=CYAN),
        paddle_right=Paddle(side="right", color=FUCHSIA),
        ball=Ball(),
    )
    game.run()
