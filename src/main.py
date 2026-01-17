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
        self.rendered = False
        self.vertical_surf = self._get_vertical_surface()
        self.horizontal_surf = self._get_horizontal_surface()
        self.vertical_rects = self._get_vertical_rectangles()
        self.horizontal_rects = self._get_horizontal_rectangles()

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

    def render(self, screen: pg.Surface) -> None:
        if self.rendered:
            return
        for rect in self.vertical_rects:
            screen.blit(self.vertical_surf, rect)
            pg.display.update(rect)
        for rect in self.horizontal_rects:
            screen.blit(self.horizontal_surf, rect)
            pg.display.update(rect)
        self.rendered = True


pg.init()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Pong")
arena = Arena(
    border_width=ARENA_BORDER_WIDTH,
    gap_length=12 * 30,
    border_color=DARK_BLUE,
)

is_running = True
while is_running:
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                is_running = False
            case _:
                pass
    # update
    arena.render(screen)

pg.quit()
