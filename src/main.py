import random
from enum import IntEnum
from pathlib import Path
from typing import Literal

import pygame as pg

import aabb

type Side = Literal["left", "right"]

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
WINDOW_TITLE = "Pong"

FPS = 60
DT_FIXED = 1_000 // FPS
DT_FIXED_ERR = 1_000 % FPS

MAX_SCORE = 20

CYAN = pg.Color(91, 200, 175)
DARK_BLUE = pg.Color(32, 32, 96)
FUCHSIA = pg.Color(176, 48, 176)

ROOT_DIR = Path(__file__).parents[1]
ASSETS_DIR = ROOT_DIR / "assets"

random.seed(a=60693174)


def get_colored_surface(size: tuple[int, int], color: pg.typing.ColorLike) -> pg.Surface:
    surf = pg.Surface(size)
    surf.fill(color)
    return surf


class Arena:
    WIDTH = WINDOW_WIDTH
    HEIGHT = WINDOW_HEIGHT
    BORDER_X = 10
    BORDER_Y = 10

    def __init__(
        self,
        /,
        *,
        rect_height: int = 100,
        color: pg.typing.ColorLike = "white",
    ) -> None:
        self._vertical_rects = self._get_vertical_rectangles(rect_height)
        self._horizontal_rects = self._get_horizontal_rectangles()
        self.rects = self._vertical_rects + self._horizontal_rects
        self._surf = self._get_surface(color)
        self._pos = (0, 0)

    def _get_vertical_rectangles(self, height: int) -> list[pg.Rect]:
        x = Arena.WIDTH - Arena.BORDER_X
        y = Arena.HEIGHT - height
        positions = [
            (0, 0),
            (0, y),
            (x, 0),
            (x, y),
        ]
        size = (Arena.BORDER_X, height)
        return [pg.Rect(position, size) for position in positions]

    def _get_horizontal_rectangles(self) -> list[pg.Rect]:
        positions = [
            (Arena.BORDER_X, 0),
            (Arena.BORDER_X, Arena.HEIGHT - Arena.BORDER_Y),
        ]
        size = (Arena.WIDTH - 2 * Arena.BORDER_X, Arena.BORDER_Y)
        return [pg.Rect(position, size) for position in positions]

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface((Arena.WIDTH, Arena.HEIGHT))
        vertical_surf = get_colored_surface(self._vertical_rects[0].size, color)
        horizontal_surf = get_colored_surface(self._horizontal_rects[0].size, color)
        blit_sequence = [(vertical_surf, rect) for rect in self._vertical_rects]
        blit_sequence += [(horizontal_surf, rect) for rect in self._horizontal_rects]
        surf.blits(blit_sequence, doreturn=0)
        return surf

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self._pos)


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
    VELOCITY = 6

    def __init__(self, /, *, side: Side, color: pg.typing.ColorLike = "white") -> None:
        self._init_pos = (12 if side == "left" else 780, 252)
        self.rect = pg.Rect(self._init_pos, (8, 96))
        self._surf = self._get_surface(color)

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface(self.rect.size)
        surf.fill(color)
        return surf

    def update(self, action_buffer: ActionBuffer) -> None:
        if action_buffer[Action.MOVE_DOWN]:
            self.rect.y = min(self.rect.y + Paddle.VELOCITY, 492)
            action_buffer[Action.MOVE_DOWN] = False
        if action_buffer[Action.MOVE_UP]:
            self.rect.y = max(self.rect.y - Paddle.VELOCITY, 12)
            action_buffer[Action.MOVE_UP] = False

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self.rect)


class Ball:
    SIZE = 10
    VELOCITY = 6
    OUT_EVENT = pg.event.custom_type()
    OUT_LEFT = pg.Event(OUT_EVENT, side="left")
    OUT_RIGHT = pg.Event(OUT_EVENT, side="right")
    UNFREEZE_EVENT = pg.event.custom_type()

    def __init__(self, /, *, color: pg.typing.ColorLike = "white") -> None:
        self._rect = pg.Rect(0, 0, Ball.SIZE, Ball.SIZE)
        self.reset(random.choice(["left", "right"]))
        self._surf = self._get_surface(color)

    def _set_random_position(self, side: Side) -> None:
        if side == "left":
            x_min, x_max = 370, 400
        else:
            x_min, x_max = 401, 431
        y_min, y_max = 60, 541
        self._rect.centerx = random.randrange(x_min, x_max)
        self._rect.centery = random.randrange(y_min, y_max)

    def _set_velocity(self, side: Side) -> None:
        self._vx = Ball.VELOCITY
        self._vy = Ball.VELOCITY
        if side == "right":
            self._vx *= -1
        if self._rect.y > 295:
            self._vy *= -1

    def _freeze(self) -> None:
        self._frozen = True
        pg.time.set_timer(Ball.UNFREEZE_EVENT, 800, loops=1)

    def unfreeze(self) -> None:
        self._frozen = False

    def reset(self, side: Side) -> None:
        self._set_random_position(side)
        self._set_velocity(side)
        self._freeze()

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface(self._rect.size)
        surf.fill(color)
        return surf

    def _check_is_out(self) -> None:
        if self._rect.x <= -Ball.SIZE:
            pg.event.post(Ball.OUT_LEFT)
        elif self._rect.x >= WINDOW_WIDTH:
            pg.event.post(Ball.OUT_RIGHT)

    def update(self, rects: list[pg.Rect]) -> None:
        if self._frozen:
            return
        hit = False
        for collider in (r for r in rects if aabb.rectangles_overlap(self._rect, r)):
            hit = True
            dx, dy = aabb.get_displacement(self._rect, collider, self._vx, self._vy)
            if dx != 0:
                self._rect.x += dx
                self._vx *= -1
            else:
                self._rect.y += dy
                self._vy *= -1
        if hit:
            return
        self._rect.x += self._vx
        self._rect.y += self._vy
        self._check_is_out()

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self._rect)


