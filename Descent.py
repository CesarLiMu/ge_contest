import Units
import math
import Spatial

from collections import namedtuple

DescentModel = namedtuple('DescentModel', [
        'TimeIntercept', #:float
        'TimeAltitude', #:float
        'TimePower', # : float
        'FuelIntercept', #:float
        'FuelAltitude', #:float
        'FuelPower', # : float
        'DistanceIntercept', #:float
        'DistanceAltitude', #:float
        'DistanceAltitudeWeight', #:float
        'MaximumRateOfDescent' 
        ])

#// Descent Model for a mediumRange Aircraft
descentModelMediumRange = DescentModel(
    0.0242256,
    0.0002435,
    0.7,
    44.24,
    10.22,
    0.4,
    6.807,
    1.135e-03,
    1.414e-08,
    -240000.0)

def calculateTime(model, altitude):
#(model:DescentModel) (altitude:float<Feet>) =
    aTime = math.pow(altitude, model.TimePower)
    time = model.TimeIntercept + model.TimeAltitude * aTime
    maxDescent = math.fabs(float(altitude / model.MaximumRateOfDescent))
    result =  math.max(maxDescent, time)
    return result

def altitudeDerivativeWrtTime(model, altitude):
# (model:DescentModel) (altitude:float<Feet>) =
    dtda = model.TimeAltitude*model.TimePower* altitude**(model.TimePower-1.0)
    dadt = 1.0/dtda * -1.0
    result = max(model.MaximumRateOfDescent, dadt)
    return result

def calculateFuel(model, altitude):
# (model:DescentModel) (altitude:float<Feet>) =
    aFuel = (altitude)**model.FuelPower
    result = model.FuelIntercept + model.FuelAltitude*aFuel
    return result

def fuelDerivativeWrtAltitude(model, altitude):
# (model:DescentModel) (altitude:float<Feet>) =
    dfda = model.FuelAltitude*model.FuelPower * float(altitude) ** (model.FuelPower-1.0)
    return dfda

def calculateRates(model, altitude, weight):
# (model:DescentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    dAltitudeDTime = altitudeDerivativeWrtTime(model, altitude)
    dFuelDAltitude = fuelDerivativeWrtAltitude(model, altitude)
    dFuelDTime = math.fabs(dAltitudeDTime * dFuelDAltitude)
    return (dAltitudeDTime, dFuelDTime)

def calculateDistance(model, altitude, weight):
# (model:DescentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    a = altitude
    w = weight
    distance = model.DistanceIntercept+model.DistanceAltitude*a+model.DistanceAltitudeWeight*a*w
    return distance

def calculateTimeFuelDistance(model, altitude, weight):
# (model:DescentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    time = calculateTime(model, altitude)
    fuel = calculateFuel(model, altitude)
    distance = Spatial.calculateDistance(model, altitude, weight)
    return (time,fuel,distance)
