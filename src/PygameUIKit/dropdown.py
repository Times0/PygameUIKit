import os

import pygame.draw
from pygame import Color
import pygame as pg

from src.PygameUIKit.button import ButtonText
from src.PygameUIKit.utilis import draw_transparent_rect_with_border_radius

PADDING = 10

cwd = os.path.dirname(__file__)
img_arrow_down = pg.image.load(os.path.join(cwd, "assets", "combo_box_arrow.png"))
img_arrow_down = pg.transform.scale(img_arrow_down, (20, 20))

img_arrow_up = img_arrow_down.copy()
img_arrow_up = pg.transform.rotate(img_arrow_up, 180)


class ComboBox(ButtonText):
    def __init__(self, elements: list[str], ui_group=None):
        super().__init__(ui_group=ui_group, text=elements[0], onclick_f=self.toggle, border_radius=5, fixed_width=200)
        self.rect.height = self.text_rect.height + PADDING * 2
        self.elements = elements
        self.selected = 0
        self.hovered = self.selected
        self.is_open = False
        self._rendered_elements: list[pg.Surface] = []
        self.actions: dict[int, callable] = {}
        self._render_elements()

    def _render_elements(self):
        for element in self.elements:
            text = self.font.render(element, True, self.color)
            self._rendered_elements.append(text)
            self.rect.width = max(self.rect.width, text.get_width() + PADDING * 2)

    def draw(self, screen, x, y):
        super().draw(screen, x, y)

        img = img_arrow_up if self.is_open else img_arrow_down
        screen.blit(img, (x + self.rect.w - img_arrow_down.get_width() - PADDING, y + 10))

        if self.is_open:
            height = self.rect.h * len(self.elements)
            draw_transparent_rect_with_border_radius(screen, pg.Rect(x, y + self.rect.h, self.rect.w, height), 5,
                                                     Color("black"), 100)
            for i in range(len(self.elements)):
                if i == self.hovered or i == self.selected:
                    draw_transparent_rect_with_border_radius(screen,
                                                             pg.Rect(x, y + self.rect.h * (i + 1), self.rect.w,
                                                                     self.rect.h).inflate(-3, -3),
                                                             5, Color("white"), 100)
                screen.blit(self._rendered_elements[i], (x + PADDING, y + PADDING + self.rect.h * (i + 1)))

    def handle_event(self, event):
        super().handle_event(event)
        if event.type == pg.MOUSEBUTTONDOWN:
            x, y = event.pos
            if self.is_open:
                if self.rect.x < x < self.rect.x + self.rect.w:
                    if self.rect.y + self.rect.h < y < self.rect.y + self.rect.h * (len(self.elements) + 1):
                        self.new_selection((y - self.rect.y - self.rect.h) // self.rect.h)
            self.is_open = False
        if event.type == pg.MOUSEMOTION:
            if self.is_open:
                mouse_pos = event.pos
                x, y = mouse_pos
                if self.rect.x < x < self.rect.x + self.rect.w:
                    if self.rect.y + self.rect.h < y < self.rect.y + self.rect.h * (len(self.elements) + 1):
                        self.hovered = (y - self.rect.y - self.rect.h) // self.rect.h

    def new_selection(self, index):
        self.selected = index
        self.change_text(self.elements[self.selected])
        if index in self.actions:
            self.actions[index]()

    def toggle(self):
        self.is_open = not self.is_open

    def add_action(self, index, action):
        self.actions[index] = action
