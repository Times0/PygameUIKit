import os

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame as pg
import pytest


@pytest.fixture(autouse=True)
def display():
    pg.init()
    surface = pg.display.set_mode((800, 600))
    yield surface
    pg.quit()
