import pywavefront
from numpy import *
from stl import mesh
from PIL import Image, ImageDraw
from timeit import default_timer as timer
from terrain3D import getGEOData


# how many pixels in horizontal meter
scaleFactor = 10
# cutoff angle for passable face
critAngle = math.pi/12

def sceneToNormalMap(scene):
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

  critSlopes = []
  print('Crit angle: ', critAngle)

  Image.MAX_IMAGE_PIXELS = None
  tif = Image.open('test_data\geo_dunes.tif')

  elevationMapImage = Image.new("RGBA", \
                                #(w*scaleFactor, l*scaleFactor), \
                                tif.size, \
                                (255,0,0,0))
  artist = ImageDraw.Draw(elevationMapImage)

  for msh in scene.mesh_list:
    print("single mesh ", dir(msh))
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
        pv1 = ((v1[0]+abs(minX))*scaleFactor, (v1[1]+abs(minY))*scaleFactor)
        pv0 = ((v0[0]+abs(minX))*scaleFactor, (v0[1]+abs(minY))*scaleFactor)
        pv2 = ((v2[0]+abs(minX))*scaleFactor, (v2[1]+abs(minY))*scaleFactor)
        artist.polygon([pv0, pv1, pv2], fill=(int(500*ang),255,0,255))

  print(shape(critSlopes))
  brushSize = scaleFactor*0.3
  meterInColor = int(255 / h)

  return elevationMapImage

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


def readNormals(m):
  """ Returns copy of the mesh without too steep faces.
  """
  critAng = math.pi/12
  trigs = []
  up = [0,0,1]

  start_time = timer()
  print(start_time, 'finding slopes for', len(m.normals), 'faces')
  for i in range(0, len(m.normals)):
    normal = m.normals[i]
    ang = angle_between(up, normal)
    if ang < critAng:
      trigs.append([m.points[i]])

  numSlopes = len(trigs)
  end_time = timer()
  print(end_time - start_time, 'found slopes: ', numSlopes)


  # noGoImg = Image.new("RGBA", , (255, 0, 0, 1))
  # drawNGI = ImageDraw.Draw(noGoImg)
  # for trig in trigs:


  data = zeros(numSlopes, dtype=mesh.Mesh.dtype)
  slopes = reshape(trigs, (-1, 9))

  for i in range(0, numSlopes -1):
    data['vectors'][i] = [slopes[i][0:3], slopes[i][3:6], slopes[i][6:9]]

  newMesh = mesh.Mesh(data.copy())

  return newMesh


def main():
  # our 3D scene
  scene = pywavefront.Wavefront('test_data/desert/texture.obj', collect_faces=True)
  sceneToNormalMap(scene).convert('RGB').save("scene_to_hmap.png",'PNG')

  # m = mesh.Mesh.from_file('test_data/texture.stl')
  # resultMesh = readNormals(m)
  # resultMesh.save('test_data/wat.stl')
  

if __name__ == '__main__':
  print('<- START ->')
  main()
  print('-> DONE <-')