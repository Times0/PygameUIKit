import math
from collections.abc import Callable
from decimal import Decimal

import pygame as pg
from pygame.typing import ColorLike

from . import utils
from .widget import Group, Widget


def _decimals(*numbers: float) -> int:
    """How many decimals it takes to write every number in ``numbers`` exactly."""
    return max(0, *(-Decimal(str(n)).normalize().as_tuple().exponent for n in numbers))


class Slider(Widget):
    """A horizontal slider for numbers from ``min`` to ``max`` in multiples of ``step``.

    ``volume = Slider(0, 100, 5, value=50, on_change=set_volume, ui_group=ui)``;
    ``volume.draw(screen, x, y, width=200)`` every frame. Drag or click the track, or press
    Left/Right/Home/End while hovering it. Setting ``value`` does not call ``on_change``.
    """

    cursor = pg.SYSTEM_CURSOR_HAND

    def __init__(
        self,
        min: float,
        max: float,
        step: float = 1,
        *,
        value: float | None = None,
        on_change: Callable[[float], None] | None = None,
        show_value: bool = False,
        font: pg.font.Font | None = None,
        fill_color: ColorLike = (59, 130, 246),
        track_color: ColorLike = (200, 200, 200),
        knob_color: ColorLike = "white",
        text_color: ColorLike = "black",
        ui_group: Group | None = None,
    ):
        if not all(math.isfinite(v) for v in (min, max, step)) or max <= min or step <= 0:
            raise ValueError("Slider requires finite min < max and step > 0")
        self.min = min
        self.max = max
        self.step = step
        self._decimals = _decimals(min, step)
        self.value = min if value is None else value
        self.on_change = on_change
        self.show_value = show_value
        self.font = font if font is not None else utils.get_font(24)
        self.fill_color = pg.Color(fill_color)
        self.track_color = pg.Color(track_color)
        self.knob_color = pg.Color(knob_color)
        self.text_color = pg.Color(text_color)
        self.dragging = False
        super().__init__(ui_group=ui_group)
        self.rect = pg.Rect(0, 0, 200, 6)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float) -> None:
        if not math.isfinite(value):
            raise ValueError("Slider value must be finite")
        value = max(self.min, min(self.max, value))
        if value != self.max:
            steps = round((value - self.min) / self.step)
            value = min(self.max, round(self.min + steps * self.step, self._decimals))
        self._value = value

    @property
    def fraction(self) -> float:
        return (self._value - self.min) / (self.max - self.min)

    @property
    def value_text(self) -> str:
        """The value as shown by ``show_value``, with as many decimals as ``step`` needs."""
        return f"{self._value:.{self._decimals}f}"

    def _reset(self) -> None:
        super()._reset()
        self.dragging = False

    def _knob_radius(self) -> int:
        radius = self.rect.h // 2 + 5
        return radius + 2 if self.hovered or self.dragging else radius

    def _hit(self, pos: tuple[int, int]) -> bool:
        reach = self.rect.h // 2 + 7
        return self.rect.inflate(2 * reach, 2 * reach - self.rect.h).collidepoint(pos)

    def _change(self, value: float) -> None:
        old = self._value
        self.value = value
        if self._value != old and self.on_change is not None:
            self.on_change(self._value)

    def _change_from_x(self, x: int) -> None:
        if self.rect.w > 0:
            fraction = (x - self.rect.x) / self.rect.w
            self._change(self.min + fraction * (self.max - self.min))

    def _nudge(self, steps: int) -> None:
        position = (self._value - self.min) / self.step
        position = math.floor(position + 1e-9) if steps > 0 else math.ceil(position - 1e-9)
        self._change(self.min + (position + steps) * self.step)

    def handle_event(self, event: pg.event.Event) -> bool:
        if not self.interactive:
            return False
        if event.type == pg.WINDOWFOCUSLOST:
            self._reset()
        elif event.type == pg.MOUSEMOTION:
            self.hovered = self._hit(event.pos)
            if self.dragging:
                self._change_from_x(event.pos[0])
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.dragging = self._hit(event.pos)
            if self.dragging:
                self._change_from_x(event.pos[0])
            return self.dragging
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.dragging:
            self._change_from_x(event.pos[0])
            self.dragging = False
            return True
        elif event.type == pg.KEYDOWN and (self.hovered or self.dragging):
            if event.key in (pg.K_LEFT, pg.K_RIGHT):
                self._nudge(1 if event.key == pg.K_RIGHT else -1)
            elif event.key in (pg.K_HOME, pg.K_END):
                self._change(self.min if event.key == pg.K_HOME else self.max)
            else:
                return False
            return True
        return False

    def draw(self, surface: pg.Surface, x: int, y: int, width: int = 200, height: int = 6) -> None:
        if not self.visible:
            return
        if width <= 0 or height <= 0:
            raise ValueError("Slider dimensions must be positive")
        self.rect = pg.Rect(x, y, width, height)
        knob_x = x + round(width * self.fraction)
        fill = self._paint(self.fill_color)
        pg.draw.rect(surface, self._paint(self.track_color), self.rect, border_radius=height // 2)
        filled = pg.Rect(x, y, knob_x - x, height)
        pg.draw.rect(surface, fill, filled, border_radius=height // 2)
        center = (knob_x, self.rect.centery)
        radius = self._knob_radius()
        pg.draw.circle(surface, fill, center, radius)
        pg.draw.circle(surface, self._paint(self.knob_color), center, radius - 2)
        if self.show_value:
            text = self.font.render(self.value_text, True, self._paint(self.text_color))
            reach = height // 2 + 7
            surface.blit(text, text.get_rect(midleft=(self.rect.right + reach + 6, center[1])))
