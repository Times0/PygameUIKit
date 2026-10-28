import pygame as pg

from .utils import get_font
from .widget import Widget

COLOR_INACTIVE = pg.Color("lightskyblue3")
COLOR_ACTIVE = pg.Color("dodgerblue2")
TIME_OUT_FIRST = 500
TIME_OUT = 40
SMALL_FONT = None


def is_char(text):
    return bool(text) and text.isprintable()


class TextInput(Widget):
    """Single-line Unicode input. Send both KEYDOWN and TEXTINPUT events to it."""

    cursor = pg.SYSTEM_CURSOR_IBEAM

    def __init__(
        self,
        *,
        text="",
        font=None,
        fixed_width=None,
        font_color=(0, 0, 0),
        border_radius=0,
        placeholder="",
        ui_group=None,
    ):
        super().__init__(ui_group=ui_group)
        if fixed_width is not None and fixed_width < 12:
            raise ValueError("fixed_width must be at least 12 pixels")
        self.color = COLOR_INACTIVE
        self.font_color = pg.Color(font_color)
        self.text = text
        self.caret = len(text)
        self.active = False
        self.font = font if font is not None else get_font()
        self.max_width = fixed_width
        self.border_radius = border_radius
        self.placeholder = placeholder
        self.bg_trans = 0
        self._scroll = 0
        self._repeat_key = None
        self._repeat_elapsed = 0
        self._repeat_delay = TIME_OUT_FIRST / 1000
        self.rect = pg.Rect(0, 0, fixed_width or 12, self.font.get_height() + 10)
        self._render()

    @property
    def event_priority(self):
        # While focused, see clicks first so clicking another widget still unfocuses.
        return int(self.active)

    def handle_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.active = self.rect.collidepoint(event.pos)
            self.color = COLOR_ACTIVE if self.active else COLOR_INACTIVE
            self._repeat_key = None
            if self.active:
                pg.key.start_text_input()
                pg.key.set_text_input_rect(self.rect)
            return self.active
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.WINDOWFOCUSLOST:
            self.active = False
            self.color = COLOR_INACTIVE
            self._repeat_key = None
        if not self.active:
            return False
        if event.type == pg.TEXTINPUT:
            self.add_letter("".join(char for char in event.text if char.isprintable()))
        elif event.type == pg.KEYDOWN:
            if getattr(event, "repeat", False):
                return True
            self.handle_key(event.key)
            if event.key in (pg.K_BACKSPACE, pg.K_DELETE, pg.K_LEFT, pg.K_RIGHT):
                self._repeat_key = event.key
                self._repeat_elapsed = 0
                self._repeat_delay = TIME_OUT_FIRST / 1000
        elif event.type == pg.KEYUP:
            if event.key == self._repeat_key:
                self._repeat_key = None
        else:
            return False
        return True

    def update(self, dt):
        if not self.active or self._repeat_key is None:
            return
        self._repeat_elapsed += max(0, dt)
        while self._repeat_elapsed >= self._repeat_delay:
            self._repeat_elapsed -= self._repeat_delay
            self._repeat_delay = TIME_OUT / 1000
            self.handle_key(self._repeat_key)

    def add_letter(self, text):
        self.text = self.text[: self.caret] + text + self.text[self.caret :]
        self.caret += len(text)
        self._render()

    def handle_key(self, key):
        if key == pg.K_BACKSPACE:
            self.remove_letter()
        elif key == pg.K_DELETE:
            self.text = self.text[: self.caret] + self.text[self.caret + 1 :]
        elif key == pg.K_LEFT:
            self.caret = max(0, self.caret - 1)
        elif key == pg.K_RIGHT:
            self.caret = min(len(self.text), self.caret + 1)
        elif key == pg.K_HOME:
            self.caret = 0
        elif key == pg.K_END:
            self.caret = len(self.text)
        self._render()

    def remove_letter(self):
        if self.caret:
            self.text = self.text[: self.caret - 1] + self.text[self.caret :]
            self.caret -= 1
            self._render()

    def _render(self):
        self.caret = max(0, min(len(self.text), self.caret))
        self.txt_surface = self.font.render(self.text, True, self.font_color)
        if self.max_width is None:
            self.rect.width = max(12, self.font.size(self.text or self.placeholder)[0] + 10)
        cursor_x = self.font.size(self.text[: self.caret])[0]
        visible_width = self.rect.width - 11
        self._scroll = max(0, min(self._scroll, cursor_x))
        self._scroll = max(self._scroll, cursor_x - visible_width)
        self._scroll = min(self._scroll, max(0, self.txt_surface.get_width() - visible_width))

    def draw(self, screen, x, y):
        self.rect.topleft = (x, y)
        self.bg_trans = 50 if self.hovered and not self.active else 0
        surface = pg.Surface(self.rect.size, pg.SRCALPHA)
        pg.draw.rect(
            surface,
            (255, 255, 255, self.bg_trans),
            surface.get_rect(),
            border_radius=self.border_radius,
        )
        pg.draw.rect(
            surface, self.color, surface.get_rect(), width=1, border_radius=self.border_radius
        )
        surface.set_clip(pg.Rect(5, 5, self.rect.width - 10, self.rect.height - 10))
        if self.text:
            surface.blit(self.txt_surface, (5 - self._scroll, 5))
        else:
            self.draw_placeholder(surface)
        if self.active:
            cursor_x = 5 + self.font.size(self.text[: self.caret])[0] - self._scroll
            pg.draw.line(surface, self.font_color, (cursor_x, 5), (cursor_x, self.rect.height - 6))
            pg.key.set_text_input_rect(self.rect)
        screen.blit(surface, self.rect)

    def draw_placeholder(self, surface):
        placeholder = self.font.render(self.placeholder, True, self.font_color)
        placeholder.set_alpha(100)
        surface.blit(placeholder, (5, 5))

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = text
        self.caret = len(text)
        self._render()
