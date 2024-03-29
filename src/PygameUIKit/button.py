import threading
from enum import Enum
import pygame as pg
from pygame import Rect
from pygame.color import Color
from .label import TextAlignment, Label, DEFAULT_FONT
from .super_object import Group, EasyObject
from . import utilis


class EasyButton(EasyObject):
    def __init__(self, onclick_f, ui_group: Group = None):
        super().__init__(ui_group=ui_group)
        self.is_hover = False
        self.clicked = False
        self.onclick_f = onclick_f
        self.ui_group = ui_group

    def is_mouse_on_button(self, pos):
        return self.rect.collidepoint(pos)

    def _on_hover(self):
        self.on_hover()
        pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_HAND)

    def on_hover(self):
        pass

    def _on_unhover(self):
        self.on_unhover()
        pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_ARROW)

    def on_unhover(self):
        pass

    def handle_events(self, events):
        for event in events:
            self.handle_event(event)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.is_mouse_on_button(event.pos):
                self.clicked = True

        if event.type == pg.MOUSEBUTTONUP:
            if self.clicked and self.is_mouse_on_button(event.pos):
                self._on_click()
            self.clicked = False

        if event.type == pg.MOUSEMOTION:
            was_hover = self.is_hover
            self.is_hover = self.is_mouse_on_button(event.pos)
            if self.is_hover and not was_hover:
                self._on_hover()
            elif not self.is_hover and was_hover:
                self._on_unhover()

    def _on_click(self):
        pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_ARROW)
        self.onclick_f()

    def connect(self, func, when="on_click"):
        if when == "on_click":
            self.onclick_f = func


class ButtonRect(EasyButton):
    def __init__(self, w, h, color, onclick_f, outline_color=None, border_radius=0, ui_group=None):
        super().__init__(onclick_f, ui_group)
        self.bg_color = color
        self.border_radius = border_radius
        self.rect = pg.Rect(0, 0, w, h)
        self.surface = None
        self.surface_hover = None
        self.surface_clicked = None
        self.outline_color = outline_color
        self.render()

    def render(self):
        self.surface = pg.surface.Surface((self.rect.w, self.rect.h), pg.SRCALPHA)
        pg.draw.rect(self.surface, self.bg_color, self.surface.get_rect(), border_radius=self.border_radius, width=0)
        if self.outline_color:
            pg.draw.rect(self.surface,
                         self.outline_color,
                         self.surface.get_rect(), border_radius=self.border_radius, width=2)
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
    def __init__(self, image, onclick_f, hover_image=None, ui_group=None):
        super().__init__(onclick_f, ui_group=ui_group)
        self.image = image
        self.hover_image = hover_image
        self.rect: Rect = self.image.get_rect()

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        if self.is_hover:
            screen.blit(self.hover_image, self.rect)
        else:
            screen.blit(self.image, self.rect)


class ButtonImageText(ButtonImage):
    def __init__(self, image, onclick_f, text, text_color=Color("white"), font=pg.font.SysFont("Arial", 15),
                 image_hover=None,
                 text_offset=(0, 0)):
        super().__init__(image, onclick_f, hover_image=image_hover)
        self.text = text
        self.text_color = text_color
        self.text_offset = text_offset
        self.font = font

    def draw(self, screen, x, y):
        super().draw(screen, x, y)
        text = self.font.render(self.text, True, self.text_color)
        text_rect = text.get_rect()
        text_rect.center = (self.rect.centerx + self.text_offset[0], self.rect.centery + self.text_offset[1])
        screen.blit(text, text_rect)


class ButtonPngIcon(ButtonImage):
    def __init__(self, image, onclick_f, hover_color=Color("gray"), opacity=0.5, inflate=10, ui_group=None):
        super().__init__(image, onclick_f, ui_group=ui_group)
        self.hover_color = hover_color
        self.opacity = int(opacity * 255)
        self.inflate = inflate

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)

        # if hover then blit a transparent rect behind the image
        if self.is_hover or self.clicked:
            utilis.draw_transparent_rect_with_border_radius(screen,
                                                            self.hover_color,
                                                            self.rect.inflate(self.inflate, self.inflate),
                                                            10,
                                                            self.opacity)

        screen.blit(self.image, self.rect)


class ButtonThreadImage(ButtonImage):
    """
    Really specific button type, useful for button that need to have a state depending on a thread
    e.g a button that start matchmaking
    """

    def __init__(self, image_idle, image_working, image_hover, img_success, onclick_f):
        super().__init__(image_idle, onclick_f)
        self.image_idle = image_idle
        self.image_working = image_working
        self.image_hover = image_hover
        self.img_success = img_success

        self.isWorking = False
        self.isSuccess = False

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)

        if self.isSuccess:
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
                self.success()
        else:
            self.idle()

    def working(self):
        self.isWorking = True

    def idle(self):
        self.isWorking = False
        self.isSuccess = False

    def success(self):
        self.isSuccess = True


