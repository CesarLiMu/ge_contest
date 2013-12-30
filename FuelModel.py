import Units
import Aircraft
import FlightTypes
import Assertions
import math
from Cruise import * 
from Descent import  *
from Ascent import *

#type FlightFunctions = Ascent.AscentModel * Descent.DescentModel * Cruise.CruiseModel * Holding.HoldingModel

FlightFunctions = {'Ascent': Ascent.AscentModel,
                   'Descent': Descent.DescentModel,
                   'Cruise': Cruise.CruiseModel,
                   'Holding': Holding.HoldingModel }

flightFunctions = (Ascent.ascentModelMediumRange, 
                   Descent.descentModelMediumRange, 
                   Cruise.cruiseModelMediumRange, 
                   Holding.holdingModelMediumRange)


def fuelBurn(weight, altitude, airSpeed, vertical):
    mediumRangeCruise = Cruise()
    cruiseFuelBurn = mediumRangeCruise.fuelBurn(weight, altitude, airSpeed)
    (modelBurn, verticalVelocity) = (0, 0)  # (0.0<FuelPounds/Hours>, 0.0<Feet/Hours>)
    if vertical == 'Descent':
        (descentRate, descentFuelBurn)= Descent().calculateRates(altitude, weight)
        (modelBurn, verticalVelocity) = (descentFuelBurn, descentRate)
    elif vertical == 'Ascent':
        (ascentRate, rawAscentFuelBurn) = Ascent().calculateRates(altitude, weight)
        ascentFuelBurn = math.max(rawAscentFuelBurn, cruiseFuelBurn)
        (modelBurn, verticalVelocity) = (ascentFuelBurn, ascentRate)
    
    verticalCruiseFuelDiff = modelBurn - cruiseFuelBurn
    return (cruiseFuelBurn, verticalCruiseFuelDiff, verticalVelocity)


# BY NICK
def fuelBurn2(ascentModel, descentModel, cruiseModel, weight, altitude, airSpeed, vertical):
# (ascentModel, descentModel, cruiseModel, _) (weight:float<Pounds>) (altitude:float<Feet>) 
# (airSpeed:float<Knots>) (vertical:VerticalMovement) =
    cruiseFuelBurn = Cruise.fuelBurn(cruiseModel, weight, altitude, airSpeed)
    #assertNumber "cruiseFuelBurn" cruiseFuelBurn
    #assertNonNegative "cruiseFuelBurn" cruiseFuelBurn
    (modelBurn, verticalVelocity) =
    if vertical == 'Descent':
        (descentRate, descentFuelBurn)= Descent.calculateRates(descentModel, altitude, weight)
        (modelBurn, verticalVelocity) = (descentFuelBurn, descentRate)
    elif vertical == 'Cruise':
        # | Cruise -> (0.0<FuelPounds/Hours>, 0.0<Feet/Hours>)
        (modelBurn, verticalVelocity) = (0, 0)
    elif vertical == 'Ascent':
        (ascentRate, rawAscentFuelBurn) = Ascent.calculateRates(ascentModel, altitude, weight)
        ascentFuelBurn = math.max(rawAscentFuelBurn, cruiseFuelBurn)
        (modelBurn, verticalVelocity) = (ascentFuelBurn, ascentRate)
    verticalCruiseFuelDiff = modelBurn - cruiseFuelBurn
    return (cruiseFuelBurn, verticalCruiseFuelDiff, verticalVelocity)
