import os

import pygame
from pygame import Color

from PygameUIKit import Group
from PygameUIKit import text_input, button, slider

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
        self.easy_objects.add(self.text_input)

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

    def draw(self, win):
        W, H = self.screen.get_size()
        win.fill(Color(224, 224, 224))
        self.text_input.draw(win, W // 2 - self.text_input.rect.w // 2, H - 200)
        self.btn_pause.draw(win, 100, 200)
        self.btn_png.draw(win, 100, 300)

        self.slider.draw(win, 100, 400)

        pygame.display.flip()


def do_nothing():
    pass


def hello_world():
    print("Hello World!")


class Snake:
    def __init__(self, n, m):
        self.body = [(0, 0), (0, 1), (0, 2)]
        self.n, self.m = n, m

    def draw(self, win: pygame.Surface):
        W, H = win.get_size()
        size_vertical = H / self.n
        size_horizontal = W / self.m
        for i, j in self.body:
            x = j * size_horizontal
            y = i * size_vertical
            pygame.draw.rect(win, RED, (x, y, size_horizontal - 2, size_vertical - 2))

    def move(self, direction):
        if direction == "up":
            self.body.insert(0, (self.body[0][0] - 1, self.body[0][1]))
        elif direction == "down":
            self.body.insert(0, (self.body[0][0] + 1, self.body[0][1]))
        elif direction == "left":
            self.body.insert(0, (self.body[0][0], self.body[0][1] - 1))
        elif direction == "right":
            self.body.insert(0, (self.body[0][0], self.body[0][1] + 1))
        self.body.pop()

    def run(self):
        time_interval = 100
        instructions = ["down"] * (self.n - 1) + ["right"] * (self.m - 1) + ["up"] * (self.n - 1) + ["left"] * (
                self.m - 1)
        timer = 0
        clock = pygame.time.Clock()
        index_last_played = 0
        while timer < (len(instructions)) * time_interval:
            timer += clock.tick(60)
            if timer // time_interval > index_last_played:
                self.move(instructions[index_last_played])
                index_last_played = timer // time_interval


if __name__ == '__main__':
    pygame.init()
    Demo().run()
    pygame.quit()
