import subprocess
import sys

import pygame as pg
import pytest

from PygameUIKit import (
    BarChart,
    Checkbox,
    Dropdown,
    Group,
    Label,
    ProgressBar,
    RadioGroup,
    Widget,
    button,
    slider,
    text_input,
    utils,
)
from PygameUIKit.utils import (
    best_contrast_color,
    disabled_color,
    disabled_image,
    lighter_color,
    load_image,
    shade,
)


def mouse(kind, pos=(20, 20), button_number=1):
    return pg.event.Event(kind, pos=pos, button=button_number)


def test_import_does_not_initialize_pygame():
    subprocess.run(
        [
            sys.executable,
            "-c",
            "import pygame; import PygameUIKit; "
            "assert not pygame.get_init(); assert not pygame.font.get_init()",
        ],
        check=True,
    )


@pytest.mark.parametrize(
    "factory",
    [
        lambda: button.Button("Hello"),
        lambda: button.ImageButton(pg.Surface((20, 20)), text="Hello"),
        lambda: Label("Hello"),
        lambda: slider.Slider(0, 10, 1),
        lambda: text_input.TextInput(),
        lambda: Dropdown(["Hello", "World"]),
        lambda: BarChart([1, 2]),
        lambda: Checkbox("Hello"),
        lambda: RadioGroup(["Hello", "World"]),
        lambda: ProgressBar(0.5, show_text=True),
    ],
)
def test_default_fonts_survive_pygame_restart(factory, display):
    factory().draw(display, 10, 10)
    pg.quit()
    pg.init()
    display = pg.display.set_mode((800, 600))
    factory().draw(display, 10, 10)


def test_button_only_activates_for_matching_left_click(display):
    calls = []
    widget = button.Button("Click", lambda: calls.append(True))
    widget.draw(display, 10, 10)
    for kind in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
        widget.handle_event(mouse(kind, button_number=3))
    assert calls == []
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP, (500, 500)))
    assert calls == []
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert calls == [True]
    assert not widget.pressed


def test_button_without_callback_and_image_without_hover(display):
    widget = button.ImageButton(pg.Surface((30, 30)))
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEMOTION))
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP))


def test_color_helpers():
    assert lighter_color(pg.Color(0, 0, 0, 10), 50).a == 0
    assert best_contrast_color("white") == pg.Color("black")
    assert best_contrast_color((40, 60, 160)) == pg.Color("white")
    assert shade((200, 100, 50, 42), 0.5) == pg.Color(100, 50, 25, 42)
    assert shade("black", 0.5) == pg.Color(128, 128, 128)


def test_image_loading_without_display_mode(tmp_path):
    path = tmp_path / "image.png"
    pg.image.save(pg.Surface((5, 5), pg.SRCALPHA), path)
    pg.display.quit()
    assert load_image(path, (10, 10)).get_size() == (10, 10)


def test_group_stops_at_first_consumer_and_survives_removal(display):
    group = Group()
    calls = []
    first = button.Button("First", lambda: group.remove(first), ui_group=group)
    second = button.Button("Second", lambda: calls.append(True), ui_group=group)
    first.draw(display, 10, 10)
    second.draw(display, 10, 10)
    assert group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    assert group.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert calls == []
    assert group.widgets == [second]
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    group.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert calls == [True]
    group.add(second)
    assert group.widgets == [second]


def test_handle_event_reports_consumption(display):
    btn = button.Button("Click")
    btn.draw(display, 10, 10)
    assert not btn.handle_event(mouse(pg.MOUSEMOTION))
    assert not btn.handle_event(mouse(pg.MOUSEBUTTONDOWN, (500, 500)))
    assert btn.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    assert btn.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert not btn.handle_event(mouse(pg.MOUSEBUTTONUP))

    bar = slider.Slider(0, 10, 1)
    bar.draw(display, 100, 100, 200, 5)
    assert not bar.handle_event(mouse(pg.MOUSEBUTTONDOWN, (500, 500)))
    assert bar.handle_event(mouse(pg.MOUSEBUTTONDOWN, (150, 102)))
    assert not bar.handle_event(mouse(pg.MOUSEMOTION, (160, 102)))
    assert bar.handle_event(mouse(pg.MOUSEBUTTONUP, (160, 102)))
    assert not bar.handle_event(mouse(pg.MOUSEBUTTONUP, (160, 102)))

    field = text_input.TextInput(width=100)
    field.draw(display, 10, 10)
    assert not field.handle_event(pg.event.Event(pg.TEXTINPUT, text="x"))
    assert field.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    assert field.handle_event(pg.event.Event(pg.TEXTINPUT, text="x"))
    assert field.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
    assert not field.handle_event(mouse(pg.MOUSEBUTTONDOWN, (500, 500)))

    for widget in (Label("Hi"), BarChart([1])):
        widget.draw(display, 10, 10)
        assert not widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))


def test_clicking_a_button_unfocuses_text_input(display):
    group = Group()
    calls = []
    btn = button.Button("Click", lambda: calls.append(True), ui_group=group)
    field = text_input.TextInput(width=100, ui_group=group)
    btn.draw(display, 10, 10)
    field.draw(display, 10, 100)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, (20, 110)))
    assert field.focused
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    group.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert not field.focused
    assert calls == [True]


