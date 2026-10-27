import math

import pygame
from pygame import Color

from .label import DEFAULT_FONT
from .super_object import EasyObject, get_font

COLOR_COMPLETED = Color(132, 214, 80)
COLOR_IN_PROGRESS = Color(200, 200, 200)

COLOR_CIRCLE1 = Color(241, 241, 241)
COLOR_CIRCLE2 = COLOR_IN_PROGRESS


class Slider(EasyObject):
    def __init__(
        self,
        min,
        max,
        step,
        show_value=False,
        font=DEFAULT_FONT,
        font_color=(0, 0, 0),
        ui_group=None,
    ):
        super().__init__(ui_group=ui_group)
        if not all(math.isfinite(v) for v in (min, max, step)) or max <= min or step <= 0:
            raise ValueError("Slider requires finite min < max and step > 0")
        self.min = min
        self.max = max

        self.step = step
        self.current_value = min
        self.show_value = show_value
        # ui
        self.circle_radius = 10
        self.rect = pygame.Rect(0, 0, 100, self.circle_radius / 2)
        self.dragging = False
        self.font = font if font is not None else get_font()
        self.font_color = font_color

        self.on_change = lambda: None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.inflate(self.circle_radius + 10, self.circle_radius + 10).collidepoint(
                event.pos
            ):
                self.dragging = True
                self._value_from_position(event.pos[0])
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging:
                self._value_from_position(event.pos[0])
            self.dragging = False
        elif event.type == pygame.WINDOWFOCUSLOST:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if not self.hovered and self.rect.inflate(
                self.circle_radius + 10, self.circle_radius + 10
            ).collidepoint(event.pos):
                self.on_hover()
            elif self.hovered and not self.rect.inflate(
                self.circle_radius + 10, self.circle_radius + 10
            ).collidepoint(event.pos):
                self.on_unhover()
            if self.dragging:
                self._value_from_position(event.pos[0])

    def _value_from_position(self, x):
        if self.rect.w > 0:
            self.change_value_to(self.min + (x - self.rect.x) / self.rect.w * (self.max - self.min))

    @property
    def fraction(self):
        return (self.current_value - self.min) / (self.max - self.min)

    def change_value_to(self, value):
        if not math.isfinite(value):
            raise ValueError("Slider value must be finite")
        value = max(self.min, min(self.max, value))
        if value not in (self.min, self.max):
            value = self.min + round((value - self.min) / self.step) * self.step
            value = max(self.min, min(self.max, value))
        if value != self.current_value:
            self.current_value = value
            self.on_change()

    def draw_bar(self, win):
        """Draws the completed part and the in progress part of the slider"""
        # Draw the completed part
        pygame.draw.rect(
            win,
            COLOR_COMPLETED,
            (self.rect.x, self.rect.y, self.rect.w * self.fraction, self.rect.h),
        )
        # Draw the in progress part
        pygame.draw.rect(
            win,
            COLOR_IN_PROGRESS,
            (
                self.rect.x + self.rect.w * self.fraction,
                self.rect.y,
                self.rect.w * (1 - self.fraction),
                self.rect.h,
            ),
        )

    def draw_circle(self, win):

        # Draw the circle
        value_pos = self.rect.x + self.rect.w * self.fraction
        y = self.rect.y + self.rect.h // 2

        rad_size = self.circle_radius if not self.dragging else 15
        pygame.draw.circle(win, COLOR_CIRCLE1, (value_pos, y), rad_size)
        pygame.draw.circle(win, COLOR_CIRCLE2, (value_pos, y), rad_size - 2)

    def draw_value(self, win):
        x, y, w, h = self.rect

        if "." in str(self.current_value):
            value = round(self.current_value, 2)
        else:
            value = int(self.current_value)

        text = self.font.render(str(value), True, self.font_color)
        win.blit(text, (x + w + 10, y + h // 2 - text.get_height() // 2))

    def draw(self, win, x, y, w=100, h=5):
        if w <= 0 or h <= 0:
            raise ValueError("Slider dimensions must be positive")
        self.rect = pygame.Rect(x, y, w, h)
        self.draw_bar(win)
        self.draw_circle(win)
        if self.show_value:
            self.draw_value(win)

    def get_value(self):
        return self.current_value

    def connect(
        self,
        f,
        when="on_change",
    ):
        """
        Connect a function to the slider events
        :param f: function to call when the WHEN event is triggered
        :param when: "on_change" only atm
        """
        if when == "on_change":
            self.on_change = f

    def on_hover(self):
        self.hovered = True
        self.circle_radius = 12

    def on_unhover(self):
        self.hovered = False
        self.circle_radius = 10
