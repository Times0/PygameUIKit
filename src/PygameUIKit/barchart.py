from colorsys import hsv_to_rgb
from math import isfinite

import pygame as pg
from pygame import Color, Rect

from .utils import draw_transparent_rect_with_border_radius, get_font
from .widget import Widget

CHANGE_SPEED = 200
SPACE_BETWEEN_BARS = 2


def color_from_float(colors):
    new_colors = []
    for color in colors:
        new_colors.append(Color(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)))
    return new_colors


class BarChart(Widget):
    """Animated bars: ``BarChart([10, 20]).draw(surface, x, y, width, height)``."""

    def __init__(
        self,
        values: list[int],
        labels: list[str] = None,
        max_value=None,
        ui_group=None,
        font=None,
        labels_color=(0, 0, 0),
    ):
        super().__init__(ui_group=ui_group)
        if any(not isfinite(v) or v < 0 for v in values):
            raise ValueError("Bar values must be finite and non-negative")
        if max_value is not None and (not isfinite(max_value) or max_value <= 0):
            raise ValueError("max_value must be finite and positive")
        if labels is not None and len(labels) != len(values):
            raise ValueError("labels must have the same length as values")
        self.values = values[:]
        self.max_value = max_value
        self.rect = pg.Rect(0, 0, 0, 0)
        self.labels_color = labels_color
        self.labels = labels
        self.values_displayed = self.values[:]

        self.font = font if font is not None else get_font(15)
        self.colors = [hsv_to_rgb(i / len(values), 0.55, 0.85) for i in range(len(values))]
        self.colors = color_from_float(self.colors)

    def change_value(self, index, value):
        if not isfinite(value) or value < 0:
            raise ValueError("Bar values must be finite and non-negative")
        self.values[index] = value

    def update(self, dt):
        dt = max(0, dt)
        for i, value in enumerate(self.values):
            if abs(self.values_displayed[i] - value) < CHANGE_SPEED * dt:
                self.values_displayed[i] = value
                continue
            if self.values_displayed[i] < value:
                self.values_displayed[i] += CHANGE_SPEED * dt
            else:
                self.values_displayed[i] -= CHANGE_SPEED * dt

    def draw_bar(self, screen, index, color=(0, 0, 0)):
        x, y, width, height = self.rect
        bar_width = width / len(self.values)
        if self.max_value is None:
            max_height = max(1, *self.values, *self.values_displayed)
        else:
            max_height = self.max_value
        fraction = min(1, self.values_displayed[index] / max_height)
        bar_height = fraction * height
        bar_x = x + index * bar_width
        bar_y = y + height - bar_height

        alpha = int(max(255 * fraction, 50))
        draw_transparent_rect_with_border_radius(
            screen,
            color,
            Rect(
                bar_x + SPACE_BETWEEN_BARS,
                bar_y,
                max(0, bar_width - 2 * SPACE_BETWEEN_BARS),
                bar_height,
            ),
            0,
            alpha,
        )

    def draw_labels(self, screen):
        if not self.values:
            return
        x, y, width, height = self.rect
        bar_width = width / len(self.values)
        font = self.font

        labels = self.labels
        if labels is None:
            labels = [f"{v:.0f}" for v in self.values_displayed]
        for i, text in enumerate(labels):
            botmid_bar = (x + i * bar_width + bar_width // 2, y + height)
            text = font.render(text, True, self.labels_color)
            screen.blit(text, text.get_rect(midtop=botmid_bar))

    def draw(self, screen, x, y, width=300, height=100):
        if width < 0 or height < 0:
            raise ValueError("Chart dimensions must be non-negative")
        self.rect = pg.Rect(x, y, width, height)
        for i in range(len(self.values_displayed)):
            self.draw_bar(screen, i, color=self.colors[i])
        self.draw_labels(screen)