def test_group_sets_cursor_of_hovered_widget(display, monkeypatch):
    cursors = []
    monkeypatch.setattr(utils, "set_system_cursor", cursors.append)
    group = Group()
    btn = button.Button("Click", ui_group=group)
    field = text_input.TextInput(width=100, ui_group=group)
    Label("Label", ui_group=group).draw(display, 10, 200)
    btn.draw(display, 10, 10)
    field.draw(display, 10, 100)

    btn.handle_event(mouse(pg.MOUSEMOTION))
    assert cursors == []
    group.handle_event(mouse(pg.MOUSEMOTION))
    group.handle_event(mouse(pg.MOUSEMOTION, (21, 21)))
    assert cursors == [pg.SYSTEM_CURSOR_HAND]
    group.handle_event(mouse(pg.MOUSEMOTION, (20, 110)))
    group.handle_event(mouse(pg.MOUSEMOTION, (20, 205)))
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, (20, 205)))
    assert cursors == [pg.SYSTEM_CURSOR_HAND, pg.SYSTEM_CURSOR_IBEAM, pg.SYSTEM_CURSOR_ARROW]


def test_widget_base_defaults():
    group = Group()
    widget = Widget(ui_group=group)
    assert group.widgets == [widget]
    assert widget.rect == pg.Rect(0, 0, 0, 0)
    assert not widget.hovered and widget.cursor is None
    assert not group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    group.update(0.1)


def test_button_focus_loss_cancels_click(display):
    calls = []
    widget = button.Button("Click", lambda: calls.append(True))
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(pg.event.Event(pg.WINDOWFOCUSLOST))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert calls == []


def click(widget, pos=(20, 20)):
    return [
        widget.handle_event(mouse(kind, pos)) for kind in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP)
    ]


def test_click_needs_press_and_release_inside(display):
    calls = []
    btn = button.Button("Click", lambda: calls.append(True))
    btn.draw(display, 10, 10)
    assert btn.handle_event(mouse(pg.MOUSEBUTTONDOWN, (500, 500))) is False
    assert btn.handle_event(mouse(pg.MOUSEBUTTONUP)) is False
    assert btn.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    assert btn.pressed
    assert not btn.handle_event(mouse(pg.MOUSEBUTTONUP, (500, 500)))
    assert not btn.pressed and calls == []
    assert click(btn) == [True, True]
    assert calls == [True]
    btn.on_click = lambda: calls.append("new")
    click(btn)
    assert calls == [True, "new"]


@pytest.mark.parametrize(
    "factory",
    [
        lambda: button.Button("Hi"),
        lambda: button.ImageButton(pg.Surface((30, 30))),
        lambda: button.IconButton(pg.Surface((30, 30))),
        lambda: button.IconToggle(pg.Surface((30, 30)), pg.Surface((30, 30))),
        lambda: Checkbox("Hi"),
    ],
)
def test_clickables_share_hover_cursor_and_focus_loss(factory, display):
    widget = factory()
    widget.draw(display, 10, 10)
    assert widget.cursor == pg.SYSTEM_CURSOR_HAND
    widget.handle_event(mouse(pg.MOUSEMOTION))
    assert widget.hovered
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.draw(display, 10, 10)
    widget.handle_event(pg.event.Event(pg.WINDOWFOCUSLOST))
    assert not widget.pressed and not widget.hovered
    assert not widget.handle_event(mouse(pg.MOUSEBUTTONUP))


def test_button_auto_size_padding_and_text_property():
    font = pg.font.Font(None, 20)
    btn = button.Button("Hi", font=font, padding=(10, 4))
    text_width, text_height = font.render("Hi", True, "white").get_size()
    assert btn.rect.size == (text_width + 20, text_height + 8)
    btn.text = "A longer label"
    assert btn.text == "A longer label"
    assert btn.rect.w == font.render("A longer label", True, "white").get_width() + 20
    fixed = button.Button("Hi", font=font, width=150)
    fixed.text = "Something else"
    assert fixed.rect.w == 150


def test_button_text_color_and_states(display):
    assert button.Button("x", color="white").label.color == pg.Color("black")
    assert button.Button("x", color="navy").label.color == pg.Color("white")
    assert button.Button("x", color="navy", text_color="gold").label.color == pg.Color("gold")
    btn = button.Button("x", color=(200, 200, 200), outline_color="black", border_radius=0)
    btn.draw(display, 0, 0)
    assert display.get_at((btn.rect.centerx, 0)) == pg.Color("black")
    normal = display.get_at((5, 5))
    btn.handle_event(mouse(pg.MOUSEMOTION, (5, 5)))
    btn.draw(display, 0, 0)
    hovered = display.get_at((5, 5))
    btn.handle_event(mouse(pg.MOUSEBUTTONDOWN, (5, 5)))
    btn.draw(display, 0, 0)
    pressed = display.get_at((5, 5))
    assert normal.r > hovered.r > pressed.r


