# limit air speed
import Atmosphere
import Units

def regulartorySpeedLimit(altitude):
    if altitude < 10000.0:
        return 250
    else:
        return Atmosphere.speedOfSound(altitude)

def limitAirSpeed(maximumMachSpeed, weight, altitude, airSpeed):
    return min(airSpeed, regulartorySpeedLimit(altitude),
               Atmosphere.speedOfSound(altitude) * maximumMachSpeed)

def calculateMaximumAltitude(weight):
    intercept = 57100
    slope = - 0.11793
    limit = weight * slope + intercept
    return limit

def limitAltitude(weight, altitude):
    limit = calculateMaximumAltitude(weight)
    result = min(limit, altitude)
    return result
