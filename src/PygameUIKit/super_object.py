import pygame as pg
from pygame import Color


class EasyObject:
    def __init__(self, *, ui_group=None):
        if ui_group is not None:
            ui_group.add(self)
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.rect = pg.Rect(self.x, self.y, self.w, self.h)
        self.hovered = False

    def update_pos(self, x, y):
        """This is used when an object is on a surface. Its position relative to the surface might be (0,0)
        but its position relative to the screen is not. This function updates the position of the object
        """
        self.rect.move_ip(x, y)
        self.x, self.y = self.rect.topleft


class Group:
    def __init__(self, *objects):
        self.objects = []
        for obj in objects:
            self.add(obj)

    def add(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)

    def remove(self, obj):
        self.objects.remove(obj)

    def draw(self, screen, x, y):
        for obj in tuple(self.objects):
            obj.draw(screen, x, y)

    def handle_event(self, event):
        # Open menus receive pointer events before widgets underneath them.
        objects = sorted(
            self.objects, key=lambda obj: getattr(obj, "event_priority", 0), reverse=True
        )
        for obj in objects:
            if hasattr(obj, "handle_event") and obj.handle_event(event):
                return True
        return False

    def update(self, dt):
        for obj in tuple(self.objects):
            if hasattr(obj, "update"):
                obj.update(dt)


class ObjectWithText(EasyObject):
    def __init__(self, fontsize, ui_group=None):
        super().__init__(ui_group=ui_group)
        self.font = get_font(fontsize)
        self.color = Color("white")


def get_font(size=30):
    """Create fonts when widgets are constructed, never at import time."""
    if not pg.font.get_init():
        pg.font.init()
    return pg.font.Font(None, size)
