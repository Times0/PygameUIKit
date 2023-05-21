import pygame as pg

from . import utilis
from .super_object import EasyObject

pg.font.init()
FONT = pg.font.Font(None, 25)


class EasyButton(EasyObject):
    def __init__(self, onclick_f):
        super().__init__()
        self.is_hover = False
        self.clicked = False
        self.onclick_f = onclick_f

    def is_mouse_on_button(self, pos):
        return self.rect.collidepoint(pos)

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.is_mouse_on_button(event.pos):
                    self.clicked = True

            if event.type == pg.MOUSEBUTTONUP:
                if self.clicked and self.is_mouse_on_button(event.pos):
                    self.onclick_f()
                self.clicked = False

            if event.type == pg.MOUSEMOTION:
                self.is_hover = self.is_mouse_on_button(event.pos)


class ButtonRect(EasyButton):
    def __init__(self, w, h, color, onclick_f, border_radius=0):
        super().__init__(onclick_f)
        self.w = w
        self.h = h
        self.color = color
        self.border_radius = border_radius
        self.rect = pg.Rect(0, 0, w, h)
        self.surface = pg.surface.Surface((self.w, self.h), pg.SRCALPHA)
        pg.draw.rect(self.surface, self.color, self.surface.get_rect(), border_radius=self.border_radius, width=0)
        self.surface_hover = None
        self.surface_clicked = None
        self.render_hover()
        self.render_clicked()

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        if self.clicked:
            screen.blit(self.surface_clicked, self.rect)
        elif self.is_hover:
            screen.blit(self.surface_hover, self.rect)
        else:
            screen.blit(self.surface, self.rect)

    def render_hover(self):
        self.surface_hover = utilis.make_surface_darker(self.surface, 30)

    def render_clicked(self):
        self.surface_clicked = utilis.make_surface_darker(self.surface, 50)


class ButtonImage(EasyButton):
    def __init__(self, image, onclick_f):
        super().__init__(onclick_f)
        self.image = image
        self.rect = self.image.get_rect()

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        screen.blit(self.image, self.rect)


class ButtonPngIcon(ButtonImage):
    def __init__(self, image, onclick_f):
        super().__init__(image, onclick_f)

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)

        # if hover then blit a transparent rect behind the image
        if self.is_hover or self.clicked:
            pg.draw.rect(screen, (76, 80, 82, 100), self.rect, border_radius=5, )
        screen.blit(self.image, self.rect)


class ButtonThread(ButtonImage):
    def __init__(self, image_idle, image_working, image_hover, img_success, onclick_f):
        super().__init__(image_idle, onclick_f)
        self.image_idle = image_idle
        self.image_working = image_working
        self.image_hover = image_hover
        self.img_success = img_success

        self.isWorking = False
        self.isSucces = False

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)

        if self.isSucces:
            image = self.img_success
        elif self.isWorking:
            image = self.image_working
        elif self.is_hover:
            image = self.image_hover

        else:
            image = self.image_idle

        screen.blit(image, self.rect)

    def check_thread(self, thread, cond):
        if not thread:
            self.idle()
            return
        if thread.is_alive():
            self.working()
            if cond:
                print("success")
                self.success()
        else:
            self.idle()

    def working(self):
        self.isWorking = True

    def idle(self):
        self.isWorking = False
        self.isSucces = False

    def success(self):
        self.isSucces = True

    def handle_events(self, events):
        for event in events:
            if event.type == pg.MOUSEBUTTONDOWN:
                if self.is_mouse_on_button(event.pos):
                    self.clicked = True

            if event.type == pg.MOUSEBUTTONUP:
                if self.clicked and not self.isWorking and not self.isSucces:
                    self.onclick_f()
                self.clicked = False

            if event.type == pg.MOUSEMOTION:
                self.is_hover = self.is_mouse_on_button(event.pos)


class ButtonText(ButtonRect):
    def __init__(self,
                 rect_color,
                 onclick_f,
                 text,
                 font_color=(0, 0, 0),
                 font=FONT,
                 border_radius=0):
        self.text = text
        self.font_color = font_color
        self.font = font
        self.text_surface = self.font.render(self.text, True, self.font_color)
        self.text_rect = self.text_surface.get_rect()

        w = self.text_surface.get_width() + 20
        h = self.text_surface.get_height() + 20
        super().__init__(w, h, rect_color, onclick_f, border_radius=border_radius)

    def draw(self, screen, x, y):
        super().draw(screen, x, y)
        screen.blit(self.text_surface, (x + 10, y + 10))
