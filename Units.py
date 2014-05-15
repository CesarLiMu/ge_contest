import math

def timeIncrement(time, increment):
    result = time + increment  # check whether time is in hours
    return result
   
def timeDifference(minuend, subtrahend):
    difference = minuend - subtrahend
    return difference # in hours

def metresToNauticalMiles(metres):
    return metres * 0.000539957

def fuelPoundsToFuelGallons(fuelPounds):
    return fuelPounds / 6.71

def fuelGallonsToFuelPounds(fuelGallons):
    return fuelGallons * 6.71

def boundAngle(angle):
    multiple = math.floor((angle+180)/360)
    result = angle - multiple * 360
    return result
