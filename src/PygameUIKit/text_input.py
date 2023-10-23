import os

import pygame as pg

from .super_object import EasyObject

pg.font.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
cwd = os.path.dirname(__file__)
FONT = pg.font.Font(cwd + "/../assets/OpenSans-Medium.ttf", 16)

TIME_OUT_FIRST_BACKSPACE = 500
TIME_OUT_BACKSPACE = 20


def is_char(unicode):
    return unicode.isalpha() or unicode.isdigit() or unicode in " .,:;?!@#$%^&*()_-+=~`[]{}\\|/<>"


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
        self.time_since_first_key = 0

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
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_RETURN:
                self.active = False
                self.color = COLOR_INACTIVE
            elif event.key == pg.K_BACKSPACE:
                self.time_since_first_key = pg.time.get_ticks()
                self.remove_letter()
            elif event.key == pg.K_LEFT:
                if self.cursor > 0:
                    self.cursor -= 1
            elif event.key == pg.K_RIGHT:
                if self.cursor < len(self.text):
                    self.cursor += 1
            elif is_char(event.unicode):
                self.add_letter(event.unicode)
                self.time_since_first_key = pg.time.get_ticks()
            self._render()

    def add_letter(self, unicode):
        self.text = self.text[:self.cursor] + unicode + self.text[self.cursor:]
        self.cursor += 1

    def handle_event(self, event):
        pass

    def handle_events(self, events):
        for event in events:
            self._handle_event(event)
        pressed = pg.key.get_pressed()
        if pressed[pg.K_BACKSPACE] and pg.time.get_ticks() - self.time_since_first_key > TIME_OUT_FIRST_BACKSPACE:
            if self.cursor > 0:
                if pg.time.get_ticks() - self.last_key_press > TIME_OUT_BACKSPACE:
                    self.remove_letter()
        # check for other keys

    def remove_letter(self):
        self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
        self.cursor -= 1
        self.last_key_press = pg.time.get_ticks()
        self._render()

    def _render(self):
        self.txt_surface = self.font.render(self.text, True, self.text_color)
        if not self.max_width:
            self.rect.width = self.txt_surface.get_width() + 10

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
        pg.draw.rect(rect_img, self.color, rect_img.get_rect(), border_radius=self.border_radius,
                     width=1)  # draw border
        rect_img.blit(self.txt_surface, (5, 5))

        # draw cursor
        if self.active:
            cursor = pg.surface.Surface((1, self.rect.h - 10))
            cursor.fill(self.text_color)
            cursor_pos = self.font.render(self.text[:self.cursor], True, self.text_color).get_width()

            rect_img.blit(cursor, (cursor_pos + 5, 5))

        screen.blit(rect_img, (self.rect.x, self.rect.y))

    def get_text(self):
        return self.text
