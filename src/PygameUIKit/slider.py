import pygame
from pygame import Color

from .super_object import EasyObject

COLOR_COMPLETED = Color(132, 214, 80)
COLOR_IN_PROGRESS = Color(200, 200, 200)

COLOR_CIRCLE1 = Color(241, 241, 241)
COLOR_CIRCLE2 = COLOR_IN_PROGRESS


class Slider(EasyObject):
    def __init__(self, min, max, step, show_value=False, font_color=Color("black"), ui_group=None):
        super().__init__(ui_group=ui_group)
        self.min = min
        self.max = max
        self.step = step
        self.current_value = min
        self.show_value = show_value
        # ui
        self.circle_radius = 10
        self.rect = pygame.Rect(0, 0, 100, self.circle_radius / 2)
        self.dragging = False
        self.font_color = font_color

        self.on_change = lambda: None

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.inflate(self.circle_radius + 10, self.circle_radius + 10).collidepoint(event.pos):
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if not self.hovered and self.rect.inflate(self.circle_radius + 10, self.circle_radius + 10).collidepoint(
                    event.pos):
                self.on_hover()
            elif self.hovered and not self.rect.inflate(self.circle_radius + 10,
                                                        self.circle_radius + 10).collidepoint(event.pos):
                self.on_unhover()
            if self.dragging:
                x, y = event.pos
                v = self.min + (x - self.rect.x) / self.rect.w * (self.max - self.min)
                v = round(v / self.step) * self.step
                v = max(self.min, min(self.max, v))
                self.change_value_to(v)

    def change_value_to(self, value):
        if value != self.current_value:
            self.current_value = value
            self.on_change()

    def draw_bar(self, win):
        """ Draws the completed part and the in progress part of the slider """
        # Draw the completed part
        pygame.draw.rect(win, COLOR_COMPLETED,
                         (self.rect.x, self.rect.y, self.rect.w * (self.current_value / self.max), self.rect.h))
        # Draw the in progress part
        pygame.draw.rect(win, COLOR_IN_PROGRESS,
                         (self.rect.x + self.rect.w * (self.current_value / self.max), self.rect.y,
                          self.rect.w * ((self.max - self.current_value) / self.max), self.rect.h))

    def draw_circle(self, win):

        # Draw the circle
        value_pos = self.rect.x + self.rect.w * (self.current_value / self.max)
        y = self.rect.y + self.rect.h // 2

        rad_size = self.circle_radius if not self.dragging else 15
        pygame.draw.circle(win, COLOR_CIRCLE1, (value_pos, y), rad_size)
        pygame.draw.circle(win, COLOR_CIRCLE2, (value_pos, y), rad_size - 2)

    def draw(self, win, x, y, w, h):
        self.rect = pygame.Rect(x, y, w, h)
        self.draw_bar(win)
        self.draw_circle(win)
        if self.show_value:
            text = self.font.render(str(self.current_value), True, self.font_color)
            win.blit(text, (x + w + 10, y + h // 2 - text.get_height() // 2))

    def get_value(self):
        return self.current_value

    def connect(self, f, when="on_change", ):
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