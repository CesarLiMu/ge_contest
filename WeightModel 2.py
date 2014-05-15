import FlightTypes
import Aircraft
import Units

import math

def grossWeight(flightParameters, flightState):
# (flightParameters:FlightParameters) (flightState:FlightState) =
#    // Passengers average 190 lb
#    // Luggage is an average of 10-20 lb per passenger
    aircraft = flightParameters.AircraftType
    payload = flightParameters.Payload
    payloadWeight = (payload.PremiumPassengerCount + 
                     payload.StandardPassengerCount)*190.0 + payload.PremiumPassengerCount * 20.0 +
                    payload.StandardPassengerCount * 10.0
    initialFuel = flightParameters.InitialFuel
    fuelWeight = math.max(0.0, (initialFuel - flightState.FuelConsumed))
    return aircraft.OperatingEmptyWeight + payloadWeight + fuelWeight
