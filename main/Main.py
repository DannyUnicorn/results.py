import sys
import os

from PIL import Image, ImageFont, ImageDraw

import csv

path = os.getcwd().replace("\\", "/").replace("/results.py-master", "")
manualMode = True
#fill this array with 2tuples of (how many lives earned or lost in this section, last placement in section). (lives earned are positive, lives lost are negative) (order the 2tuples by the order of the sections)
sections = [(1, 2), (0, 5), (-1, 26)] #this is an example, prompt 4 Tattoo leaderboard

def manualSections(sections):
  arr = []
  sections.insert(0, (0, 0))
  for i in range(sections.__len__() - 1):
    for j in range(sections[i][1], sections[i+1][1]):
      arr.append(sections[i+1][0])
  return arr



if(manualMode):
  manual = manualSections(sections) #turning the above into a usable array

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
        heartName = "empty" #backround grey heart
      heart = path + "/mod results assets/hearts/" + heartName + " heart.png"
      OpenPaste(im, heart, (w, h))
  
  return total #for a backround change if they're dead and for danger/peril

def ManaHearts(im, manaH): #mana hearts paste
  for i in range(919, 910, -4):
    h = int((919 - i) * 30 / 4) + 5
    for w in range(i, i + 61, 30):
      if(manaH > 0):
        heartName = "mana"
        manaH -= 1
        heart = path + "/mod results assets/hearts/" + heartName + " heart.png"
        OpenPaste(im, heart, (w, h))

