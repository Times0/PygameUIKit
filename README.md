# PygameUIKit

Small UI widgets for Pygame: buttons, sliders, dropdowns, text inputs, labels, and animated bar charts. You control the layout; the kit handles interaction and drawing.

![The PygameUIKit demo: cards showing every widget and an event log](https://raw.githubusercontent.com/Times0/PygameUIKit/master/images/img.png)

Requires Python 3.11+ (tested through 3.15). Uses [pygame-ce](https://pyga.me/), which provides the familiar `import pygame` API. Use a fresh environment when upgrading from classic `pygame`; the two packages share the same import name.

## Install

```sh
uv add PygameUIKit
```

Or use `pip install PygameUIKit`.

## Try it

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed:

```sh
git clone https://github.com/Times0/PygameUIKit.git
cd PygameUIKit
uv run pygameuikit-demo
```

uv installs Python and dependencies automatically. The demo is also included in the installed package: `pygameuikit-demo` or `python -m PygameUIKit.demo`. It shows every widget with its main options, and an event log shows each callback as it fires. Its source, [`demo.py`](https://github.com/Times0/PygameUIKit/blob/master/src/PygameUIKit/demo.py), is meant to be copied from. `--screenshot demo.png` saves one frame without opening a window.

## Use it

```python
import pygame
from PygameUIKit import Button, Dropdown, Group, Label, Slider

pygame.init()
screen = pygame.display.set_mode((640, 360))
clock = pygame.time.Clock()

ui = Group()
title = Label("Volume")
volume = Slider(0, 100, value=50, show_value=True, on_change=print, ui_group=ui)
quality = Dropdown(["Low", "Medium", "High"], on_change=print, ui_group=ui)


def mute():
    volume.value = 0  # setting a value never calls on_change


mute_button = Button("Mute", mute, ui_group=ui)

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif not ui.handle_event(event):
            pass  # no widget used this event: handle your own keys and clicks here
    ui.update(dt)

    screen.fill("white")
    title.draw(screen, 20, 20)
    volume.draw(screen, 20, 60, width=240)
    mute_button.draw(screen, 340, 45)
    quality.draw(screen, 20, 100)  # dropdowns last, so their menu covers other widgets
    pygame.display.flip()

pygame.quit()
```

- **Group.** Pass `ui_group=ui` to every interactive widget. Forward each event once with `ui.handle_event(event)`. It returns `True` when a widget used the event (a button click, typing into a focused text input), so check it before your own handling. Call `ui.update(dt)` with seconds every frame; it animates charts and repeats held keys. After mouse motion, the group sets the cursor of the hovered widget.
- **Drawing.** There is no layout system. Call `widget.draw(surface, x, y, ...)` every frame. The widget stores the drawn area in `widget.rect`, which is also its clickable area. Draw dropdowns last.
- **Callbacks.** `on_click()`, `on_change(value)` and `on_submit(text)` are keyword arguments, and attributes you can reassign; `None` means no callback. They run only for user interaction, never when you set `value` or `text` yourself.
- **Colors and fonts.** Colors are anything `pygame.Color` accepts. Pass `font=pygame.font.Font(...)` for a particular font or character set; default fonts are created when the widget is.

### Widgets

Options after `*` are keyword-only, and every widget also takes `ui_group`.

- `Label(text, color="black", *, font=None, align="left")`. Draws at exactly (x, y). `draw(surface, x, y, width=None)` aligns the text within `width` (`"left"`, `"center"` or `"right"`). Properties: `text`, `color`.
- `Button(text, on_click=None, *, color=(59, 130, 246), text_color=None, outline_color=None, border_radius=6, padding=(16, 8), font=None, width=None, align="center")`. Sized to its text unless `width` is set; `align` places the text within `width`. Hover and pressed shades come from `color`, and the text is black or white for contrast unless `text_color` is set. Properties: `text` (resizes the button), `hovered`, `pressed`. Callback: `on_click()`.
- `ImageButton(image, on_click=None, *, hover_image=None, text="", text_color="white", font=None)`. An image, swapped for `hover_image` while hovered or pressed, with optional centered `text`.
- `IconButton(image, on_click=None, *, hover_color=(128, 128, 128), hover_alpha=128, padding=6, border_radius=6)`. An icon with a translucent backdrop while hovered. The clickable area is the icon plus `padding`, starting at (x, y).
- `IconToggle(image_off, image_on, on_change=None, *, value=False, ...)`. Like `IconButton`, but each click switches `value` and the icon. Callback: `on_change(value)` with the new bool.
- `Slider(min, max, step=1, *, value=None, on_change=None, show_value=False, font=None, fill_color, track_color, knob_color, text_color)`. `draw(surface, x, y, width=200, height=6)`. Drag or click the track; Left/Right, Home and End work while it is hovered. `value` is clamped and snapped to `step`, and `show_value` prints it to the right of the track. Callback: `on_change(value)`.
- `TextInput(text="", *, placeholder="", width=200, font=None, text_color, placeholder_color, background_color, border_color, focus_color, border_radius=4, on_change=None, on_submit=None)`. A fixed-width, single-line field. Click it to focus it; Enter calls `on_submit(text)` and Escape unfocuses. Properties: `text`, `focused`. Callbacks: `on_change(text)` after each edit, `on_submit(text)`. It reads `TEXTINPUT` events for Unicode text and `KEYDOWN` for editing, so forward both, once, through the group.
- `Dropdown(options, *, index=0, on_change=None, width=None, font=None, color, text_color, highlight_color, outline_color, border_radius=6)`. Click to open the menu, then pick with the mouse or with Up/Down and Enter. Escape or a click elsewhere closes it. Properties: `value` (the option), `index`, `is_open`. Callback: `on_change(value)` when the user picks a different option.
- `BarChart(values, *, labels=None, max_value=None, colors=None, font=None, label_color="black", speed=200)`. `draw(surface, x, y, width=300, height=100)`. Bars move toward their values at `speed` units per second during `ui.update(dt)`. `set_value(index, value)` changes one bar; setting `values` replaces them all. Values must be non-negative. Without `labels`, each bar shows its value; without `max_value`, the tallest bar fills the height. `colors` cycle.

## Develop

```sh
uv sync --locked
uv run ruff check .
uv run ruff format --check .
uv run pytest
uv build
```

Tests use SDL's dummy drivers and don't need a display. CI checks Python 3.11–3.15 on Linux and Python 3.15 on Windows and macOS. See [RELEASING.md](https://github.com/Times0/PygameUIKit/blob/master/RELEASING.md) for publishing.

MIT licensed. Contributions welcome.
