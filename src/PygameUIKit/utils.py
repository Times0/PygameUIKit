import pygame as pg
from pygame import Color
from pygame.typing import ColorLike


def draw_transparent_rect_with_border_radius(screen, color, rect, border_radius, alpha):
    color = Color(color)
    surf = pg.Surface(rect.size, pg.SRCALPHA)
    surf.fill((color.r, color.g, color.b, 0))  # antialiased edges blend toward color, not black
    draw_rounded_rect(surf, color, surf.get_rect(), border_radius)
    surf.set_alpha(alpha)
    screen.blit(surf, rect)


def draw_rounded_rect(
    surface: pg.Surface,
    color: ColorLike,
    rect: pg.Rect,
    radius: int,
    *,
    outline_color: ColorLike | None = None,
    outline_width: int = 1,
) -> None:
    """A filled rectangle with antialiased rounded corners, optionally inside an outline.

    The outline is drawn as the whole shape in ``outline_color`` with the fill inset by
    ``outline_width`` on top, so the fill should be opaque.
    """
    rect = pg.Rect(rect)
    if outline_color is not None and outline_width > 0:
        _fill_rounded_rect(surface, outline_color, rect, radius)
        rect = rect.inflate(-2 * outline_width, -2 * outline_width)
        radius -= outline_width
    _fill_rounded_rect(surface, color, rect, radius)


def _fill_rounded_rect(surface: pg.Surface, color: ColorLike, rect: pg.Rect, radius: int) -> None:
    if rect.w <= 0 or rect.h <= 0:
        return
    radius = min(radius, rect.w // 2, rect.h // 2)
    if radius < 1:
        surface.fill(color, rect)
        return
    # Three bands rather than two overlapping rectangles: fill cost grows with the row count.
    band = pg.Rect(rect.x + radius, rect.y, rect.w - 2 * radius, radius)
    surface.fill(color, band)
    surface.fill(color, band.move(0, rect.h - radius))
    surface.fill(color, rect.inflate(0, -2 * radius))
    left, top = rect.x + radius, rect.y + radius
    right, bottom = rect.right - radius - 1, rect.bottom - radius - 1
    pg.draw.aacircle(surface, color, (left, top), radius, draw_top_left=True)
    pg.draw.aacircle(surface, color, (right, top), radius, draw_top_right=True)
    pg.draw.aacircle(surface, color, (left, bottom), radius, draw_bottom_left=True)
    pg.draw.aacircle(surface, color, (right, bottom), radius, draw_bottom_right=True)


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