@pytest.mark.parametrize(
    "kwargs",
    [dict(align="middle"), dict(width=0), dict(padding=(-1, 0)), dict(border_radius=-1)],
)
def test_button_validation_happens_before_joining_group(kwargs):
    group = Group()
    with pytest.raises(ValueError):
        button.Button("x", ui_group=group, **kwargs)
    with pytest.raises(ValueError):
        button.IconButton(pg.Surface((5, 5)), hover_alpha=300, ui_group=group)
    assert group.widgets == []


def test_image_button_hover_image_and_text(display):
    image, hover = pg.Surface((40, 20)), pg.Surface((60, 30))
    widget = button.ImageButton(image, hover_image=hover, text="Go")
    widget.draw(display, 10, 10)
    assert widget.rect == pg.Rect(10, 10, 40, 20)
    widget.handle_event(mouse(pg.MOUSEMOTION))
    widget.draw(display, 10, 10)
    assert widget.rect.size == (60, 30)
    assert widget.label.rect.centerx == widget.rect.centerx
    widget.text = "Stop"
    assert widget.label.text == "Stop"


def test_icon_button_area_includes_padding(display):
    calls = []
    widget = button.IconButton(pg.Surface((20, 20)), lambda: calls.append(1), padding=5)
    assert widget.rect.size == (30, 30)
    widget.draw(display, 10, 10)
    assert widget.rect == pg.Rect(10, 10, 30, 30)
    click(widget, (12, 12))
    assert calls == [1]


def test_icon_toggle_reports_new_value(display):
    values = []
    widget = button.IconToggle(pg.Surface((30, 30)), pg.Surface((40, 40)), values.append)
    widget.draw(display, 10, 10)
    click(widget)
    widget.draw(display, 10, 10)
    assert values == [True] and widget.value
    assert widget.rect.size == (52, 52)
    click(widget)
    assert values == [True, False] and not widget.value
    widget.value = True
    assert values == [True, False]
    assert button.IconToggle(pg.Surface((1, 1)), pg.Surface((1, 1)), value=True).value


@pytest.mark.parametrize("align,offset", [("left", 0), ("center", 25), ("right", 50)])
def test_label_draws_exactly_at_position_and_aligns(align, offset):
    font = pg.font.Font(None, 20)
    label = Label("Hi", font=font, align=align)
    text_width, text_height = font.render("Hi", True, "white").get_size()
    target = pg.Surface((300, 100), pg.SRCALPHA)
    label.draw(target, 10, 20, width=text_width + 50)
    assert label.rect == pg.Rect(10, 20, text_width + 50, text_height)
    bounds = target.get_bounding_rect()
    assert bounds.x - 10 - offset in range(0, 3)
    assert bounds.y >= 20
    label.draw(target, 5, 6)
    assert label.rect == pg.Rect(5, 6, text_width, text_height)


def test_label_rerenders_only_on_change():
    label = Label("Hi", "red")
    surface = label.surface
    label.text = "Hi"
    label.color = (255, 0, 0)
    assert label.surface is surface
    label.text = "Bye"
    assert label.surface is not surface and label.text == "Bye"
    surface = label.surface
    label.color = "blue"
    assert label.surface is not surface and label.color == pg.Color("blue")
    with pytest.raises(ValueError):
        Label("Hi", align="justify")


@pytest.mark.parametrize("low,high", [(10, 20), (-10, 0), (-20, -10), (0, 1)])
def test_slider_uses_actual_range_and_clamps(low, high, display):
    values = []
    widget = slider.Slider(low, high, (high - low) / 10, on_change=values.append)
    widget.draw(display, 100, 100, 200, 6)
    assert widget.fraction == 0
    assert widget.handle_event(mouse(pg.MOUSEBUTTONDOWN, (200, 103)))
    assert widget.value == pytest.approx((low + high) / 2)
    assert widget.fraction == pytest.approx(0.5)
    widget.handle_event(mouse(pg.MOUSEMOTION, (500, 103)))
    assert widget.value == high
    assert widget.handle_event(mouse(pg.MOUSEBUTTONUP, (0, 103)))
    assert widget.value == low
    assert values == [pytest.approx((low + high) / 2), high, low]
    widget.value = high + 100
    assert widget.value == high and len(values) == 3
    widget.draw(display, 100, 100, 200, 6)


def test_slider_steps_are_relative_to_minimum():
    widget = slider.Slider(3, 14, 2, value=7)
    assert widget.value == 7
    widget.value = 8.2
    assert widget.value == 9
    widget.value = 100
    assert widget.value == 14
    assert slider.Slider(0, 10).value == 0


@pytest.mark.parametrize(
    "args,kwargs",
    [
        ((0, 0, 1), {}),
        ((2, 1, 1), {}),
        ((0, 1, 0), {}),
        ((0, 1, -1), {}),
        ((0, 1), {"value": float("nan")}),
    ],
)
def test_slider_rejects_invalid_arguments_before_joining_group(args, kwargs):
    group = Group()
    with pytest.raises(ValueError):
        slider.Slider(*args, ui_group=group, **kwargs)
    assert group.widgets == []


