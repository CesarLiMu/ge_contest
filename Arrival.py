import Units
#import Assertions
import Spatial
import Airspace
import FlightTypes
#import ProximityTree
import Units

from collections import namedtuple
# /// Checks if flightState is within X distance to the airport
def withinArrivalZone(flightParams, state):
#(flightParams : FlightParameters) (state : FlightState) =
    airport = flightParams.DestinationAirport
    arrivalAltitude = airport.ArrivalAltitude
    arrivalDistance = airport.ArrivalDistance
    position = state.AircraftPosition
    altitude = Spatial.positionToAltitude(position)
    distance = Spatial.calculateDistance(Spatial.positionToLocation(position),
                                         Spatial.positionToLocation(airport.Position))
    result = altitude <= arrivalAltitude and distance <= arrivalDistance
    return result

GroundConditionsEntry = namedtuple('GroundConditionsEntry', [
        'Dewpoint', # : float
        'WindSpeed', # : float
        'Visibility', # : float
        'WindGusts', # : float
        'Temperature' # : float
        ])

# TODO, check Airport Ground Conditions
#type AirportGroundConditions = {
#    GroundConditionsMap : GroundConditionsEntry[]
#    TimeAxis : ProximityTree * float * float
#} with
#    member this.ConditionsAt (time:float<Time>) =
#        let timeValue = float time
#        let (tree, low, high) = this.TimeAxis
#        if timeValue < low || timeValue > high then
#            {Dewpoint=0.0;WindSpeed=0.0;Visibility=10.0;WindGusts=0.0;Temperature=45.0}
#        else
#            let timeIndex = findNearest tree timeValue
#            this.GroundConditionsMap.[timeIndex]

# /// Predicts time & fuel use given aircraft's current altitude
def arrivalModel(flightParams):
#    (airportEnvironment:AirportEnvironment) (_, descentModel, _, holdingModel)
#    (flightParams:FlightParameters) (position:Spatial.Position) weight time =
#    let airport = flightParams.DestinationAirport
#    let altitude = positionToAltitude position
#    let (descentTime, descentFuel, descentDistance) =
#        Descent.calculateTimeFuelDistance descentModel altitude weight
#    assertPositive "descentFuel" descentFuel
#    assertPositive "descentTime" descentTime
#
#    let landingModel = airportEnvironment.LandingModel
##    let taxiModel = airportEnvironment.TaxiModel
#    let airportConditions = airportEnvironment.GroundConditions
#    let airportLandings = airportEnvironment.LandingEvents
#    let landingTimePrediction = predictLanding landingModel airportConditions airportLandings flightParams time * 1.0<Hours>
#    let ratio = landingTimePrediction/descentTime
#    let taxiTimePrediction = predictTaxi taxiModel airportConditions airportLandings flightParams time * 1.0<Hours>
#    let holdingTime = max 0.0<Hours> (landingTimePrediction - descentTime)
#    let holdingFuelBurn = Holding.fuelBurn holdingModel weight altitude
#    assertPositive "holdingFuelBurn" holdingFuelBurn
#    let holdingFuel = holdingTime*holdingFuelBurn

#    let taxiFuel = taxiTimePrediction * flightParams.AircraftType.TaxiFuelBurn
    airport = flightParams.DestinationAirport
    return FlightTypes.FlightState(
        AircraftPosition = airport.Position,
        FuelConsumed = 0, #holdingFuel+descentFuel+taxiFuel
        TimeElapsed = 0,
        AirSpeed = 0.0,
        GroundSpeed = 0.0,
        IntersectedAirspace = Airspace.emptyIntersection,
        TimeElapsedInTurbulence = 0.0,
        Messages = [])
