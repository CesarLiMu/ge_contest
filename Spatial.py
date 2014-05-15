import Units 
from collections import namedtuple
import math

Vector = namedtuple('Vector', ['PositionX', 'PositionY'])

Location = namedtuple('Location', ['PositionX', 'PositionY'])

Position = namedtuple('Position', ['PositionX', 'PositionY', 'Feet'])

LineSegment = namedtuple('LineSegment', ['Location1', 'Location2'])

Polygon = [] # an array of Locations

Polyhedron = namedtuple('Polyhedron', ['Polygon', 'LowerBound', 'UpperBound'])

# A few functions here are very trial
def positionToLocation(position):
    return Location(position.PositionX, position.PositionY)

def positionToAltitude(position):
    return position.Feet

def locationToVector(location):
    return Vector(location.PositionX, location.PositionY)

# should we define classes for all these metrics? or just use internal
# tuples to represent each pair, or triplets?

def calculateMidpoint (line):
    return Location((line.Location1.PositionX + line.Location2.PositionX) / 2.0,
                    (line.Location1.PositionY + line.Location2.PositionY) / 2.0)

def calculateRadians(v):
    try:
        r = math.atan2(v.DirectionY, v.DirectionX)
    except:
        r = math.atan2(v.PositionY, v.PositionX)
    return r

def calculateMagnitude(v):
    try:
        r = math.sqrt(math.pow(v.DirectionX, 2) + math.pow(v.DirectionY, 2))
    except:
        r = math.sqrt(math.pow(v.PositionX, 2) + math.pow(v.PositionY, 2))
    return r

def calculateMagnitude1(v):
    return math.sqrt(math.pow(v.PositionX, 2) + math.pow(v.PositionY, 2))

def calculateLocationDifference(origin, destination): # orig, dest are two locations, unit in meters?
    return Location(destination.PositionX - origin.PositionX, 
                    destination.PositionY - origin.PositionY)

def calculateDistance(origin, destination):
    diff = calculateLocationDifference(origin, destination)
    distance = calculateMagnitude(diff)
    # convert to NauticaMiles
    return distance

def calculateDistance1(origin, destination):
    diff = calculateLocationDifference(origin, destination)
    distance = calculateMagnitude1(diff)
# convert to NauticaMiles                                                                        
    return distance


def calculateSum(u, v): # u,v are vectors
#    return Vector(u.DirectionX + v.DirectionX, u.DirectionY + v.DirectionY)
    return Vector(u.PositionX + v.PositionX, u.PositionY + v.PositionY)

def calculateDifference(u, v):
#    return Vector(u.DirectionX - v.DirectionX, u.DirectionY - v.DirectionY)
    return Vector(u.PositionX - v.PositionX, u.PositionY - v.PositionY)

def calculateDotProduct(u, v):
 #   return u.DirectionX * v.DirectionX + u.DirectionY * v.DirectionY
    return u.PositionX * v.PositionX + u.PositionY * v.PositionY

def toNormalVector(v):
    return Vector(-v.PositionY, v.PositionX)
#    return r

def toUnitVector(v):
    length = calculateMagnitude(v)
    if length == 0:
        return Vector(0, 0)
    return Vector(v.PositionX/ length, v.PositionY / length)



