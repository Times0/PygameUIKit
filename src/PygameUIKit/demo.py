"""A tour of every PygameUIKit widget: run ``pygameuikit-demo``.

Each card shows one widget family, its main options and a one-line summary of its API.
Every callback writes to the event log card. To add a card, write a ``draw_<name>`` method
and add one ``Card`` to ``Demo.cards``.
"""

import argparse
import os
import random
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import pygame as pg

from PygameUIKit import (
    BarChart,
    Button,
    Dropdown,
    Group,
    IconButton,
    IconToggle,
    ImageButton,
    Label,
    Slider,
    TextInput,
)

SIZE = (1100, 720)
ASSETS = Path(__file__).parent / "assets"

BACKGROUND = (241, 243, 246)
CARD = (255, 255, 255)
BORDER = (222, 226, 232)
INK = (17, 24, 39)
MUTED = (107, 114, 128)
CODE = (79, 70, 229)
BLUE = (59, 130, 246)
GREEN = (22, 163, 74)
RED = (220, 38, 38)

MARGIN, GAP, PAD = 24, 16, 16
HEADER = 60
COLUMNS = 3
ROWS = (202, 158, 244)  # card heights, top to bottom

PALETTES = {
    "Ocean": ["#0e7490", "#0891b2", "#06b6d4", "#22d3ee", "#67e8f9", "#0369a1"],
    "Forest": ["#15803d", "#16a34a", "#4ade80", "#65a30d", "#a3e635", "#047857"],
    "Sunset": ["#be185d", "#e11d48", "#f97316", "#f59e0b", "#facc15", "#db2777"],
    "Mono": ["#374151", "#4b5563", "#6b7280", "#9ca3af", "#d1d5db", "#1f2937"],
}


def cell(column: int, row: int, columns: int = 1) -> pg.Rect:
    """The rectangle of the card at ``column``, ``row`` spanning ``columns`` grid columns."""
    width = (SIZE[0] - 2 * MARGIN - (COLUMNS - 1) * GAP) // COLUMNS
    top = HEADER + sum(ROWS[:row]) + row * GAP
    return pg.Rect(
        MARGIN + column * (width + GAP), top, columns * width + (columns - 1) * GAP, ROWS[row]
    )


@dataclass
class Card:
    """A titled panel. ``draw_content(surface, area)`` draws the widgets inside ``area``."""

    title: str
    caption: str
    rect: pg.Rect
    draw_content: Callable[[pg.Surface, pg.Rect], None]

    def draw(self, surface: pg.Surface, title_font: pg.font.Font, code_font: pg.font.Font):
        pg.draw.rect(surface, CARD, self.rect, border_radius=10)
        pg.draw.rect(surface, BORDER, self.rect, 1, border_radius=10)
        x, y = self.rect.x + PAD, self.rect.y + PAD
        surface.blit(title_font.render(self.title, True, INK), (x, y))
        y += title_font.get_height() + 4
        surface.blit(code_font.render(self.caption, True, CODE), (x, y))
        y += code_font.get_height() + 14
        self.draw_content(surface, pg.Rect(x, y, self.rect.w - 2 * PAD, self.rect.bottom - y - PAD))


