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
        self.text = text
        self.color = color
        self._rendered: tuple[str, pg.Color] | None = None
        super().__init__(ui_group=ui_group)
        self.rect = self.surface.get_rect()

    @property
    def color(self) -> pg.Color:
        return self._color

    @color.setter
    def color(self, value: ColorLike) -> None:
        self._color = pg.Color(value)

    @property
    def surface(self) -> pg.Surface:
        """The rendered text; re-rendered only when ``text``, ``color`` or ``enabled`` change."""
        key = (self.text, self._paint(self._color))
        if key != self._rendered:
            self._surface = self.font.render(key[0], True, key[1])
            self._rendered = key
        return self._surface

    def draw(self, surface: pg.Surface, x: int, y: int, width: int | None = None) -> None:
        text = self.surface
        text_width, height = text.get_size()
        width = text_width if width is None else width
        self.rect = pg.Rect(x, y, width, height)
        offset = {"left": 0, "center": (width - text_width) // 2, "right": width - text_width}
        surface.blit(text, (x + offset[self.align], y))
