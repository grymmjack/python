from PIL import Image
import pygame

window_size = (720, 480)

pygame.display.set_mode(window_size)
pygame.init()
pygame.display.init()

im = Image.open('gj-logo-inv.png')
w = im.width 
h = im.height
imb = im.tobytes()
myImage = pygame.image.fromstring(im.tobytes(), im.size, im.mode)

i = 0

# a.hex(sep=' ').split(sep='0a')[1:-1]
a = b'''
..XXXX..
..X..X..
..XXXX..
..X..X..
..X..X..
'''

# aa.split(sep='\n')[1:-1]
aa = '''
..XXXX..
..X..X..
..XXXX..
..X..X..
..X..X..
'''


b = b'''
..XXXX..
..X..X..
..XXX...
..X..X..
..XXXX..
'''


while i <= len(imb):
    print(f"{imb[i:w].hex(sep=' ', bytes_per_sep=1)}")
    i = i + w

print(imb, myImage)
