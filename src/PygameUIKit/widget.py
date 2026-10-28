import pygame as pg

from . import utils


class Widget:
    """Base class for every widget.

    Subclasses draw themselves with ``draw(surface, x, y, ...)`` each frame and store the
    drawn area in ``rect``. Pass ``ui_group=group`` to receive events through a ``Group``.
    """

    cursor: int | None = None
    event_priority: int = 0

    def __init__(self, *, ui_group: "Group | None" = None):
        self.rect = pg.Rect(0, 0, 0, 0)
        self.hovered = False
        if ui_group is not None:
            ui_group.add(self)

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
        """
        consumed = False
        for widget in self._by_priority():
            if not consumed:
                consumed = widget.handle_event(event)
            elif event.type == pg.MOUSEMOTION:
                widget.hovered = False
        if event.type == pg.MOUSEMOTION:
            self._update_cursor()
        return consumed

    def update(self, dt: float) -> None:
        for widget in tuple(self.widgets):
            widget.update(dt)

    def _update_cursor(self) -> None:
        cursor = next(
            (w.cursor for w in self._by_priority() if w.hovered and w.cursor is not None),
            pg.SYSTEM_CURSOR_ARROW,
        )
        if cursor != self._cursor:
            self._cursor = cursor
            utils.set_system_cursor(cursor)
