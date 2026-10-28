from collections.abc import Sequence
from colorsys import hsv_to_rgb
from math import copysign, isfinite

import pygame as pg
from pygame.typing import ColorLike

from . import utils
from .widget import Group, Widget

BAR_GAP = 4
LABEL_GAP = 4


def _check_values(values: Sequence[float]) -> list[float]:
    if any(not isfinite(value) or value < 0 for value in values):
        raise ValueError("Bar values must be finite and non-negative")
    return list(values)


def _palette(count: int) -> list[pg.Color]:
    return [
        pg.Color([round(c * 255) for c in hsv_to_rgb(i / count, 0.55, 0.85)]) for i in range(count)
    ]


class BarChart(Widget):
    """Bars that grow and shrink toward their values, with a label under each bar.

    ``chart = BarChart([3, 5, 2], labels=["A", "B", "C"], max_value=10, ui_group=ui)``; call
    ``chart.set_value(1, 8)`` or set ``chart.values``, ``ui.update(dt)`` to animate and
    ``chart.draw(screen, x, y, width=300, height=100)`` every frame. Without ``labels`` the
    bars show their values; without ``max_value`` the tallest bar fills the height.
    """

    def __init__(
        self,
        values: Sequence[float],
        *,
        labels: Sequence[str] | None = None,
        max_value: float | None = None,
        colors: Sequence[ColorLike] | None = None,
        font: pg.font.Font | None = None,
        label_color: ColorLike = "black",
        speed: float = 200,
        ui_group: Group | None = None,
    ):
        values = _check_values(values)
        if labels is not None and len(labels) != len(values):
            raise ValueError("labels must have the same length as values")
        if colors is not None and len(colors) == 0:
            raise ValueError("colors must not be empty")
        if max_value is not None and (not isfinite(max_value) or max_value <= 0):
            raise ValueError("max_value must be finite and positive")
        if not isfinite(speed) or speed <= 0:
            raise ValueError("speed must be finite and positive")
        self._values = values
        self.values_displayed = values[:]
        self.labels = labels
        self.max_value = max_value
        self._auto_colors = colors is None
        self.colors = _palette(len(values)) if colors is None else [pg.Color(c) for c in colors]
        self.font = font if font is not None else utils.get_font(18)
        self.label_color = pg.Color(label_color)
        self.speed = speed
        super().__init__(ui_group=ui_group)

    @property
    def values(self) -> tuple[float, ...]:
        return tuple(self._values)

    @values.setter
    def values(self, values: Sequence[float]) -> None:
        values = _check_values(values)
        shown = self.values_displayed[: len(values)]
        self.values_displayed = shown + [0] * (len(values) - len(shown))
        if self._auto_colors and len(values) != len(self._values):
            self.colors = _palette(len(values))
        self._values = values

    def set_value(self, index: int, value: float) -> None:
        self._values[index] = _check_values([value])[0]

    def update(self, dt: float) -> None:
        change = self.speed * max(0, dt)
        for i, target in enumerate(self._values):
            difference = target - self.values_displayed[i]
            if abs(difference) <= change:
                self.values_displayed[i] = target
            else:
                self.values_displayed[i] += copysign(change, difference)

    def draw(
        self, surface: pg.Surface, x: int, y: int, width: int = 300, height: int = 100
    ) -> None:
        if width < 0 or height < 0:
            raise ValueError("Chart dimensions must be non-negative")
        self.rect = pg.Rect(x, y, width, height)
        if not self._values:
            return
        scale = self.max_value or max(1, *self._values, *self.values_displayed)
        slot = width / len(self._values)
        labels = self.labels
        if labels is None:
            labels = [f"{value:.0f}" for value in self.values_displayed]
        for i, shown in enumerate(self.values_displayed):
            bar_height = round(min(1, shown / scale) * height)
            left = round(x + i * slot + BAR_GAP / 2)
            bar = pg.Rect(left, y + height - bar_height, max(0, round(slot - BAR_GAP)), bar_height)
            color = self.colors[i % len(self.colors)]
            pg.draw.rect(surface, color, bar, border_top_left_radius=3, border_top_right_radius=3)
            if i < len(labels):
                text = self.font.render(labels[i], True, self.label_color)
                center = round(x + (i + 0.5) * slot)
                surface.blit(text, text.get_rect(midtop=(center, y + height + LABEL_GAP)))
