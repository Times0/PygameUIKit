import os
from collections.abc import Callable

import pygame as pg
from pygame import Color

from .button import Button
from .label import Label
from .utils import draw_transparent_rect_with_border_radius, load_image

PADDING = 10

cwd = os.path.dirname(__file__)


class ComboBox(Button):
    def __init__(self, elements: list[str], ui_group=None, font=None, font_color=(0, 0, 0)):
        if not elements:
            raise ValueError("ComboBox requires at least one element")
        super().__init__(
            elements[0],
            self.toggle_open,
            color="white",
            text_color=font_color,
            border_radius=5,
            padding=(PADDING, PADDING),
            font=font,
            align="left",
            ui_group=ui_group,
        )
        self.font = self.label.font
        self.elements = elements
        self.selected_index = 0
        self.hovered_index = self.selected_index
        self.is_open = False
        self._labels: list[Label] = []
        self.actions: dict[int, Callable[[], None]] = {}

        self.img_arrow_down = load_image(
            os.path.join(cwd, "assets", "combo_box_arrow.png"), (20, 20)
        )
        self.img_arrow_down.fill((0, 0, 0, 255), special_flags=pg.BLEND_RGBA_MULT)
        self._pressed_index = None
        self.img_arrow_up = pg.transform.rotate(self.img_arrow_down.copy(), 180)

        self.width = max(200, max(self.font.size(text)[0] for text in elements) + 50)
        self._resize()
        self._render_elements()

    def _render_elements(self):
        self._labels.clear()
        for element in self.elements:
            self._labels.append(Label(element, "white", font=self.font))

    def draw(self, screen, x, y):
        super().draw(screen, x, y)
        img = self.img_arrow_up if self.is_open else self.img_arrow_down
        arrow_y = y + (self.rect.h - img.get_height()) // 2
        screen.blit(img, (x + self.rect.w - img.get_width() - PADDING, arrow_y))

        if self.is_open:
            height = self.rect.h * len(self.elements)
            draw_transparent_rect_with_border_radius(
                screen, Color("black"), pg.Rect(x, y + self.rect.h, self.rect.w, height), 5, 200
            )
            for i in range(len(self.elements)):
                if i == self.hovered_index or i == self.selected_index:
                    draw_transparent_rect_with_border_radius(
                        screen,
                        Color("white"),
                        pg.Rect(x, y + self.rect.h * (i + 1), self.rect.w, self.rect.h).inflate(
                            -PADDING, -PADDING
                        ),
                        border_radius=5,
                        alpha=100,
                    )
                label_y = y + self.rect.h * (i + 1) + PADDING
                self._labels[i].draw(screen, x + PADDING, label_y)

    @property
    def event_priority(self):
        return int(self.is_open)

    def _option_at(self, pos):
        menu = pg.Rect(self.rect.x, self.rect.bottom, self.rect.w, self.rect.h * len(self.elements))
        if menu.collidepoint(pos):
            return (pos[1] - menu.y) // self.rect.h
        return None

    def handle_event(self, event):
        if event.type == pg.WINDOWFOCUSLOST or (
            event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE
        ):
            self.is_open = False
            self._pressed_index = None
            self.pressed = False
        if self.is_open and event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP, pg.MOUSEMOTION):
            index = self._option_at(event.pos)
            if event.type == pg.MOUSEMOTION:
                self.change_hovered(index)
                if index is not None:
                    return True
            elif event.button == 1:
                if event.type == pg.MOUSEBUTTONDOWN:
                    self._pressed_index = index
                    if index is not None:
                        return True
                    if not self.rect.collidepoint(event.pos):
                        self.is_open = False
                else:
                    pressed = self._pressed_index
                    self._pressed_index = None
                    if index is not None:
                        self.is_open = False
                        if index == pressed:
                            self.change_selected(index)
                        return True
                    if not self.rect.collidepoint(event.pos):
                        self.is_open = False
            elif index is not None:
                return True
        return super().handle_event(event)

    def change_selected(self, index):
        if not 0 <= index < len(self.elements):
            raise IndexError("ComboBox index out of range")
        self.selected_index = index
        self.hovered_index = index
        self.text = self.elements[self.selected_index]
        self._render_elements()
        if index in self.actions:
            self.actions[index]()

    def toggle_open(self):
        self.is_open = not self.is_open
        if self.is_open:
            self._render_elements()

    def add_action(self, index, action):
        self.actions[index] = action

    def get_value(self) -> str:
        return self.elements[self.selected_index]

    def change_hovered(self, i):
        if i != self.hovered_index:
            self.hovered_index = i
            self._render_elements()
