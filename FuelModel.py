import Units
import Aircraft
import FlightTypes
#import Assertions
import math
import Ascent
import Descent
import Cruise
import Holding

from collections import namedtuple
#type FlightFunctions = Ascent.AscentModel * Descent.DescentModel * Cruise.CruiseModel * Holding.HoldingModel

FlightFunctions = namedtuple('FlightFunctions', [
        'Ascent', 'Descent', 'Cruise', 'Holding'])

#{'Ascent': Ascent.AscentModel,
#                   'Descent': Descent.DescentModel,
#                   'Cruise': [],
#                   'Holding': Holding.HoldingModel }

flightFunctions = FlightFunctions(Ascent.ascentModelMediumRange, 
                                  Descent.descentModelMediumRange, 
                                  Cruise.cruiseModelMediumRange, 
                                  Holding.holdingModelMediumRange)

def fuelBurn(f,
             weight, altitude, airSpeed, vertical):
# (ascentModel, descentModel, cruiseModel, _) (weight:float<Pounds>) (altitude:float<Feet>) 
# (airSpeed:float<Knots>) (vertical:VerticalMovement) =
    cruiseFuelBurn = Cruise.fuelBurn(f.Cruise, weight, altitude, airSpeed)
    #assertNumber "cruiseFuelBurn" cruiseFuelBurn
    #assertNonNegative "cruiseFuelBurn" cruiseFuelBurn
    if vertical == 'Descent':
        (descentRate, descentFuelBurn)= Descent.calculateRates(f.Descent, altitude, weight)
        (modelBurn, verticalVelocity) = (descentFuelBurn, descentRate)
    elif vertical == 'Cruise':
        # | Cruise -> (0.0<FuelPounds/Hours>, 0.0<Feet/Hours>)
        (modelBurn, verticalVelocity) = (0, 0)
    elif vertical == 'Ascent':
        (ascentRate, rawAscentFuelBurn) = Ascent.calculateRates(f.Ascent, altitude, weight)
        ascentFuelBurn = max(rawAscentFuelBurn, cruiseFuelBurn)
        (modelBurn, verticalVelocity) = (ascentFuelBurn, ascentRate)
    verticalCruiseFuelDiff = modelBurn - cruiseFuelBurn
    return (cruiseFuelBurn, verticalCruiseFuelDiff, verticalVelocity)
