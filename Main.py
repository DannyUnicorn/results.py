import sys

from PIL import Image, ImageDraw

import csv

def openPaste(image, link, PSCoor = (1, 1)):
  opened = Image.open(link)
  zeroCoor = (PSCoor[0]-1, PSCoor[1]-1)
  image.paste(opened, zeroCoor, opened)

im = Image.new("RGB",(1200, 101))

openPaste(im, "G:/Images/Firecracker/Pillow Results/results assets/backrounds/Prize backround.png") #backround

for i in range(919, 910, -4): #hearts
  h = int((919 - i) * 30 / 4) + 5
  for w in range(i, i + 61, 30):
    heart = "G:/Images/Firecracker/Pillow Results/results assets/hearts/regular heart.png"
    openPaste(im, heart, (w, h))
#heart 1: (919, 5) 
#heart spaces: rows: (30, 0) columns: (4, 30) 



im.save("new.png")

