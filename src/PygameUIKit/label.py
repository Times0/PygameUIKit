from enum import Enum

import pygame as pg

from .super_object import EasyObject

DEFAULT_FONT = pg.font.SysFont(None, 30)  # Leads to bugs https://github.com/pygame/pygame/issues/2971


class TextAlignment(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class Label(EasyObject):
    def __init__(self, text, font_color, font=DEFAULT_FONT, text_align=TextAlignment.LEFT, bounding_rect=None):
        super().__init__()
        self.bounds = bounding_rect  # Used only when centering the text
        self.text = text
        self.font_color = font_color
        self.font = font or DEFAULT_FONT
        self.text_surface: pg.Surface | None = None
        self.rect: pg.Rect | None = None
        self.text_align: TextAlignment = text_align or TextAlignment.LEFT
        self.render_text()

    def draw(self, screen, x, y):
        if self.text_align == TextAlignment.LEFT or self.text_align == TextAlignment.LEFT.value:
            xx, yy = x + 10, y + 10
        elif self.text_align == TextAlignment.RIGHT or self.text_align == TextAlignment.RIGHT.value:
            xx, yy = x + self.bounds.w - self.text_surface.get_width() - 10, y
        elif self.text_align == TextAlignment.CENTER or self.text_align == TextAlignment.CENTER.value:
            xx, yy = x + self.bounds.w // 2 - self.text_surface.get_width() // 2, y + 10
        else:
            raise ValueError(f"Unknown text alignment {self.text_align}")
        screen.blit(self.text_surface, (xx, yy))

    def render_text(self):
        self.text_surface = self.font.render(self.text, True, self.font_color)
        self.rect = self.text_surface.get_rect()
