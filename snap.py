import arcpy
import os
from arcpy import env
#Change environment
env.workspace = r'C:\Users\chris\OneDrive - University of New Mexico\Documents\Yan internship\CrowSwat\newHRU\HRU_SNAP'
env.overwriteOutput = 1
# the path to the fishnet files
path = r'C:\Users\chris\OneDrive - University of New Mexico\Documents\Yan internship\CrowSwat\newHRU\HRU_SNAP\fishnet'

# Arguments
fishnet = ()
points = ()
lines = ()

#  Created Fishnet Features  --Will take a while only needs to be run once
with arcpy.da.SearchCursor(fishnet,['ID_1']) as cursor:
     for row in cursor:
         # set the variable newName as the old ID_1
         NewName = row[0]
         # print out a status message
         print('Selecting points that fall within polygon # ' + str(NewName))
         # format your sql statement to single out each row at a time
         where = '"ID_1" = ' + "'%s'" %NewName
         # select each row seperately
         arcpy.SelectLayerByAttribute_management(fishnet,'NEW_SELECTION',where)
         # Select points by location
         arcpy.management.SelectLayerByLocation(points, 'WITHIN', fishnet,'', 'NEW_SELECTION')
         # Snap selected points to line





# your centroid file to be snapped
centroid = arcpy.MakeFeatureLayer_management('centroid_1.shp')
# the original file to snap the features to
snapenv = arcpy.MakeFeatureLayer_management('StreamRoutes.shp')
# list the directory of the fishnet files
dir = os.listdir(path)
# create the snap environment, this should be in a list, item one is the feature, item 2 is EDGE, VERTEX, or END, and the third item is the distance
snapenv1 = [snapenv,'EDGE','500 Feet']

# cycle through the files in the directory
for file in dir:
    # if the file is a shapefile
    if file[-3:] == 'shp':
        # make the file a layer
        fishnet = arcpy.MakeFeatureLayer_management(path + '\\' + file)
        # select all centroids that intersect the file
        arcpy.SelectLayerByLocation_management(centroid,'INTERSECT',fishnet)
        # snap those features to the snap environment
        arcpy.Snap_edit(centroid,[snapenv1])
        # print out a status message
        print('snapping ' + str(filen))
