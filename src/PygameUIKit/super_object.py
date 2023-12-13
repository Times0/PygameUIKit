import pygame as pg
from pygame import Color

pg.font.init()
FONT = pg.font.SysFont("Arial", 20)


class EasyObject:
    def __init__(self, *, ui_group=None, font=FONT):
        if ui_group:
            ui_group.add(self)
        self.font = font
        self.x = 0
        self.y = 0
        self.w = 0
        self.h = 0
        self.rect = pg.Rect(self.x, self.y, self.w, self.h)

        self.hovered = False

    def update_pos(self, x, y):
        """ This is used when an object is on a surface. Its position relative to the surface might be (0,0)
        but its position relative to the screen is not. This function updates the position of the object
        """
        self.rect.x += x
        self.rect.y += y
        self.x = x
        self.y = y


class Group:
    def __init__(self, *objects):
        self.objects = []
        for obj in objects:
            self.objects.append(obj)

    def add(self, obj):
        self.objects.append(obj)

    def remove(self, obj):
        self.objects.remove(obj)

    def draw(self, screen, x, y):
        for obj in self.objects:
            obj.draw(screen, x, y)

    def handle_event(self, event):
        for obj in self.objects:
            if hasattr(obj, "handle_event"):
                obj.handle_event(event)

    def update(self, dt):
        for obj in self.objects:
            if hasattr(obj, "update"):
                obj.update(dt)


class ObjectWithText(EasyObject):
    def __init__(self, fontsize, ui_group=None):
        super().__init__(ui_group=ui_group)
        self.font = pg.font.SysFont("Arial", fontsize)
        self.color = Color("white")
