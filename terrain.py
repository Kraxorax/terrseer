import random
from numpy import *
from PIL import Image, ImageFilter, ImageDraw
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from terrain3D import scaleFactor

im = Image.open('scene_to_hmap.png' ).convert("RGBA")
res = Image.new("RGBA", im.size, (255,255,255,0))

artist = ImageDraw.Draw(res)

## Starting sampling params
# meters to take next measure from
s_samplingStep = 4 * scaleFactor
# how far ahead we want to measure
s_sightLength = 10 * scaleFactor
# finess of sampling along the line of sight
s_sightStep = 1 * scaleFactor
# step for rotation to look around
s_sightRotStep = math.pi / 8
# number of looks to take around
s_numRotSteps = int((2*math.pi)/s_sightRotStep)
# amx angle 30 degrees
s_maxAngle = math.pi/6

###
maxColorDiffPerStep = (s_sightStep*0.7)

# number of passes to perform
# each pass applies finer params
numPasses = 1

# cliffs
critDiff = 6

# visibility
ownHeight = 1

# reacts to sudden changes in height
def seeHeights(heights, sightStep):
  index = 0
  for (x, y, h) in heights:
    li = index - 1 if index - 1 > 0 else 0
    (lx, ly, lh) = heights[li]
    ad = abs(h - lh)
    diffCrit = ad > maxColorDiffPerStep
    badness = int(ad / maxColorDiffPerStep)
    if badness > 0:
      width = int(abs(x-lx)+abs(y-ly))
      artist.line([x, y, lx, ly], (255, 0, 0, 255), 5, None)
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
    if (ex < 0 or ey < 0 or ex >= im.width - 1 or ey >= im.height - 1): break
    pxl = im.getpixel((ex, ey))
    (_r, _g, height, _a) = pxl
    heightPoint = (ex, ey, height)
    heightsAhead.append(heightPoint)

  if not heightsAhead == []:
    # visibilityCheck(heightsAhead, sightStep)
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

# checks colors to decide if pixel can be passed thru
def isPassablePixel(r, g, b):
  return b > 0 and not(r > b)

# creates a matrix for A*
def makePathMatrix(img):
  matrix = []
  for y in range(0, img.height - 1):
    matrix.append([])
    for x in range(0, img.width - 1):
      (r, g, b, _a) = img.getpixel((x, y))
      free = 1 if isPassablePixel(r, g, b) else 0
      matrix[y].append(free)
  return matrix 

# picks a random passable point from map
def pickPoint(img):
  r, g, b = 0, 0, 0
  while not isPassablePixel(r, g, b):
    x = random.randint(0, img.width)
    y = random.randint(0, img.height)
    (pr, pg, pb, _a) = img.getpixel((x, y))
    r, g, b = pr, pg, pb
  return (x, y)

# draws path on image
def drawPath(img, path):
  draw = ImageDraw.Draw(img)
  if len(path) < 2: return
  for i in range(1, len(path) - 1):
    sx, sy = path[i-1]
    ex, ey = path[i]
    draw.line([sx, sy, ex, ey], (0, 255, 0, 255), 2, None)
  # draw start
  print(path[0])
  print(path[len(path)-1])
  draw.regular_polygon(((path[0]), 3*scaleFactor), 3)
  # draw end
  draw.regular_polygon(((path[len(path)-1]), 3*scaleFactor), 5)

# testing helper
def writeMatrixFile(matrix):
  matrixFile = open('matrixFile.txt', 'w')
  for row in matrix:
    for cell in row:
      matrixFile.write(str(cell))
    matrixFile.write("\n")
  matrixFile.close()

def main():
  multiPass(im, numPasses)

  noGoImg = Image.alpha_composite(im, res)
  noGoImg.convert('RGB').save("result.png",'PNG')
  ngi = Image.open('result.png').convert("RGBA")

  startX, startY = pickPoint(ngi)
  endX, endY = pickPoint(ngi)

  # startX, startY, endX, endY = 212, 237, 203, 167

  matrix = makePathMatrix(noGoImg)

  grid = Grid(matrix=matrix)

  start = grid.node(startX, startY)
  end = grid.node(endX, endY)

  finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
  path, runs = finder.find_path(start, end, grid)

  print(startX, startY, " -> ", endX, endY)
  print('operations:', runs, 'path length:', len(path))
  print(path)

  # writeMatrixFile(matrix)

  drawPath(ngi, path)

  ngi.convert('RGB').save("found_path.png",'PNG')


  print('terrain py --> WIN!')


if __name__ == '__main__':
  main()