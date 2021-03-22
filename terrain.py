from PIL import Image, ImageFilter, ImageDraw
from numpy import *

im = Image.open( 'hmap.jpg' ).convert("RGBA")
res = Image.new("RGBA", im.size, (255,255,255,0))

artist = ImageDraw.Draw(res)

## Starting sampling params
# step to take next measure from
s_samplingStep = 100
# how far ahead we want to measure
s_sightLength = 600
# finess of sampling along the line of sight
s_sightStep = 30
# step for rotation to look around
s_sightRotStep = math.pi / 8
# number of looks to take around
s_numRotSteps = int((2*math.pi)/s_sightRotStep)

# number of passes to perform
# each pass applies finer params
numPasses = 3

# cliffs
critDiff = 30

# visibility
ownHeight = 10

# looks for pi/4 (45deg) rise
def visibilityCheck(heights, sightStep):
  index = 0
  sx, sy, sh = heights[index]
  for (x, y, h) in heights:
    tooHigh = (sh + ownHeight + sightStep * index) - h < 0
    if tooHigh:
      artist.line([x, y, sx, sy], (128, 0, 192, 192), int(10/index), None)
      return
    index += 1

# reacts to sudden changes in height
def seeHeights(heights, sightStep):
  index = 0
  for (x, y, h) in heights:
    li = index - 1 if index - 1 > 0 else 0
    (lx, ly, lh) = heights[li]
    ad = abs(h - lh)
    diffCrit = ad > critDiff
    badness = int(ad / critDiff)
    if badness > 0:
      artist.line([x, y, lx, ly], (255, 0, 0, 255), badness, None)
    index += 1
  

# get array of heights in some direction for sightLenght at sightStep
# pass the array to some 'comprehension' functions
# returns array of height in line
def lookStraigth(x,y, a, sightLength, sightStep):
  heightsAhead = []
  for ter in range(1, int(sightLength/sightStep)):
    dist = ter * sightStep
    dx = int(dist * math.sin(a))
    dy = int(dist * math.cos(a))
    ex = x + dx
    ey = y + dy
    if (ex >= im.width or ey >= im.height): break
    pxl = im.getpixel((ex, ey))
    (_r, _g, height, _a) = pxl
    heightPoint = (ex, ey, height)
    heightsAhead.append(heightPoint)

  if not heightsAhead == []:
    visibilityCheck(heightsAhead, sightStep)
    seeHeights(heightsAhead, sightStep)
  
  return heightsAhead

# goes thru all the angles around sampling position and lookStraight/5
# returns all sights around
def lookAround(x, y, sightLength, sightRotStep, sightStep):
  numRotSteps = int((2*math.pi) / sightRotStep)
  looksAround = []
  for angleStep in range(1, numRotSteps):
    angle = angleStep * sightRotStep
    lookAhead = lookStraigth(x, y, angle, sightLength, sightStep)
    looksAround.append(lookAhead)

  return looksAround

# goes thru image and selects sampling positions, then lookAround/5
def sampleImage(im, samplingStep, sightLength, sightRotStep, sightStep):
  for stepNumHorizontal in range(1, int(im.width/samplingStep)):
    xPos = samplingStep * stepNumHorizontal
    if (stepNumHorizontal % 2) == 0:
      xPos += samplingStep / 2

    for stepNumVertical in range(1, int(im.height/samplingStep)):
      yPos = samplingStep * stepNumVertical
      lookAround(xPos, yPos, sightLength, sightRotStep, sightStep)

# given image and number of passes will run sampleImage/5
# with increasing finesse
def multiPass(im, numPasses):
  def doPass(num):
    ss = s_samplingStep / num
    sl = s_sightLength / num
    srs = s_sightRotStep / num
    sis = s_sightStep / num
    sampleImage(im, ss, sl, srs, sis)

  if numPasses <= 1:
    doPass(1)
  else:
    for stepNum in range(1, numPasses):
      doPass(stepNum)



multiPass(im, numPasses)



out = Image.alpha_composite(im, res)

out.convert('RGB').save("result.jpg",'JPEG' )
# out.show()

print('terrain py --> WIN!')