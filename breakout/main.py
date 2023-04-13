import pygame
import sys

pygame.display.set_mode((720, 480))
pygame.init()
pygame.display.init()
pygame.display.set_caption('Breakout')

screen = pygame.display.get_surface()

block_size = (10, 10)
offset = (0, 0)


class Ball:
    color = 0xFF0000

    def __init__(self):
        print(self.color)

    def Draw(self, surface, x, y):
        rx = x * block_size[0] + offset[0]
        ry = y * block_size[1] + offset[1]
        rw = block_size[0]
        rh = block_size[1]
        r = pygame.Rect(rx, ry, rw, rh)
        pygame.draw.rect(surface, self.color, r, 0)


ball = Ball()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    screen.fill((0, 0, 0))
    ball.Draw(screen, 0, 0)
    pygame.display.flip()
