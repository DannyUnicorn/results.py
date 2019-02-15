import sys
import os

from PIL import Image, ImageDraw

import csv

path = os.getcwd().replace("\\", "/")

def OpenPaste(image, link, PSCoor = (1, 1)):
  opened = Image.open(link)
  zeroCoor = (PSCoor[0]-1, PSCoor[1]-1)
  if (PSCoor == (1, 1)):
    image.paste(opened, zeroCoor)
  else:
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

  total = normal + prize #total amount of lives left
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
          heartName = "regular"
          normal -= 1
        elif(pain != 0):
          heartName = "dying"
          pain -= 1
        elif(spell != 0):
          heartName = "spent"
          spell -= 1
        elif(prize != 0):
          heartName = "bonus"
          prize -= 1
        elif(prizePain != 0):
          heartName = "gold" #right now this should never happen (and I also don't have dying bonus art currently) so it's a gold version of the bonus heart
          prizePain -= 1
        elif(prizeSpell != 0):
          heartName = "spent bonus"
          prizeSpell -= 1
        displaySum -= 1
      else:
        heartName = "empty"
      heart = path + "/mod results assets/hearts/" + heartName + " heart.png" #backround grey heart
      OpenPaste(im, heart, (w, h))
  
  return total #for a backround change if they're dead and for danger/peril
  
with open(path + "/results.tsv", encoding="utf8") as tsvfile:
  reader = csv.DictReader(tsvfile, dialect='excel-tab')
  contestants = 0
  
  for row in reader: #checking the placement of the last contestant to see how many contestants are there
    try:
      contestants = int(row['placement'])
    except:
      pass

with open(path + "/results.tsv", encoding="utf8") as tsvfile:
  reader = csv.DictReader(tsvfile, dialect='excel-tab')

  for row in reader:
    im = Image.new("RGB",(1200, 101))
    score = round(float(row['score'][:-1]), 2)
    prizeLives = 0 #change to the column of the bonus lives when that gets added to the .tsv file
    spellLives = row['spellLives']
    painLives = 0

    try: #backround check (terrible puns in comments that don't make any sense ftw)
      placement = int(row['placement'])
      nr = (placement - 1)/(contestants - 1) #normalized ranks... sorta, first place is 0 and last place is 1
      if (nr < 0.1):
        backround = "prize"
        prizeLives += 1
      elif (nr < 0.5):
        backround = "normal"
      elif (nr < 0.8):
        if (score > 30):
          backround = "bottom 50"
          painLives = 1
        else:
          backround = "/shrug" #it's unlikely and PMP and I wanted to make this a meme but he did it using the old program so I'll make a new meme backround eventually
          painLives = 4
      else:
        if (score > 30):
          backround = "bottom 20"
          painLives = 3
        else:
          backround = "under 30"
          painLives = 6
    except:
      placement = row['placement'] + row['score']
      backround = "spell"
    OpenPaste(im, path + "/mod results assets/backrounds/" + backround + " backround.png")

    #hearts paste and check if the person is dead (yeah I know it's ineffecient but idc that much)
    if (backround != "spell"): #if it's a spell, no need for lives
      if (Hearts(im, int(row['lives']), prizeLives, painLives, int(row['spellLives'])) < 1):
        OpenPaste(im, path + "/mod results assets/backrounds/dead backround.png")
        Hearts(im, int(row['lives']), prizeLives, painLives, int(row['spellLives']))

    im.save(path + "/tests/slide" + str(placement) + ".png", "PNG")

#im = Image.new("RGB",(1200, 101))

#OpenPaste(im, path + "/mod results assets/backrounds/prize backround.png") #backround

#lives = Hearts(im, 9, 0, 2, 5)

#im.save("slide" + placement + ".png")

#Todo:
#Text: name, response, placement, score and std dev
#Booksona
#Combining all finished slides into one big leaderboard