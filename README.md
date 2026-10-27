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
from PygameUIKit import Group, button

pygame.init()
screen = pygame.display.set_mode((640, 360))
clock = pygame.time.Clock()
ui = Group()
hello = button.ButtonText(
    "Say hello",
    lambda: print("Hello!"),
    rect_color=(85, 145, 92),
    border_radius=8,
    ui_group=ui,
)

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

Add widgets with `ui_group=ui`, forward each event once, and call `ui.update(dt)` with seconds. Draw each widget at your chosen position. Sliders accept `draw(screen, x, y, width, height)`; charts use the same layout arguments. Draw dropdowns last so their menus appear above other widgets.

- `button`: text, image, icon, toggle, and thread-status buttons.
- `slider.Slider(min, max, step)`: `get_value()` and `connect(callback)`.
- `combobox.ComboBox(["One", "Two"])`: `get_value()` and `add_action(index, callback)`.
- `text_input.TextInput(placeholder="Name")`: `get_text()` and `set_text(text)`.
- `label.Label("Hello", "white")`: update the `text` property.
- `barchart.BarChart([10, 20, 30])`: `change_value(index, value)`; accepts non-negative values.

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
