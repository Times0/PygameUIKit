from enum import Enum

import pygame as pg

from .super_object import EasyObject, get_font

DEFAULT_FONT = None  # Kept for callers that imported the old default; resolved lazily.


class TextAlignment(Enum):
    LEFT = "left"
    RIGHT = "right"
    CENTER = "center"


class Label(EasyObject):
    def __init__(
        self,
        text,
        font_color,
        font=DEFAULT_FONT,
        text_align=TextAlignment.LEFT,
        bounding_rect=None,
        ui_group=None,
    ):
        super().__init__(ui_group=ui_group)
        self.bounds = bounding_rect  # Used only when centering the text
        self._text = text
        self.font_color = font_color
        self.font = font if font is not None else get_font()
        self.text_surface: pg.Surface | None = None
        self.rect: pg.Rect | None = None
        self.text_align = TextAlignment(text_align or TextAlignment.LEFT)
        if self.text_align != TextAlignment.LEFT and self.bounds is None:
            raise ValueError("Center and right alignment require a bounding_rect")
        self.render_text()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        if self._text != value:
            self._text = value
            self.render_text()

    def draw(self, screen, x, y):
        if self.text_align == TextAlignment.LEFT or self.text_align == TextAlignment.LEFT.value:
            xx, yy = x + 10, y + 10
        elif self.text_align == TextAlignment.RIGHT or self.text_align == TextAlignment.RIGHT.value:
            xx, yy = x + self.bounds.w - self.text_surface.get_width() - 10, y + 10
        elif (
            self.text_align == TextAlignment.CENTER or self.text_align == TextAlignment.CENTER.value
        ):
            xx, yy = x + self.bounds.w // 2 - self.text_surface.get_width() // 2, y + 10
        else:
            raise ValueError(f"Unknown text alignment {self.text_align}")
        self.rect.topleft = (xx, yy)
        screen.blit(self.text_surface, self.rect)

    def render_text(self):
        self.text_surface = self.font.render(self.text, True, self.font_color)
        position = self.rect.topleft if self.rect is not None else (0, 0)
        self.rect = self.text_surface.get_rect(topleft=position)
