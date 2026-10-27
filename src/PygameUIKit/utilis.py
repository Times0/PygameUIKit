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
    amount = max(-255, min(255, amount))
    blend = pg.BLEND_RGB_SUB if amount >= 0 else pg.BLEND_RGB_ADD
    new_surface.fill((abs(amount),) * 3, special_flags=blend)
    return new_surface


def draw_transparent_rect_with_border_radius(screen, color, rect, border_radius, alpha):
    surf = pg.Surface(rect.size, pg.SRCALPHA)
    pg.draw.rect(surf, color, surf.get_rect().inflate(-1, -1), border_radius=border_radius)
    surf.set_alpha(alpha)
    screen.blit(surf, rect)


def best_contrast_color(rgb_color: Color | tuple):
    if isinstance(rgb_color, Color):
        rgb_color = rgb_color.r, rgb_color.g, rgb_color.b
    r, g, b = rgb_color[:3]
    if r + g + b < 500:
        return 255, 255, 255
    else:
        return 0, 0, 0


def load_image(path, size=None) -> pg.Surface:
    image = pg.image.load(path)
    if size is not None:
        image = pg.transform.scale(image, size)
    return image


def ligther_color(color: Color, strength: int = 50) -> Color:
    return Color(color.r, color.g, color.b, max(0, min(255, color.a - strength)))


def set_system_cursor(cursor):
    """Some SDL drivers (including headless ones) do not provide system cursors."""
    try:
        pg.mouse.set_cursor(cursor)
    except pg.error:
        pass
