from PIL import Image
with Image.open("gj-logo.png") as im:
    im.rotate(45).show()