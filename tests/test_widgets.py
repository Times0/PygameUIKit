import subprocess
import sys

import pygame as pg
import pytest

from PygameUIKit import Group, Widget, button, slider, text_input, utils
from PygameUIKit.barchart import BarChart
from PygameUIKit.combobox import ComboBox
from PygameUIKit.label import Label, TextAlignment
from PygameUIKit.utils import lighter_color, load_image, make_surface_darker


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
        lambda: button.ButtonText("Hello"),
        lambda: button.ButtonImageText(pg.Surface((20, 20)), None, "Hello"),
        lambda: button.ButtonThreadText(text_before="Start"),
        lambda: Label("Hello", "white"),
        lambda: slider.Slider(0, 10, 1),
        lambda: text_input.TextInput(),
        lambda: ComboBox(["Hello", "World"]),
        lambda: BarChart([1, 2]),
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
    widget = button.ButtonText("Click", lambda: calls.append(True))
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
    assert not widget.clicked


def test_button_without_callback_and_image_without_hover(display):
    widget = button.ButtonImage(pg.Surface((30, 30)), None)
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEMOTION))
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP))


def test_text_input_through_group_unicode_editing_and_focus(display):
    group = Group()
    widget = text_input.TextInput(text="ab", fixed_width=100, ui_group=group)
    widget.draw(display, 10, 10)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_e, unicode="é"))
    group.handle_event(pg.event.Event(pg.TEXTINPUT, text="é世"))
    assert widget.get_text() == "abé世"
    assert widget.caret == 4
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_BACKSPACE))
    assert widget.get_text() == "ab世"
    group.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_DELETE))
    assert widget.get_text() == "ab"
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, (400, 400)))
    group.handle_event(pg.event.Event(pg.TEXTINPUT, text="ignored"))
    assert widget.get_text() == "ab"


def test_text_input_repeat_and_scroll(display):
    widget = text_input.TextInput(text="a" * 100, fixed_width=80)
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_BACKSPACE))
    widget.update(0.6)
    assert len(widget.text) < 99
    widget.handle_event(pg.event.Event(pg.KEYUP, key=pg.K_BACKSPACE))
    text = widget.text
    widget.update(1)
    assert widget.text == text
    widget.handle_key(pg.K_HOME)
    assert widget._scroll == 0
    widget.handle_key(pg.K_END)
    assert widget._scroll > 0
    widget.draw(display, 10, 10)


@pytest.mark.parametrize("low,high", [(10, 20), (-10, 0), (-20, -10), (0, 1)])
def test_slider_uses_actual_range_and_clamps(low, high, display):
    widget = slider.Slider(low, high, (high - low) / 10)
    widget.draw(display, 100, 100, 200, 5)
    assert widget.fraction == 0
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN, (200, 102)))
    assert widget.get_value() == pytest.approx((low + high) / 2)
    assert widget.fraction == pytest.approx(0.5)
    widget.handle_event(mouse(pg.MOUSEMOTION, (500, 102)))
    assert widget.get_value() == high
    widget.handle_event(mouse(pg.MOUSEBUTTONUP, (0, 102)))
    assert widget.get_value() == low
    widget.change_value_to(high + 100)
    assert widget.get_value() == high
    widget.draw(display, 100, 100, 200, 5)


def test_slider_steps_are_relative_to_minimum():
    widget = slider.Slider(3, 14, 2)
    widget.change_value_to(7)
    assert widget.get_value() == 7
    widget.change_value_to(100)
    assert widget.get_value() == 14


@pytest.mark.parametrize("args", [(0, 0, 1), (2, 1, 1), (0, 1, 0), (0, 1, -1)])
def test_slider_rejects_invalid_ranges(args):
    with pytest.raises(ValueError):
        slider.Slider(*args)


def test_combobox_selection_and_callback_observe_current_value(display):
    group = Group()
    widget = ComboBox(["One", "A much longer second option"], ui_group=group)
    widget.draw(display, 10, 10)
    assert widget.surface.get_width() == widget.rect.width
    values = []
    widget.add_action(1, lambda: values.append((widget.get_value(), widget.text)))
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    group.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert widget.is_open
    widget.draw(display, 10, 10)
    pos = (20, 10 + 2 * widget.rect.height + 5)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, pos))
    group.handle_event(mouse(pg.MOUSEBUTTONUP, pos))
    assert widget.selected_index == 1
    assert values == [(widget.elements[1], widget.elements[1])]
    assert not widget.is_open


def test_combobox_rejects_empty_and_bad_indices():
    with pytest.raises(ValueError):
        ComboBox([])
    with pytest.raises(IndexError):
        ComboBox(["One"]).change_selected(-1)


@pytest.mark.parametrize("values", [[], [0], [0, 0], [5, 10]])
def test_chart_handles_empty_zero_and_narrow_draws(values, display):
    widget = BarChart(values)
    widget.draw(display, 0, 0, 2, 100)
    if values:
        widget.change_value(0, 100)
        widget.update(1)
        widget.draw(display, 0, 0, 300, 100)
        assert widget.values_displayed[0] == 100


@pytest.mark.parametrize(
    "kwargs", [dict(values=[-1]), dict(values=[1], max_value=0), dict(values=[1], labels=[])]
)
def test_chart_validation(kwargs):
    with pytest.raises(ValueError):
        BarChart(**kwargs)


