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


class Hud:
    WIDTH = WINDOW_WIDTH
    PADDING_X = 8
    PADDING_Y = 8
    WIN_DIGITS = 5
    SCORE_DIGITS = 3
    WIN_EVENT = pg.event.custom_type()

    def __init__(
        self,
        /,
        *,
        font_name: str = "PressStart2P-Regular",
        font_size: int = 24,
        background_color: pg.typing.ColorLike = "black",
        foreground_color: pg.typing.ColorLike = "white",
    ) -> None:
        self._font = pg.Font(ASSETS_DIR / f"{font_name}.ttf", font_size)
        self._font_size = font_size
        self._background_color = background_color
        self._foreground_color = foreground_color
        self.height = font_size + 2 * Hud.PADDING_Y
        self._wins = [0, 0]
        self._scores = [0, 0]
        self._rects = self._get_rectangles()
        self._surf = self._get_surface()

    def _get_rectangles(self) -> list[pg.Rect]:
        win_width = (Hud.WIN_DIGITS + 3) * self._font_size
        score_width = (Hud.SCORE_DIGITS + 3) * self._font_size
        x1 = Hud.PADDING_X
        x2 = x1 + win_width + self._font_size
        x4 = Hud.WIDTH - score_width - Hud.PADDING_X
        x3 = x4 - win_width - self._font_size
        return [
            pg.Rect(x1, Hud.PADDING_Y, win_width, self._font_size),
            pg.Rect(x2, Hud.PADDING_Y, score_width, self._font_size),
            pg.Rect(x3, Hud.PADDING_Y, win_width, self._font_size),
            pg.Rect(x4, Hud.PADDING_Y, score_width, self._font_size),
        ]

    def _get_surface(self) -> pg.Surface:
        surf = get_colored_surface((Hud.WIDTH, self.height), self._background_color)
        text_surfs = [
            self._font.render(f"W: {self._wins[0]}", True, self._foreground_color),
            self._font.render(f"S: {self._scores[0]}", True, self._foreground_color),
            self._font.render(f"W: {self._wins[1]}", True, self._foreground_color),
            self._font.render(f"S: {self._scores[1]}", True, self._foreground_color),
        ]
        blit_sequence = list(zip(text_surfs, self._rects, strict=True))
        surf.blits(blit_sequence, doreturn=0)
        return surf

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf)

    def update_wins(self, player: int, value: int | None = None) -> None:
        i = player - 1
        if value is None:
            self._wins[i] += 1
        else:
            self._wins[i] = value
        j = 2 * i
        self._surf.fill(self._background_color, self._rects[j])
        new_text = self._font.render(f"W: {self._wins[i]}", True, self._foreground_color)
        self._surf.blit(new_text, self._rects[j])

    def update_score(self, player: int, value: int | None = None) -> None:
        i = player - 1
        if value is None:
            self._scores[i] += 1
        else:
            self._scores[i] = value
        j = 2 * i + 1
        self._surf.fill(self._background_color, self._rects[j])
        new_text = self._font.render(f"S: {self._scores[i]}", True, self._foreground_color)
        self._surf.blit(new_text, self._rects[j])
        if self._scores[i] >= MAX_SCORE:
            event = pg.Event(Hud.WIN_EVENT, player=player)
            pg.event.post(event)

    def reset_score(self) -> None:
        self.update_score(1, 0)
        self.update_score(2, 0)


class Arena:
    WIDTH = WINDOW_WIDTH
    BORDER_X = 10
    BORDER_Y = 10

    def __init__(
        self,
        /,
        *,
        height: int,
        y: int,
        rect_height: int = 100,
        color: pg.typing.ColorLike = "white",
    ) -> None:
        self.height = height
        self.pos = (0, y)
        self._vertical_rects = self._get_vertical_rectangles(rect_height)
        self._horizontal_rects = self._get_horizontal_rectangles()
        self._surf = self._get_surface(color)
        self.rects = self._get_collision_rectangles()
        del self._vertical_rects
        del self._horizontal_rects

    def _get_vertical_rectangles(self, height: int) -> list[pg.Rect]:
        x = Arena.WIDTH - Arena.BORDER_X
        y = self.height - height
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
            (Arena.BORDER_X, self.height - Arena.BORDER_Y),
        ]
        size = (Arena.WIDTH - 2 * Arena.BORDER_X, Arena.BORDER_Y)
        return [pg.Rect(position, size) for position in positions]

    def _get_surface(self, color: pg.typing.ColorLike) -> pg.Surface:
        surf = pg.Surface((Arena.WIDTH, self.height))
        vertical_surf = get_colored_surface(self._vertical_rects[0].size, color)
        horizontal_surf = get_colored_surface(self._horizontal_rects[0].size, color)
        blit_sequence = [(vertical_surf, rect) for rect in self._vertical_rects]
        blit_sequence += [(horizontal_surf, rect) for rect in self._horizontal_rects]
        surf.blits(blit_sequence, doreturn=0)
        return surf

    def _get_collision_rectangles(self) -> list[pg.Rect]:
        rects = self._vertical_rects + self._horizontal_rects
        x, y = self.pos
        for rect in rects:
            rect.move_ip(x, y)
        return rects

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self._surf, self.pos)


