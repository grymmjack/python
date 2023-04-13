import os
import sys
import pygame
pygame.init()

size = width, height = 720, 480
speed = [1, 1]
black = 255, 128, 0

screen = pygame.display.set_mode(size)

script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
rel_path = "intro_ball.gif"
abs_file_path = os.path.join(script_dir, rel_path)

# orig - abs path = ball = pygame.image.load(r'B:\Dropbox\P\learning\intro\intro_ball.gif')
# new:
ball = pygame.image.load(os.path.join(script_dir, rel_path))
# 
# ball = pygame.image.load("./intro_ball.gif")
ballrect = ball.get_rect()

FPS = 300
clock = pygame.time.Clock()

while 1:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    ballrect = ballrect.move(speed)
    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]
    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    screen.fill(black)
    screen.blit(ball, ballrect)
    pygame.display.flip()
    clock.tick(FPS)
