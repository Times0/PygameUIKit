import pygame as pg


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
