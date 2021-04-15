import pywavefront
from numpy import *
from stl import mesh
from PIL import Image, ImageDraw

# Using an existing stl file:
# mesh = mesh.Mesh.from_file('100x100 desert.stl')
scene = pywavefront.Wavefront('test_data/desert/texture.obj')

# how many pixels in horizontal meter
scaleFactor = 10

def sceneToElevationMap(scene):
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

  print('w, l, h <-', w, l, h)
  print('pixels in meter:', scaleFactor)

  brushSize = scaleFactor*0.3
  meterInColor = int(255 / h)

  elevationMapImage = Image.new("RGBA", (w*scaleFactor, l*scaleFactor), (255,0,0,0))
  artist = ImageDraw.Draw(elevationMapImage)

  print("drawing ...")
  for x, y, z in scene.vertices:
    height = z + abs(minZ)
    xPos = (x + abs(minX))*scaleFactor
    yPos = (y + abs(minY))*scaleFactor
    color = int(meterInColor * height)
    artist.regular_polygon(((xPos, yPos), brushSize), 6, 0, (color, color, color, 0))

  return elevationMapImage


if __name__ == '__main__':
  sceneToElevationMap(scene).convert('RGB').save("scene_to_hmap.png",'PNG')


print("WIN!")