def test_slider_on_change_fires_only_for_new_values_from_interaction(display):
    values = []
    widget = slider.Slider(0, 10, value=4, on_change=values.append)
    widget.draw(display, 0, 100, 100, 6)
    widget.value = 6
    assert values == []
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN, (60, 103)))
    widget.handle_event(mouse(pg.MOUSEMOTION, (61, 103)))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP, (61, 103)))
    assert values == []
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN, (80, 103)))
    assert values == [8]
    widget.handle_event(pg.event.Event(pg.WINDOWFOCUSLOST))
    widget.handle_event(mouse(pg.MOUSEMOTION, (90, 300)))
    assert values == [8] and not widget.dragging


def test_slider_keys_step_while_hovered(display):
    values = []
    widget = slider.Slider(3, 14, 2, value=13, on_change=values.append)
    widget.draw(display, 0, 100, 100, 6)
    right = pg.event.Event(pg.KEYDOWN, key=pg.K_RIGHT)
    assert not widget.handle_event(right)
    radius = widget._knob_radius()
    widget.handle_event(mouse(pg.MOUSEMOTION, (50, 103)))
    assert widget._knob_radius() > radius
    assert widget.handle_event(right)
    assert widget.value == 14
    assert widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
    assert widget.value == 13
    widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_HOME))
    widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
    assert widget.value == 3
    widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_END))
    assert values == [14, 13, 3, 14]
    assert not widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_a))


@pytest.mark.parametrize(
    "args,value,text",
    [
        ((0, 100, 5), 50, "50"),
        ((0, 1, 0.1), 0.3, "0.3"),
        ((0, 1, 0.25), 0.5, "0.50"),
        ((0.5, 10, 1), 2.5, "2.5"),
        ((0, 1e-4, 1e-5), 3e-5, "0.00003"),
        ((0, 10, 2.0), 4, "4"),
    ],
)
def test_slider_value_text_uses_step_precision(args, value, text, display):
    widget = slider.Slider(*args, value=value, show_value=True)
    assert widget.value_text == text
    widget.draw(display, 10, 10)


def test_slider_snaps_without_float_drift():
    widget = slider.Slider(0, 1, 0.1)
    widget._nudge(1)
    widget._nudge(1)
    widget._nudge(1)
    assert widget.value == 0.3
    assert isinstance(slider.Slider(0, 100, value=42.4).value, int)


def test_text_input_through_group_unicode_editing_and_focus(display):
    group = Group()
    changes = []
    widget = text_input.TextInput("ab", width=100, on_change=changes.append, ui_group=group)
    widget.draw(display, 10, 10)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    assert widget.focused and widget.event_priority == 1
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_e, unicode="é"))
    group.handle_event(pg.event.Event(pg.TEXTINPUT, text="é世"))
    assert widget.text == "abé世"
    assert widget.caret == 4
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_BACKSPACE))
    assert widget.text == "ab世"
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_DELETE))
    assert widget.text == "ab"
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_DELETE))
    assert changes == ["abé世", "ab世", "ab"]
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, (400, 400)))
    assert not widget.focused
    group.handle_event(pg.event.Event(pg.TEXTINPUT, text="ignored"))
    assert widget.text == "ab"


def test_text_input_repeat_and_scroll(display):
    widget = text_input.TextInput("a" * 100, width=80)
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_BACKSPACE))
    widget.update(0.6)
    assert len(widget.text) < 99
    widget.handle_event(pg.event.Event(pg.KEYUP, key=pg.K_BACKSPACE))
    text = widget.text
    widget.update(1)
    assert widget.text == text
    widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_HOME))
    assert widget._scroll == 0
    widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_END))
    assert widget._scroll > 0
    assert widget.rect.w == 80
    widget.draw(display, 10, 10)


def test_text_input_enter_submits_and_escape_unfocuses(display):
    submitted, changes = [], []
    widget = text_input.TextInput(on_submit=submitted.append, on_change=changes.append)
    widget.draw(display, 10, 10)
    enter = pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN)
    assert not widget.handle_event(enter)
    widget.focused = True
    widget.handle_event(pg.event.Event(pg.TEXTINPUT, text="hi"))
    assert widget.handle_event(enter)
    assert submitted == ["hi"] and widget.focused
    assert widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE))
    assert not widget.focused and widget.event_priority == 0
    assert changes == ["hi"]
    widget.on_submit = None
    widget.focused = True
    widget.handle_event(enter)


def test_text_input_text_setter_moves_caret_without_callback(display):
    changes = []
    widget = text_input.TextInput("start", placeholder="Name", on_change=changes.append)
    assert widget.caret == 5
    widget.draw(display, 10, 10)
    widget.text = ""
    widget.draw(display, 10, 10)
    widget.text = "hello"
    assert widget.caret == 5 and changes == []
    assert text_input.TextInput(width=300).rect.w == 300


@pytest.mark.parametrize("kwargs", [dict(width=10), dict(border_radius=-1)])
def test_text_input_validation_happens_before_joining_group(kwargs):
    group = Group()
    with pytest.raises(ValueError):
        text_input.TextInput(ui_group=group, **kwargs)
    assert group.widgets == []


def option_pos(menu, index):
    return menu._row_rect(index).center


