import pygame as pg

from PygameUIKit import demo


def click(app, widget, pos=None):
    for kind in (pg.MOUSEBUTTONDOWN, pg.MOUSEBUTTONUP):
        app.handle_event(pg.event.Event(kind, pos=pos or widget.rect.center, button=1))


def test_demo_runs_a_few_frames():
    app = demo.Demo()
    app.run(frames=3)
    assert app.screen.get_size() == demo.SIZE


def test_demo_logs_callbacks_and_routes_unused_keys():
    app = demo.Demo()
    app.draw()
    click(app, app.randomize)
    click(app, app.animate)
    assert list(app.events) == ['Button("Randomize").on_click()', "IconToggle.on_change(True)"]

    values = app.chart.values
    click(app, app.text_input)
    app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_r, mod=0, unicode="r"))
    app.handle_event(pg.event.Event(pg.TEXTINPUT, text="r"))
    assert app.text_input.text == "r" and app.chart.values == values
    assert app.events[-1] == "TextInput.on_change('r')"

    app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_ESCAPE, mod=0, unicode=""))
    app.handle_event(pg.event.Event(pg.KEYDOWN, key=pg.K_r, mod=0, unicode="r"))
    assert app.chart.values != values


def test_demo_screenshot(tmp_path):
    path = tmp_path / "demo.png"
    demo.main(["--screenshot", str(path)])
    assert pg.image.load(path).get_size() == demo.SIZE


def test_demo_disables_and_hides_the_showcase_widgets():
    app = demo.Demo()
    app.draw()
    click(app, app.disable)
    assert not any(widget.enabled for widget in app.showcase)
    assert app.disable.text == "Enable widgets"
    click(app, app.text_input)
    assert not app.text_input.focused
    click(app, app.hide)
    app.draw()
    assert not any(widget.visible for widget in app.showcase)
    click(app, app.disable)
    click(app, app.hide)
    assert all(widget.enabled and widget.visible for widget in app.showcase)
    assert list(app.events) == [
        "widget.enabled = False",
        "widget.visible = False",
        "widget.enabled = True",
        "widget.visible = True",
    ]


def test_demo_choices_drive_the_chart_and_progress_follows():
    app = demo.Demo()
    app.draw()
    click(app, app.animate_box)
    assert app.animate.value and app.animate_box.value
    click(app, app.animate)
    assert not app.animate_box.value
    click(app, app.values_box)
    assert app.chart.labels is None
    click(app, app.speed, app.speed._rows[2].center)
    assert app.chart.speed == demo.SPEEDS["Fast"]
    assert list(app.events) == [
        "Checkbox.on_change(True)",
        "IconToggle.on_change(False)",
        "Checkbox.on_change(True)",
        "RadioGroup.on_change('Fast')",
    ]
    app.int_slider.value = 70
    app.update(0.5)
    assert app.slider_progress.value == 70 and 0 < app.loading.fraction <= 1
