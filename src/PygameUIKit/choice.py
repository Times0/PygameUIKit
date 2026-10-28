from collections.abc import Callable, Sequence

import pygame as pg
from pygame.typing import ColorLike

from . import utils
from .button import _Clickable
from .label import Label
from .widget import Group, Widget

GAP = 8
BORDER = (170, 170, 170)
DIRECTIONS = ("vertical", "horizontal")


def _mark_size(font: pg.font.Font) -> int:
    """The side of a checkbox and the diameter of a radio circle for ``font``."""
    return font.get_height() + 2


class Checkbox(_Clickable):
    """A box with a check mark and an optional label; clicking either toggles ``value``.

    ``sound = Checkbox("Sound", value=True, on_change=set_sound, ui_group=ui)``;
    ``sound.draw(screen, x, y)`` every frame. ``on_change(value)`` gets the new bool; setting
    ``value`` does not call it.
    """

    def __init__(
        self,
        text: str = "",
        *,
        value: bool = False,
        on_change: Callable[[bool], None] | None = None,
        color: ColorLike = (59, 130, 246),
        text_color: ColorLike = "black",
        font: pg.font.Font | None = None,
        ui_group: Group | None = None,
    ):
        self.value = bool(value)
        self.on_change = on_change
        self.color = pg.Color(color)
        self.font = font if font is not None else utils.get_font(24)
        self.label = Label(text, text_color, font=self.font)
        super().__init__(None, ui_group=ui_group)
        self._layout(0, 0)

    @property
    def text(self) -> str:
        return self.label.text

    @text.setter
    def text(self, value: str) -> None:
        self.label.text = value

    @property
    def text_color(self) -> pg.Color:
        return self.label.color

    @text_color.setter
    def text_color(self, value: ColorLike) -> None:
        self.label.color = value

    def _activate(self) -> None:
        self.value = not self.value
        if self.on_change is not None:
            self.on_change(self.value)

    def _layout(self, x: int, y: int) -> pg.Rect:
        """Set ``rect`` for a draw at (x, y) and return the box."""
        size = _mark_size(self.font)
        width, height = size, size
        if self.text:
            text_width, text_height = self.label.surface.get_size()
            width, height = size + GAP + text_width, max(size, text_height)
        self.rect = pg.Rect(x, y, width, height)
        return pg.Rect(x, y + (height - size) // 2, size, size)

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        if not self.visible:
            return
        box = self._layout(x, y)
        radius = max(2, box.w // 5)
        if self.value:
            fill = utils.shade(self.color, 0.25 if self.pressed else 0.12 if self.hovered else 0)
            utils.draw_rounded_rect(surface, self._paint(fill), box, radius)
            self._draw_check(surface, box, self._paint(utils.best_contrast_color(self.color)))
        else:
            fill = utils.shade("white", 0.08) if self.pressed else pg.Color("white")
            border = self.color if self.hovered or self.pressed else pg.Color(BORDER)
            paint = self._paint
            utils.draw_rounded_rect(
                surface, paint(fill), box, radius, outline_color=paint(border), outline_width=2
            )
        if self.text:
            self.label.enabled = self.enabled
            label_y = self.rect.centery - self.label.surface.get_height() // 2
            self.label.draw(surface, box.right + GAP, label_y)

    @staticmethod
    def _draw_check(surface: pg.Surface, box: pg.Rect, color: pg.Color) -> None:
        # Drawn four times larger and scaled down, which smooths the edges and the joint.
        scale = 4
        size = box.w * scale
        mark = pg.Surface((size, size), pg.SRCALPHA)
        mark.fill((color.r, color.g, color.b, 0))  # no dark fringe when scaled
        points = [(0.26 * size, 0.5 * size), (0.43 * size, 0.67 * size), (0.75 * size, 0.33 * size)]
        width = max(2 * scale, round(size / 6))
        pg.draw.lines(mark, color, False, points, width)
        for point in points:
            pg.draw.circle(mark, color, point, width / 2)
        surface.blit(pg.transform.smoothscale(mark, box.size), box)


class RadioGroup(Widget):
    """A list of options with a radio circle each, of which exactly one is selected.

    ``speed = RadioGroup(["Slow", "Fast"], on_change=set_speed, ui_group=ui)``;
    ``speed.draw(screen, x, y)`` every frame. Click an option or its circle to select it.
    ``on_change(value)`` runs when the user picks a different option; setting ``value`` or
    ``index`` does not call it. ``direction="horizontal"`` lays the options out in a row.
    """

    cursor = pg.SYSTEM_CURSOR_HAND

    def __init__(
        self,
        options: Sequence[str],
        *,
        index: int = 0,
        on_change: Callable[[str], None] | None = None,
        direction: str = "vertical",
        spacing: int = 10,
        color: ColorLike = (59, 130, 246),
        text_color: ColorLike = "black",
        font: pg.font.Font | None = None,
        ui_group: Group | None = None,
    ):
        if not options:
            raise ValueError("RadioGroup requires at least one option")
        if not 0 <= index < len(options):
            raise IndexError("RadioGroup index out of range")
        if direction not in DIRECTIONS:
            raise ValueError(f"direction must be one of {DIRECTIONS}, not {direction!r}")
        if spacing < 0:
            raise ValueError("spacing must not be negative")
        self.options = tuple(options)
        self._index = index
        self.on_change = on_change
        self.direction = direction
        self.spacing = spacing
        self.color = pg.Color(color)
        self.text_color = pg.Color(text_color)
        self.font = font if font is not None else utils.get_font(24)
        self.highlighted: int | None = None
        self._pressed: int | None = None
        self._labels = [Label(option, font=self.font) for option in self.options]
        super().__init__(ui_group=ui_group)
        self._layout(0, 0)

    @property
    def index(self) -> int:
        return self._index

    @index.setter
    def index(self, value: int) -> None:
        if not 0 <= value < len(self.options):
            raise IndexError("RadioGroup index out of range")
        self._index = value

    @property
    def value(self) -> str:
        return self.options[self._index]

    @value.setter
    def value(self, value: str) -> None:
        if value not in self.options:
            raise ValueError(f"{value!r} is not one of the options")
        self._index = self.options.index(value)

    def _layout(self, x: int, y: int) -> None:
        """Set ``rect`` and the clickable row of each option for a draw at (x, y)."""
        size = _mark_size(self.font)
        self._rows: list[pg.Rect] = []
        for option in self.options:
            text_width, text_height = self.font.size(option)
            row = pg.Rect(x, y, size + GAP + text_width, max(size, text_height))
            self._rows.append(row)
            if self.direction == "vertical":
                y = row.bottom + self.spacing
            else:
                x = row.right + self.spacing
        self.rect = self._rows[0].unionall(self._rows[1:])

    def _option_at(self, pos: tuple[int, int]) -> int | None:
        return next((i for i, row in enumerate(self._rows) if row.collidepoint(pos)), None)

    def _reset(self) -> None:
        super()._reset()
        self.highlighted = None
        self._pressed = None

    def handle_event(self, event: pg.event.Event) -> bool:
        if not self.interactive:
            return False
        if event.type == pg.WINDOWFOCUSLOST:
            self._reset()
        elif event.type == pg.MOUSEMOTION:
            self.highlighted = self._option_at(event.pos)
            self.hovered = self.highlighted is not None
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self._pressed = self._option_at(event.pos)
            return self._pressed is not None
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self._pressed is not None:
            pressed, self._pressed = self._pressed, None
            if self._option_at(event.pos) == pressed:
                if pressed != self._index:
                    self._index = pressed
                    if self.on_change is not None:
                        self.on_change(self.value)
                return True
        return False

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        if not self.visible:
            return
        self._layout(x, y)
        size = _mark_size(self.font)
        radius = size // 2
        for i, (row, label) in enumerate(zip(self._rows, self._labels, strict=True)):
            center = (row.x + radius, row.centery)
            selected = i == self._index
            border = self.color if selected or i == self.highlighted else pg.Color(BORDER)
            fill = utils.shade("white", 0.08) if i == self._pressed else pg.Color("white")
            pg.draw.aacircle(surface, self._paint(border), center, radius)
            pg.draw.aacircle(surface, self._paint(fill), center, radius - 2)
            if selected:
                dot = utils.shade(self.color, 0.12) if i == self.highlighted else self.color
                pg.draw.aacircle(surface, self._paint(dot), center, radius // 2)
            label.color, label.enabled = self.text_color, self.enabled
            label.draw(surface, row.x + size + GAP, row.centery - label.surface.get_height() // 2)
