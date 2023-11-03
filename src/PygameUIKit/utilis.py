from typing import Union

import pygame as pg
from pygame import Color


def make_surface_darker(surface: pg.Surface, amount: int = 50) -> pg.Surface:
    """
    Make the given surface darker by the given amount.
    You can make the surface lighter by passing a negative amount.
    :param surface: The surface to make darker.
    :param amount: The amount to make the surface darker by.
    :return: The darker surface.
    """
    new_surface = surface.copy()
    for i in range(new_surface.get_width()):
        for j in range(new_surface.get_height()):
            pixel = new_surface.get_at((i, j))
            new_pixel = (max(0, pixel[0] - amount), max(0, pixel[1] - amount), max(0, pixel[2] - amount), pixel[3])
            new_surface.set_at((i, j), new_pixel)
    return new_surface


def draw_transparent_rect_with_border_radius(screen,color, rect, border_radius, alpha):
    surf = pg.Surface(rect.size, pg.SRCALPHA)
    pg.draw.rect(surf, color, surf.get_rect().inflate(-1, -1), border_radius=border_radius)
    surf.set_alpha(alpha)
    screen.blit(surf, rect)


def best_contrast_color(rgb_color: Union[Color, tuple]):
    if isinstance(rgb_color, Color):
        rgb_color = rgb_color.r, rgb_color.g, rgb_color.b
    r, g, b = rgb_color
    if r + g + b < 500:
        return 255, 255, 255
    else:
        return 0, 0, 0
