from numpy import *
from stl import mesh
from PIL import Image, ImageDraw

# Using an existing stl file:
mesh = mesh.Mesh.from_file('terrain_model.stl')

# The mesh normals (calculated automatically)
mesh.normals
# print(mesh.normals)
# The mesh vectors
mesh.v0, mesh.v1, mesh.v2

def getHighestVertex(point):
  return point[2] if (point[2] > point[5] and point[2] > point[8]) else (point[5] if point[5] > point[8] else point[8])

def getPointX(point):
  return (point[0] + point[3] + point[6]) / 3

def getPointY(point):
  return (point[1] + point[4] + point[7]) / 3

def getMaxWidthAndLength(points):
  return (points[0][1], points[len(points) - 1][0])

def getStepSize(points):
  index = 0
  allDiffsX = 0
  allDiffsY = 0
  for point in points:
    if index > 0:
      lastPoint = points[index - 1]
      diffX = abs(getPointX(point) - getPointX(lastPoint))
      allDiffsX += diffX
      diffY = abs(getPointY(point) - getPointY(lastPoint))
      allDiffsY += diffY
    index += 1

  avgDiffX = allDiffsX / len(points)
  avgDiffY = allDiffsY / len(points)
  return (avgDiffX, avgDiffY)


def getAverageHeight(points):
  sumH = 0
  for point in points:
    sumH += getHighestVertex(point)
  return sumH / len(points)

def getMaxHeight(points):
  maxHeight = 0
  for point in points:
    highestVertex = getHighestVertex(point)
    maxHeight = highestVertex if highestVertex > maxHeight else maxHeight
  return maxHeight


res = None

eH = 0.00001

def drawHeightMap(points):
  print("looking ...")
  (width, length) = getMaxWidthAndLength(points)
  (stepSizeX, stepSizeY) = getStepSize(points)
  (ssX, ssY) = (int(stepSizeX), int(stepSizeY))
  maxHeight = getMaxHeight(points)
  averageHeight = getAverageHeight(points)
  hRes = int(width / stepSizeX)
  vRes = int(length / stepSizeY)

  hRes = 600
  vRes = 600

  scaleX = 1.3 / stepSizeX
  scaleY = 1 / stepSizeY

  print("size", hRes, vRes)

  res = Image.new("RGBA", (hRes, vRes), (0,0,0,0))
  artist = ImageDraw.Draw(res)

  print("drawing ...")
  for point in points:
    height = getHighestVertex(point)
    x = getPointX(point)
    y = getPointY(point)
    color = int(255/(maxHeight/(height or eH)))
    artist.line([scaleX*x, scaleY*y, scaleX*(x + ssX), scaleY*(y + ssY)], (color, color, color, 255), ssX+ssY, None)

  return res

drawHeightMap(mesh.points).convert('RGB').save("cloud_to_hmap.jpg",'JPEG')


# getHeightAt(mesh.points, 50, 50)

# print(your_mesh.points)
mesh.save('new_stl_file.stl')

print("WIN!")