class Score:
    SPACING_X = 8
    OFFSET_Y = 18
    WIN_EVENT = pg.event.custom_type()

    def __init__(
        self,
        /,
        *,
        font_name: str = "PressStart2P-Regular",
        font_size: int = 24,
        color: pg.typing.ColorLike = "white",
    ) -> None:
        self._font = pg.Font(ASSETS_DIR / f"{font_name}.ttf", font_size)
        self._font_size = font_size
        self._color = color
        self._scores = [0, 0]
        self._rects = self._get_rectangles()
        self._surf = self._get_surface()
        self._pos = self._get_surface_position()

    def _get_rectangles(self) -> list[pg.Rect]:
        width = 2 * self._font_size
        size = (width, self._font_size)
        return [
            pg.Rect((0, 0), size),
            pg.Rect((width + 2 * Score.SPACING_X, 0), size),
        ]

    def _get_surface(self) -> pg.Surface:
        width = 2 * (Score.SPACING_X + 2 * self._font_size)
        surf = pg.Surface((width, self._font_size))
        surfs = [self._font.render(f"{score:02}", True, self._color) for score in self._scores]
        blit_sequence = list(zip(surfs, self._rects, strict=True))
        surf.blits(blit_sequence, doreturn=0)
        return surf

    def _get_surface_position(self) -> tuple[int, int]:
        offset_x = (WINDOW_WIDTH - self._surf.width) // 2
        return offset_x, Score.OFFSET_Y

    def update(self, side: Side) -> None:
        idx = int(side == "left")
        self._scores[idx] += 1
        if self._scores[idx] == MAX_SCORE:
            event = pg.Event(Score.WIN_EVENT, player=idx + 1)
            pg.event.post(event)
        self._surf.fill("black", self._rects[idx])
        new_score = self._font.render(f"{self._scores[idx]:02}", True, self._color)
        self._surf.blit(new_score, self._rects[idx])

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self._pos)

    def reset(self) -> None:
        self._scores = [0, 0]
        self._surf = self._get_surface()


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
        score: Score,
    ) -> None:
        self.arena = arena
        self.divider = divider
        self.paddle_left = paddle_left
        self.paddle_right = paddle_right
        self.ball = ball
        self.score = score
        self._action_buffers = [ActionBuffer() for _ in range(len(PLAYER_KEYBINDINGS))]
        self._is_running = False
        self._rects = [*arena.rects, paddle_left.rect, paddle_right.rect]

    def run(self) -> None:
        self.screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pg.display.set_caption(WINDOW_TITLE)
        time_acc = 0
        time_err = 0
        clock = pg.time.Clock()
        self._is_running = True
        while self._is_running:
            for event in pg.event.get():
                self.handle_event(event)
            self.get_actions()
            time_acc += clock.tick()  # TODO: enforce max value
            if time_acc >= DT_FIXED:
                self.update()
                time_acc -= DT_FIXED
                time_err += DT_FIXED_ERR
                if time_err >= FPS:
                    time_acc -= 1
                    time_err -= FPS
            self.render()

    def handle_keydown(self, key: int) -> None:
        match key:
            case pg.K_ESCAPE | pg.K_q:
                self._is_running = False
            case _:
                pass

    def handle_event(self, event: pg.Event) -> None:
        match event.type:
            case pg.QUIT:
                self._is_running = False
            case pg.KEYDOWN:
                self.handle_keydown(event.key)
            case Ball.OUT_EVENT:
                self.score.update(event.side)
                self.ball.reset(event.side)
            case Ball.UNFREEZE_EVENT:
                self.ball.unfreeze()
            case Score.WIN_EVENT:
                print(f"Player {event.player} won!")  # just a placeholder
                self.score.reset()
                self.ball.reset("right" if event.player == 1 else "left")
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
        self.score.render(self.screen)
        self.divider.render(self.screen)
        self.paddle_left.render(self.screen)
        self.paddle_right.render(self.screen)
        self.ball.render(self.screen)
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    game = Game(
        arena=Arena(color=DARK_BLUE),
        divider=Divider(color=DARK_BLUE),
        paddle_left=Paddle(side="left", color=CYAN),
        paddle_right=Paddle(side="right", color=FUCHSIA),
        ball=Ball(),
        score=Score(color="gray"),
    )
    game.run()
    pg.quit()