def badge(size: tuple[int, int], top: pg.typing.ColorLike, bottom: pg.typing.ColorLike):
    """A rounded gradient image. Normally you would ``pg.image.load`` one instead."""
    gradient = pg.Surface((1, 2), pg.SRCALPHA)
    gradient.set_at((0, 0), top)
    gradient.set_at((0, 1), bottom)
    image = pg.transform.smoothscale(gradient, size)
    mask = pg.Surface(size, pg.SRCALPHA)
    pg.draw.rect(mask, "white", mask.get_rect(), border_radius=size[1] // 2)
    image.blit(mask, (0, 0), special_flags=pg.BLEND_RGBA_MIN)
    return image


class Demo:
    def __init__(self):
        self.screen = pg.display.set_mode(SIZE)
        pg.display.set_caption("PygameUIKit demo")
        self.clock = pg.time.Clock()
        self.done = False
        self.events: deque[str] = deque(maxlen=8)

        self.card_font = pg.font.Font(None, 28)
        self.code_font = pg.font.SysFont("consolas,menlo,dejavusansmono,monospace", 15)
        self.font = pg.font.Font(None, 22)
        self.small_font = pg.font.Font(None, 20)
        play = pg.image.load(ASSETS / "play.png")
        pause = pg.image.load(ASSETS / "stop.png")

        self.title = Label("PygameUIKit", INK, font=pg.font.Font(None, 40))
        self.subtitle = Label(
            "Every widget and its main options. Callbacks appear in the event log.",
            MUTED,
            font=self.font,
        )

        # Every widget joins one Group, which routes events and sets the mouse cursor.
        self.ui = ui = Group()
        font = self.font

        # Buttons
        self.color_buttons = [
            Button(name, self.on_click(name), color=color, font=font, ui_group=ui)
            for name, color in (("Primary", BLUE), ("Success", GREEN), ("Danger", RED))
        ]
        self.outline_button = Button(
            "Outline",
            self.on_click("Outline"),
            color="white",
            outline_color=BORDER,
            font=font,
            ui_group=ui,
        )
        self.clicks = 0
        self.counter = Button("Clicked 0 times", self.count, color=INK, font=font, ui_group=ui)
        self.aligned_buttons = [
            Button(align, self.on_click(align), width=96, align=align, font=font, ui_group=ui)
            for align in ("left", "center", "right")
        ]

        # Icons
        self.icon_button = IconButton(play, self.on_icon_click, ui_group=ui)
        self.animate = IconToggle(play, pause, self.on_animate, ui_group=ui)
        self.image_button = ImageButton(
            badge((120, 36), (129, 140, 248), (79, 70, 229)),
            lambda: self.log("ImageButton.on_click()"),
            hover_image=badge((120, 36), (165, 180, 252), (99, 102, 241)),
            text="Image",
            font=font,
            ui_group=ui,
        )
        self.icon_captions = [
            Label(text, MUTED, font=self.small_font, align="center")
            for text in ("IconButton", "IconToggle", "ImageButton")
        ]
        self.icon_hint = Label("The IconToggle animates the chart", MUTED, font=self.small_font)

        # Label
        self.aligned_labels = [
            Label(f'align="{align}"', INK, font=font, align=align)
            for align in ("left", "center", "right")
        ]
        self.label_hint = Label(
            "draw(surface, x, y, width) aligns in width", MUTED, font=self.small_font
        )

        # Slider
        self.int_slider = Slider(
            0,
            100,
            value=40,
            show_value=True,
            on_change=lambda value: self.log(f"Slider.on_change({value})", replace=True),
            ui_group=ui,
        )
        self.float_slider = Slider(
            0,
            1,
            0.05,
            value=0.5,
            show_value=True,
            fill_color=GREEN,
            on_change=lambda value: self.log(f"Slider.on_change({value})", replace=True),
            ui_group=ui,
        )
        self.slider_labels = [Label(text, INK, font=font) for text in ("Integer", "Step 0.05")]
        self.slider_hint = Label("Hover, then Left/Right or Home/End", MUTED, font=self.small_font)

        # TextInput
        self.text_input = TextInput(
            placeholder="Type, then press Enter",
            on_change=lambda text: self.log(f"TextInput.on_change({text!r})", replace=True),
            on_submit=self.on_submit,
            width=cell(1, 1).w - 2 * PAD,
            ui_group=ui,
        )
        self.submitted = Label("Submitted: (nothing yet)", INK, font=font)
        self.text_hint = Label("Click to focus, Escape to unfocus", MUTED, font=self.small_font)

        # Dropdown
        self.palette = Dropdown(list(PALETTES), on_change=self.on_palette, ui_group=ui)
        self.palette_label = Label("Chart colors", INK, font=font)
        self.palette_value = Label("", MUTED, font=self.small_font)

        # BarChart
        self.chart = BarChart(
            [40, 75, 30, 90, 55, 65],
            labels=["Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
            max_value=100,
            colors=PALETTES[self.palette.value],
            font=self.small_font,
            label_color=MUTED,
            ui_group=ui,
        )
        self.randomize = Button("Randomize", self.on_randomize, font=font, ui_group=ui)
        self.chart_hints = [
            Label(text, MUTED, font=self.small_font)
            for text in (
                "Press R (ignored while typing)",
                "Animate with the IconToggle",
                "Recolor with the Dropdown",
            )
        ]
        self.animation_timer = 0.0

        self.log_empty = Label("Interact with a widget...", MUTED, font=self.code_font)

        # The layout lives here. Cards are drawn in this order, so the Dropdown card comes
        # last: its open menu then covers the cards below it.
        self.cards = [
            Card("Buttons", 'Button("OK", on_click, color=...)', cell(0, 0), self.draw_buttons),
            Card("Icons", "IconToggle(off, on, on_change=...)", cell(1, 0), self.draw_icons),
            Card("Label", 'Label("Hi", align="center")', cell(2, 0), self.draw_labels),
            Card("Slider", "Slider(0, 100, on_change=...)", cell(0, 1), self.draw_sliders),
            Card("TextInput", "TextInput(on_submit=...)", cell(1, 1), self.draw_text_input),
            Card(
                "BarChart",
                "BarChart(values, labels=..., max_value=100)",
                cell(0, 2, 2),
                self.draw_chart,
            ),
            Card("Event log", "on_click() / on_change(value)", cell(2, 2), self.draw_log),
            Card("Dropdown", "Dropdown(options, on_change=...)", cell(2, 1), self.draw_dropdown),
        ]

    # Callbacks

    def log(self, event: str, replace: bool = False) -> None:
        """Add ``event`` to the event log; ``replace`` overwrites a run of the same callback."""
        if replace and self.events and self.events[-1].split("(")[0] == event.split("(")[0]:
            self.events[-1] = event
        else:
            self.events.append(event)

    def on_click(self, name: str) -> Callable[[], None]:
        return lambda: self.log(f'Button("{name}").on_click()')

    def count(self) -> None:
        self.clicks += 1
        self.counter.text = f"Clicked {self.clicks} time{'s' * (self.clicks != 1)}"
        self.log(f"Button.on_click()  # click {self.clicks}")

    def on_icon_click(self) -> None:
        self.log("IconButton.on_click()")

    def on_animate(self, value: bool) -> None:
        self.log(f"IconToggle.on_change({value})")

    def on_submit(self, text: str) -> None:
        self.submitted.text = f"Submitted: {text}"
        self.log(f"TextInput.on_submit({text!r})")

    def on_palette(self, value: str) -> None:
        self.chart.colors = PALETTES[value]
        self.log(f"Dropdown.on_change({value!r})")

    def on_randomize(self) -> None:
        self.randomize_chart()
        self.log('Button("Randomize").on_click()')

    def randomize_chart(self) -> None:
        self.chart.values = [random.randint(5, 100) for _ in self.chart.values]

    # Main loop

    def run(self, frames: int | None = None) -> None:
        self.draw()
        count = 0
        while not self.done and (frames is None or count < frames):
            dt = self.clock.tick(60) / 1000
            for event in pg.event.get():
                self.handle_event(event)
            self.update(dt)
            self.draw()
            count += 1

    def handle_event(self, event: pg.event.Event) -> None:
        if event.type == pg.QUIT:
            self.done = True
        # handle_event returns True when a widget used the event, e.g. a key typed into the
        # focused TextInput. Only unused events reach the demo's own shortcuts.
        elif not self.ui.handle_event(event):
            if event.type == pg.KEYDOWN and event.key == pg.K_r:
                self.randomize_chart()

    def update(self, dt: float) -> None:
        self.ui.update(dt)  # animates the chart and repeats held keys in the text input
        if self.animate.value:
            self.animation_timer += dt
            if self.animation_timer >= 0.2:
                self.animation_timer = 0
                self.chart.set_value(random.randrange(6), random.randint(5, 100))

    def draw(self) -> None:
        self.screen.fill(BACKGROUND)
        self.title.draw(self.screen, MARGIN, 20)
        self.subtitle.draw(self.screen, self.title.rect.right + 16, self.title.rect.bottom - 20)
        for card in self.cards:
            card.draw(self.screen, self.card_font, self.code_font)
        pg.display.flip()

    # Cards: each draws its widgets inside ``area``, the card without its title and caption.

    def draw_buttons(self, surface: pg.Surface, area: pg.Rect) -> None:
        x, y = area.topleft
        for btn in self.color_buttons:
            btn.draw(surface, x, y)
            x = btn.rect.right + 8
        x, y = area.x, btn.rect.bottom + 10
        self.outline_button.draw(surface, x, y)
        self.counter.draw(surface, self.outline_button.rect.right + 8, y)
        x, y = area.x, self.counter.rect.bottom + 10
        for btn in self.aligned_buttons:
            btn.draw(surface, x, y)
            x = btn.rect.right + 8

    def draw_icons(self, surface: pg.Surface, area: pg.Rect) -> None:
        widgets = (self.icon_button, self.animate, self.image_button)
        slot = area.w // len(widgets)
        for i, (widget, caption) in enumerate(zip(widgets, self.icon_captions, strict=True)):
            center = area.x + i * slot + slot // 2
            widget.draw(surface, center - widget.rect.w // 2, area.y + 20 - widget.rect.h // 2)
            caption.draw(surface, area.x + i * slot, area.y + 52, slot)
        self.icon_hint.draw(surface, area.x, area.y + 82)

    def draw_labels(self, surface: pg.Surface, area: pg.Rect) -> None:
        box = pg.Rect(area.x, area.y, area.w, 3 * 26 + 8)
        pg.draw.rect(surface, BACKGROUND, box, border_radius=6)
        for i, label in enumerate(self.aligned_labels):
            label.draw(surface, box.x + 10, box.y + 10 + i * 26, box.w - 20)
        self.label_hint.draw(surface, area.x, box.bottom + 10)

    def draw_sliders(self, surface: pg.Surface, area: pg.Rect) -> None:
        for i, (label, bar) in enumerate(
            zip(self.slider_labels, (self.int_slider, self.float_slider), strict=True)
        ):
            y = area.y + 8 + i * 32
            label.draw(surface, area.x, y - label.rect.h // 2 + 3)
            bar.draw(surface, area.x + 98, y, width=160)
        self.slider_hint.draw(surface, area.x, area.y + 66)

    def draw_text_input(self, surface: pg.Surface, area: pg.Rect) -> None:
        self.text_input.draw(surface, area.x, area.y)
        self.submitted.draw(surface, area.x, self.text_input.rect.bottom + 12)
        self.text_hint.draw(surface, area.x, self.submitted.rect.bottom + 10)

    def draw_dropdown(self, surface: pg.Surface, area: pg.Rect) -> None:
        self.palette_label.draw(surface, area.x, area.y + 10)
        self.palette_value.text = f"value={self.palette.value!r}  index={self.palette.index}"
        self.palette_value.draw(surface, area.x, area.y + 52)
        self.palette.draw(surface, area.x + 120, area.y)

    def draw_chart(self, surface: pg.Surface, area: pg.Rect) -> None:
        chart_width = area.w - 240
        self.chart.draw(surface, area.x, area.y, chart_width, area.h - 24)
        x = area.x + chart_width + 24
        self.randomize.draw(surface, x, area.y)
        for i, hint in enumerate(self.chart_hints):
            hint.draw(surface, x, self.randomize.rect.bottom + 14 + i * 22)

    def draw_log(self, surface: pg.Surface, area: pg.Rect) -> None:
        if not self.events:
            self.log_empty.draw(surface, area.x, area.y)
        surface.set_clip(area)
        for i, event in enumerate(self.events):
            text = self.code_font.render(event, True, INK)
            surface.blit(text, (area.x, area.y + i * (self.code_font.get_height() + 1)))
        surface.set_clip(None)


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Explore the PygameUIKit widgets")
    parser.add_argument("--frames", type=int, help="exit after this many frames")
    parser.add_argument("--screenshot", metavar="PATH", help="save the last frame as a PNG, exit")
    args = parser.parse_args(argv)
    frames = args.frames
    if args.screenshot:
        os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # no window needed
        frames = 1 if frames is None else frames
    pg.init()
    try:
        demo = Demo()
        demo.run(frames)
        if args.screenshot:
            pg.image.save(demo.screen, args.screenshot)
    finally:
        pg.quit()


if __name__ == "__main__":
    main()