class Divider:
    def __init__(
        self,
        /,
        *,
        height: int,
        y: int,
        rect_height: int = 4,
        rect_width: int | None = None,
        color: pg.typing.ColorLike = "white",
    ) -> None:
        self._surf = self._get_surface(
            height,
            rect_width if rect_width is not None else rect_height,
            rect_height,
            color,
        )
        self._pos = self._get_surface_position(y)

    def _get_rectangles(self, height: int, rect_width: int, rect_height: int) -> list[pg.Rect]:
        max_rects = height // rect_height
        num_rects = max_rects // 2 if max_rects % 2 == 0 else (max_rects + 1) // 2
        gap_total = height - num_rects * rect_height
        delta_y = rect_height + gap_total // (num_rects - 1)
        r = gap_total % (num_rects - 1)
        rects = [pg.Rect(0, 0, rect_width, rect_height) for _ in range(num_rects)]
        rects[1].y = delta_y + r // 2 if r % 2 == 0 else (r - 1) // 2
        rects[-1].y = height - rect_height
        for i in range(2, num_rects - 1):
            rects[i].y = rects[i - 1].y + delta_y
        return rects

    def _get_surface(
        self,
        height: int,
        rect_width: int,
        rect_height: int,
        color: pg.typing.ColorLike,
    ) -> pg.Surface:
        surf = pg.Surface((rect_width, height))
        rect_surf = get_colored_surface((rect_width, rect_height), color)
        rects = self._get_rectangles(height, rect_width, rect_height)
        blit_sequence = [(rect_surf, rect) for rect in rects]
        surf.blits(blit_sequence, doreturn=0)
        return surf

    def _get_surface_position(self, y: int) -> tuple[int, int]:
        x = (Arena.WIDTH - self._surf.width) // 2
        return x, y

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

    def clear(self, action: Action | None = None) -> None:
        if action is not None:
            self[action] = False
            return
        for i in range(len(self.values)):
            self.values[i] = False


class Paddle:
    OFFSET_X = 2
    OFFSET_Y = 2

    def __init__(
        self,
        /,
        *,
        width: int = 8,
        height: int = 96,
        velocity: int = 6,
        color: pg.typing.ColorLike = "white",
    ) -> None:
        self.rect = pg.Rect(0, 0, width, height)
        self._velocity = velocity
        self._surf = get_colored_surface(self.rect.size, color)

    def set_position(self, side: Side, arena: Arena) -> "Paddle":
        if side == "left":
            x = Arena.BORDER_X + Paddle.OFFSET_X
        else:
            x = Arena.WIDTH - Arena.BORDER_X - Paddle.OFFSET_X - self.rect.width
        y = (arena.height - self.rect.height) // 2
        x += arena.pos[0]
        y += arena.pos[1]
        self.rect.move_ip(x, y)
        self._init_pos = self.rect.topleft
        return self

    def reset(self) -> None:
        self.rect = self.rect.move_to(topleft=self._init_pos)

    def set_y_range(self, arena: Arena) -> "Paddle":
        self._min_y = Arena.BORDER_Y + Paddle.OFFSET_Y
        self._max_y = arena.height - Arena.BORDER_Y - Paddle.OFFSET_Y - self.rect.height
        self._min_y += arena.pos[1]
        self._max_y += arena.pos[1]
        return self

    def update(self, action_buffer: ActionBuffer) -> None:
        if action_buffer[Action.MOVE_DOWN]:
            self.rect.y = min(self.rect.y + self._velocity, self._max_y)
            action_buffer.clear(Action.MOVE_DOWN)
        if action_buffer[Action.MOVE_UP]:
            self.rect.y = max(self.rect.y - self._velocity, self._min_y)
            action_buffer.clear(Action.MOVE_UP)

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
    def __init__(self) -> None:
        self.hud = Hud()
        self.arena = Arena(
            height=WINDOW_HEIGHT - self.hud.height,
            y=self.hud.height,
            color=DARK_BLUE,
        )
        self.divider = Divider(
            height=self.arena.height - 2 * Arena.BORDER_Y,
            y=self.arena.pos[1] + Arena.BORDER_Y,
            color=DARK_BLUE,
        )
        self.paddle_left = (
            Paddle(color=CYAN).set_position("left", self.arena).set_y_range(self.arena)
        )
        self.paddle_right = (
            Paddle(color=FUCHSIA).set_position("right", self.arena).set_y_range(self.arena)
        )
        self.ball = Ball()
        self._action_buffers = [ActionBuffer() for _ in range(len(PLAYER_KEYBINDINGS))]
        self._is_running = False
        self._rects = [*self.arena.rects, self.paddle_left.rect, self.paddle_right.rect]

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
                player = 2 if event.side == "left" else 1
                self.hud.update_score(player)
                self.ball.reset(event.side)
            case Ball.UNFREEZE_EVENT:
                self.ball.unfreeze()
            case Hud.WIN_EVENT:
                self.hud.update_wins(event.player)
                self.hud.reset_score()
                side = "right" if event.player == 1 else "left"
                self.ball.reset(side)
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
        self.hud.render(self.screen)
        self.arena.render(self.screen)
        self.divider.render(self.screen)
        self.paddle_left.render(self.screen)
        self.paddle_right.render(self.screen)
        self.ball.render(self.screen)
        pg.display.flip()


if __name__ == "__main__":
    pg.init()
    game = Game()
    game.run()
    pg.quit()