def test_color_adjustment_clamps_and_preserves_alpha():
    surface = pg.Surface((1, 1), pg.SRCALPHA)
    surface.fill((250, 10, 100, 42))
    assert make_surface_darker(surface, -50).get_at((0, 0)) == (255, 60, 150, 42)
    assert make_surface_darker(surface, 50).get_at((0, 0)) == (200, 0, 50, 42)
    assert surface.get_at((0, 0)) == (250, 10, 100, 42)
    assert lighter_color(pg.Color(0, 0, 0, 10), 50).a == 0


def test_image_loading_without_display_mode(tmp_path):
    path = tmp_path / "image.png"
    pg.image.save(pg.Surface((5, 5), pg.SRCALPHA), path)
    pg.display.quit()
    assert load_image(path, (10, 10)).get_size() == (10, 10)


@pytest.mark.parametrize("alignment", [TextAlignment.CENTER, "right"])
def test_alignment_requires_bounds(alignment):
    with pytest.raises(ValueError):
        button.ButtonText("Hello", text_align=alignment)
    with pytest.raises(ValueError):
        Label("Hello", "white", text_align=alignment)


def test_group_stops_at_first_consumer_and_survives_removal(display):
    group = Group()
    calls = []
    first = button.ButtonText("First", lambda: group.remove(first), ui_group=group)
    second = button.ButtonText("Second", lambda: calls.append(True), ui_group=group)
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
    btn = button.ButtonText("Click")
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

    field = text_input.TextInput(fixed_width=100)
    field.draw(display, 10, 10)
    assert not field.handle_event(pg.event.Event(pg.TEXTINPUT, text="x"))
    assert field.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    assert field.handle_event(pg.event.Event(pg.TEXTINPUT, text="x"))
    assert field.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_LEFT))
    assert not field.handle_event(mouse(pg.MOUSEBUTTONDOWN, (500, 500)))

    for widget in (Label("Hi", "white"), BarChart([1])):
        widget.draw(display, 10, 10)
        assert not widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))


def test_clicking_a_button_unfocuses_text_input(display):
    group = Group()
    calls = []
    btn = button.ButtonText("Click", lambda: calls.append(True), ui_group=group)
    field = text_input.TextInput(fixed_width=100, ui_group=group)
    btn.draw(display, 10, 10)
    field.draw(display, 10, 100)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, (20, 110)))
    assert field.active
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    group.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert not field.active
    assert calls == [True]


def test_group_sets_cursor_of_hovered_widget(display, monkeypatch):
    cursors = []
    monkeypatch.setattr(utils, "set_system_cursor", cursors.append)
    group = Group()
    btn = button.ButtonText("Click", ui_group=group)
    field = text_input.TextInput(fixed_width=100, ui_group=group)
    Label("Label", "white", ui_group=group).draw(display, 10, 200)
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


def test_dropdown_consumes_clicks_over_other_widgets(display):
    group = Group()
    calls = []
    underneath = button.ButtonText("Under menu", lambda: calls.append(True), ui_group=group)
    menu = ComboBox(["First", "Second"], ui_group=group)
    menu.draw(display, 10, 10)
    underneath.draw(display, 10, 10 + menu.rect.height)
    menu.is_open = True
    pos = (20, underneath.rect.y + 5)
    group.handle_event(mouse(pg.MOUSEBUTTONDOWN, pos))
    group.handle_event(mouse(pg.MOUSEBUTTONUP, pos))
    assert not menu.is_open
    assert calls == []


def test_dropdown_does_not_select_on_unmatched_release(display):
    menu = ComboBox(["First", "Second"])
    menu.draw(display, 10, 10)
    menu.is_open = True
    menu.handle_event(mouse(pg.MOUSEBUTTONUP, (20, 15 + 2 * menu.rect.height)))
    assert menu.selected_index == 0


def test_button_focus_loss_cancels_click(display):
    calls = []
    widget = button.ButtonText("Click", lambda: calls.append(True))
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(pg.event.Event(pg.WINDOWFOCUSLOST))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP))
    assert calls == []


def test_toggle_callback_sees_new_state(display):
    states = []
    widget = button.ButtonTwoStates(pg.Surface((30, 30)), pg.Surface((40, 40)), None)
    widget.connect(lambda: states.append(widget.state))
    widget.draw(display, 10, 10)
    widget.handle_event(mouse(pg.MOUSEBUTTONDOWN))
    widget.handle_event(mouse(pg.MOUSEBUTTONUP))
    widget.draw(display, 10, 10)
    assert states == [2]
    assert widget.rect.size == (40, 40)


def test_thread_buttons_complete_and_reset():
    import threading

    thread = threading.Thread(target=lambda: None)
    thread.start()
    thread.join()
    surface = pg.Surface((20, 20))
    image = button.ButtonThreadImage(surface, surface, None, surface, None)
    text = button.ButtonThreadText(rect_color=(10, 20, 30), text_before="Go", text_after="Done")
    for widget in (image, text):
        widget.check_thread(thread, True)
        assert widget.isSuccess and not widget.isWorking
        widget.working()
        assert widget.isWorking and not widget.isSuccess
        widget.idle()
        assert not widget.isWorking and not widget.isSuccess
    assert text.bg_color == (10, 20, 30)
