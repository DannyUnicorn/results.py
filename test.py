import sys
import os

from PIL import Image, ImageFont, ImageDraw

import csv

path = os.getcwd().replace("\\", "/").replace("/results.py-master", "")

fontPath = path + "/mod results assets/fonts/DS_Mysticora.ttf"

font = ImageFont.truetype("DS_Mysticora", 60)

print(font.getsize("t")[0])