import threading

import pygame

from PygameUIKit import button, text_input, Group

#
#
# This is a file to showcase every EasyObject
#
#

RED = (255, 0, 0)
BTN_GREEN = (0, 169, 0)
BTN_BLUE = (83, 131, 232)


class Main:
    def __init__(self):
        self.done = False
        self.screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()

        self.text_input = text_input.InputBox(width=200)
        img = pygame.image.load("assets/play.png")
        img = pygame.transform.scale(img, (50, 50)).convert_alpha()
        self.btn_play = button.ButtonPngIcon(img, do_nothing)

        self.text_btn = button.ButtonText(BTN_BLUE, hello_world, "Hello World", border_radius=10,
                                          font_color=(255, 255, 255))
        self.snake = Snake(20, 20)
        self.thread_snake = threading.Thread(target=self.snake.run)
        self.btn_thread_snake = button.ButtonThreadText(rect_color=BTN_GREEN, onclick_f=self.thread_snake.start,
                                                        text_before="Start Snake",
                                                        text_during="Snake running",
                                                        text_after="Snake finished",
                                                        border_radius=10,
                                                        text_color=(255, 255, 255))

        self.easy_objects = Group(self.text_input, self.btn_play, self.text_btn, self.btn_thread_snake)

    def run(self):
        while not self.done:
            self.clock.tick(60)
            self.events()
            self.draw()

    def events(self):
        events = pygame.event.get()
        self.btn_thread_snake.check_thread(self.thread_snake)
        self.easy_objects.handle_events(events)
        for event in events:
            if event.type == pygame.QUIT:
                self.done = True

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.snake.draw(self.screen)
        self.text_input.draw(self.screen, 100, 300)
        self.btn_play.draw(self.screen, 100, 100)
        self.text_btn.draw(self.screen, 300, 100)
        self.btn_thread_snake.draw(self.screen, 100, 200)

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
    Main().run()
    pygame.quit()
