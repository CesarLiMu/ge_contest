import Units
import Spatial
import math

def calculateSpeed(v):
    # v is vector
    m = Spatial.calculateMagnitude(v)
    return m

def rescale(v, s):
    m = calculateSpeed(v)
    ratio = 0
    if m > 0:
        ratio = s / m
    try:
        r = Spatial.Vector(v.DirectionX * ratio, v.DirectionY * ratio)
    except:
        r = Spatial.Vector(v.PositionX * ratio, v.PositionY * ratio)
    return r

def calculateGroundVelocity(airspeed, groundDirection, wind):
    windDirection = Spatial.calculateRadians(wind)
    windspeed = Spatial.calculateMagnitude(wind)
    aDirection = (windDirection - groundDirection) % ( 2 * math.pi)
    precision = 1e-6
    
    # no wind, groundspeed is airspeed
    if windspeed <= precision:
        return airspeed
    elif math.fAbs(aDirection) <= precision: # then // Same direction
        return airspeed + windspeed
    elif math.fabs(aDirection - math.pi) <= precision: # then // Opposite direction
        return airspeed - windspeed
    else:
        w = math.asin((windspeed * math.sin(aDirection)) / airspeed)
        g = math.pi - aDirection - w
        return airspeed * math.sin(g) / math.sin(aDirection)
