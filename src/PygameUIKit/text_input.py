from collections.abc import Callable

import pygame as pg
from pygame.typing import ColorLike

from . import utils
from .widget import Group, Widget

PAD_X, PAD_Y = 8, 6
REPEAT_DELAY = 0.5
REPEAT_INTERVAL = 0.04
REPEATING_KEYS = (pg.K_BACKSPACE, pg.K_DELETE, pg.K_LEFT, pg.K_RIGHT)


class TextInput(Widget):
    """A fixed-width, single-line Unicode text field.

    ``name = TextInput(placeholder="Name", on_submit=print, ui_group=ui)``;
    ``name.draw(screen, x, y)`` every frame. Click it to focus it, type, press Enter to call
    ``on_submit(text)`` or Escape to unfocus. ``on_change(text)`` runs after every edit; setting
    ``text`` does not call it. Forward both ``KEYDOWN`` and ``TEXTINPUT`` events.
    """

    cursor = pg.SYSTEM_CURSOR_IBEAM

    def __init__(
        self,
        text: str = "",
        *,
        placeholder: str = "",
        width: int = 200,
        font: pg.font.Font | None = None,
        text_color: ColorLike = "black",
        placeholder_color: ColorLike = (150, 150, 150),
        background_color: ColorLike = "white",
        border_color: ColorLike = (170, 170, 170),
        focus_color: ColorLike = (59, 130, 246),
        border_radius: int = 4,
        on_change: Callable[[str], None] | None = None,
        on_submit: Callable[[str], None] | None = None,
        ui_group: Group | None = None,
    ):
        if width < 2 * PAD_X + 4:
            raise ValueError(f"width must be at least {2 * PAD_X + 4} pixels")
        if border_radius < 0:
            raise ValueError("border_radius must not be negative")
        self.placeholder = placeholder
        self.font = font if font is not None else utils.get_font(24)
        self.text_color = pg.Color(text_color)
        self.placeholder_color = pg.Color(placeholder_color)
        self.background_color = pg.Color(background_color)
        self.border_color = pg.Color(border_color)
        self.focus_color = pg.Color(focus_color)
        self.border_radius = border_radius
        self.on_change = on_change
        self.on_submit = on_submit
        self._focused = False
        self._scroll = 0
        self._repeat_key: int | None = None
        self._repeat_elapsed = 0.0
        self._repeat_delay = REPEAT_DELAY
        super().__init__(ui_group=ui_group)
        self.rect = pg.Rect(0, 0, width, self.font.get_height() + 2 * PAD_Y)
        self.text = text

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self.caret = len(value)
        self._scroll_to_caret()

    @property
    def focused(self) -> bool:
        return self._focused

    @focused.setter
    def focused(self, value: bool) -> None:
        if value and not self._focused:
            pg.key.start_text_input()
            pg.key.set_text_input_rect(self.rect)
        self._focused = bool(value)
        self._repeat_key = None

    @property
    def event_priority(self) -> int:
        # While focused, see clicks first so clicking another widget still unfocuses.
        return int(self._focused)

    def handle_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.focused = self.rect.collidepoint(event.pos)
            return self._focused
        if event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.WINDOWFOCUSLOST:
            self.focused = self.hovered = False
        if not self._focused:
            return False
        if event.type == pg.TEXTINPUT:
            self._insert("".join(char for char in event.text if char.isprintable()))
        elif event.type == pg.KEYDOWN:
            if getattr(event, "repeat", False):
                return True
            if event.key in (pg.K_RETURN, pg.K_KP_ENTER):
                if self.on_submit is not None:
                    self.on_submit(self._text)
            elif event.key == pg.K_ESCAPE:
                self.focused = False
            else:
                self._press(event.key)
                if event.key in REPEATING_KEYS:
                    self._repeat_key = event.key
                    self._repeat_elapsed = 0.0
                    self._repeat_delay = REPEAT_DELAY
        elif event.type == pg.KEYUP:
            if event.key == self._repeat_key:
                self._repeat_key = None
        else:
            return False
        return True

    def update(self, dt: float) -> None:
        if not self._focused or self._repeat_key is None:
            return
        self._repeat_elapsed += max(0, dt)
        while self._repeat_elapsed >= self._repeat_delay:
            self._repeat_elapsed -= self._repeat_delay
            self._repeat_delay = REPEAT_INTERVAL
            self._press(self._repeat_key)

    def _edit(self, text: str, caret: int) -> None:
        changed = text != self._text
        self._text = text
        self.caret = caret
        self._scroll_to_caret()
        if changed and self.on_change is not None:
            self.on_change(text)

    def _insert(self, text: str) -> None:
        before, after = self._text[: self.caret], self._text[self.caret :]
        self._edit(before + text + after, self.caret + len(text))

    def _press(self, key: int) -> None:
        text, caret = self._text, self.caret
        if key == pg.K_BACKSPACE and caret:
            self._edit(text[: caret - 1] + text[caret:], caret - 1)
        elif key == pg.K_DELETE:
            self._edit(text[:caret] + text[caret + 1 :], caret)
        elif key in (pg.K_LEFT, pg.K_RIGHT, pg.K_HOME, pg.K_END):
            moves = {pg.K_LEFT: caret - 1, pg.K_RIGHT: caret + 1, pg.K_HOME: 0}
            self._edit(text, moves.get(key, len(text)))

    def _scroll_to_caret(self) -> None:
        self.caret = max(0, min(len(self._text), self.caret))
        caret_x = self.font.size(self._text[: self.caret])[0]
        visible = self.rect.w - 2 * PAD_X - 1
        self._scroll = max(0, min(self._scroll, caret_x))
        self._scroll = max(self._scroll, caret_x - visible)
        self._scroll = min(self._scroll, max(0, self.font.size(self._text)[0] - visible))

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        self.rect.topleft = (x, y)
        box = pg.Surface(self.rect.size, pg.SRCALPHA)
        area = box.get_rect()
        pg.draw.rect(box, self.background_color, area, border_radius=self.border_radius)
        if self._focused:
            border, thickness = self.focus_color, 2
        else:
            border = utils.shade(self.border_color, 0.25) if self.hovered else self.border_color
            thickness = 1
        pg.draw.rect(box, border, area, thickness, border_radius=self.border_radius)
        box.set_clip(area.inflate(-2 * PAD_X, 0))
        text_y = (area.h - self.font.get_height()) // 2
        if self._text:
            rendered = self.font.render(self._text, True, self.text_color)
            box.blit(rendered, (PAD_X - self._scroll, text_y))
        elif self.placeholder:
            box.blit(
                self.font.render(self.placeholder, True, self.placeholder_color), (PAD_X, text_y)
            )
        if self._focused:
            caret_x = PAD_X + self.font.size(self._text[: self.caret])[0] - self._scroll
            pg.draw.line(box, self.text_color, (caret_x, text_y), (caret_x, area.h - text_y - 1))
            pg.key.set_text_input_rect(self.rect)
        surface.blit(box, self.rect)
