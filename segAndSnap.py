################################################################################
#
# segAndSnap.py
# Author: Daniel Beene, September 17, 2021
#
# ABOUT:
# This script is part of the downstream drainage distance model, for which
# the Hydrologic Response Unit (HRU) polygon feature class is exploded from
# multipart to singlepart structure and represented as points for each polygon
# centroid. Depending on input arguments dictating the HRU, there can be close
# 1,000,000 points - presenting an intractible processing burden on the ArcGIS
# linear referencing tool to locate features along routes.
#
# This script improves processing time of input points by segmenting the HRU
# feature class into many small parts (e.g. 10,000), and snapping points that
# fall within a prescribed distance to the route polyline feature class.
#
# After snapping, the next step will be to locate features along routes without
# any consideration of perpindicular distance from polylines, thereby reducing
# processing time.
#
# STEPS/CONSIDERATIONS:
# 1) Define workspace
# 2) Define HRU point feature class (variable = 'points')
# 3) Define routes feature class (variable = 'routes')
# 4) Select an appropriate number of cells to segment feature class
#    (e.g. 100 x 100 = 10,000 operations)
# 5) Select an appropriate snapping distance for analysis (e.g. mean shape
#    distance of HRU polygon feature class)
#
################################################################################
#
# FUTURE MODIFICATIONS:
# 1) Code as tool GUI in ArcMap
# 2) Allow user to select number of cells for fishnet and define vars for
#    # of rows,cols as square root of input argument rounded to nearest int.
# 3) Add messages to each processing step
#
################################################################################

# Import modules, set environments
import arcpy
from arcpy import env
arcpy.env.overwriteOutput = True
arcpy.env.workspace = r'D:\P50'

# Arguments
# points
points = '20210616HRUPts.shp'
arcpy.management.MakeFeatureLayer(points, 'points')

# return extents of point feature class
desc = arcpy.Describe(points)
xmin = desc.extent.XMin
xmax = desc.extent.XMax
ymin = desc.extent.YMin
ymax = desc.extent.YMax

# routes
routes = arcpy.management.MakeFeatureLayer('StreamRoutes.shp')

# create fishnet
# fishnet arguments
def coord(a,b):
    return (str(a) + " " + str(b)).strip()
def tempcoord(a,b,c,d):
    return (str(a) + " " + str(b) + " " + str(c) + " " + str(d)).strip()

fishnet = arcpy.CreateFishnet_management(out_feature_class="fishnet.shp",
origin_coord=coord(xmin,ymin),
y_axis_coord=coord(xmin,ymin+1),
cell_width="",
cell_height="",
number_rows="100",
number_columns="100",
corner_coord=coord(xmax,ymax),
labels="NO_LABELS",
template=tempcoord(xmin,ymin,xmax,ymax),
geometry_type="POLYGON")
print('Fishnet created.')

# Select fishnet features coincident with HRU points
arcpy.management.SelectLayerByLocation("fishnet", "COMPLETELY_CONTAINS", "points")
fish = arcpy.CopyFeatures_management("fishnet", "fishnet_selection.shp")
print('Fishnet subset.')

# Snap environment
snapEnv = [[routes,'EDGE','652.999574 Meters']] # Change distance

# Loop through each polygon in fishnet feature layer, select coincident points, snap selection to routes
with arcpy.da.SearchCursor("fishnet_selection",['FID']) as cursor:
     for row in cursor:
         # set the variable newName as the old ID_1
         NewName = row[0]
         # print out a status message
         print('Selecting points that fall within polygon # ' + str(NewName))
         # format your sql statement to single out each row at a time
         where = '"FID" = ' + str(NewName)
         # select each row seperately
         arcpy.SelectLayerByAttribute_management("fishnet_selection", 'NEW_SELECTION', where)
         # Select points by location
         arcpy.management.SelectLayerByLocation("points", 'WITHIN', "fishnet_selection", '', 'NEW_SELECTION')
         # Snap selected points to line
         arcpy.Snap_edit("points",snapEnv)
         print('Polygon # ' +str(NewName) + ' finished processing.')