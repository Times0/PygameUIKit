import pygame as pg

from .super_object import EasyObject

pg.font.init()


class Label(EasyObject):
    def __init__(self, text, font_color, font=None):
        super().__init__(font=font)
        self.text = text
        self.font_color = font_color
        self.font = font
        self.text_surface: pg.Surface | None = None
        self.rect: pg.Rect | None = None
        self.render_new_text()

    def draw(self, screen, x, y, center=False):
        self.rect.topleft = (x, y)
        if center:
            self.rect.center = (x, y)
        screen.blit(self.text_surface, self.rect)

    def render_new_text(self):
        self.text_surface = self.font.render(self.text, True, self.font_color)
        self.rect = self.text_surface.get_rect()
