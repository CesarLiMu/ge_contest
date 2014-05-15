import Units
import math

from collections import namedtuple

LambertProjection = namedtuple('LambertProjection', [
        'StandardParallel', # : float<Latitude>
        'ReferenceLatitude', # : float<Latitude>
        'ReferenceLongitude', # : float<Longitude>
        'EarthRadius' # : float
        ])

def latitudeDegreesToRadians(latitude):
    return latitude / 180.0 * math.pi

def longitudeDegreesToRadians(longitude):
    return longitude / 180.0 * math.pi

def radiansToLatitudeDegrees(radians):
    return radians / math.pi * 180.0

def radiansToLongitudeDegrees(radians):
    return radians / math.pi * 180.0

def _boundLongitude (angle):
    return Units.boundAngle(angle) * 1.0 # <Longitude>

def _adjustAngle(angle):
    quarterPi = 0.25 * math.pi
    return 0.5 * angle + quarterPi

def _inverseAdjustAngle(adjustedAngle):
    return (_adjustedAngle - 0.25*math.pi) * 2.0

def _toEastingNorthing(earthRadius, n, rho, rho0, referenceLongitude, longitude):
#referenceLongitude:float<Longitude>) (longitude:float<Longitude>) =
    theta = n*(longitudeDegreesToRadians(_boundLongitude(longitude)) - 
               longitudeDegreesToRadians(_boundLongitude(referenceLongitude)))
    easting = rho * math.sin(theta) *earthRadius
    northing = (rho0 - rho* math.cos (theta))*earthRadius
    return (easting,northing)

def _calculateN(projection): #:LambertProjection) =
    sp1 = latitudeDegreesToRadians(projection.StandardParallel)
    result = math.sin(sp1)
    return result

def _calculateRho(projection, n, latitude):
#(projection:LambertProjection) n (latitude:float<Latitude>) =
    sp1 = latitudeDegreesToRadians(projection.StandardParallel)
    angle = latitudeDegreesToRadians(latitude)
    result = ((math.tan(_adjustAngle(sp1))/ math.tan(_adjustAngle(angle))) ** n) \
        * math.cos(sp1) / n
    return result

def _inverseRho(projection, n, rho):
#:LambertProjection) n rho =
    sp1 = latitudeDegreesToRadians(projection.StandardParallel)
    tanAngle = (math.tan(_adjustAngle(sp1))) / ((rho * n / cos(sp1)) ** (1.0/n))
    result = radiansToLatitudeDegress(inverseAdjustAngle(math.atan(tanAngle)))
    return result

#///  Converts Latitude/Longitude to LambertProjection


def toLambert(projection, coordinates):
# (projection:LambertProjection) (coordinates:float<Latitude>*float<Longitude>) =
    (latitude,longitude) = coordinates
    n = _calculateN(projection)
    rho = _calculateRho(projection, n, latitude)
    rho0 = _calculateRho(projection, n, (projection.ReferenceLatitude))
    result = _toEastingNorthing(projection.EarthRadius, n, rho, rho0, 
                                projection.ReferenceLongitude, longitude)
    #(fst result * 1.0<PositionX>, snd result * 1.0<PositionY>)
    return result

#/// Converts LambertProjection to Latitude/Longitude
def fromLambert(projection, coordinates):
#(projection:LambertProjection) (coordinates:float<PositionX>*float<PositionY>) =
    (easting,northing) = coordinates
    n = _calculateN(projection)
    rho0 = _calculateRho(projection, n , (projection.ReferenceLatitude))
    coNorthing = rho0 - ((northing)/projection.EarthRadius)
    scaledEasting = easting/projection.EarthRadius
    theta = math.atan(scaledEasting / coNorthing)
    rho = math.sqrt(scaledEasting*scaledEasting + coNorthing*coNorthing) * float(math.copysign(1, n))
    latitude = _inverseRho(projection, n, rho)
    longitude = projection.ReferenceLongitude + radiansToLongitudeDegrees(theta/n)
    return (latitude,longitude)

def toGribCoordinates(projection, latitude, longitude, altitude):
    (easting,northing) = _toLambert(projection, (latitude, longitude))
    return Spatial.Position(easting, northing, altitude)
