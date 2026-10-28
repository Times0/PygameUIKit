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
- `Label(text, color="black", *, font=None, align="left")` draws exactly at (x, y) (the color is now optional); `draw(surface, x, y, width=None)` aligns the text within `width`. Setting `text` or `color` re-renders only when the value changes.
- `IconButton`'s clickable area and hover backdrop are the icon plus `padding` on each side, starting at (x, y).
- Add `utils.shade(color, amount)`; `utils.best_contrast_color` uses perceived brightness and returns a `pygame.Color`.
- Remove the duplicate root `src/demo.py` and `src/assets/`; the packaged `pygameuikit-demo` is the demo.
- `Slider(min, max, step=1, *, value=None, on_change=None, show_value=False, font=None, fill_color, track_color, knob_color, text_color)` has a `value` property (clamped and snapped to `step`, without float drift) and draws with `draw(surface, x, y, width=200, height=6)`. The knob grows on hover and while dragging. Left/Right step it and Home/End jump to the ends while it is hovered or dragged. `show_value` uses as many decimals as `min` and `step` need (`value_text`).
- `TextInput(text="", *, placeholder="", width=200, font=None, text_color, placeholder_color, background_color, border_color, focus_color, border_radius=4, on_change=None, on_submit=None)` has a fixed width and an opaque background. Enter calls `on_submit(text)`, Escape unfocuses, and `on_change(text)` runs after every edit. `focused` and `text` are settable.
- `Dropdown(options, *, index=0, on_change=None, width=None, font=None, color, text_color, highlight_color, outline_color, border_radius)` replaces `ComboBox`. It draws itself (no longer a `Button` subclass) with a drawn chevron, highlights the hovered and selected options, and can be driven with Up/Down, Enter/Space and Escape while open. While open it consumes mouse events over itself and its menu; a click elsewhere, Escape or window focus loss closes it. `on_change(value)` runs only when the user picks a different option.
- When a widget consumes a `MOUSEMOTION` (an open dropdown menu under the pointer), `Group` marks the widgets after it as not hovered, so nothing underneath an open menu stays highlighted or sets the cursor.
- `BarChart(values, *, labels=None, max_value=None, colors=None, font=None, label_color="black", speed=200)`: `values` is a property (a tuple; setting it replaces all bars and regenerates automatic colors when the count changes), `set_value(index, value)` updates one bar, `colors` cycle if there are fewer than bars, and `speed` is the animation rate in value units per second. Bars are solid with rounded tops.
- Every widget has `enabled` and `visible` properties (both `True` by default). Disabled widgets are drawn greyed out (`utils.disabled_color` and `utils.disabled_image`); hidden widgets draw nothing. Both ignore events, whether they come through a `Group` or a direct `handle_event` call, and turning either off clears hover, press, drag, focus and open menus. `Group` skips widgets that aren't `interactive` (enabled and visible); your own widgets should start `draw` with `if not self.visible: return`.
- `Group` updates the cursor after every event and `update(dt)`, not only after mouse motion, so disabling or hiding the widget under the pointer restores the arrow right away.
- The demo (`pygameuikit-demo`) is rewritten as a showcase: one card per widget family with its main options and API, an event log that shows each callback as it fires, and a States card that disables or hides a set of widgets. `--screenshot PATH` saves a frame as a PNG and exits without opening a window.
- The README has a short guide to the main loop and a reference for every widget.
- Add `Checkbox(text="", *, value=False, on_change=None, color, text_color, font=None)`: a box with an antialiased check mark and an optional label; clicking the box or the label toggles `value` and calls `on_change(value)`.
- Add `RadioGroup(options, *, index=0, on_change=None, direction="vertical", spacing=10, color, text_color, font=None)`: one widget that draws a list of radio options, vertically or horizontally, with `value` and `index` like `Dropdown` and a highlight on the hovered option. `on_change(value)` runs when the user picks a different option.
- Add `ProgressBar(value=0.0, *, max_value=1.0, color, track_color, border_radius=None, show_text=False, font=None, text_color)`: a display-only bar with a clamped `value`, `fraction` and an optional percentage, drawn with `draw(surface, x, y, width=200, height=12)`.
- Add `utils.draw_rounded_rect(surface, color, rect, radius)`, a filled rectangle with antialiased corners.
- The demo has Checkbox and RadioGroup and ProgressBar cards: checkboxes animate the chart (in sync with the IconToggle) and show its values, a horizontal RadioGroup sets the bar speed, and two progress bars loop and follow the Integer slider. The States card also toggles the new widgets. The window is now 1200×860.

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
- Slider: `slider.get_value()` and `slider.current_value` → `slider.value`; `change_value_to(v)` → `slider.value = v` (no callback). `connect(f)` → `on_change=f` (or assign `slider.on_change`); the callback now receives the new value. `font_color` → `text_color`. `step` defaults to 1, and options after `step` are keyword-only. `draw(win, x, y, w=100, h=5)` → `draw(surface, x, y, width=200, height=6)`. `circle_radius`, `draw_bar`, `draw_circle` and `draw_value` are removed.
- TextInput: `text` is now the first positional argument. `fixed_width=None` (auto-grow) → `width=200` (always fixed). `font_color` → `text_color`. `active` → `focused`. `get_text()`/`set_text(t)` → the `text` property (setting it moves the caret to the end). `add_letter`, `remove_letter`, `handle_key`, `draw_placeholder`, `color` and `bg_trans` are removed. Enter and Escape are now handled (submit and unfocus).
- `PygameUIKit.combobox` → `PygameUIKit.dropdown`; `ComboBox(elements, font=..., font_color=...)` → `Dropdown(options, font=..., text_color=...)`. `elements` → `options` (a tuple), `selected_index` → `index`, `get_value()` → `value`, `change_selected(i)` → `index = i` (no callback). `add_action(index, f)` → one `on_change(value)` callback for every selection. `toggle_open()` and `change_hovered()` are removed; `hovered_index` → `highlighted`. The `combo_box_arrow.png` asset is removed.
- BarChart: `labels`, `max_value`, `font` and `ui_group` are keyword-only. `labels_color` → `label_color`. `change_value(index, value)` → `set_value(index, value)`. `values` is read as a tuple; assign a new sequence instead of mutating it. `CHANGE_SPEED` → the `speed` argument.

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
