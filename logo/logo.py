import pygame
import sys

# too-puhl = tuple
block_size = (50, 50)
window_size = (720, 480)
color_background = 0x3377CC
color_grid = 0x2266BB
color_fill = 0x5599EE
color_stroke = 0x77BBFF
width_grid = 0
width_stroke = 0

pygame.display.set_mode(window_size)
pygame.init()
pygame.display.init()
pygame.display.set_caption('Test')
screen = pygame.display.get_surface()

logo_data = [
    '00111100',
    '00100000',
    '00101100',
    '00100100',
    '00100100',
    '00000100',
    '00111100'

    # '0000000000000000',
    # '0000111111110000',
    # '0000111111110000',
    # '0000110000000000',
    # '0000110000000000',
    # '0000110011110000',
    # '0000110011110000',
    # '0000110000110000',
    # '0000110000110000',
    # '0000000000110000',
    # '0000000000110000',
    # '0000111111110000',
    # '0000111111110000',
    # '0000000000000000'

    # '000000000000000000000000',
    # '001111111111111100111100',
    # '001100000000110000001100',
    # '001100000011000000001100',
    # '001100001100000000001100',
    # '001100110000000000001100',
    # '001111000001100000001100',
    # '001100001111111111111100',
    # '000000000000000000000000',
    # '001111111111111111111100',
    # '001100000000000000001100',
    # '001100000000000000001100',
    # '001111000000000000111100',
    # '000011111000000111110000',
    # '000000111111111111000000',
    # '000000000000000000000000'
]

for line in logo_data:
    print(line, flush=True)

logo_size_w = len(logo_data[0]) * block_size[0]
logo_size_h = len(logo_data) * block_size[1]
logo_size_in_px = (logo_size_w, logo_size_h)

print(logo_size_in_px)


def logo(surf: pygame.Surface,
         fill_color: pygame.Color,
         stroke_color: pygame.Color,
         width: int = 0,
         offset: list = (0, 0)):
    x = 0
    y = 0
    for row in logo_data:
        x = 0
        for col in row:
            if (col == '1'):
                rx = x * block_size[0] + offset[0]
                ry = y * block_size[1] + offset[1]
                rw = block_size[0]
                rh = block_size[1]
                r = pygame.Rect(rx, ry, rw, rh)
                # fill
                pygame.draw.rect(screen, fill_color, r, 0)
                if width:
                    # stroke
                    pygame.draw.rect(screen, stroke_color, r, width)
            x += 1
        y += 1


def render(surf: pygame.Surface):
    screen.fill(color_background)
    logo(
        screen, color_fill, color_stroke, width_stroke, 
        (
            (window_size[0] - logo_size_in_px[0]) / 2, 
            (window_size[1] - logo_size_in_px[1]) / 2
        )
    )
    grid(screen, block_size[0], block_size[1], color_grid, width_grid)
    pygame.display.flip()


def grid(surf: pygame.Surface, 
         w: int, 
         h: int, 
         color: pygame.Color, 
         width: int = 0):
    rect = surf.get_rect()
    for row in range(0, rect.h, h):
        pygame.draw.line(surf, color, (0, row), (rect.w, row), width)
        for col in range(0, rect.w, w):
            pygame.draw.line(surf, color, (col, row), (col, rect.h), width)


render(screen)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                sys.exit()
