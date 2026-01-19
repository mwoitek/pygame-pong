from enum import IntEnum

import pygame as pg

type number = int | float

WINDOW_WIDTH = 12 * 67
WINDOW_HEIGHT = 12 * 51

FPS = 60
MAX_FRAME_TIME = 0.25

BORDER_WIDTH = 12
PADDLE_WIDTH = 8
PADDLE_HEIGHT = 12 * 10
PADDLE_OFFSET = 4
PADDLE_VELOCITY = 12 * 39 / 1.5

CYAN = pg.Color(91, 200, 175)
DARK_BLUE = pg.Color(32, 32, 96)
FUCHSIA = pg.Color(176, 48, 176)


class Arena:
    def __init__(
        self,
        /,
        *,
        gap_length: int,
        border_width: int = BORDER_WIDTH,
        border_color: pg.typing.ColorLike = "white",
    ) -> None:
        self.gap_length = gap_length
        self.border_width = border_width
        self.border_color = border_color
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

    def _get_vertical_blit_sequence(self) -> list[tuple[pg.Surface, pg.Rect]]:
        vertical_surf = self._get_vertical_surface()
        x = WINDOW_WIDTH - self.border_width
        y = vertical_surf.height + self.gap_length
        positions = [
            (0, 0),
            (0, y),
            (x, 0),
            (x, y),
        ]
        size = vertical_surf.size
        return [(vertical_surf, pg.Rect(position, size)) for position in positions]

    def _get_horizontal_blit_sequence(self) -> list[tuple[pg.Surface, pg.Rect]]:
        horizontal_surf = self._get_horizontal_surface()
        positions = [
            (self.border_width, 0),
            (self.border_width, WINDOW_HEIGHT - self.border_width),
        ]
        size = horizontal_surf.size
        return [(horizontal_surf, pg.Rect(position, size)) for position in positions]

    def _get_surface(self) -> pg.Surface:
        surf = pg.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        blit_sequence = self._get_vertical_blit_sequence()
        blit_sequence.extend(self._get_horizontal_blit_sequence())
        surf.blits(blit_sequence, doreturn=0)
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
        num_rects = (WINDOW_HEIGHT - 2 * BORDER_WIDTH + self.gap_length) // delta_y
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
            ((WINDOW_WIDTH - self.square_side) // 2, BORDER_WIDTH),
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
        width: float = PADDLE_WIDTH,
        height: float = PADDLE_HEIGHT,
        velocity: float = PADDLE_VELOCITY,
        color: pg.typing.ColorLike = "white",
    ) -> None:
        self.rect = pg.FRect(x, y, width, height)
        self.velocity = velocity
        self.color = color
        self.max_y = WINDOW_HEIGHT - BORDER_WIDTH - height
        self.surf = self._get_surface()

    def _get_surface(self) -> pg.Surface:
        surf = pg.Surface(self.rect.size)
        surf.fill(self.color)
        return surf

    def update(self, action_buffer: ActionBuffer, dt: float) -> None:
        y = self.rect.y
        if action_buffer[Action.MOVE_DOWN]:
            y += self.velocity * dt
            y = min(y, self.max_y)
            action_buffer[Action.MOVE_DOWN] = False
        if action_buffer[Action.MOVE_UP]:
            y -= self.velocity * dt
            y = max(y, BORDER_WIDTH)
            action_buffer[Action.MOVE_UP] = False
        self.rect.y = y

    def render(self, screen: pg.Surface) -> None:
        screen.blit(self.surf, self.rect)


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


def poll_inputs(action_buffers: list[ActionBuffer]) -> None:
    keys = pg.key.get_pressed()
    for action_buffer, bindings in zip(action_buffers, PLAYER_KEYBINDINGS, strict=True):
        for action, key in bindings.items():
            if keys[key]:
                action_buffer[action] = True


pg.init()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Pong")

arena = Arena(
    border_width=BORDER_WIDTH,
    gap_length=12 * 30,
    border_color=DARK_BLUE,
)
divider = Divider(square_side=4, color=DARK_BLUE)
paddle_left = Paddle(
    x=BORDER_WIDTH + PADDLE_OFFSET,
    y=(WINDOW_HEIGHT - PADDLE_HEIGHT) // 2,
    color=CYAN,
)
paddle_right = Paddle(
    x=WINDOW_WIDTH - BORDER_WIDTH - PADDLE_OFFSET - PADDLE_WIDTH,
    y=(WINDOW_HEIGHT - PADDLE_HEIGHT) // 2,
    color=FUCHSIA,
)
action_buffers = [ActionBuffer(), ActionBuffer()]

dt = 1 / FPS
time_acc = 0
clock = pg.time.Clock()

is_running = True
while is_running:
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                is_running = False
            case _:
                pass
    poll_inputs(action_buffers)

    frame_time = min(clock.tick() / 1e3, MAX_FRAME_TIME)
    time_acc += frame_time
    if time_acc >= dt:
        paddle_left.update(action_buffers[0], dt)
        paddle_right.update(action_buffers[1], dt)
        time_acc -= dt

    screen.fill("black")
    arena.render(screen)
    divider.render(screen)
    paddle_left.render(screen)
    paddle_right.render(screen)
    pg.display.flip()

pg.quit()
