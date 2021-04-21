import random
from numpy import *
from PIL import Image, ImageFilter, ImageDraw
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder
from terrain3D import scaleFactor




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
  return 0 if r == 255 else r

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
    draw.line([sx, sy, ex, ey], (0, 0, 0, 255), int(scaleFactor/3), None)
  print('start', path[0])
  print('end', path[len(path)-1])
  # draw start point
  draw.regular_polygon(((path[0]), scaleFactor), 3, fill=(0, 0, 0, 255))
  # draw end point
  draw.regular_polygon(((path[len(path)-1]), scaleFactor), 5, fill=(0, 0, 0, 255))

# testing helper
def writeMatrixFile(matrix):
  matrixFile = open('matrixFile.txt', 'w')
  for row in matrix:
    for cell in row:
      matrixFile.write(str(cell))
    matrixFile.write("\n")
  matrixFile.close()

def doPF(im):
  # startX, startY = pickPoint(im)
  # endX, endY = pickPoint(im)
  startX, startY, endX, endY = 561, 488, 823, 1123
  print(startX, startY, " -> ", endX, endY)

  matrix = makePathMatrix(im)

  grid = Grid(matrix=matrix)

  start = grid.node(startX, startY)
  end = grid.node(endX, endY)

  finder = AStarFinder(diagonal_movement=DiagonalMovement.always)
  path, runs = finder.find_path(start, end, grid)

  print('operations:', runs, 'path length:', len(path))
  return path

def pathToGPArray(path, pw, ph, oLa, oLo):
  print('pw, ph, oLa, oLo <-', pw, ph, oLa, oLo)
  geoPath = []
  for (xPos, yPos) in path:
    geoPosX = xPos*pw + oLa
    geoPosY = yPos*ph + oLo
    geoPath.append((geoPosX, geoPosY))
  return geoPath


def getGEOData():
  gdFile = open('test_data\geo_dunes.tfw')
  return gdFile.readlines()

def plotIt(path):
  # importing the required module
  import matplotlib.pyplot as plt

  xA = []
  yA = []
  for x, y in path:
    xA.append(x)
    yA.append(y)
    
  # plotting the points 
  plt.plot(xA, yA)
    
  # naming the axis
  plt.xlabel('x - axis')
  plt.ylabel('y - axis')
    
  # giving a title to my graph
  plt.title('Some data')

  # function to show the plot
  plt.show()

def main():
  Image.MAX_IMAGE_PIXELS = None
  tif = Image.open('test_data\geo_dunes.tif')
  im = Image.open('scene_to_hmap.png' ).convert("RGBA")
  res = Image.new("RGBA", im.size, (0,0,0,0))
  path = doPF(im)

  [pw, _a, _b, ph, oriLat, oriLong] = getGEOData()
  print(pw, _a, _b, ph, oriLat, oriLong)

  GPPath = pathToGPArray(path, (tif.width/im.width)*float(pw), (tif.height/im.height)*float(ph), float(oriLat), float(oriLong))
  pathGM=open('qgis\points.py','w')
  pathGM.write('POINTS = [')
  for lng, lat in GPPath:
    pathGM.write('('+str(lat)+','+str(lng)+'),')
  pathGM.write(']')
  pathGM.close()

  plotIt(GPPath)

  drawPath(res, path)

  resultImg = Image.alpha_composite(im, res)
  resultImg.convert('RGB').save("found_path.png",'PNG')

  print('terrain py --> WIN!')


if __name__ == '__main__':
  main()