from collections.abc import Callable, Sequence

import pygame as pg
from pygame.typing import ColorLike

from . import utils
from .label import Label
from .widget import Group, Widget

PAD_X, PAD_Y = 12, 8
ARROW = 10
GAP = 4
INSET = 4
HEADER = -1


class Dropdown(Widget):
    """A box showing the selected option that opens a menu of all options below it.

    ``size = Dropdown(["Small", "Large"], on_change=print, ui_group=ui)``; draw it after the
    widgets its menu can cover. Choose with the mouse, or with Up/Down and Enter while it is
    open; Escape, window focus loss or a click elsewhere closes it. ``on_change(value)`` runs
    when the user picks a different option; setting ``value`` or ``index`` does not call it.
    """

    cursor = pg.SYSTEM_CURSOR_HAND

    def __init__(
        self,
        options: Sequence[str],
        *,
        index: int = 0,
        on_change: Callable[[str], None] | None = None,
        width: int | None = None,
        font: pg.font.Font | None = None,
        color: ColorLike = "white",
        text_color: ColorLike | None = None,
        highlight_color: ColorLike = (59, 130, 246),
        outline_color: ColorLike | None = (170, 170, 170),
        border_radius: int = 6,
        ui_group: Group | None = None,
    ):
        if not options:
            raise ValueError("Dropdown requires at least one option")
        if not 0 <= index < len(options):
            raise IndexError("Dropdown index out of range")
        if width is not None and width <= 0:
            raise ValueError("width must be positive")
        if border_radius < 0:
            raise ValueError("border_radius must not be negative")
        self.options = tuple(options)
        self._index = index
        self.on_change = on_change
        self.width = width
        self.font = font if font is not None else utils.get_font(24)
        self.color = pg.Color(color)
        self.text_color = None if text_color is None else pg.Color(text_color)
        self.highlight_color = pg.Color(highlight_color)
        self.outline_color = None if outline_color is None else pg.Color(outline_color)
        self.border_radius = border_radius
        self.is_open = False
        self.highlighted: int | None = None
        self._pressed: int | None = None
        self._labels = [Label(option, font=self.font) for option in self.options]
        self._header = Label(self.options[index], font=self.font)
        super().__init__(ui_group=ui_group)
        self.rect = pg.Rect(0, 0, self._width(), self.font.get_height() + 2 * PAD_Y)

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int) -> None:
        if not 0 <= value < len(self.options):
            raise IndexError("Dropdown index out of range")
        self._index = value

    @property
    def value(self) -> str:
        return self.options[self._index]

    @value.setter
    def value(self, value: str) -> None:
        if value not in self.options:
            raise ValueError(f"{value!r} is not one of the options")
        self._index = self.options.index(value)

    @property
    def event_priority(self) -> int:
        # An open menu sees events before the widgets it covers.
        return int(self.is_open)

    def _width(self) -> int:
        if self.width is not None:
            return self.width
        return max(self.font.size(option)[0] for option in self.options) + 3 * PAD_X + ARROW

    def _menu_rect(self) -> pg.Rect:
        height = len(self.options) * self.rect.h + 2 * INSET
        return pg.Rect(self.rect.x, self.rect.bottom + GAP, self.rect.w, height)

    def _row_rect(self, index: int) -> pg.Rect:
        menu = self._menu_rect()
        top = menu.y + INSET + index * self.rect.h
        return pg.Rect(menu.x + INSET, top, menu.w - 2 * INSET, self.rect.h)

    def _target(self, pos: tuple[int, int]) -> int | None:
        """``HEADER``, the index of the option under ``pos``, or None."""
        if self.rect.collidepoint(pos):
            return HEADER
        if self.is_open:
            return next(
                (i for i in range(len(self.options)) if self._row_rect(i).collidepoint(pos)), None
            )
        return None

    def _covers(self, pos: tuple[int, int]) -> bool:
        return self.rect.collidepoint(pos) or (self.is_open and self._menu_rect().collidepoint(pos))

    def _set_open(self, is_open: bool) -> None:
        self.is_open = is_open
        self.highlighted = self._index if is_open else None

    def _reset(self) -> None:
        super()._reset()
        self._set_open(False)
        self._pressed = None

    def _choose(self, index: int) -> None:
        self._set_open(False)
        if index != self._index:
            self._index = index
            if self.on_change is not None:
                self.on_change(self.value)

    def handle_event(self, event: pg.event.Event) -> bool:
        if not self.interactive:
            return False
        if event.type == pg.WINDOWFOCUSLOST:
            self._reset()
        elif event.type == pg.MOUSEMOTION:
            self.hovered = self._covers(event.pos)
            if self.is_open:
                target = self._target(event.pos)
                self.highlighted = None if target == HEADER else target
            return self.is_open and self.hovered
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self._pressed = self._target(event.pos)
            if self._pressed is None and not self._covers(event.pos):
                self._set_open(False)
            return self._covers(event.pos)
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            pressed, self._pressed = self._pressed, None
            target = self._target(event.pos)
            if target is not None and target == pressed:
                if target == HEADER:
                    self._set_open(not self.is_open)
                else:
                    self._choose(target)
                return True
            return self.is_open and self._covers(event.pos)
        elif event.type in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
            return self.is_open and self._covers(event.pos)
        elif event.type == pg.KEYDOWN and self.is_open:
            if event.key == pg.K_ESCAPE:
                self._set_open(False)
            elif event.key in (pg.K_UP, pg.K_DOWN):
                start = self._index if self.highlighted is None else self.highlighted
                step = 1 if event.key == pg.K_DOWN else -1
                self.highlighted = max(0, min(len(self.options) - 1, start + step))
            elif event.key in (pg.K_RETURN, pg.K_KP_ENTER, pg.K_SPACE):
                if self.highlighted is not None:
                    self._choose(self.highlighted)
            else:
                return False
            return True
        return False

    def _text_color(self, highlighted: bool = False) -> pg.Color:
        if highlighted:
            return utils.best_contrast_color(self.highlight_color)
        if self.text_color is not None:
            return self.text_color
        return utils.best_contrast_color(self.color)

    def _draw_box(self, surface: pg.Surface, rect: pg.Rect, fill: pg.Color) -> None:
        outline = None if self.outline_color is None else self._paint(self.outline_color)
        utils.draw_rounded_rect(
            surface, self._paint(fill), rect, self.border_radius, outline_color=outline
        )

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        if not self.visible:
            return
        self.rect = pg.Rect(x, y, self._width(), self.font.get_height() + 2 * PAD_Y)
        if self._pressed == HEADER:
            fill = utils.shade(self.color, 0.25)
        elif self.is_open or self.hovered:
            fill = utils.shade(self.color, 0.08)
        else:
            fill = self.color
        self._draw_box(surface, self.rect, fill)
        label = self._header
        label.text, label.color, label.enabled = self.value, self._text_color(), self.enabled
        label.draw(surface, x + PAD_X, self.rect.centery - label.surface.get_height() // 2)
        self._draw_arrow(surface, self._paint(label.color))
        if not self.is_open:
            return
        menu = self._menu_rect()
        shadow = menu.move(0, 3)
        utils.draw_transparent_rect_with_border_radius(
            surface, pg.Color("black"), shadow, self.border_radius, 40
        )
        self._draw_box(surface, menu, self.color)
        for i, option_label in enumerate(self._labels):
            row = self._row_rect(i)
            if i == self.highlighted:
                fill = self.highlight_color
            elif i == self._index:
                fill = utils.shade(self.color, 0.1)
            else:
                fill = self.color
            if fill != self.color:
                utils.draw_rounded_rect(surface, fill, row, self.border_radius - 2)
            option_label.color = self._text_color(i == self.highlighted)
            label_y = row.centery - option_label.surface.get_height() // 2
            option_label.draw(surface, x + PAD_X, label_y)

    def _draw_arrow(self, surface: pg.Surface, color: pg.Color) -> None:
        cx, cy = self.rect.right - PAD_X - ARROW // 2, self.rect.centery
        half, rise = ARROW // 2, -(ARROW // 4) if self.is_open else ARROW // 4
        points = [(cx - half, cy - rise), (cx, cy + rise), (cx + half, cy - rise)]
        pg.draw.lines(surface, color, False, points, 2)
