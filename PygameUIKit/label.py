from super_object import EasyObject

import pygame as pg

pg.font.init()
FONT = pg.font.Font(None, 25)


class Label(EasyObject):
    def __init__(self, text, font_color, font=FONT):
        super().__init__()
        self.text = text
        self.font_color = font_color
        self.text_surface = font.render(self.text, True, self.font_color)
        self.rect = self.text_surface.get_rect()

    def draw(self, screen, x, y, center=False):
        self.rect.topleft = (x, y)
        if center:
            self.rect.center = (x, y)
        screen.blit(self.text_surface, self.rect)
