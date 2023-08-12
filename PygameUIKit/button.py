import pygame as pg

from PygameUIKit.super_object import Group, EasyObject
from . import utilis

pg.font.init()
FONT = pg.font.Font(None, 25)


class EasyButton(EasyObject):
    def __init__(self, onclick_f, ui_group: Group = None):
        super().__init__()
        self.is_hover = False
        self.clicked = False
        self.onclick_f = onclick_f
        self.ui_group = ui_group
        if self.ui_group:
            self.ui_group.add(self)

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
                    self.on_hover()
                elif not self.is_hover and was_hover:
                    self.on_unhover()

    def _on_click(self):
        pg.mouse.set_system_cursor(pg.SYSTEM_CURSOR_ARROW)
        self.onclick_f()


class ButtonRect(EasyButton):
    def __init__(self, w, h, color, onclick_f, border_radius=0, ui_group=None):
        super().__init__(onclick_f, ui_group)
        self.color = color
        self.border_radius = border_radius
        self.rect = pg.Rect(0, 0, w, h)
        self.surface = None
        self.surface_hover = None
        self.surface_clicked = None
        self.render()

    def render(self):
        self.surface = pg.surface.Surface((self.rect.w, self.rect.h), pg.SRCALPHA)
        pg.draw.rect(self.surface, self.color, self.surface.get_rect(), border_radius=self.border_radius, width=0)
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
    def __init__(self, image, hover_color, onclick_f):
        super().__init__(image, onclick_f)
        self.hover_color = hover_color

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)

        # if hover then blit a transparent rect behind the image
        if self.is_hover or self.clicked:
            draw_transparent_rect_with_border_radius(screen, self.rect, 10, self.hover_color, 100)

        screen.blit(self.image, self.rect)


class ButtonThreadImage(ButtonImage):
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


from pygame.color import Color


def get_best_text_color(rgb_color: tuple | Color):
    if isinstance(rgb_color, Color):
        rgb_color = rgb_color.r, rgb_color.g, rgb_color.b
    r, g, b = rgb_color
    if r + g + b < 500:
        return 255, 255, 255
    else:
        return 0, 0, 0


class ButtonText(ButtonRect):
    def __init__(self,
                 text,
                 onclick_f,
                 rect_color,
                 font=FONT,
                 border_radius=0,
                 font_color=None,
                 ui_group=None):
        self.text = text
        if font_color is None:
            self.text_color = get_best_text_color(rect_color)
        else:
            self.text_color = font_color
        self.font = font
        self.text_surface = self.font.render(self.text, True, self.text_color)
        self.text_rect = self.text_surface.get_rect()

        w = self.text_surface.get_width() + 20
        h = self.text_surface.get_height() + 20
        super().__init__(w, h, rect_color, onclick_f, border_radius=border_radius, ui_group=ui_group)

    def draw(self, screen, x, y):
        super().draw(screen, x, y)
        screen.blit(self.text_surface, (x + 10, y + 10))


class ButtonThreadText(ButtonRect):
    def __init__(self, *, rect_color=(0, 0, 0),
                 onclick_f=None,
                 text_before="",
                 text_during="",
                 text_after="",
                 border_radius=0,
                 font=FONT,
                 text_color=(255, 255, 255)):
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
        super().__init__(w, h, rect_color, onclick_f, border_radius)

        self.isWorking = False
        self.isSucces = False

    def render_text_surfaces(self):
        self.text_surface_idle = self.font.render(self.text_before, True, self.font_color)
        self.text_surface_working = self.font.render(self.text_during, True, self.font_color)
        self.text_surface_success = self.font.render(self.text_after, True, self.font_color)

    def draw(self, screen, x, y):
        super().draw(screen, x, y)
        if self.isSucces:
            screen.blit(self.text_surface_success, (x + 10, y + 10))
        elif self.isWorking:
            screen.blit(self.text_surface_working, (x + 10, y + 10))
        else:
            screen.blit(self.text_surface_idle, (x + 10, y + 10))

    def check_thread(self, thread):
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
                self.success()

    def working(self):
        self.isWorking = True
        self.isSucces = False

        self.rect.w = self.text_surface_working.get_width() + 20
        super().render()

    def idle(self):
        self.isWorking = False
        self.isSucces = False
        self.rect.w = self.text_surface_idle.get_width() + 20
        super().render()

    def success(self):
        self.isSucces = True
        self.isWorking = False
        self.rect.w = self.text_surface_success.get_width() + 20
        super().render()


def draw_transparent_rect_with_border_radius(screen, rect, border_radius, color, alpha):
    surf = pg.Surface(rect.size, pg.SRCALPHA)
    pg.draw.rect(surf, color, surf.get_rect().inflate(-1, -1), border_radius=border_radius)
    surf.set_alpha(alpha)
    screen.blit(surf, rect)
