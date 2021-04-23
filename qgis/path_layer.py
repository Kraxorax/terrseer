lines = iface.addVectorLayer("LineString?crs=wpsg:4326&field=id:integer&index=yes", "Lines", "memory")
lines.startEditing()
feature = QgsFeature()
qgsPoints = []
for lat, lng in POINTS:
    qgsPoints.append(QgsPoint(lng, lat))
feature.setGeometry(QgsGeometry.fromPolyline(qgsPoints))
feature.setAttributes([1])
lines.addFeature(feature)
lines.commitChanges()
#iface.zoomToActiveLayer()