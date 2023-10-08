import pygame as pg

from .super_object import EasyObject

pg.font.init()
COLOR_INACTIVE = pg.Color('lightskyblue3')
COLOR_ACTIVE = pg.Color('dodgerblue2')
FONT = pg.font.Font(None, 25)


class InputBox(EasyObject):

    def __init__(self, *,
                 text="",
                 font: pg.font.Font = FONT,
                 fixed_width: int = None,
                 text_color=pg.Color('white'),
                 border_radius=0,
                 ui_group=None):
        """
        if width is None, then the width will be the width of the text
        """
        super().__init__(ui_group=ui_group)
        self.color = COLOR_INACTIVE
        self.text_color = text_color
        self.text = text
        self.active = False
        self.font = font
        self.max_width = fixed_width
        self.border_radius = border_radius

        if fixed_width:
            self.rect = pg.Rect(0, 0, fixed_width, 20, )  # width is fixed
        else:
            self.rect = pg.Rect(0, 0, 0, 20)  # width will be changed when rendering

        # Render the text to get the height
        fake_render = self.font.render("A", True, self.text_color)
        self.rect.h = fake_render.get_height() + 10

        self.last_backspace = 0
        self.bg_trans = 0
        self.hover = False
        self._render()

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE

        if event.type == pg.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)

        # needs to be active to do the following
        if not self.active:
            return
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_BACKSPACE:
                self.last_backspace = pg.time.get_ticks()
                self.text = self.text[:-1]
            elif event.key == pg.K_RETURN:
                self.active = False
                self.color = COLOR_INACTIVE
            else:
                self.text += event.unicode
        if event.type == pg.KEYUP and event.key == pg.K_BACKSPACE:
            self.last_backspace = 0

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
            rect_img.blit(cursor, (self.txt_surface.get_width() + 5, 5))

        screen.blit(rect_img, (self.rect.x, self.rect.y))

    def get_text(self):
        return self.text