class ButtonText(ButtonRect):
    def __init__(self,
                 text="",
                 onclick_f=None,
                 rect_color=Color("black"),
                 border_radius=0,
                 font=DEFAULT_FONT,
                 font_color=None,
                 outline_color=None,
                 fixed_width=None,
                 text_align=None,
                 ui_group=None):

        if not font_color:
            font_color = utilis.best_contrast_color(rect_color)
        self.fixed_width = fixed_width

        if text_align == "center" and fixed_width is None:
            raise ValueError("Text align center is only available with fixed width")

        rect = Rect(0, 0, fixed_width, 0) if fixed_width else None
        self.label = Label(text, font_color, font=font, text_align=text_align, bounding_rect=rect)

        super().__init__(0, 0, rect_color, onclick_f, border_radius=border_radius, ui_group=ui_group,
                         outline_color=outline_color)

    def render(self):
        self.label.render_text()
        if self.fixed_width:
            self.rect.w = self.fixed_width
        else:
            self.rect.w = self.label.rect.w + 20
        self.rect.h = self.label.rect.h + 20
        super().render()

    def change_text(self, new_text):
        if new_text == self.label.text:
            return
        self.label.text = new_text
        self.render()

    def draw(self, screen, x, y):
        super().draw(screen, x, y)
        self.label.draw(screen, x, y)


class ButtonThreadText(ButtonRect):
    def __init__(self, *, rect_color=(0, 0, 0),
                 onclick_f=None,
                 thread=None,
                 text_before="",
                 text_during="",
                 text_after="",
                 border_radius=0,
                 font=pg.font.SysFont("Arial", 15),
                 ui_group=None,
                 text_color=(255, 255, 255)):

        self.thread = thread

        self.text_before = text_before
        self.text_during = text_during
        self.text_after = text_after
        self.font = font
        self.font_color = text_color

        self.text_surface_idle = self.font.render(self.text_before, True, self.font_color)
        self.text_surface_working = None
        self.text_surface_success = None
        self.text_surface_hover = None
        self.render_text_surfaces()

        w = self.text_surface_idle.get_width() + 20
        h = self.text_surface_idle.get_height() + 20
        super().__init__(w, h, rect_color, onclick_f, border_radius=border_radius, ui_group=ui_group)

        self.isWorking = False
        self.isSuccess = False

    def render_text_surfaces(self):
        self.text_surface_idle = self.font.render(self.text_before, True, self.font_color)
        self.text_surface_working = self.font.render(self.text_during, True, self.font_color)
        self.text_surface_success = self.font.render(self.text_after, True, self.font_color)

    def draw(self, screen, x, y):
        super().draw(screen, x, y)
        if self.isSuccess:
            screen.blit(self.text_surface_success, (x + 10, y + 10))
        elif self.isWorking:
            screen.blit(self.text_surface_working, (x + 10, y + 10))
        else:
            screen.blit(self.text_surface_idle, (x + 10, y + 10))

    def check_thread(self, thread: threading.Thread, success_condition):
        if not thread:
            self.idle()
            return
        # check if thread did not start or is running or is done
        if thread.is_alive():
            self.working()
        else:
            if thread.ident is None:
                self.idle()
            else:
                if success_condition:
                    self.success()
                else:
                    self.idle()

    def working(self):
        self.isWorking = True
        self.isSuccess = False

        self.rect.w = self.text_surface_working.get_width() + 20
        super().render()

    def idle(self):
        self.isWorking = False
        self.isSuccess = False
        self.rect.w = self.text_surface_idle.get_width() + 20
        super().render()

    def success(self):
        self.isSuccess = True
        self.isWorking = False
        self.rect.w = self.text_surface_success.get_width() + 20
        self.bg_color = Color((87, 147, 94))
        super().render()


class ButtonTwoStates(ButtonPngIcon):
    def __init__(self, image_default, image_click, onclick_f, hover_color=Color("gray"), opacity=0.5, inflate=10,
                 ui_group=None):
        super().__init__(image_default, onclick_f, hover_color, opacity, inflate, ui_group)
        self.images = {
            1: image_default,
            2: image_click
        }

        self.state = 1

    def draw(self, screen, x, y):
        self.image = self.images[self.state]
        super().draw(screen, x, y)

    def _on_click(self):
        super()._on_click()
        self.state = 2 if self.state == 1 else 1
