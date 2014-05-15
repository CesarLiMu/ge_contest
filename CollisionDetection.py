#n Assertions
import Units
import Spatial
import Zone
import math

from collections import namedtuple

ShapeProjection = namedtuple('ShapeProjection', [
        'Min', #:float
        'Max' #:float
        ])


def _range(array):
    #(array:float[]) = 
    return (min(array), max(array))

def projectLocationOntoAxis(location, axis):
# (location:Location) (axis:Vector) =
    vector = Spatial.locationToVector(location)
    return Spatial.calculateDotProduct(vector, axis)

def projectPolygonOntoAxis(polygon, axis):
# (polygon:Polygon) (axis:Vector) =
    projects = [ projectLocationOntoAxis(v, axis) for v in polygon ]
    # let projections = polygon |> Array.map (fun loc -> projectLocationOntoAxis loc axis)
    minV = min(projects)
    maxV = max(projects)
    return ShapeProjection(minV, maxV)

def projectSegmentOntoAxis(lineSegment, axis):
# (lineSegment:LineSegment) (axis:Vector) =
    point1 = projectLocationOntoAxis(lineSegment.Location1, axis)
    point2 = projectLocationOntoAxis(lineSegment.Location2, axis)
    minV = min(point1, point2)
    maxV = max(point1, point2)
    return ShapeProjection(minV, maxV)

def detect2DCollision(lineSegment, polygon):
#(lineSegment:LineSegment) (polygon:Polygon) =
#    // Check characteristics of the shapes
 #   assertGreaterEqualTo "sides" (float polygon.Length) "3 sides" 3.0
# http://stackoverflow.com/questions/12222700/determine-if-line-segment-is-inside-polygon
# first, sort a polygon. Here, polygons are assumed to be sorted already
    
  #  // Gather the sides for the polygon
    polygonSides = []
    for i in range(len(polygon)):
        if i == len(polygon) - 1:
            endPoint = polygon[0]
        else:
            endPoint = polygon[i+1]
        polygonSides.append(Spatial.LineSegment(polygon[i], endPoint))
            
    axes = polygonSides
    axes.append(lineSegment)
    axes = [ Spatial.toUnitVector(Spatial.toNormalVector(
                Spatial.calculateLocationDifference(v.Location1, v.Location2)))
             for v in axes ]

    #    // Check for separation between objects
    separationExists = False
    for axis in axes:
        polyProj = projectPolygonOntoAxis(polygon, axis)
        lineSegmentProj = projectSegmentOntoAxis(lineSegment, axis)
        #// Do gaps exist between max/min intervals?
        if polyProj.Min > lineSegmentProj.Max or lineSegmentProj.Min > polyProj.Max:
            separationExists = True
    return not separationExists

def detect3DCollision(lineSegment, altitude, polyhedron):
# (lineSegment:LineSegment) (altitude:float<Feet>) (polyhedron:Polyhedron) = 
 #   // Check bound values
#    assertGreaterEqualTo "altitude" (float altitude) "0.0" 0.0
#    assertGreaterEqualTo "Zone LowerBound" (float polyhedron.LowerBound) "0.0" 0.0
 #   assertGreaterThan "Zone UpperBound" (float polyhedron.UpperBound) "LowerBound" (float polyhedron.LowerBound)
    
    segmentMidPoint = Spatial.calculateMidpoint(lineSegment)
    #// Check upper/lower bounds and then 2d collision detection
    return polyhedron.LowerBound < altitude and altitude < polyhedron.UpperBound \
        and Spatial.calculateDistance(segmentMidPoint, polyhedron.Polygon[0]) < 600.0 \
        and detect2DCollision(lineSegment, polyhedron.Polygon)
