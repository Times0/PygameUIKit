import math

import pygame as pg
from pygame.typing import ColorLike

from . import utils
from .widget import Group, Widget

TEXT_GAP = 8


class ProgressBar(Widget):
    """A horizontal bar filled to ``value / max_value``; it only displays, never takes input.

    ``loading = ProgressBar(max_value=total, show_text=True)``; set ``loading.value = done``
    and call ``loading.draw(screen, x, y, width=200, height=12)`` every frame. ``value`` is
    clamped to 0..``max_value``; ``show_text`` prints the percentage right of the bar.
    """

    def __init__(
        self,
        value: float = 0.0,
        *,
        max_value: float = 1.0,
        color: ColorLike = (59, 130, 246),
        track_color: ColorLike = (220, 223, 228),
        border_radius: int | None = None,
        show_text: bool = False,
        font: pg.font.Font | None = None,
        text_color: ColorLike = "black",
        ui_group: Group | None = None,
    ):
        if not math.isfinite(max_value) or max_value <= 0:
            raise ValueError("max_value must be finite and positive")
        if border_radius is not None and border_radius < 0:
            raise ValueError("border_radius must not be negative")
        self.max_value = max_value
        self.value = value
        self.color = pg.Color(color)
        self.track_color = pg.Color(track_color)
        self.border_radius = border_radius
        self.show_text = show_text
        self.font = font if font is not None else utils.get_font(24)
        self.text_color = pg.Color(text_color)
        super().__init__(ui_group=ui_group)
        self.rect = pg.Rect(0, 0, 200, 12)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        if not math.isfinite(value):
            raise ValueError("ProgressBar value must be finite")
        self._value = max(0, min(self.max_value, value))

    @property
    def fraction(self) -> float:
        """How full the bar is, from 0 to 1."""
        return min(1.0, self._value / self.max_value)

    @property
    def percent_text(self) -> str:
        """The percentage shown by ``show_text``, such as ``"42%"``."""
        return f"{self.fraction:.0%}"

    def draw(self, surface: pg.Surface, x: int, y: int, width: int = 200, height: int = 12) -> None:
        if not self.visible:
            return
        if width <= 0 or height <= 0:
            raise ValueError("ProgressBar dimensions must be positive")
        self.rect = pg.Rect(x, y, width, height)
        radius = height // 2 if self.border_radius is None else self.border_radius
        utils.draw_rounded_rect(surface, self._paint(self.track_color), self.rect, radius)
        filled = pg.Rect(x, y, round(width * self.fraction), height)
        if filled.w:
            # Draw the whole track shape clipped to the filled part, so even a sliver keeps
            # the track's rounded left end.
            clip = surface.get_clip()
            surface.set_clip(filled.clip(clip))
            utils.draw_rounded_rect(surface, self._paint(self.color), self.rect, radius)
            surface.set_clip(clip)
        if self.show_text:
            text = self.font.render(self.percent_text, True, self._paint(self.text_color))
            surface.blit(
                text, text.get_rect(midleft=(self.rect.right + TEXT_GAP, self.rect.centery))
            )
