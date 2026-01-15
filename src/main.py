import pygame as pg

WINDOW_WIDTH = 12 * 67
WINDOW_HEIGHT = 12 * 50

pg.init()

screen = pg.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pg.display.set_caption("Pong")

is_running = True
while is_running:
    for event in pg.event.get():
        match event.type:
            case pg.QUIT:
                is_running = False
            case _:
                pass
    # update
    # render

pg.quit()
