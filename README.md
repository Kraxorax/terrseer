# terrseer
Terrain analysis and path finding.


## The problem
Given .obj, .tif and .tfw use A* to find a path of GPS coords that avoids too steep slopes

## Proposed solution
A* works in 2D. We need to encode face slopes from .obj into 2D representation.

```python
for face in mesh.faces:
  if face.normal < too_steep:
    img.draw(face)
```

Now we have 2D space encoded into image. Each pixel represents a cell in A* grid.
Apply A* to the grid and get a list of image coordinates, the path.

Now image coordinates have to be translated into GPS coords.
.tif and .twf files can be used to for that, under a couple of assumptions.
We assume that source .obj fits .tif, eg. no translation or rotation between them.

```python
# read from .twf file
# pixel X width, pixel X scew, pixel Y scew, pixel Y width, lat and lng at origin
pw, _, _, ph, oLat, oLng 

for (xPos, yPos) in path:
  geoPosX = xPos*pw + oLat
  geoPosY = yPos*ph + oLng
```

These GPS coords can be written to a .py file to be read by QGIS software.
A python script in QGIS takes those GPS coords to create new layer and draw polyLine in it.
