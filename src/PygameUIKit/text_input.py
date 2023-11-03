import os

import pygame as pg
from pygame.locals import *
from .super_object import EasyObject

pg.font.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.SysFont('Arial', 20)
TIME_OUT_FIRST = 500
TIME_OUT = 40


def is_char(unicode):
    return unicode.isalpha() or unicode.isdigit() or unicode in " .,:;?!@#$%^&*()_-+=~`[]{}\\|/<>\"'"


class InputBox(EasyObject):
    def __init__(self, *,
                 text="",
                 font: pg.font.Font = FONT,
                 fixed_width: int = None,
                 text_color=pg.Color('black'),
                 border_radius=0,
                 ui_group=None):
        """
        if width is None, then the width will be the width of the text
        """
        super().__init__(ui_group=ui_group)
        self.color = COLOR_INACTIVE
        self.text_color = text_color
        self.text = text
        self.cursor = 0
        self.active = False
        self.font = font
        self.max_width = fixed_width
        self.border_radius = border_radius

        self.last_key_press = 0
        self.time_since_first_key_press = 0

        self.last_press_type = None
        self.linked_unicode = None

        if fixed_width:
            self.rect = pg.Rect(0, 0, fixed_width, 20, )  # width is fixed
        else:
            self.rect = pg.Rect(0, 0, 0, 20)  # width will be changed when rendering

        # Render the text to get the height
        fake_render = self.font.render("A", True, self.text_color)
        self.rect.h = fake_render.get_height() + 10
        self.bg_trans = 0
        self.hover = False
        self._render()

    def _handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if event.type == pg.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        if not self.active:
            return

        if event.type == pg.KEYUP and event.key == self.last_press_type:
            self.last_press_type = None
            self.last_key_press = 0
            self.time_since_first_key_press = 0

        elif event.type == pg.KEYDOWN:
            self.last_press_type = event.key
            self.last_key_press = pg.time.get_ticks()
            self.time_since_first_key_press = pg.time.get_ticks()
            self.linked_unicode = event.unicode
            self.handle_key(event.key)

    def add_letter(self, unicode):
        self.text = self.text[:self.cursor] + unicode + self.text[self.cursor:]
        self.cursor += 1

    def handle_event(self, event):
        pass

    def handle_events(self, events):
        for event in events:
            self._handle_event(event)

        if not self.active:
            return
        pressed = pg.key.get_pressed()

        for key in [K_BACKSPACE, K_LEFT, K_RIGHT] + [i for i in range(32, 127)]:
            if not pressed[key] or not self.should_handle_key(key):
                continue
            self.handle_key(key)

    def should_handle_key(self, k):
        # First entrance
        if self.last_press_type != k:
            return False

        # Waiting for the right amount of time before handling the key
        if pg.time.get_ticks() - self.time_since_first_key_press > TIME_OUT_FIRST:
            if pg.time.get_ticks() - self.last_key_press > TIME_OUT:
                return True
        return False

    def handle_key(self, k):
        if k == K_BACKSPACE:
            self.remove_letter()
        elif k == K_LEFT:
            if self.cursor > 0:
                self.cursor -= 1
        elif k == K_RIGHT:
            if self.cursor < len(self.text):
                self.cursor += 1
        elif is_char(self.linked_unicode):
            self.add_letter(self.linked_unicode)
        self._render()

    def remove_letter(self):
        if self.cursor == 0:
            return
        self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
        self.cursor -= 1
        self._render()

    def _render(self):
        self.txt_surface = self.font.render(self.text, True, self.text_color)
        if not self.max_width:
            self.rect.width = self.txt_surface.get_width() + 1

    def draw(self, screen, x, y):
        self.rect.x = x
        self.rect.y = y

        if self.hover and not self.active:
            self.bg_trans = 50
        else:
            self.bg_trans = 0
        rect_img = pg.surface.Surface((self.rect.w, self.rect.h), pg.SRCALPHA)
        pg.draw.rect(rect_img,
                     (255, 255, 255, self.bg_trans),
                     rect_img.get_rect(),
                     border_radius=self.border_radius)  # draw background
        pg.draw.rect(rect_img, self.color, rect_img.get_rect(), border_radius=self.border_radius, width=1)

        # Draw text
        text_width = self.txt_surface.get_width()
        if text_width > self.rect.width - 10:
            rect_img.blit(self.txt_surface, self.txt_surface.get_rect(topright=(self.rect.width - 5, 5)))
        else:
            rect_img.blit(self.txt_surface, (5, 5))

        # Draw cursor
        if self.active:
            cursor = pg.surface.Surface((1, self.rect.h - 10))
            cursor.fill(self.text_color)
            cursor_pos = self.font.render(self.text[:self.cursor], True, self.text_color).get_width()
            if cursor_pos > self.rect.width - 10:
                rect_img.blit(cursor, cursor.get_rect(topright=(self.rect.width - 5, 5)))
            else:
                rect_img.blit(cursor, (cursor_pos + 5, 5))
        screen.blit(rect_img, (self.rect.x, self.rect.y))

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.cursor = len(text)
        self._render()
