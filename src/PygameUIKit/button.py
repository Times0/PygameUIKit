from collections.abc import Callable

import pygame as pg
from pygame.typing import ColorLike

from . import utils
from .label import Label
from .widget import Group, Widget


class _Clickable(Widget):
    """Calls ``on_click()`` when the left button is pressed and released inside ``rect``."""

    cursor = pg.SYSTEM_CURSOR_HAND

    def __init__(self, on_click: Callable[[], None] | None, *, ui_group: Group | None):
        super().__init__(ui_group=ui_group)
        self.on_click = on_click
        self.pressed = False

    def handle_event(self, event: pg.event.Event) -> bool:
        if not self.interactive:
            return False
        if event.type == pg.WINDOWFOCUSLOST:
            self._reset()
        elif event.type == pg.MOUSEMOTION:
            self.hovered = self.rect.collidepoint(event.pos)
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            self.pressed = self.rect.collidepoint(event.pos)
            return self.pressed
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1 and self.pressed:
            self.pressed = False
            if self.rect.collidepoint(event.pos):
                self._activate()
                return True
        return False

    def _reset(self) -> None:
        super()._reset()
        self.pressed = False

    def _activate(self) -> None:
        if self.on_click is not None:
            self.on_click()


class Button(_Clickable):
    """A rounded button with a text label, sized to fit unless ``width`` is given.

    ``play = Button("Play", start_game, color="seagreen", ui_group=ui)``;
    ``play.draw(screen, x, y)`` every frame. Hover and press shades are derived from ``color``
    and the text is black or white for contrast unless ``text_color`` is set.
    """

    def __init__(
        self,
        text: str,
        on_click: Callable[[], None] | None = None,
        *,
        color: ColorLike = (59, 130, 246),
        text_color: ColorLike | None = None,
        border_radius: int = 6,
        outline_color: ColorLike | None = None,
        padding: tuple[int, int] = (16, 8),
        font: pg.font.Font | None = None,
        width: int | None = None,
        align: str = "center",
        ui_group: Group | None = None,
    ):
        if border_radius < 0:
            raise ValueError("border_radius must not be negative")
        if len(padding) != 2 or min(padding) < 0:
            raise ValueError("padding must be two non-negative numbers (x, y)")
        if width is not None and width <= 0:
            raise ValueError("width must be positive")
        self.color = pg.Color(color)
        self.text_color = None if text_color is None else pg.Color(text_color)
        self.outline_color = None if outline_color is None else pg.Color(outline_color)
        self.border_radius = border_radius
        self.padding = padding
        self.width = width
        self.label = Label(text, self._text_color(), font=font, align=align)
        super().__init__(on_click, ui_group=ui_group)
        self._resize()

    @property
    def text(self) -> str:
        return self.label.text

    @text.setter
    def text(self, value: str) -> None:
        self.label.text = value
        self._resize()

    def _text_color(self) -> pg.Color:
        if self.text_color is not None:
            return self.text_color
        return utils.best_contrast_color(self.color)

    def _resize(self) -> None:
        text_width, text_height = self.label.surface.get_size()
        pad_x, pad_y = self.padding
        self.rect.size = (self.width or text_width + 2 * pad_x, text_height + 2 * pad_y)

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        if not self.visible:
            return
        self._resize()
        self.rect.topleft = (x, y)
        if self.pressed:
            fill = utils.shade(self.color, 0.25)
        elif self.hovered:
            fill = utils.shade(self.color, 0.12)
        else:
            fill = self.color
        pg.draw.rect(surface, self._paint(fill), self.rect, border_radius=self.border_radius)
        if self.outline_color is not None:
            outline = self._paint(self.outline_color)
            pg.draw.rect(surface, outline, self.rect, 2, border_radius=self.border_radius)
        self.label.color = self._text_color()
        self.label.enabled = self.enabled
        pad_x = self.padding[0]
        label_y = y + (self.rect.h - self.label.surface.get_height()) // 2
        self.label.draw(surface, x + pad_x, label_y, self.rect.w - 2 * pad_x)