def test_dropdown_selection_and_callback_observe_current_value(display):
    group = Group()
    widget = Dropdown(["One", "A much longer second option"], ui_group=group)
    widget.draw(display, 10, 10)
    assert widget.rect.width >= widget.font.size(widget.options[1])[0] + 30
    values = []
    widget.on_change = lambda value: values.append((value, widget.value, widget.index))
    click(widget)
    assert widget.is_open and widget.event_priority == 1
    widget.draw(display, 10, 10)
    pos = option_pos(widget, 1)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, pos))
    group.handle_event(mouse(pg.MOUSEBUTTONUP, pos))
    assert values == [(widget.options[1], widget.options[1], 1)]
    assert not widget.is_open and widget.event_priority == 0
    click(widget)
    click(widget, option_pos(widget, 1))
    assert len(values) == 1


def test_dropdown_setters_do_not_fire_and_validate():
    values = []
    widget = Dropdown(["A", "B", "C"], index=2, on_change=values.append)
    assert widget.value == "C"
    widget.index = 0
    widget.value = "B"
    assert widget.index == 1 and values == []
    with pytest.raises(IndexError):
        widget.index = 3
    with pytest.raises(ValueError):
        widget.value = "D"
    group = Group()
    for kwargs in (dict(options=[]), dict(options=["A"], width=0)):
        with pytest.raises(ValueError):
            Dropdown(ui_group=group, **kwargs)
    with pytest.raises(IndexError):
        Dropdown(["A"], index=-1, ui_group=group)
    assert group.widgets == []
    assert Dropdown(["A"], width=150).rect.w == 150


def test_dropdown_consumes_clicks_over_other_widgets(display):
    group = Group()
    calls = []
    underneath = button.Button("Under menu", lambda: calls.append(True), ui_group=group)
    menu = Dropdown(["First", "Second"], ui_group=group)
    menu.draw(display, 10, 10)
    underneath.draw(display, 10, 10 + menu.rect.height + 8)
    click(menu)
    pos = option_pos(menu, 0)
    assert underneath.rect.collidepoint(pos)
    assert group.handle_event(mouse(pg.MOUSEBUTTONDOWN, pos))
    assert group.handle_event(mouse(pg.MOUSEBUTTONUP, pos))
    assert not menu.is_open
    assert calls == []
    click(menu)
    assert group.handle_event(mouse(pg.MOUSEBUTTONDOWN, pos, button_number=3))
    assert menu.is_open


def test_dropdown_does_not_select_on_unmatched_release(display):
    menu = Dropdown(["First", "Second"])
    menu.draw(display, 10, 10)
    click(menu)
    assert menu.handle_event(mouse(pg.MOUSEBUTTONUP, option_pos(menu, 1)))
    assert menu.index == 0 and menu.is_open


def test_dropdown_closes_on_outside_click_escape_and_focus_loss(display):
    group = Group()
    calls = []
    menu = Dropdown(["First", "Second"], ui_group=group)
    outside = button.Button("Outside", lambda: calls.append(True), ui_group=group)
    menu.draw(display, 10, 10)
    outside.draw(display, 400, 10)
    click(menu)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, (410, 15)))
    group.handle_event(mouse(pg.MOUSEBUTTONUP, (410, 15)))
    assert not menu.is_open and calls == [True]
    escape = pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE)
    assert not menu.handle_event(escape)
    click(menu)
    assert menu.handle_event(escape)
    assert not menu.is_open
    click(menu)
    menu.handle_event(pg.event.Event(pg.WINDOWFOCUSLOST))
    assert not menu.is_open


def test_dropdown_keyboard_navigation(display):
    values = []
    menu = Dropdown(["A", "B", "C"], on_change=values.append)
    menu.draw(display, 10, 10)
    down = pg.event.Event(pg.KEYDOWN, key=pg.K_DOWN)
    enter = pg.event.Event(pg.KEYDOWN, key=pg.K_RETURN)
    assert not menu.handle_event(down)
    click(menu)
    assert menu.highlighted == 0
    for _ in range(5):
        assert menu.handle_event(down)
    assert menu.highlighted == 2
    menu.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_UP))
    menu.draw(display, 10, 10)
    assert menu.handle_event(enter)
    assert values == ["B"] and not menu.is_open
    assert not menu.handle_event(enter)


def test_open_dropdown_occludes_hover_and_sets_cursor(display, monkeypatch):
    cursors = []
    monkeypatch.setattr(utils, "set_system_cursor", cursors.append)
    group = Group()
    field = text_input.TextInput(width=200, ui_group=group)
    menu = Dropdown(["First", "Second"], ui_group=group)
    menu.draw(display, 10, 10)
    field.draw(display, 10, menu.rect.bottom + 8)
    pos = option_pos(menu, 0)
    assert field.rect.collidepoint(pos)
    group.handle_event(mouse(pg.MOUSEMOTION, pos))
    assert field.hovered and cursors == [pg.SYSTEM_CURSOR_IBEAM]
    click(menu)
    assert group.handle_event(mouse(pg.MOUSEMOTION, pos))
    assert not field.hovered and menu.hovered and menu.highlighted == 0
    assert cursors[-1] == pg.SYSTEM_CURSOR_HAND
    menu.draw(display, 10, 10)
    assert not group.handle_event(mouse(pg.MOUSEMOTION, (500, 500)))
    assert not menu.hovered and menu.highlighted is None
    assert cursors[-1] == pg.SYSTEM_CURSOR_ARROW


