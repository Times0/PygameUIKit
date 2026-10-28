import pygame as pg
from pygame import Color
from pygame.typing import ColorLike


def draw_transparent_rect_with_border_radius(screen, color, rect, border_radius, alpha):
    surf = pg.Surface(rect.size, pg.SRCALPHA)
    pg.draw.rect(surf, color, surf.get_rect().inflate(-1, -1), border_radius=border_radius)
    surf.set_alpha(alpha)
    screen.blit(surf, rect)


def _luma(color: pg.Color) -> float:
    return 0.299 * color.r + 0.587 * color.g + 0.114 * color.b


def best_contrast_color(color: ColorLike) -> Color:
    """Black or white, whichever reads better on ``color``."""
    return Color("black") if _luma(Color(color)) >= 150 else Color("white")


def shade(color: ColorLike, amount: float) -> Color:
    """Mix ``color`` toward black (toward white if it is very dark) by ``amount`` in 0..1."""
    color = Color(color)
    shaded = color.lerp("white" if _luma(color) < 60 else "black", amount)
    shaded.a = color.a
    return shaded


def disabled_color(color: ColorLike) -> Color:
    """``color`` mostly desaturated and faded toward white: how disabled widgets are drawn."""
    color = Color(color)
    grey = round(_luma(color))
    faded = color.lerp((grey, grey, grey), 0.7).lerp("white", 0.45)
    faded.a = color.a
    return faded


def disabled_image(image: pg.Surface) -> pg.Surface:
    """A greyscale, translucent copy of ``image`` to match ``disabled_color``."""
    faded = pg.transform.grayscale(image)
    faded.set_alpha(140)
    return faded


def load_image(path, size=None) -> pg.Surface:
    image = pg.image.load(path)
    if size is not None:
        image = pg.transform.scale(image, size)
    return image


def lighter_color(color: Color, strength: int = 50) -> Color:
    return Color(color.r, color.g, color.b, max(0, min(255, color.a - strength)))


def set_system_cursor(cursor):
    """Some SDL drivers (including headless ones) do not provide system cursors."""
    try:
        pg.mouse.set_cursor(cursor)
    except pg.error:
        pass


def get_font(size: int = 30) -> pg.font.Font:
    """Create fonts when widgets are constructed, never at import time."""
    if not pg.font.get_init():
        pg.font.init()
    return pg.font.Font(None, size)
