import pywavefront
from numpy import *
from stl import mesh
from PIL import Image, ImageDraw

# Using an existing stl file:
# mesh = mesh.Mesh.from_file('100x100 desert.stl')
scene = pywavefront.Wavefront('test_data/desert/texture.obj')

# print(len(scene.vertices))
# print(scene.vertices)

# for name, mesh in scene.meshes.items():
#   print(dir(mesh))
#   print('MATRIJAL -> ' + str(name))
#   # Contains the vertex format (string) such as "T2F_N3F_V3F"
#   # T2F, C3F, N3F and V3F may appear in this string
#   print(material.vertex_format)

#   # Contains the vertex list of floats in the format described above
#   print(shape(material.vertices))
#   verts = int(len(material.vertices) / 5)
#   print("Num vertex: ", verts)
#   for bit in range(0, verts):
#       ver = material.vertices[bit:bit+5:]


res = None

eH = 0.00001

scaleFactor = 4

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

  scaleX = 1 / stepSizeX
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

def analizeScene(scene):
  minX, minY, minZ = float('inf'), float('inf'), float('inf')
  maxX, maxY, maxZ = float('-inf'), float('-inf'), float('-inf')
  print("analyzing ...")
  for x, y, z in scene.vertices:
    minX = x if x < minX else minX
    maxX = x if x > maxX else maxX
    minY = y if y < minY else minY
    maxY = y if y > maxY else maxY
    minZ = z if z < minZ else minZ
    maxZ = z if z > maxZ else maxZ

  print(str(minX) + " < X > " + str(maxX))
  print(str(minY) + " < Y > " + str(maxY))
  print(str(minZ) + " < Z > " + str(maxZ))

  w = int(maxX - minX)
  l = int(maxY - minY)
  h = int(maxZ - minZ)

  numPixels = w * l
  pixelDensity = len(scene.vertices) / numPixels

  print(w, l, h)
  print(scaleFactor)

  res = Image.new("RGBA", (w*scaleFactor, l*scaleFactor), (0,0,0,0))
  artist = ImageDraw.Draw(res)

  print("drawing ...")
  for x, y, z in scene.vertices:
    height = z + abs(minZ)
    xPos = (x + abs(minX))*scaleFactor
    yPos = (y + abs(minY))*scaleFactor
    color = int(255/(h/(height or eH)))
    # print(h, height, color)
    # artist.line([xPos, yPos, xPos, yPos], (color, color, color, 255), 8, None)
    artist.regular_polygon(((xPos, yPos), scaleFactor*0.3), 6, 0, (color, color, color, 255))
  # decide up axis
  return res


analizeScene(scene).convert('RGB').save("scene_to_hmap.png",'PNG')

# drawHeightMap(mesh.points).convert('RGB').save("cloud_to_hmap.jpg",'JPEG')


# getHeightAt(mesh.points, 50, 50)

# print(your_mesh.points)
# mesh.save('new_stl_file.stl')

print("WIN!")