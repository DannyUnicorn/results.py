import sys
import os

from PIL import Image, ImageFont, ImageDraw

import csv

path = os.getcwd().replace("\\", "/").replace("/results.py-master", "")

#a function for opening a picture based on a link and pasting it on an image, based on photoshop coordinates which are 0-indexed
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
  #Also this accidentally works for dead people too, where normal is either 0 or negative
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
    while(displaySum > 9 & prizeSpell > 0):
      displaySum -= 1
      prizeSpell -= 1
    while(displaySum > 9 & prizePain > 0):
      displaySum -= 1
      prizePain -= 1
    while(displaySum > 9 & prize > 0):
      displaySum -= 1
      prize -= 1

  #pasting the hearts
  #heart 1: (919, 5) 
  #heart spaces: rows: (30, 0) columns: (4, 30) 
  for i in range(919, 910, -4):
    h = int((919 - i) * 30 / 4) + 5
    for w in range(i, i + 61, 30):
      if(displaySum > 0):
        if(normal > 0):
          heartName = "regular"
          normal -= 1
        elif(pain > 0):
          heartName = "dying"
          pain -= 1
        elif(spell > 0):
          heartName = "spent"
          spell -= 1
        elif(prize > 0):
          heartName = "bonus"
          prize -= 1
        elif(prizePain > 0):
          heartName = "gold" #right now this should never happen (and I also don't have dying bonus art currently) so it's a gold version of the bonus heart
          prizePain -= 1
        elif(prizeSpell > 0):
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
  units = []
  counter = 0
  last = [0, 0, 0] #[0] is the last person in the top 50, [1] is last in top 80 and [2] is last before under 30%
  secondLast = [0, 0, 0] #second to last person in each section

  for row in reader:
    counter += 1
    im = Image.new("RGB",(1200, 101))
    score = round(float(row['score'][:-1]), 2)
    prizeLives = 0 #change to the column of the bonus lives when that gets added to the .tsv file
    spellLives = row['spellLives']
    painLives = 0
    font = "Alegreya-Regular"

    try: #backround check (terrible puns in comments that don't make any sense ftw)
      placement = int(row['placement'])
      if (placement < round(contestants * 0.1) + 1):
        backround = "prize"
        prizeLives += 1
        font = "DS_Mysticora"
        secondLast[0] = last[0]
        last[0] = counter #just in case
      elif (placement < round(contestants * 0.5) + 1):
        backround = "normal"
        secondLast[0] = last[0]
        last[0] = counter
      elif (placement < round(contestants * 0.8) + 1):
        if (score > 30):
          backround = "bottom 50"
          painLives = 1
          secondLast[1] = last[1]
          last[1] = counter
        else:
          backround = "/shrug" #it's unlikely and PMP and I wanted to make this a meme but he did it using the old program so I'll make a new meme backround eventually
          painLives = 4
          secondLast[1] = last[1]
          last[1] = counter
      else:
        if (score > 30):
          backround = "bottom 20"
          painLives = 3
          secondLast[2] = last[2]
          last[2] = counter
        else:
          backround = "under 30"
          painLives = 6
    except:
      placement = row['placement'] + row['score']
      backround = "spell"
    OpenPaste(im, path + "/mod results assets/backrounds/" + backround + " backround.png")

    #booksona (in a try block cuz I don't feel like manually adding IDs to everyone in the test leaderboard, so some people will have no data and it'll crash)
    try:
      booksonaCenter = (864, 50)
      for file in os.listdir(path + "/mod results assets/booksonas"):
        if file.startswith(row['ID']):
          booksona = Image.open(path + "/mod results assets/booksonas/" + row['ID'] + ".png")

          #resizing to fit the allowed area (but keeping the aspect ratio)
          if(booksona.size[0] > 92):
            newSize = (92, booksona.size[1] - (booksona.size[0] - 92))
            booksona.thumbnail(newSize)
          if(booksona.size[1] > 92):
            newSize = (booksona.size[0] - (booksona.size[1] - 92), 92)
            booksona.thumbnail(newSize)
          
          #recentering based on size (since paste() takes the top left corner of an image)
          booksonaCoor = (booksonaCenter[0] - int(booksona.size[0] / 2), booksonaCenter[1] - int(booksona.size[1] / 2))
          im.paste(booksona, booksonaCoor, booksona)
    except:
      pass

    #hearts paste and check if the person is dead (yeah I know it's ineffecient but idc that much)
    if (backround != "spell"): #if it's a spell, no need for lives
      if (Hearts(im, int(row['lives']), prizeLives, painLives, int(row['spellLives'])) < 1):
        font = "SpecialElite"
        OpenPaste(im, path + "/mod results assets/backrounds/dead backround.png")
        Hearts(im, int(row['lives']), prizeLives, painLives, int(row['spellLives']))
        im.paste(booksona, (booksonaCenter[0] - int(booksona.size[0] / 2), booksonaCenter[1] - int(booksona.size[1] / 2)), booksona)
        OpenPaste(im, path + "/mod results assets/spiral thingy.png", (booksonaCoor[0] + 1, booksonaCoor[1] + 1))

    #text stuff (a whole lotta variables for easy adjustment) (score stuff is also used for std dev except for coor)
    if (font == "DS_Mysticora"): #prize
      placementCenter = (58, 37)
      placementSize = 84
      placementFont = ImageFont.truetype(font, placementSize)
      placementCoor = (placementCenter[0] - int(placementFont.getsize(row['placement'])[0] / 2), placementCenter[1] - int(placementFont.getsize(row['placement'])[1] / 2))
      placementColor = (224, 207, 76, 255)

      nameSize = 48
      nameFont = ImageFont.truetype(font, nameSize)
      nameCoor = (110, -3)
      nameColor = (224, 207, 76, 255)

      responseSize = 19
      responseFont = ImageFont.truetype(font, responseSize)
      responseCoor = (120, 61)
      responseColor = (0, 0, 0, 255)

      scoreSize = 24
      scoreFont = ImageFont.truetype(font, scoreSize)
      scoreCoor = (1062, 9)
      stdDevCoor = (1062, 57)
      scoreColor = (255, 255, 255, 255)
    elif (backround == "spell"): #spell
      placementCenter = (52, 35)
      placementSize = 84
      placementFont = ImageFont.truetype(font, placementSize)
      placementCoor = (placementCenter[0] - int(placementFont.getsize(row['placement'])[0] / 2), placementCenter[1] - int(placementFont.getsize(row['placement'])[1] / 2))
      placementColor = (0, 0, 0, 255)

      nameSize = 48
      nameFont = ImageFont.truetype(font, nameSize)
      nameCoor = (110, -3)
      nameColor = (0, 0, 0, 255)

      responseSize = 19
      responseFont = ImageFont.truetype(font, responseSize)
      responseCoor = (120, 61)
      responseColor = (0, 0, 0, 255)

      scoreSize = 24
      scoreFont = ImageFont.truetype(font, scoreSize)
      scoreCoor = (1062, 9)
      stdDevCoor = (1062, 57)
      scoreColor = (255, 255, 255, 255)
    elif (font == "Alegreya-Regular"): #normal
      placementCenter = (56, 36)
      placementSize = 84
      placementFont = ImageFont.truetype(font, placementSize)
      placementCoor = (placementCenter[0] - int(placementFont.getsize(row['placement'])[0] / 2), placementCenter[1] - int(placementFont.getsize(row['placement'])[1] / 2))
      placementColor = (255, 255, 255, 255)

      nameSize = 48
      nameFont = ImageFont.truetype(font, nameSize)
      nameCoor = (110, -3)
      nameColor = (255, 255, 255, 255)

      responseSize = 19
      responseFont = ImageFont.truetype(font, responseSize)
      responseCoor = (120, 61)
      responseColor = (0, 0, 0, 255)

      scoreSize = 24
      scoreFont = ImageFont.truetype("Alegreya-Bold", scoreSize)
      scoreCoor = (1062, 9)
      stdDevCoor = (1062, 57)
      scoreColor = (255, 255, 255, 255)
    else: #dead
      placementCenter = (58, 37)
      placementSize = 84
      placementFont = ImageFont.truetype(font, placementSize)
      placementCoor = (placementCenter[0] - int(placementFont.getsize(row['placement'])[0] / 2), placementCenter[1] - int(placementFont.getsize(row['placement'])[1] / 2))
      placementColor = (224, 207, 76, 255)

      nameSize = 48
      nameFont = ImageFont.truetype(font, nameSize)
      nameCoor = (110, -3)
      nameColor = (224, 207, 76, 255)

      responseSize = 19
      responseFont = ImageFont.truetype(font, responseSize)
      responseCoor = (120, 61)
      responseColor = (0, 0, 0, 255)

      scoreSize = 24
      scoreFont = ImageFont.truetype(font, scoreSize)
      scoreCoor = (1062, 9)
      stdDevCoor = (1062, 57)
      scoreColor = (255, 255, 255, 255)

    draw = ImageDraw.Draw(im)
    draw.text(placementCoor, row['placement'], placementColor, placementFont)
    draw.text(nameCoor, row['name'], nameColor, nameFont)
    draw.text(responseCoor, row['response'], responseColor, responseFont)
    draw.text(scoreCoor, row['score'], scoreColor, scoreFont)
    draw.text(stdDevCoor, row['std dev'], scoreColor, scoreFont)

    units.append(im)
  
  #results slides generation
  nameCounter = 1
  im = Image.new("RGB", (1200, 101))
  im.paste(units[0])
  im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
  nameCounter += 1
  im = Image.new("RGB", (1200, 202))
  im.paste(units[0])
  im.paste(units[1], (0, 101))
  im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
  nameCounter += 1
  last.insert(0, 0) #shifts last[] values back so last[x]:secondLast[x] are whole zones (excluding the last and second to last people)
  for i in range(0, 3): #going through each zone
    #generating size 5 slides until it can't without showing the second to last person
    for j in range(last[i], secondLast[i] - 5, 5):
      im = Image.new("RGB", (1200, 505))
      for k in range(j, j + 5):
        im.paste(units[k], (0, (k - j) * 101))
      im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
      nameCounter += 1
      k = 0

    #generating the last large slide (if the zone's size isn't a multiple of 5, if it is it'll be included in the previous loop) before the second to last person, where 1 by 1s will begin
    im = Image.new("RGB", (1200, 101 * (secondLast[i] - j - 6)))
    for m in range(j + 3, secondLast[i] - 1): 
      im.paste(units[m], (0, 101 * (m - j - 5)))
    try: #if the image has 0 height (which will happen if the zone's size is a multiple of 5) saving it will crash
      im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
      nameCounter += 1
    except:
      pass

    #generating 1 by 1s from the second to last person to the last person, including both
    for l in range(m + 1, last[i+1]):
      im = Image.new("RGB", (1200, 101))
      im.paste(units[l])
      im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
      nameCounter += 1

    #resetting variables
    j = 0
    k = 0
    m = 0
    l = 0 

  #taking care of the last zone, where final 1 by 1s aren't necessary
  for j in range(last[3], int(units.__len__() / 5) * 5 + 1, 5):
    #generating size 5 slides until the last slide, which is smaller than the rest
    im = Image.new("RGB", (1200, 505))
    for k in range(j, j + 5):
      im.paste(units[k], (0, (k - j) * 101))
    im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
    nameCounter += 1
    k = 0

  #generating the last smaller slide
  im = Image.new("RGB", (1200, 101 * (units.__len__() - j - 5)))
  for e in range(j + 5, units.__len__()):
    im.paste(units[e], (0, 101 * (e - j - 5)))
  try: #again, if the zone's size is a multiple of 5 then the height is zero which will crash when trying to save
    im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
  except:
    pass
  
  #generating the full leaderboard
  im = Image.new("RGB", (1200, 101 * counter))
  for i in range(0, counter):
    im.paste(units[i], (0, i * 101))
  im.save(path + "/tests/leaderboard.png", "PNG")

#Todo:
#Booksona
#Fix bug where non UTF-8 characters appear as a space
#Add a whole bunch of shit to the github repository