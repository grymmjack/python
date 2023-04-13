import pygame, sys

pygame.display.set_mode((720, 480))
pygame.init()
pygame.display.init()
pygame.display.set_caption('Temp')

screen = pygame.display.get_surface()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()

    screen.fill((0, 0, 0))
    pygame.display.flip()