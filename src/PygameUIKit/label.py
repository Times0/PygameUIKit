import pygame as pg
from pygame.typing import ColorLike

from .utils import get_font
from .widget import Group, Widget

ALIGNMENTS = ("left", "center", "right")


def _check_align(align: str) -> str:
    if align not in ALIGNMENTS:
        raise ValueError(f"align must be one of {ALIGNMENTS}, not {align!r}")
    return align


class Label(Widget):
    """A line of text drawn with its top-left corner at (x, y).

    ``score = Label("Score: 0")``; ``score.draw(screen, 10, 10)`` every frame. Set ``score.text``
    to change it. With ``draw(..., width=w)`` the text is aligned within ``w`` pixels.
    """

    def __init__(
        self,
        text: str,
        color: ColorLike = "black",
        *,
        font: pg.font.Font | None = None,
        align: str = "left",
        ui_group: Group | None = None,
    ):
        self.align = _check_align(align)
        self.font = font if font is not None else get_font()
        self._text = text
        self._color = pg.Color(color)
        self.surface = self.font.render(text, True, self._color)
        super().__init__(ui_group=ui_group)
        self.rect = self.surface.get_rect()

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        if value != self._text:
            self.surface = self.font.render(value, True, self._color)
            self._text = value

    @property
    def color(self) -> pg.Color:
        return self._color

    @color.setter
    def color(self, value: ColorLike) -> None:
        value = pg.Color(value)
        if value != self._color:
            self._color = value
            self.surface = self.font.render(self._text, True, value)

    def draw(self, surface: pg.Surface, x: int, y: int, width: int | None = None) -> None:
        text_width, height = self.surface.get_size()
        width = text_width if width is None else width
        self.rect = pg.Rect(x, y, width, height)
        offset = {"left": 0, "center": (width - text_width) // 2, "right": width - text_width}
        surface.blit(self.surface, (x + offset[self.align], y))
