import pygame


class Slider:
    def __init__(self, min, max, step, ui_group=None):
        self.ui_group = ui_group
        if self.ui_group is not None:
            self.ui_group.add(self)
        self.min = min
        self.max = max
        self.step = step

        self.current_value = min

        # ui
        self.circle_radius = 10
        self.rect = pygame.Rect(0, 0, 100, self.circle_radius * 2)

        self.dragging = False

        self.font = pygame.font.SysFont("Arial", 20)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION:
            if self.dragging:
                x, y = event.pos
                if self.rect.collidepoint(x, y):
                    self.current_value = self.min + (x - self.rect.x) / self.rect.w * (self.max - self.min)
                    self.current_value = round(self.current_value / self.step) * self.step
                    self.current_value = max(self.min, min(self.max, self.current_value))

    def draw(self, win, x, y):
        self.rect.x = x
        self.rect.y = y

        displayed_rect = self.rect.copy()
        displayed_rect.y = 2
        pygame.draw.rect(win, (0, 0, 0), self.rect.inflate(0, -19), 2)

        circle_x = self.rect.x + ((self.current_value - self.min) / (self.max - self.min)) * self.rect.w
        circle_y = self.rect.y + self.rect.h // 2
        pygame.draw.circle(win, (0, 0, 0), (int(circle_x), int(circle_y)), self.circle_radius)

        text = self.font.render(str(self.current_value), True, (0, 0, 0))
        # display text in the top center of the slider
        win.blit(text, text.get_rect(center=self.rect.center).move(0, -20))

        # all get rect args : topleft, topright, bottomleft, bottomright, midtop, midleft, midbottom, midright, center, centerx, centery, size, width, height
