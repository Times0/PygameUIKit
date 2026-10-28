# Changelog

## Unreleased (0.3.0)

0.3.0 is a deliberate breaking cleanup; there are no compatibility aliases.

- Add `Widget`, the base class of every widget, with `rect`, `hovered`, `cursor`, `handle_event(event) -> bool`, `update(dt)` and `draw(surface, x, y, ...)`. `Widget` and `Group` live in `PygameUIKit.widget`.
- Every `handle_event` returns `True` when it consumed the event (button presses and clicks, slider drags, clicks and typing in a focused text input, open-dropdown interactions). `Group.handle_event` stops at the first widget that consumes an event and returns whether one did.
- `Group` now sets the mouse cursor after each `MOUSEMOTION`: the `cursor` of the hovered widget (hand for buttons, sliders and dropdowns; I-beam for text inputs), otherwise the arrow. Widgets no longer change the cursor themselves.
- A focused text input sees mouse clicks first, so clicking another widget still unfocuses it.
- Export `Group`, `Widget` and all widget classes from the top-level package (`from PygameUIKit import Button, Slider`). Submodules remain importable.
- Remove `Group.draw`, which drew every widget at the same position.
- Replace the eight button classes with four: `Button` (rounded text button), `ImageButton`, `IconButton` and `IconToggle`. All click on a left press and release inside the button, cancel on window focus loss, and expose `pressed`.
- `Button` sizes itself to its text (or a fixed `width` with `align`), derives hover and pressed shades from `color`, picks black or white text for contrast unless `text_color` is given, and defaults to `border_radius=6` and `padding=(16, 8)`. `outline_color` draws a 2 px outline. `button.text` is a property that resizes the button.
- `Label(text, color="white", *, font=None, align="left")` draws exactly at (x, y); `draw(surface, x, y, width=None)` aligns the text within `width`. Setting `text` or `color` re-renders only when the value changes.
- `IconButton`'s clickable area and hover backdrop are the icon plus `padding` on each side, starting at (x, y).
- Add `utils.shade(color, amount)`; `utils.best_contrast_color` uses perceived brightness and returns a `pygame.Color`.
- Remove the duplicate root `src/demo.py` and `src/assets/`; the packaged `pygameuikit-demo` is the demo.

### Upgrading from 0.2

- `PygameUIKit.super_object` → `PygameUIKit.widget`; `EasyObject` → `Widget`. `ObjectWithText` and `EasyObject.update_pos` are removed.
- `PygameUIKit.utilis` → `PygameUIKit.utils`; `ligther_color` → `lighter_color`; `get_font` moved from `super_object` to `utils`.
- `label.DEFAULT_FONT` is removed; pass `font=None` (the default) for the default font.
- `Group.objects` → `Group.widgets`. `Group.draw(screen, x, y)` is removed; draw each widget yourself.
- `handle_events(events)` on buttons and text inputs is removed; call `handle_event(event)` per event (or use `Group`).
- Button `is_hover` and text input `hover` → `hovered`.
- `TextInput.cursor` (caret index) → `TextInput.caret`; `cursor` is now the widget's system cursor.
- Button `on_hover()`/`on_unhover()` hooks and Slider `on_hover()`/`on_unhover()` are removed; read `hovered` instead.
- Widgets no longer call `pygame.mouse.set_cursor`; route `MOUSEMOTION` events through a `Group` to get cursor changes.
- Overlapping widgets in a `Group` no longer all react to the same click; only the first one that consumes it does.
- Buttons take `on_click` (second positional argument or keyword) instead of `onclick_f`; reassign `button.on_click` instead of calling `connect()`. `clicked` → `pressed`.
- `ButtonText(text, onclick_f, rect_color=..., font_color=..., fixed_width=..., text_align=...)` → `Button(text, on_click, color=..., text_color=..., width=..., align=...)`. `change_text(text)` → `button.text = text`.
- `ButtonRect(w, h, color, onclick_f)` → `Button(text, on_click, color=..., width=w)` (the height follows the font and `padding`), or an `ImageButton` showing a filled `pygame.Surface((w, h))`.
- `ButtonImage(image, onclick_f, hover_image)` → `ImageButton(image, on_click, hover_image=...)`.
- `ButtonImageText(image, onclick_f, text, text_color, font, image_hover, text_offset)` → `ImageButton(image, on_click, hover_image=..., text=..., text_color=..., font=...)`; text is centered and `text_offset` is removed.
- `ButtonPngIcon(image, onclick_f, hover_color, opacity, inflate)` → `IconButton(image, on_click, hover_color=..., hover_alpha=int(opacity * 255), padding=inflate // 2)`. The icon is now drawn at (x + padding, y + padding).
- `ButtonTwoStates(image_default, image_click, onclick_f)` → `IconToggle(image_off, image_on, on_change)`; `on_change` receives the new `value` (bool) and `state` (1/2) → `value` (False/True).
- `ButtonThreadImage` and `ButtonThreadText` are removed. Set `button.text` (or `image_button.image`) from your own state each frame instead, e.g. `button.text = "Searching..." if thread.is_alive() else "Find match"`.
- `Label(text, font_color, font, text_align, bounding_rect)` → `Label(text, color, font=..., align=...)`. Pass the bounding width to `draw(surface, x, y, width)` instead of `bounding_rect`; the `TextAlignment` enum is removed (use `"left"`, `"center"`, `"right"`). Labels no longer add 10 px of padding: draw at `(x + 10, y + 10)` for the old placement. `label.render_text()` and `label.text_surface` → `label.surface` (re-rendered automatically).
- `utils.make_surface_darker` is removed; use `utils.shade` for colors.

## 0.2.0

- Support Python 3.11–3.15 with pygame-ce, installed automatically as a dependency.
- Use uv for dependency management, Python installation, builds, and publishing; use Ruff for linting and formatting.
- Ship a runnable `pygameuikit-demo` command with all required assets.
- Fix text inputs receiving events through `Group`, Unicode input, editing-key repeat, and scrolling to the cursor.
- Fix slider positions for nonzero and negative ranges, step alignment, clamping, and click-to-seek.
- Fix image-button hover, optional callbacks, toggle state, and thread-status reset behavior.
- Fix dropdown sizing, selection callbacks, and clicks passing through open menus.
- Handle empty and all-zero charts without Seaborn or division errors.
- Create fonts lazily so importing the package doesn't initialize Pygame.
- Add headless regression tests, cross-platform CI, and tag-based releases.

### Upgrading from 0.1

Use a fresh virtual environment: pygame-ce and classic pygame share the `pygame` import name and must not be installed together. Python 3.7–3.10 are no longer supported.

Continue using `import pygame` and `from PygameUIKit import ...`. Forward every Pygame event once through `Group.handle_event`; text inputs now receive characters from `TEXTINPUT`, not `KEYDOWN.unicode`. Call `Group.update(dt)` with elapsed seconds for editing-key repeat and chart animation. Default fonts are created per widget; pass your own `pygame.font.Font` when you need to share one.
