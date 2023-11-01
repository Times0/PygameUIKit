import pygame as pg
from pygame import Color, Rect
import seaborn as sns

from .super_object import EasyObject
from .utilis import draw_transparent_rect_with_border_radius

CHANGE_SPEED = 200
SPACE_BETWEEN_BARS = 2


def color_from_float(colors):
    new_colors = []
    for color in colors:
        new_colors.append(Color(int(color[0] * 255), int(color[1] * 255), int(color[2] * 255)))
    return new_colors


class BarChart(EasyObject):
    def __init__(self, values: list[int],
                 labels: list[str] = None,
                 max_value=None,
                 ui_group=None,
                 labels_color=pg.Color("black")):
        super().__init__(ui_group=ui_group)
        self.values = values[:]
        self.max_value = max_value
        self.rect = pg.Rect(0, 0, 0, 0)
        self.labels_color = labels_color
        self.labels = labels
        self.values_displayed = self.values[:]


        self.colors = sns.color_palette("husl", len(self.values))
        self.colors = color_from_float(self.colors)

    def change_value(self, index, value):
        self.values[index] = value

    def update(self, dt):
        for i, value in enumerate(self.values):
            if abs(self.values_displayed[i] - value) < CHANGE_SPEED * dt:
                self.values_displayed[i] = value
                continue
            if self.values_displayed[i] < value:
                self.values_displayed[i] += CHANGE_SPEED * dt
            else:
                self.values_displayed[i] -= CHANGE_SPEED * dt

    def draw_bar(self, screen, index, color=pg.Color("black")):
        x, y, width, height = self.rect
        bar_width = width / len(self.values)
        if self.max_value is None:
            max_height = max(self.values)
        else:
            max_height = self.max_value
        bar_height = self.values_displayed[index] / max_height * height
        bar_x = x + index * bar_width
        bar_y = y + height - bar_height

        alpha = max(255 * (self.values_displayed[index] / max_height), 50)
        draw_transparent_rect_with_border_radius(screen, color,
                                                 Rect(bar_x + SPACE_BETWEEN_BARS,
                                                      bar_y,
                                                      bar_width - 2 * SPACE_BETWEEN_BARS,
                                                      bar_height),
                                                 0,
                                                 alpha)

    def draw_labels(self, screen):
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

    def draw(self, screen, x, y, width, height):
        self.rect = pg.Rect(x, y, width, height)
        for i, value in enumerate(self.values_displayed):
            self.draw_bar(screen, i, color=self.colors[i])
        self.draw_labels(screen)