def Generate(im, backround, row, prizeLives, spellLives, painLives, manaLives, units, font, counter, isFool):
  OpenPaste(im, path + "/mod results assets/backrounds/" + backround + " backround.png")

  #booksona (in a try block cuz I don't feel like manually adding IDs to everyone in the test leaderboard, so some people will have no data and it'll crash)
  hasBooksona = False
  try:
    booksonaCenter = (864, 50)
    for file in os.listdir(path + "/mod results assets/booksonas"):
      if file.startswith(row['ID']):
        booksona = Image.open(path + "/mod results assets/booksonas/" + row['ID'] + ".png")

        #resizing to fit the allowed area (but keeping the aspect ratio)
        if(booksona.size[0] < 92):
          new = (92 * booksona.size[0]) / booksona.size[1]
          newSize = (92, new)
          booksona.thumbnail(newSize)
        if(booksona.size[0] > 92):
          new = booksona.size[1] - ((booksona.size[0] - 92) * booksona.size[1]) / booksona.size[0]
          newSize = (92, new)
          booksona.thumbnail(newSize)
        if(booksona.size[1] > 92):
          new = booksona.size[0] - ((booksona.size[1] - 92) * booksona.size[0]) / booksona.size[1]
          newSize = (new, 92)
          booksona.thumbnail(newSize)
        #recentering based on size (since paste() takes the top left corner of an image)
        booksonaCoor = (booksonaCenter[0] - int(booksona.size[0] / 2), booksonaCenter[1] - int(booksona.size[1] / 2))
        im.paste(booksona, booksonaCoor, booksona)
        hasBooksona = True
  except:
    pass

  spiralCenter = (820, 4)
  #hearts paste, status and check if the person is dead (yeah I know it's ineffecient but idc that much)
  if (backround != "spell"): #if it's a spell, no need for lives
    heartCount = Hearts(im, int(row['lives']), prizeLives, painLives, int(row['spellLives']))
    if (heartCount < 1 or backround == "dead"):
      font = "SpecialElite"
      OpenPaste(im, path + "/mod results assets/backrounds/dead backround.png")
      Hearts(im, int(row['lives']), prizeLives, painLives, int(row['spellLives']))
      if(hasBooksona):
        im.paste(booksona, (booksonaCenter[0] - int(booksona.size[0] / 2), booksonaCenter[1] - int(booksona.size[1] / 2)), booksona)
      OpenPaste(im, path + "/mod results assets/spiral thingy.png", (spiralCenter[0] + 1, spiralCenter[1] + 1))
    elif (heartCount == 1):
      OpenPaste(im, path + "/mod results assets/status/peril.png", (755, 11))
    elif (heartCount <= 3):
      OpenPaste(im, path + "/mod results assets/status/danger.png", (755, 11))
    
    ManaHearts(im, int(manaLives))

  #text stuff (a whole lotta variables for easy adjustment) (score stuff is also used for std dev except for coor)
  if (font == "DS_Mysticora"): #prize
    placementCenter = (58, 37)
    placementSize = 84
    placementFont = ImageFont.truetype(font, placementSize)
    if(isFool):
      placementCoor = (placementCenter[0] - int(placementFont.getsize(str(counter))[0] / 2), placementCenter[1] - int(placementFont.getsize(str(counter))[1] / 2))
    else:
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
    if(isFool):
      placementCoor = (placementCenter[0] - int(placementFont.getsize(str(counter))[0] / 2), placementCenter[1] - int(placementFont.getsize(str(counter))[1] / 2))
    else:
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
    if(isFool):
      placementCoor = (placementCenter[0] - int(placementFont.getsize(str(counter))[0] / 2), placementCenter[1] - int(placementFont.getsize(str(counter))[1] / 2))
    else:
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
    placementCenter = (55, 51)
    placementSize = 84
    placementFont = ImageFont.truetype(font, placementSize)
    if(isFool):
      placementCoor = (placementCenter[0] - int(placementFont.getsize(str(counter))[0] / 2), placementCenter[1] - int(placementFont.getsize(str(counter))[1] / 2))
    else:
      placementCoor = (placementCenter[0] - int(placementFont.getsize(row['placement'])[0] / 2), placementCenter[1] - int(placementFont.getsize(row['placement'])[1] / 2))
    placementColor = (255, 255, 255, 255)

    nameSize = 48
    nameFont = ImageFont.truetype(font, nameSize)
    nameCoor = (119, 12)
    nameColor = (255, 255, 255, 255)

    responseSize = 19
    responseFont = ImageFont.truetype(font, responseSize)
    responseCoor = (127, 66)
    responseColor = (0, 0, 0, 255)

    scoreSize = 24
    scoreFont = ImageFont.truetype(font, scoreSize)
    scoreCoor = (1057, 18)
    stdDevCoor = (1057, 66)
    scoreColor = (0, 0, 0, 255)

  draw = ImageDraw.Draw(im)
  calls = round((float(row['callouts'][:row['callouts'].index("/")]))/float(row['callouts'][row['callouts'].index("/")+1:]), 2)

  if (row['placement'] == "~"):
    if (calls < 0.5):
      bookmark = "success"
    else:
      bookmark = "failure"
  elif (calls != 0):
    bookmark = "real"
    
  try:
    OpenPaste(im, path + "/mod results assets/bookmarks/" + bookmark + ".png", (0, 1))
    n1 = row['callouts'][:row['callouts'].index("/")]
    n2 = row['callouts'][row['callouts'].index("/")+1:]
    center1 = (94, 4)
    center2 = (100, 19)
    color1 = (0, 0, 0, 0)
    color2 = (0, 0, 0, 0)
    size1 = 14
    size2 = 14
    if(n1.__len__() == 2):
      size1 = 10
    if(n2.__len__() == 2):
      size2 = 10
    font1 = ImageFont.truetype("DS_Mysticora", size1)
    font2 = ImageFont.truetype("DS_Mysticora", size2)
    coor1 = (center1[0] - int(font1.getsize(n1)[0] / 2), center1[1] - int(font1.getsize(n1)[1] / 2))
    coor2 = (center2[0] - int(font2.getsize(n2)[0] / 2), center2[1] - int(font2.getsize(n2)[1] / 2))

    draw.text(coor1, n1, color1, font1)
    draw.text(coor2, n2, color2, font2)
  except:
    pass

  draw.text(nameCoor, row['name'], nameColor, nameFont)
  draw.text(responseCoor, row['response'], responseColor, responseFont)
  draw.text(scoreCoor, row['score'], scoreColor, scoreFont)
  if(isFool):
    draw.text(placementCoor, str(counter), placementColor, placementFont)
  else:
    draw.text(placementCoor, row['placement'], placementColor, placementFont)
  draw.text(stdDevCoor, row['std dev'], scoreColor, scoreFont)

  units.append(im)

  if(isFool):
    im.save(path + "/tests/fool slide " + str(counter) + ".png", "PNG")

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
  units1 = []
  counter = 0
  counter1 = 0
  last = [0, 0, 0] #[0] is the last person in the top 50, [1] is last in top 80 and [2] is last before under 30%
  secondLast = [0, 0, 0] #second to last person in each section

  for row in reader:
    counter += 1
    im = Image.new("RGB",(1200, 101))
    score = round(float(row['score'][:-1]), 2)
    prizeLives = 0 #change to the column of the bonus lives when that gets added to the .tsv file
    spellLives = row['spellLives']
    painLives = 0
    manaLives = row['manaHearts']
    font = "Alegreya-Regular"
    fool = ""
    try: #backround check (terrible puns in comments that don't make any sense ftw)
      placement = int(row['placement'])
      if (manualMode):
        if (manual[placement - 1] > 0):
          backround = "prize"
          prizeLives = manual[placement - 1]
          font = "DS_Mysticora"
        elif (manual[placement - 1] == 0):
          backround = "normal"
        else:
          painLives = -1 * manual[placement - 1]
          if (manual[placement - 1] > -3):
            backround = "bottom 50"
          elif (manual[placement - 1] > -6):
            backround = "bottom 20"
          else:
            backround = "under 30"
      else:
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
      if (row['placement'] == "-"):
        placement = row['placement'] + row['score']
        backround = "spell"
      else:
        placement = row['placement'] + row['score']
        backround = "spell"
        calls = round((float(row['callouts'][:row['callouts'].index("/")]))/float(row['callouts'][row['callouts'].index("/")+1:]), 2)
        if (calls > 0.5):
          fool = "dead"
        elif (score > 40):
          fool = "normal"
        else:
          fool = "prize"

    OpenPaste(im, path + "/mod results assets/backrounds/" + backround + " backround.png")

    Generate(im, backround, row, prizeLives, spellLives, painLives, manaLives, units, font, counter, False)

    if (fool != ""):
      counter1 += 1
      im1 = Image.new("RGB",(1200, 101))
      score1 = round(float(row['score'][:-1]), 2)
      prizeLives1 = 0 #change to the column of the bonus lives when that gets added to the .tsv file
      spellLives1 = row['spellLives']
      painLives1 = 0
      manaLives1 = row['manaHearts']
      if (fool == "dead"):
        font1 = "SpecialElite"
      elif (fool == "normal"):
        font1 = "Alegreya-Regular"
      else:
        font1 = "DS_Mysticora"
      OpenPaste(im1, path + "/mod results assets/backrounds/" + fool + " backround.png")
      Generate(im1, fool, row, prizeLives1, spellLives1, painLives1, manaLives1, units1, font1, counter1, True)

  #generating the full leaderboard
  im = Image.new("RGB", (1200, 101 * counter))
  for i in range(0, counter):
    im.paste(units[i], (0, i * 101))
  im.save(path + "/tests/leaderboard.png", "PNG")
  
  #results slides generation
  if (not manualMode): #basically impossible with custom zones
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

      if(j == 0 and last[i] > 5):
        j = last[i] - 5

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
    for j in range(last[3] + 5, int(units.__len__() / 5) * 5, 5):
      #generating size 5 slides until the last slide, which is smaller than the rest
      im = Image.new("RGB", (1200, 505))
      for k in range(j - 5, j):
        print(k)
        im.paste(units[k], (0, (k - j) * 101))
      im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
      nameCounter += 1
      k = 0
    if (j == 0):
      j = last[3]
    #generating the last smaller slide
    im = Image.new("RGB", (1200, 101 * (units.__len__() - j)))
    for e in range(j, units.__len__()):
      im.paste(units[e], (0, 101 * (e - j)))
    try: #again, if the zone's size is a multiple of 5 then the height is zero which will crash when trying to save
      im.save(path + "/tests/slide" + str(nameCounter) + ".png", "PNG")
    except:
      pass

    #generating the full leaderboard
  
  units1.reverse()
  im = Image.new("RGB", (1200, 101 * counter1))
  for i in range(0, counter1):
    im.paste(units1[i], (0, i * 101))
  im.save(path + "/tests/fool leaderboard.png", "PNG")
#Todo:
#Fix bug where characters not in the font appear as a space
#Resize text if it's too long
#Add redness to -3 backround