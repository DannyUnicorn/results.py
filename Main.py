import sys

from PIL import Image, ImageDraw

import csv

def OpenPaste(image, link, PSCoor = (1, 1)):
  opened = Image.open(link)
  zeroCoor = (PSCoor[0]-1, PSCoor[1]-1)
  image.paste(opened, zeroCoor, opened)

def Hearts(im, normalH, prizeH, painH, spellH):

  #heart display calculation
  #the display order should be: normal, prize, prize hurt OR normal, normal hurt, prize hurt 
  #where hurt is either pain or spell, spell always comes after pain
  #the display is calculated backwards (don't ask why)
  if (prizeH > painH + spellH):
    prize = prizeH - painH - spellH
    prizeSpell = spellH
    prizePain = painH
    spell = 0
    pain = 0
    normal = normalH
  else:
    prize = 0
    if (prizeH > spellH):
      prizeSpell = spellH
      prizePain = prizeH - spellH
      spell = 0
      pain = painH - prizePain
    else:
      prizeSpell = prizeH
      prizePain = 0
      spell = spellH - prizeH
      pain = painH
    normal = normalH + prizeH - painH - spellH

  displaySum = normal + pain + spell + prize + prizePain + prizeSpell #total lives displayed

  #correcting for over 9 display hearts (this also corrects for having more than 9 lives) (normal, spell and pain can never be more than 9 so no need to correct those)
  if(displaySum > 9):
    while(displaySum > 9 & prizeSpell != 0):
      displaySum -= 1
      prizeSpell -= 1
    while(displaySum > 9 & prizePain != 0):
      displaySum -= 1
      prizePain -= 1
    while(displaySum > 9 & prize != 0):
      displaySum -= 1
      prize -= 1

  #pasting the hearts
  #heart 1: (919, 5) 
  #heart spaces: rows: (30, 0) columns: (4, 30) 
  for i in range(919, 910, -4):
    h = int((919 - i) * 30 / 4) + 5
    for w in range(i, i + 61, 30):
      if(displaySum != 0):
        if(normal != 0):
          heartName = "regular heart"
          normal -= 1
        elif(pain != 0):
          heartName = "dying heart"
          pain -= 1
        elif(spell != 0):
          heartName = "spent heart"
          spell -= 1
        elif(prize != 0):
          heartName = "bonus heart"
          prize -= 1
        elif(prizePain != 0):
          heartName = "gold heart" #right now this should never happen (and I also don't have prize pain art currently) so it's a gold version of the bonus heart
          prizePain -= 1
        elif(prizeSpell != 0):
          heartName = "spent bonus heart"
          prizeSpell -= 1
        displaySum -= 1
      else:
        heartName = "empty heart slot"
      heart = "G:/Images/Firecracker/Pillow/mod results assets/hearts/" + heartName + ".png" #backround grey heart
      OpenPaste(im, heart, (w, h))
  


im = Image.new("RGB",(1200, 101))

OpenPaste(im, "G:/Images/Firecracker/Pillow/mod results assets/backrounds/Prize backround.png") #backround

Hearts(im, 9, 0, 2, 5)

im.save("new.png")