@pytest.mark.parametrize("values", [[], [0], [0, 0], [5, 10]])
def test_chart_handles_empty_zero_and_narrow_draws(values, display):
    widget = BarChart(values)
    widget.draw(display, 0, 0, 2, 100)
    if values:
        widget.set_value(0, 100)
        widget.update(1)
        widget.draw(display, 0, 0, 300, 100)
        assert widget.values_displayed[0] == 100


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(values=[-1]),
        dict(values=[1], max_value=0),
        dict(values=[1], labels=[]),
        dict(values=[1], colors=[]),
        dict(values=[1], speed=0),
    ],
)
def test_chart_validation_happens_before_joining_group(kwargs):
    group = Group()
    with pytest.raises(ValueError):
        BarChart(ui_group=group, **kwargs)
    assert group.widgets == []
    with pytest.raises(ValueError):
        BarChart([1]).set_value(0, float("inf"))


def test_chart_values_setter_and_animation_speed(display):
    widget = BarChart([10, 20], speed=10)
    colors = widget.colors
    widget.values = [30, 0]
    assert widget.values == (30, 0) and widget.colors == colors
    widget.update(0.5)
    assert widget.values_displayed == [15, 15]
    widget.values = [1, 2, 3]
    assert widget.values_displayed == [15, 15, 0]
    assert len(widget.colors) == 3 and widget.colors[:2] != colors
    widget.update(10)
    assert widget.values_displayed == [1, 2, 3]
    custom = BarChart([1], colors=["red"], labels=["A"])
    custom.values = [1, 2]
    assert custom.colors == [pg.Color("red")]
    custom.draw(display, 0, 0)
    with pytest.raises(ValueError):
        widget.values = [1, -1]