class ImageButton(_Clickable):
    """A clickable image, optionally swapped for ``hover_image`` and with centered ``text``.

    ``ImageButton(pg.image.load("play.png"), start_game, ui_group=ui).draw(screen, x, y)``
    """

    def __init__(
        self,
        image: pg.Surface,
        on_click: Callable[[], None] | None = None,
        *,
        hover_image: pg.Surface | None = None,
        text: str = "",
        text_color: ColorLike = "white",
        font: pg.font.Font | None = None,
        ui_group: Group | None = None,
    ):
        self.image = image
        self.hover_image = hover_image
        self.label = Label(text, text_color, font=font, align="center")
        super().__init__(on_click, ui_group=ui_group)
        self.rect = image.get_rect()

    @property
    def text(self) -> str:
        return self.label.text

    @text.setter
    def text(self, value: str) -> None:
        self.label.text = value

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        if not self.visible:
            return
        image = self.image
        if self.hover_image is not None and (self.hovered or self.pressed):
            image = self.hover_image
        self.rect = image.get_rect(topleft=(x, y))
        surface.blit(image if self.enabled else utils.disabled_image(image), self.rect)
        self.label.enabled = self.enabled
        label_y = self.rect.centery - self.label.surface.get_height() // 2
        self.label.draw(surface, x, label_y, self.rect.w)


class IconButton(_Clickable):
    """An icon with a translucent rounded backdrop while hovered or pressed.

    ``IconButton(icon, open_settings, ui_group=ui).draw(screen, x, y)``; the clickable area is
    the icon plus ``padding`` on every side, starting at (x, y).
    """

    def __init__(
        self,
        image: pg.Surface,
        on_click: Callable[[], None] | None = None,
        *,
        hover_color: ColorLike = (128, 128, 128),
        hover_alpha: int = 128,
        padding: int = 6,
        border_radius: int = 6,
        ui_group: Group | None = None,
    ):
        if not 0 <= hover_alpha <= 255:
            raise ValueError("hover_alpha must be between 0 and 255")
        if padding < 0 or border_radius < 0:
            raise ValueError("padding and border_radius must not be negative")
        self.image = image
        self.hover_color = pg.Color(hover_color)
        self.hover_alpha = hover_alpha
        self.padding = padding
        self.border_radius = border_radius
        super().__init__(on_click, ui_group=ui_group)
        width, height = image.get_size()
        self.rect = pg.Rect(0, 0, width + 2 * padding, height + 2 * padding)

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        if not self.visible:
            return
        width, height = self.image.get_size()
        self.rect = pg.Rect(x, y, width + 2 * self.padding, height + 2 * self.padding)
        if self.hovered or self.pressed:
            alpha = min(255, self.hover_alpha * 3 // 2) if self.pressed else self.hover_alpha
            utils.draw_transparent_rect_with_border_radius(
                surface, self.hover_color, self.rect, self.border_radius, alpha
            )
        image = self.image if self.enabled else utils.disabled_image(self.image)
        surface.blit(image, (x + self.padding, y + self.padding))


class IconToggle(IconButton):
    """An icon button that switches between two images; ``on_change(value)`` gets the new state.

    ``pause = IconToggle(play_icon, pause_icon, lambda playing: print(playing), ui_group=ui)``.
    Read or set ``pause.value``; setting it does not call ``on_change``.
    """

    def __init__(
        self,
        image_off: pg.Surface,
        image_on: pg.Surface,
        on_change: Callable[[bool], None] | None = None,
        *,
        value: bool = False,
        hover_color: ColorLike = (128, 128, 128),
        hover_alpha: int = 128,
        padding: int = 6,
        border_radius: int = 6,
        ui_group: Group | None = None,
    ):
        self.image_off = image_off
        self.image_on = image_on
        self.on_change = on_change
        self.value = bool(value)
        super().__init__(
            image_on if self.value else image_off,
            hover_color=hover_color,
            hover_alpha=hover_alpha,
            padding=padding,
            border_radius=border_radius,
            ui_group=ui_group,
        )

    def _activate(self) -> None:
        self.value = not self.value
        if self.on_change is not None:
            self.on_change(self.value)

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        if not self.visible:
            return
        self.image = self.image_on if self.value else self.image_off
        super().draw(surface, x, y)
