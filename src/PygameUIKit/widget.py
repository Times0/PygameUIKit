from functools import wraps

import pygame as pg

from . import utils


def _ignored_while_inactive(handle_event):
    @wraps(handle_event)
    def wrapper(self: "Widget", event: pg.event.Event) -> bool:
        return self.enabled and self.visible and handle_event(self, event)

    return wrapper


def _skipped_while_hidden(draw):
    @wraps(draw)
    def wrapper(self: "Widget", *args, **kwargs) -> None:
        if self.visible:
            draw(self, *args, **kwargs)

    return wrapper


class Widget:
    """Base class for every widget.

    Subclasses draw themselves with ``draw(surface, x, y, ...)`` each frame and store the
    drawn area in ``rect``. Pass ``ui_group=group`` to receive events through a ``Group``.
    Set ``enabled = False`` to grey a widget out and ``visible = False`` to hide it; either
    way it ignores events. Every subclass's ``handle_event`` and ``draw`` get these checks.
    """

    cursor: int | None = None
    event_priority: int = 0
    _enabled = True
    _visible = True

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if "handle_event" in vars(cls):
            cls.handle_event = _ignored_while_inactive(cls.handle_event)
        if "draw" in vars(cls):
            cls.draw = _skipped_while_hidden(cls.draw)

    def __init__(self, *, ui_group: "Group | None" = None):
        self.rect = pg.Rect(0, 0, 0, 0)
        self.hovered = False
        if ui_group is not None:
            ui_group.add(self)

    @property
    def enabled(self) -> bool:
        """Disabled widgets are drawn greyed out and ignore events."""
        return self._enabled

    @enabled.setter
    def enabled(self, value: bool) -> None:
        self._enabled = bool(value)
        if not value:
            self._reset()

    @property
    def visible(self) -> bool:
        """Hidden widgets draw nothing and ignore events."""
        return self._visible

    @visible.setter
    def visible(self, value: bool) -> None:
        self._visible = bool(value)
        if not value:
            self._reset()

    def _reset(self) -> None:
        """Drop hover, press, drag, focus and open menus: when disabled, hidden or unfocused."""
        self.hovered = False

    def _paint(self, color: pg.Color) -> pg.Color:
        """``color``, greyed out while the widget is disabled."""
        return color if self._enabled else utils.disabled_color(color)

    def handle_event(self, event: pg.event.Event) -> bool:
        """Handle one event; return True if it was consumed."""
        return False

    def update(self, dt: float) -> None:
        """Advance animations by ``dt`` seconds."""

    def draw(self, surface: pg.Surface, x: int, y: int) -> None:
        raise NotImplementedError


class Group:
    """Forwards events and updates to widgets and sets the mouse cursor.

    ``ui = Group()``; create widgets with ``ui_group=ui``; call ``ui.handle_event(event)``
    for every event and ``ui.update(dt)`` every frame. Draw each widget yourself.
    """

    def __init__(self, *widgets: Widget):
        self.widgets: list[Widget] = []
        self._cursor: int | None = None
        for widget in widgets:
            self.add(widget)

    def add(self, widget: Widget) -> None:
        if widget not in self.widgets:
            self.widgets.append(widget)

    def remove(self, widget: Widget) -> None:
        self.widgets.remove(widget)

    def _by_priority(self) -> list[Widget]:
        # Open menus receive events before the widgets underneath them.
        return sorted(self.widgets, key=lambda widget: widget.event_priority, reverse=True)

    def handle_event(self, event: pg.event.Event) -> bool:
        """Dispatch until a widget consumes the event; return True if one did.

        A widget consumes ``MOUSEMOTION`` when the pointer is over it and it covers what is
        below (an open dropdown menu), so the remaining widgets are marked not hovered.
        Disabled and hidden widgets ignore every event.
        """
        consumed = False
        for widget in self._by_priority():
            if not consumed:
                consumed = widget.handle_event(event)
            elif event.type == pg.MOUSEMOTION:
                widget.hovered = False
        self._update_cursor()
        return consumed

    def update(self, dt: float) -> None:
        for widget in tuple(self.widgets):
            widget.update(dt)
        self._update_cursor()

    def _update_cursor(self) -> None:
        # Also runs after clicks and updates, so disabling or hiding the widget under the
        # pointer gives the arrow back without waiting for the mouse to move.
        cursor = next(
            (w.cursor for w in self._by_priority() if w.hovered and w.cursor is not None),
            pg.SYSTEM_CURSOR_ARROW,
        )
        if cursor != self._cursor:
            self._cursor = cursor
            utils.set_system_cursor(cursor)
