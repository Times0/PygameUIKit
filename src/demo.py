import os

import pygame
from pygame import Color

from PygameUIKit import Group
from PygameUIKit import text_input, button, slider, dropdown

#
#
# This is a file to showcase every EasyObject
#
#

RED = (255, 0, 0)
BTN_GREEN = (0, 169, 0)
BTN_BLUE = (83, 131, 232)

cwd = os.path.dirname(__file__)
img_play = pygame.image.load(os.path.join(cwd, "assets/play.png"))
img_stop = pygame.image.load(os.path.join(cwd, "assets/stop.png"))


class Demo:
    def __init__(self):
        self.done = False
        self.screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()

        self.easy_objects = Group()
        self.text_input = text_input.InputBox(fixed_width=200, border_radius=2, ui_group=self.easy_objects)
        self.btn_pause = button.ButtonTwoStates(img_play, img_stop, do_nothing, ui_group=self.easy_objects)
        self.btn_png = button.ButtonPngIcon(img_play, hello_world, inflate=10, ui_group=self.easy_objects)

        self.slider = slider.Slider(0, 100, 1, ui_group=self.easy_objects)
        self.dropdown = dropdown.ComboBox(["Hello", "World", "And", "You"], ui_group=self.easy_objects)

        for i in range(4):
            # Set input text to the button text
            self.dropdown.add_action(i, lambda i=i: self.text_input.set_text(self.dropdown.elements[i]))

    def run(self):
        while not self.done:
            self.clock.tick(60)
            self.events()
            self.draw(self.screen)

    def events(self):
        events = pygame.event.get()
        for event in events:
            self.easy_objects.handle_event(event)
            if event.type == pygame.QUIT:
                self.done = True

        self.text_input.handle_events(events)

    def draw(self, win):
        W, H = self.screen.get_size()
        win.fill(Color(224, 224, 224))
        self.text_input.draw(win, W // 2 - self.text_input.rect.w // 2, H - 200)
        self.btn_pause.draw(win, 100, 200)
        self.btn_png.draw(win, 100, 300)
        self.slider.draw(win, 100, 400)
        self.dropdown.draw(win, 100, 100)

        pygame.display.flip()


def do_nothing():
    pass


def hello_world():
    print("Hello World!")


if __name__ == '__main__':
    pygame.init()
    Demo().run()
    pygame.quit()
