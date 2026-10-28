# PygameUIKit

Small UI widgets for Pygame: buttons, sliders, dropdowns, text inputs, labels, and animated bar charts. You control the layout; the kit handles interaction and drawing.

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

uv installs Python and dependencies automatically. The demo is also included in the installed package: `pygameuikit-demo` or `python -m PygameUIKit.demo`.

## Use it

```python
import pygame
from PygameUIKit import Button, Group

pygame.init()
screen = pygame.display.set_mode((640, 360))
clock = pygame.time.Clock()
ui = Group()
hello = Button("Say hello", lambda: print("Hello!"), color=(85, 145, 92), ui_group=ui)

running = True
while running:
    dt = clock.tick(60) / 1000
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        else:
            ui.handle_event(event)
    if not running:
        break
    ui.update(dt)
    screen.fill((30, 32, 36))
    hello.draw(screen, 240, 150)
    pygame.display.flip()

pygame.quit()
```

Add widgets with `ui_group=ui`, forward each event once, and call `ui.update(dt)` with seconds. `ui.handle_event(event)` returns `True` when a widget consumed the event (for example a button click or typing into a focused text input), so you can skip your own handling for it. The group also sets the mouse cursor for the hovered widget. Draw each widget at your chosen position; sliders and charts also take `width` and `height`. Draw dropdowns last so their menus appear above other widgets. Callbacks (`on_click`, `on_change`, `on_submit`) run only for user interaction, never when you set `value` or `text` yourself.

- `Button("Play", on_click, color="seagreen")`: rounded text button sized to its text; set `text` to relabel it. Options: `width` and `align`, `outline_color`, `border_radius`, `padding`, `text_color` (black or white for contrast by default).
- `ImageButton(image, on_click, hover_image=None, text="")`: an image, optionally with centered text.
- `IconButton(icon, on_click)`: an icon with a translucent backdrop on hover.
- `IconToggle(icon_off, icon_on, on_change)`: switches icons on click and calls `on_change(value)`; read or set `value`.
- `Slider(0, 100, 5, value=50, on_change=callback, show_value=True)`: drag, click or use the arrow keys while hovering; read or set `value`.
- `TextInput(placeholder="Name", width=200, on_change=callback, on_submit=callback)`: Enter calls `on_submit(text)`, Escape unfocuses; read or set `text` and `focused`.
- `Dropdown(["One", "Two"], on_change=callback)`: pick with the mouse or Up/Down and Enter; read or set `value` (the option) or `index`.
- `Label("Hello", "white")`: draws at exactly (x, y); `draw(screen, x, y, width)` aligns it within `width` using `align="left" | "center" | "right"`. Set `text` to change it.
- `BarChart([10, 20, 30], labels=["A", "B", "C"], max_value=50)`: animated bars; `set_value(index, value)` or set `values`. Values must be non-negative.

Text inputs use Pygame's `TEXTINPUT` events for Unicode text and `KEYDOWN` for editing. Forward both through `Group`; don't also forward the same events separately to the input. Pass a custom `pygame.font.Font` if you need a particular font or character set.

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
