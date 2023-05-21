import pygame

import button
import text_input
from super_object import Group

#
#
# This is a file to showcase every EasyObject
#
#

RED = (255, 0, 0)


class Main:
    def __init__(self):
        self.done = False
        self.screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()

        self.text_input = text_input.InputBox(width=200)
        img = pygame.image.load("play.png")
        img = pygame.transform.scale(img, (50, 50)).convert_alpha()
        self.btn_play = button.ButtonPngIcon(img, do_nothing)

        img = pygame.image.load("redcross.png")
        img = pygame.transform.scale(img, (30, 30)).convert_alpha()

        self.text_btn = button.ButtonText((83, 131, 232), hello_world, "Hello World", border_radius=10,
                                          font_color=(255, 255, 255))

        self.easy_objects = Group(self.text_input, self.btn_play, self.text_btn)

    def run(self):
        while not self.done:
            self.clock.tick(60)
            self.events()
            self.draw()

    def events(self):
        events = pygame.event.get()
        self.easy_objects.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True

    def draw(self):
        self.screen.fill((30, 30, 30))

        self.text_input.draw(self.screen, 100, 300)
        self.btn_play.draw(self.screen, 100, 100)
        self.text_btn.draw(self.screen, 300, 100)

        pygame.display.flip()


def do_nothing():
    pass


def hello_world():
    print("Hello World!")


if __name__ == '__main__':
    pygame.init()
    Main().run()
    pygame.quit()
