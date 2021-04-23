import pywavefront
import random
import matplotlib.pyplot as plt
from numpy import *
from stl import mesh
from PIL import Image, ImageDraw
from timeit import default_timer as timer
from PIL import Image, ImageFilter, ImageDraw
from pathfinding.core.diagonal_movement import DiagonalMovement
from pathfinding.core.grid import Grid
from pathfinding.finder.a_star import AStarFinder

# source paths
path_to_obj = 'test_data/desert/texture.obj'
path_to_tfw = 'test_data/geo_dunes.tfw'
path_to_tif = 'test_data/geo_dunes.tif'
# result paths
path_to_img_result = "test_data/found_path.png"
path_to_PF_matrix_txt = 'test_data/matrixFile.txt'
path_to_QGIS_point_path = 'qgis\points.py'

# how many pixels(A* grid cells) in a meter (1 unit of distance in .obj)
scaleFactor = 4
# cutoff angle for passable face
critAngle = math.pi/14


def sceneToNormalMap(scene):
  ''' Draws faces in 2D map, coloring slopes
      Returns PNG, pixels as map cells
  '''
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

  slopeMapImage = Image.new("RGBA", \
                                (w*scaleFactor, l*scaleFactor), \
                                (255,0,0,0))
  artist = ImageDraw.Draw(slopeMapImage)

  print('drawing slope map...')
  for msh in scene.mesh_list:
    for face in msh.faces:
      v0, v1, v2 =  scene.vertices[face[0]], \
                    scene.vertices[face[1]], \
                    scene.vertices[face[2]]

      vx = v0[0] - v1[0]
      vy = v0[1] - v1[1]
      vz = v0[2] - v1[2]
      ux = v0[0] - v2[0]
      uy = v0[1] - v2[1]
      uz = v0[2] - v2[2]

      n = cross((vx, vy, vz), (ux, uy, uz))
      ang = angle_between(unit_vector(n), [0,0,1])

      if (ang < critAngle):
        pv1 = ((v1[0]+abs(minX))*scaleFactor, (abs(maxY)-v1[1])*scaleFactor)
        pv0 = ((v0[0]+abs(minX))*scaleFactor, (abs(maxY)-v0[1])*scaleFactor)
        pv2 = ((v2[0]+abs(minX))*scaleFactor, (abs(maxY)-v2[1])*scaleFactor)
        artist.polygon([pv0, pv1, pv2], fill=(int(1000*ang),255,0,255))

  return slopeMapImage

def unit_vector(vector):
    """ Returns the unit vector of the vector.  """
    return vector / linalg.norm(vector)

def angle_between(v1, v2):
    """ Returns the angle in radians between vectors 'v1' and 'v2'::

            >>> angle_between((1, 0, 0), (0, 1, 0))
            1.5707963267948966
            >>> angle_between((1, 0, 0), (1, 0, 0))
            0.0
            >>> angle_between((1, 0, 0), (-1, 0, 0))
            3.141592653589793
    """
    v1_u = unit_vector(v1)
    v2_u = unit_vector(v2)
    return arccos(clip(dot(v1_u, v2_u), -1.0, 1.0))

# checks colors to decide if pixel can be passed thru
def isPassablePixel(r, g, b):
  return 0 if r == 255 else 255-r

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
  foundPassable = None
  while foundPassable == None:
    x = random.randint(0, img.width)
    y = random.randint(0, img.height)
    (pr, _pg, _pb, _a) = img.getpixel((x, y))
    if pr < 255:
      foundPassable = (x, y)
  return foundPassable

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
  matrixFile = open(path_to_PF_matrix_txt, 'w')
  for row in matrix:
    for cell in row:
      matrixFile.write(str(cell))
    matrixFile.write("\n")
  matrixFile.close()

def doPF(im):
  startX, startY = pickPoint(im)
  endX, endY = pickPoint(im)
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
  gdFile = open(path_to_tfw)
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

def writePointsForQGIS(GPPath):
  pathGM=open(path_to_QGIS_point_path,'w')
  pathGM.write('POINTS = [')
  for lng, lat in GPPath:
    pathGM.write('('+str(lat)+','+str(lng)+'),')
  pathGM.write(']')
  pathGM.close()

def main():
  scene = pywavefront.Wavefront(path_to_obj, collect_faces=True)
  slopeMap = sceneToNormalMap(scene)

  Image.MAX_IMAGE_PIXELS = None
  tif = Image.open(path_to_tif)
  res = Image.new("RGBA", slopeMap.size, (0,0,0,0))
  path = doPF(slopeMap)

  [pw, _a, _b, ph, oriLat, oriLong] = getGEOData()
  print(pw, _a, _b, ph, oriLat, oriLong)

  GPPath = pathToGPArray(path, (tif.width/slopeMap.width)*float(pw), (tif.height/slopeMap.height)*float(ph), float(oriLat), float(oriLong))

  writePointsForQGIS(GPPath)

  plotIt(GPPath)

  drawPath(res, path)

  resultImg = Image.alpha_composite(slopeMap, res)
  resultImg.convert('RGB').save(path_to_img_result,'PNG')


if __name__ == '__main__':
  print('<- START ->')
  main()
  print('-> DONE <-')