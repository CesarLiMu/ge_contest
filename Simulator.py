import Units
#import Assertions
import CostModel
import FlightTypes
import SimulationTypes
import SimulationParameters
import CostParameters
import Flight
import Spatial
import Zone
import Airspace
import Aircraft
import AirSpeedLimiter
import Weather
import Messages
import FlightEntry
# import InstructionParser
import Arrival
import Serialization
import FuelModel
import WeightModel

#/// Container for core simulator functions
fullCoreFunctions = SimulationTypes.SimulationCoreFunctions(
    FuelModel.fuelBurn,
    WeightModel.grossWeight,
    AirSpeedLimiter.limitAirSpeed,
    AirSpeedLimiter.limitAltitude,
    Arrival.arrivalModel)
#    InstructionValidator.CleanInstruction)


#/// Simulates a single flight
def simulateFlight(coreFunctions, simParams, airportEnvironment, airspace, costParameters, weather,
                   state, flightParams, instructions):
    # (coreFunctions:SimulationCoreFunctions) (simParams:SimulationParameters) airportEnvironment airspace
    # costParameters (weather:WeatherState) (state:FlightState) (flightParams:FlightParameters) (instructions:Route) =
    instructionStatus, remainingSteps, log, endState = Flight.runInstructions(
        coreFunctions, simParams, flightParams, weather, airspace, state, instructions)
    reachedArrivalPoint = (instructionStatus != 'Failed' and 
                           simParams['LandingMode'] != SimulationParameters.LandingMode.NoLanding \
                               and Arrival.withinArrivalZone(flightParams, endState))

    landed = False
    if reachedArrivalPoint:
        weight = coreFunctions.WeightModel(flightParams, endState)
        time = Units.timeIncrement(flightParams.ActualGateDepartureTime, endState.TimeElapsed)
        landingState = coreFunctions.ArrivalModel(flightParams) #airportEnvironment, FuelModel.flightFunctions,
#                                                  flightParams, endState.AircraftPosition, weight, 
#                                                  time)
        updatedState = Flight.updateSimulationState(endState, landingState)
        
        # // Check that fuel tank was not exhausted during arrival
        if updatedState.FuelConsumed > flightParams.InitialFuel:
            airport = flightParams.DestinationAirport
            message = Messages.FuelExhausted(flightParams.FlightId, endState.AircraftPosition)
            Flight.addMessageToState(updatedState, message)
        else: 
            landed = True
        results = updatedState
    else:
        airport = flightParams.DestinationAirport
     #   print airport
        message = Messages.CannotLand(
            flightParams.FlightId, endState.AircraftPosition,
            airport.Code)
        Flight.addMessageToState(endState, message)
        results = endState

    fuelConsumed = Units.fuelPoundsToFuelGallons(results.FuelConsumed)
    delay = None
    if landed:
        arrivalTime = Units.timeIncrement(flightParams.ActualGateDepartureTime, 
                                           results.TimeElapsed)
        delay = Units.timeDifference(arrivalTime, flightParams.ScheduledGateArrivalTime)

    
    costs = CostModel.flightCost(costParameters, instructions, flightParams.Payload, 
                       fuelConsumed, delay, results.TimeElapsedInTurbulence)

#    // Add final record to flight log
    (east,north,altitude) = results.AircraftPosition

    finalLogEntry = FlightTypes.FlightLogEntry(
        FlightId = flightParams.FlightId,
        Latitude = 0.0, # <Latitude>
        Longitude =  0.0, # <Longitude>
        Easting = east,
        Northing = north,
        ElapsedTime = results.TimeElapsed,
        AirSpeed = 0.0, # <Knots>
        GroundSpeed = 0.0, #<Knots>
        Altitude = altitude,
        FuelConsumed = results.FuelConsumed,
        Weight = coreFunctions.WeightModel(flightParams, results),
        InRestrictedZones = False,
        InTurbulentZones = False,
        Status = 'Landed' if landed else 'Crashed'
    )
    updatedLog = log.append(finalLogEntry)
    return { 
        'FlightId'            : flightParams.FlightId,
        'Duration'            : results.TimeElapsed,
        'FuelBurned'          : results.FuelConsumed,
        'Messages'            : results.Messages,
        'Log'                 : updatedLog,
        'ReachedDestination'  : landed,
        'CostDetail'          : costs,
        'Cost'                : CostModel.accumulateCosts(costs)
    }


# /// Simulates a day of flights with the given instructions
def simulateFlights(simulationParameters, airports, airspace, weather, 
                    flightsAndCosts, instructions):
#    simulationParameters (airports:IDictionary<string,Airport.Airport*Arrival.AirportEnvironment>) (airspace:Airspace)
#    weather (flightsAndCosts:(FlightEntry*CostParameters)[]) (instructions:(int64*Instruction[])[]) =
    # TODO: convert instructions to a table of Id:instructions
    #let instructionTable = Map.ofArray instructions
    # instructions is a map of flightId to routes
    # Simulate each flight and return results in parallel
    # how to do it sequentially?
    flightResults = { } # id: cost 
    # does each flight have a cost parameter?
    for flightEntry, costParameters in flightsAndCosts:
       # print flightEntry
        if (flightEntry.Id in instructions) and (flightEntry.DepartureAirport in airports) and  \
                (flightEntry.ArrivalAirport in airports):
            instruction = instructions[flightEntry.Id]
            (flightParams, flightState) = FlightEntry.generateParametersAndState(
                airports, flightEntry)
            airportEnvironment = None
            #airportEnvironment = airports[flightEntry.ArrivalAirport][1] # TODO check the snd
            results = simulateFlight(fullCoreFunctions, simulationParameters, 
                                     airportEnvironment, 
                                     airspace,
                                     costParameters, weather, flightState, 
                                     flightParams, instruction)
            flightResults[flightEntry.Id] = results
    return flightResults
