import os

import pygame.draw
from pygame import Color
import pygame as pg

from .button import ButtonText
from .utilis import draw_transparent_rect_with_border_radius, best_contrast_color

PADDING = 10

cwd = os.path.dirname(__file__)
img_arrow_down = pg.image.load(os.path.join(cwd, "assets", "combo_box_arrow.png"))
img_arrow_down = pg.transform.scale(img_arrow_down, (20, 20))

img_arrow_up = img_arrow_down.copy()
img_arrow_up = pg.transform.rotate(img_arrow_up, 180)


class ComboBox(ButtonText):
    def __init__(self, elements: list[str], ui_group=None, font_color=Color("black")):
        super().__init__(ui_group=ui_group, text=elements[0], onclick_f=self.open, border_radius=5, fixed_width=200,
                         font_color=best_contrast_color(font_color))
        self.text = elements[0]
        self.rect.height = self.text_rect.height + PADDING * 2
        self.elements = elements
        self.selected_index = 0
        self.hovered_index = self.selected_index
        self.is_open = False
        self._rendered_elements: list[pg.Surface] = []
        self.actions: dict[int, callable] = {}
        self._render_elements()

    def _render_elements(self):
        self._rendered_elements.clear()
        for i, element in enumerate(self.elements):
            if self.selected_index == i or self.hovered_index == i:
                print(f"rendering {i} with selected color ({self.bg_color}")
                color = self.bg_color
            else:
                color = best_contrast_color(self.bg_color)
            text = self.font.render(element, True, color)
            self._rendered_elements.append(text)
            self.rect.width = max(self.rect.width, text.get_width() + PADDING * 2)

    def draw(self, screen, x, y):
        super().draw(screen, x, y)

        img = img_arrow_up if self.is_open else img_arrow_down
        screen.blit(img, (x + self.rect.w - img_arrow_down.get_width() - PADDING, y + 10))

        if self.is_open:
            height = self.rect.h * len(self.elements)
            draw_transparent_rect_with_border_radius(screen,
                                                     Color("black"),
                                                     pg.Rect(x, y + self.rect.h, self.rect.w, height),
                                                     5,
                                                     200)
            for i in range(len(self.elements)):
                if i == self.hovered_index or i == self.selected_index:
                    draw_transparent_rect_with_border_radius(screen,
                                                             Color("white"),
                                                             pg.Rect(x, y + self.rect.h * (i + 1), self.rect.w,
                                                                     self.rect.h).inflate(-3, -3),
                                                             border_radius=5, alpha=100)

                screen.blit(self._rendered_elements[i], (x + PADDING, y + PADDING + self.rect.h * (i + 1)))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pg.MOUSEBUTTONUP:
            x, y = event.pos
            if self.is_open:
                if self.rect.x < x < self.rect.x + self.rect.w:
                    if self.rect.y + self.rect.h < y < self.rect.y + self.rect.h * (len(self.elements) + 1):
                        self.change_selected((y - self.rect.y - self.rect.h) // self.rect.h)
            if not self.rect.colliderect(pg.Rect(x, y, 1, 1)):  # Clicked outside the combo box button
                self.is_open = False
        if event.type == pg.MOUSEMOTION:
            if self.is_open:
                mouse_pos = event.pos
                x, y = mouse_pos
                if self.rect.x < x < self.rect.x + self.rect.w:
                    if self.rect.y + self.rect.h < y < self.rect.y + self.rect.h * (len(self.elements) + 1):
                        self.change_hovered((y - self.rect.y - self.rect.h) // self.rect.h)

    def change_selected(self, index):
        self.selected_index = index
        self.change_text(self.elements[self.selected_index])
        if index in self.actions:
            self.actions[index]()
        self.text = self.elements[self.selected_index]


    def open(self):
        self.is_open = not self.is_open
        self._render_elements()

    def add_action(self, index, action):
        self.actions[index] = action

    def get_value(self) -> str:
        return self.elements[self.selected_index]

    def change_hovered(self, i):
        if i != self.hovered_index:
            self.hovered_index = i
            self._render_elements()