def test_checkbox_toggles_on_box_and_label_clicks(display):
    calls = []
    box = Checkbox("Sound", on_change=calls.append)
    box.draw(display, 10, 10)
    size = box.rect.h
    assert box.rect.w > 2 * size and box.cursor == pg.SYSTEM_CURSOR_HAND
    assert click(box, (10 + size // 2, box.rect.centery)) == [True, True]
    assert box.value and calls == [True]
    click(box, (box.rect.right - 2, box.rect.centery))
    assert not box.value and calls == [True, False]
    assert click(box, (box.rect.right + 5, box.rect.centery)) == [False, False]
    box.value = True
    box.text = "Music"
    assert box.value and calls == [True, False]
    plain = Checkbox(value=1)
    plain.draw(display, 10, 50)
    assert plain.value is True and plain.rect.w == plain.rect.h


def test_radio_group_selects_clicked_option(display):
    calls = []
    radio = RadioGroup(["Slow", "Normal", "Fast"], index=1, on_change=calls.append)
    radio.draw(display, 10, 10)
    rows = radio._rows
    assert radio.rect == rows[0].unionall(rows[1:]) and rows[1].y > rows[0].bottom
    assert click(radio, (rows[2].right - 2, rows[2].centery)) == [True, True]
    assert (radio.index, radio.value, calls) == (2, "Fast", ["Fast"])
    assert click(radio, (rows[2].x + 2, rows[2].centery)) == [True, True]
    assert calls == ["Fast"]
    radio.handle_event(mouse(pg.MOUSEBUTTONDOWN, rows[0].center))
    radio.handle_event(mouse(pg.MOUSEBUTTONUP, rows[1].center))
    assert radio.index == 2
    gap = (rows[0].centerx, rows[0].bottom + 2)
    assert click(radio, gap) == [False, False]
    radio.handle_event(mouse(pg.MOUSEMOTION, rows[0].center))
    assert radio.hovered and radio.highlighted == 0
    radio.handle_event(mouse(pg.MOUSEMOTION, gap))
    assert not radio.hovered and radio.highlighted is None
    radio.on_change = lambda value: calls.append(radio.value)
    click(radio, rows[0].center)
    assert calls == ["Fast", "Slow"]


def test_radio_group_horizontal_layout(display):
    radio = RadioGroup(["A", "B"], direction="horizontal", spacing=20)
    radio.draw(display, 10, 10)
    first, second = radio._rows
    assert second.x == first.right + 20 and second.y == first.y
    assert radio.rect.h == first.h


def test_radio_group_setters_do_not_fire_and_validate():
    calls = []
    radio = RadioGroup(["A", "B", "C"], index=2, on_change=calls.append)
    assert radio.value == "C"
    radio.index = 0
    radio.value = "B"
    assert radio.index == 1 and calls == []
    with pytest.raises(IndexError):
        radio.index = 3
    with pytest.raises(IndexError):
        radio.index = -1
    with pytest.raises(ValueError):
        radio.value = "D"
    group = Group()
    for kwargs in (dict(options=[]), dict(direction="diagonal"), dict(spacing=-1)):
        with pytest.raises(ValueError):
            RadioGroup(**{"options": ["A"], **kwargs}, ui_group=group)
    with pytest.raises(IndexError):
        RadioGroup(["A"], index=1, ui_group=group)
    assert group.widgets == []


def test_progress_bar_clamps_and_reports_fraction(display):
    bar = ProgressBar(2)
    assert bar.value == 1 and bar.fraction == 1 and bar.percent_text == "100%"
    bar.value = -3
    assert bar.value == 0 and bar.fraction == 0
    bar = ProgressBar(25, max_value=50, color="red", track_color="black")
    assert bar.fraction == 0.5 and bar.percent_text == "50%"
    bar.max_value = 20
    assert bar.fraction == 1
    bar.max_value = 100
    display.fill("white")
    bar.draw(display, 10, 10, width=100, height=10)
    assert bar.rect == pg.Rect(10, 10, 100, 10)
    assert display.get_at((30, 15)) == pg.Color("red")
    assert display.get_at((50, 15)) == pg.Color("black")
    assert not bar.handle_event(mouse(pg.MOUSEBUTTONDOWN, (30, 15))) and bar.cursor is None
    with pytest.raises(ValueError):
        bar.value = float("nan")
    with pytest.raises(ValueError):
        bar.draw(display, 0, 0, width=0)
    group = Group()
    for kwargs in (dict(max_value=0), dict(max_value=float("inf")), dict(border_radius=-1)):
        with pytest.raises(ValueError):
            ProgressBar(ui_group=group, **kwargs)
    with pytest.raises(ValueError):
        ProgressBar(float("nan"), ui_group=group)
    assert group.widgets == []


@pytest.mark.parametrize("state", ["enabled", "visible"])
def test_disabled_or_hidden_choices_ignore_clicks_and_reset(state, display):
    calls = []
    group = Group()
    box = Checkbox("Sound", on_change=calls.append, ui_group=group)
    radio = RadioGroup(["A", "B"], on_change=calls.append, ui_group=group)
    box.draw(display, 10, 10)
    radio.draw(display, 10, 50)
    target = radio._rows[1].center
    for widget, pos in ((box, box.rect.center), (radio, target)):
        widget.handle_event(mouse(pg.MOUSEMOTION, pos))
        widget.handle_event(mouse(pg.MOUSEBUTTONDOWN, pos))
    assert box.pressed and radio.highlighted == 1 and radio.hovered
    for widget in (box, radio):
        setattr(widget, state, False)
    assert not box.pressed and not box.hovered
    assert radio.highlighted is None and not radio.hovered
    for widget, pos in ((box, box.rect.center), (radio, target)):
        assert not any(click(widget, pos))
        group.handle_event(mouse(pg.MOUSEBUTTONDOWN, pos))
        group.handle_event(mouse(pg.MOUSEBUTTONUP, pos))
    assert not box.value and radio.index == 0 and calls == []
    setattr(radio, state, True)
    assert not radio.handle_event(mouse(pg.MOUSEBUTTONUP, target))
    click(radio, target)
    assert calls == ["B"]


def interactive_widgets(group, calls):
    return [
        button.Button("Click", lambda: calls.append("click"), ui_group=group),
        button.IconToggle(pg.Surface((20, 20)), pg.Surface((20, 20)), calls.append, ui_group=group),
        slider.Slider(0, 10, on_change=calls.append, ui_group=group),
        text_input.TextInput(width=100, on_change=calls.append, ui_group=group),
        Dropdown(["A", "B"], on_change=calls.append, ui_group=group),
    ]


def poke(widget, send):
    """Hover, click, type into and press keys on ``widget``; return what was consumed."""
    pos = widget.rect.center
    events = [mouse(pg.MOUSEMOTION, pos), mouse(pg.MOUSEBUTTONDOWN, pos)]
    events += [mouse(pg.MOUSEBUTTONUP, pos), pg.event.Event(pg.TEXTINPUT, text="x")]
    events += [pg.event.Event(pg.KEYDOWN, key=key) for key in (pg.K_RIGHT, pg.K_DOWN, pg.K_RETURN)]
    return [send(event) for event in events]


@pytest.mark.parametrize("state", ["enabled", "visible"])
@pytest.mark.parametrize("through_group", [True, False])
def test_disabled_and_hidden_widgets_ignore_events(state, through_group, display):
    group = Group()
    calls = []
    widgets = interactive_widgets(group, calls)
    for i, widget in enumerate(widgets):
        widget.draw(display, 20, 20 + 60 * i)
        setattr(widget, state, False)
    for widget in widgets:
        consumed = poke(widget, group.handle_event if through_group else widget.handle_event)
        assert not any(consumed)
        assert not widget.hovered
    assert calls == []
    assert not widgets[3].focused and not widgets[4].is_open
    setattr(widgets[0], state, True)
    click(widgets[0], widgets[0].rect.center)
    assert calls == ["click"]


@pytest.mark.parametrize("state", ["enabled", "visible"])
def test_disabling_or_hiding_clears_interaction_state(state, display):
    btn, toggle, bar, field, menu = interactive_widgets(Group(), [])
    for i, widget in enumerate((btn, bar, field, menu)):
        widget.draw(display, 20, 20 + 60 * i)
        widget.handle_event(mouse(pg.MOUSEMOTION, widget.rect.center))
        widget.handle_event(mouse(pg.MOUSEBUTTONDOWN, widget.rect.center))
    menu.handle_event(mouse(pg.MOUSEBUTTONUP, menu.rect.center))
    assert btn.pressed and bar.dragging and field.focused and menu.is_open
    for widget in (btn, bar, field, menu):
        assert widget.hovered
        setattr(widget, state, False)
        assert not widget.hovered and widget.event_priority == 0
    assert not btn.pressed and not bar.dragging and not field.focused and not menu.is_open
    setattr(btn, state, True)
    assert not btn.handle_event(mouse(pg.MOUSEBUTTONUP, btn.rect.center))


@pytest.mark.parametrize(
    "factory",
    [
        lambda: Label("Hello"),
        lambda: button.Button("Hello"),
        lambda: button.ImageButton(pg.Surface((30, 30)), text="Hello"),
        lambda: button.IconButton(pg.Surface((30, 30))),
        lambda: button.IconToggle(pg.Surface((30, 30)), pg.Surface((30, 30))),
        lambda: slider.Slider(0, 10, value=5, show_value=True),
        lambda: text_input.TextInput("Hello"),
        lambda: Dropdown(["Hello", "World"]),
        lambda: BarChart([1, 2], labels=["A", "B"]),
        lambda: Checkbox("Hello"),
        lambda: Checkbox(value=True),
        lambda: RadioGroup(["Hello", "World"], direction="horizontal"),
        lambda: ProgressBar(0.5, show_text=True),
    ],
)
def test_hidden_widgets_draw_nothing_and_disabled_ones_draw_dimmed(factory, display):
    widget = factory()

    def pixels_after_draw():
        display.fill((40, 120, 200))
        widget.draw(display, 10, 10)
        return pg.image.tobytes(display, "RGB")

    display.fill((40, 120, 200))
    background = pg.image.tobytes(display, "RGB")
    normal = pixels_after_draw()
    widget.enabled = False
    disabled = pixels_after_draw()
    widget.visible = False
    assert pixels_after_draw() == background
    widget.enabled = widget.visible = True
    assert pixels_after_draw() == normal
    assert normal != background and disabled not in (normal, background)


def test_cursor_resets_when_the_hovered_widget_is_disabled_or_hidden(display, monkeypatch):
    cursors = []
    monkeypatch.setattr(utils, "set_system_cursor", cursors.append)
    group = Group()
    btn = button.Button("Busy", lambda: setattr(btn, "enabled", False), ui_group=group)
    btn.draw(display, 10, 10)
    group.handle_event(mouse(pg.MOUSEMOTION))
    assert cursors == [pg.SYSTEM_CURSOR_HAND]
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    group.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert cursors[-1] == pg.SYSTEM_CURSOR_ARROW
    group.handle_event(mouse(pg.MOUSEMOTION, (21, 21)))
    assert cursors[-1] == pg.SYSTEM_CURSOR_ARROW and not btn.hovered
    btn.enabled = True
    group.handle_event(mouse(pg.MOUSEMOTION))
    assert cursors[-1] == pg.SYSTEM_CURSOR_HAND
    btn.visible = False
    group.update(0.1)
    assert cursors == [pg.SYSTEM_CURSOR_HAND, pg.SYSTEM_CURSOR_ARROW] * 2


def test_group_skips_inactive_custom_widgets():
    calls = []

    class Box(Widget):
        def handle_event(self, event):
            calls.append(event)
            return True

    box = Box()
    group = Group(box)
    assert group.handle_event(mouse(pg.MOUSEMOTION)) and len(calls) == 1
    box.enabled = False
    assert not group.handle_event(mouse(pg.MOUSEMOTION))
    box.enabled, box.visible = True, False
    assert not group.handle_event(mouse(pg.MOUSEMOTION))
    assert len(calls) == 1 and not box.interactive


def test_disabled_color_and_image_helpers():
    blue = pg.Color(59, 130, 246, 200)
    dimmed = disabled_color(blue)
    assert dimmed.a == 200
    assert dimmed.hsva[1] < blue.hsva[1] / 2 and sum(dimmed[:3]) > sum(blue[:3])
    assert disabled_color("white") == pg.Color("white")
    image = pg.Surface((4, 3), pg.SRCALPHA)
    image.fill("red")
    faded = disabled_image(image)
    assert faded.get_size() == (4, 3) and faded.get_alpha() < 255
    r, g, b, _ = faded.get_at((0, 0))
    assert r == g == b


def test_draw_rounded_rect_fill_outline_and_antialiased_corners():
    surface = pg.Surface((40, 30))
    surface.fill("white")
    utils.draw_rounded_rect(surface, "red", pg.Rect(5, 5, 30, 20), 6, outline_color="blue")
    assert surface.get_at((20, 15)) == pg.Color("red")
    assert surface.get_at((20, 5)) == pg.Color("blue") and surface.get_at((5, 15)) == pg.Color(
        "blue"
    )
    assert surface.get_at((5, 5)) == pg.Color("white")
    corner = [surface.get_at((x, y)) for x in range(5, 11) for y in range(5, 11)]
    assert any(c not in (pg.Color("white"), pg.Color("blue"), pg.Color("red")) for c in corner)
    utils.draw_rounded_rect(surface, "red", pg.Rect(0, 0, 0, 10), 6)
