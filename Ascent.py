import Units
import math

from collections import namedtuple

AscentModel = namedtuple('AscentModel', [
        'DistanceIntercept', #:float
        'DistanceAltitude', #:float
        'DistanceWeight', #:float
        'DistanceAltitudeWeight', #:float
        'TimeAltitudePower', # : float
        'TimeIntercept', #:float
        'TimeAltitude', #:float
        'TimeWeight', #:float
        'TimeAltitudeWeight', #:float
        'FuelIntercept', # : float
        'FuelAltitude', # : float
        'FuelAltitudeSqrt',# : float
        'FuelWeight', # : float
        'FuelAltitudeWeight', # : float
        'FuelAltitudeSqrtWeight', # :float
        'MaximumRateOfAscent'
        ])

ascentModelMediumRange = AscentModel(
     1.062,
      5.224e-5,
      5.215e-6,
     2.029e-10,
      1.2,
      -3.775229,
      3.226931e-06,
      5.633243e-06,
      2.077038e-11,
      3.985,
      -5.179e-05,
      2.366e-02,
      1.463e-05,
      4.899e-10,
      -1.121e-07,
      240000.0)

def calculateTime(model, altitude, weight):
#(model:AscentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    a = altitude
    w = weight
    aTime = math.pow(a, model.TimeAltitudePower)
    result = math.exp(model.TimeIntercept + model.TimeAltitude*aTime + model.TimeWeight*w + model.TimeAltitudeWeight*aTime*w)
    return result

def altitudeDerivativeWrtTime(model, altitude, weight):
#(model:AscentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    a = max(1, altitude)
    w = weight
    time = calculateTime(model, altitude, weight)
    multiplicand = \
        (model.TimeAltitude + model.TimeAltitudeWeight*w) * \
        model.TimeAltitudePower * math.pow(a, model.TimeAltitudePower-1.0)
    dtda = time * multiplicand / 1.0
    dadt = 1.0/dtda
    result = min(model.MaximumRateOfAscent, dadt)
    return result

def calculateFuel(model, altitude, weight):
#(model:AscentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    a = altitude
    w = weight
    aFuel = math.sqrt(altitude)
    result = math.exp(
        model.FuelIntercept + model.FuelAltitude*a + model.FuelAltitudeSqrt*aFuel + \
        model.FuelWeight*w + \
            model.FuelAltitudeWeight*a*w + model.FuelAltitudeSqrtWeight*aFuel*w)
    return result

def fuelDerivativeWrtAltitude(model, altitude, weight):
# (model:AscentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    a = altitude
    w = weight
    aFuelDerivative = 0.5/math.sqrt(a)
    fuel = calculateFuel(model, altitude, weight)
    multiplicand = \
        model.FuelAltitude + model.FuelAltitudeSqrt*aFuelDerivative + \
        model.FuelAltitudeWeight * w + model.FuelAltitudeSqrtWeight * w * aFuelDerivative
    dfda = fuel*multiplicand
    return dfda


def calculateRates(model, altitude, weight):
#(model:AscentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    dAltitudeDTime = altitudeDerivativeWrtTime(model, altitude, weight)
    dFuelDAltitude = fuelDerivativeWrtAltitude(model, altitude, weight)
    dFuelDTime = dFuelDAltitude*dAltitudeDTime
    return (dAltitudeDTime, dFuelDTime)

def calculateTimeFuelDistance(model, altitude, weight):
# (model:AscentModel) (altitude:float<Feet>) (weight:float<Pounds>) =
    a = altitude
    w = weight
    time = calculateTime(model, altitude, weight)
    fuel = calculateFuel(model, altitude, weight)
    distance = math.exp(model.DistanceIntercept + model.DistanceAltitude * a +  \
                        model.DistanceWeight * w + model.DistanceAltitudeWeight * a * w)
    return (time,fuel,distance)
