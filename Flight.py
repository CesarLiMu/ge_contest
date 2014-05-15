import Units
import Spatial
import Zone
import Airspace
import Aircraft
import Airport
import CostParameters
#import InstructionValidator
import SimulationParameters
import SimulationTypes
import Weather
import Messages
import FlightTypes
import Movement
#import Assertions
import FuelModel

import math

def updateSimulationState(state, updateState):
    # FlightState
    state = FlightTypes.FlightState(
        AircraftPosition=updateState.AircraftPosition,
        AirSpeed=updateState.AirSpeed,
        GroundSpeed=updateState.GroundSpeed,
        TimeElapsed=state.TimeElapsed + updateState.TimeElapsed,
        FuelConsumed=state.FuelConsumed + updateState.FuelConsumed,
        IntersectedAirspace=updateState.IntersectedAirspace,
        TimeElapsedInTurbulence=state.TimeElapsedInTurbulence + \
            updateState.TimeElapsedInTurbulence,
        Messages= state.Messages + updateState.Messages)
    return state

def addMessageToState(state, message):
    return # TODO

def calculateMovement(coreFunctions, parameters, weather, state, instruction):
    # (coreFunctions:SimulationCoreFunctions)
    # (parameters:FlightParameters) 
    # (weather:WeatherState) (state:FlightState) (instruction:Instruction)
    time = parameters.ActualGateDepartureTime + state.TimeElapsed*1.0 # <Time/Hours>
    currentPosition = state.AircraftPosition
    altitude = Spatial.positionToAltitude(currentPosition)

    grossWeight = coreFunctions.WeightModel(parameters, state)
    (destination, instructedAirSpeed) = instruction

    currentLocation = Spatial.positionToLocation(currentPosition)
    destinationLocation = Spatial.positionToLocation(destination)
    destinationAltitude = coreFunctions.AltitudeLimiter(grossWeight,
            Spatial.positionToAltitude(destination))
    airSpeed = coreFunctions.AirSpeedLimiter(
        parameters.AircraftType.MaximumMachSpeed,
        grossWeight, altitude, instructedAirSpeed)
    deltaVector = Spatial.calculateLocationDifference(currentLocation, destinationLocation)
    distance = Spatial.calculateDistance1(currentLocation, destinationLocation)
    if distance <= 0.0 :
        zeroGroundSpeed = Spatial.Vector(0.0, 0.0)
        return (0.0, zeroGroundSpeed, 0.0, 0.0, 0.0, [])
    else:
        #windVector = getWindVelocity(weather, time, currentPosition)
        windVector = Weather.zeroWindVelocity
        groundSpeed = Movement.calculateGroundVelocity(airSpeed, 
                                                       Spatial.calculateRadians(deltaVector),
                                                       windVector)
        groundVector = Movement.rescale(deltaVector, groundSpeed)
        (cruiseBurn, verticalCruiseFuelDiff, verticalVelocity) =  \
        coreFunctions.FuelModel(FuelModel.flightFunctions, grossWeight, altitude, 
                                airSpeed,
                                FlightTypes.getVerticalState(altitude, destinationAltitude))
        return (cruiseBurn, groundVector, verticalCruiseFuelDiff, verticalVelocity, airSpeed, [])

def stepToWaypoint(coreFunctions, timeStep, arrivalRadius, parameters, weather, airspace, 
                   state, instruction):
    #(coreFunctions:SimulationCoreFunctions) (timeStep:float<Hours>) (arrivalRadius:float<NauticalMiles>)
    #(parameters:FlightParameters) (weather:WeatherState) (airspace:Airspace) (state:FlightState) (instruction:Instruction) =
    (currentX, currentY, currentZ) = state.AircraftPosition
    (destinationX, destinationY, destinationZRaw) = instruction.Waypoint
    grossWeight = coreFunctions.WeightModel(parameters, state)
    destinationZ = coreFunctions.AltitudeLimiter(grossWeight, destinationZRaw)
    distanceRemaining = Spatial.calculateDistance1(Spatial.Location(currentX, currentY), 
                                                   Spatial.Location(destinationX, destinationY))

    (cruiseBurn, groundVector, verticalCruiseFuelDiff, VerticalVelocity, airSpeed, messages) = \
        calculateMovement(coreFunctions, parameters, weather, state, instruction)
    # assertNonNegative "cruiseBurn" cruiseBurn
    groundSpeed = Movement.calculateSpeed(groundVector)
    distanceTravelled = groundSpeed * timeStep
    reachedDestination = distanceRemaining <= (distanceTravelled + arrivalRadius)
#    print 'distanceRemaing: ' + str(distanceRemaining) + 'distanceTravelled: ' + str(distanceTravelled + arrivalRadius)
    
    (groundSpeedX, groundSpeedY) = groundVector
    (groundX, groundY) = (float (groundSpeedX * timeStep), float (groundSpeedY * timeStep))
    elapsedRatio = 0.0
    if distanceTravelled > 0.0:
        elapsedRatio = min(distanceRemaining, distanceTravelled)/distanceTravelled

    timeElapsed = elapsedRatio * timeStep
    climbTimeElapsed = 0.0
    if math.fabs(VerticalVelocity) > 0.0:
        climbTimeElapsed = \
            min(1.0, 
                     ((destinationZ - currentZ)/(VerticalVelocity * timeElapsed)) * timeElapsed)
    newPosition = Spatial.Position(currentX+groundX*elapsedRatio,
                                   currentY+groundY*elapsedRatio,
                                   currentZ + VerticalVelocity*climbTimeElapsed)
    totalFuelBurn = cruiseBurn * timeElapsed + verticalCruiseFuelDiff * climbTimeElapsed
#    print 'totalFuelBurn:' + str(totalFuelBurn) + 'curise:' + str(cruiseBurn * timeElapsed) + \
#        'verticalBurn:' + str(verticalCruiseFuelDiff * climbTimeElapsed)

    intersectedAirspace = Airspace.aircraftInAirspace(airspace, state.AircraftPosition, newPosition)
    timeInTurbulence = 0.0
    if intersectedAirspace.TurbulentZone:
        timeInTurbulence = timeElapsed
    # Aircraft's new state
    return (reachedDestination,  
            FlightTypes.FlightState(
            AircraftPosition=newPosition,
            AirSpeed = airSpeed,
            GroundSpeed = groundSpeed,
            TimeElapsed = timeElapsed,
            FuelConsumed = totalFuelBurn,
            IntersectedAirspace = intersectedAirspace,
            TimeElapsedInTurbulence = timeInTurbulence,
            Messages = []))

def needToAbort(parameters, state, remainingSteps, arrived):
  #(parameters:FlightParameters) (state:FlightState) (remainingSteps:int) (arrived:bool): 
    exhaustedFuel = state.FuelConsumed > parameters.InitialFuel
    exhaustedSteps = remainingSteps < 1 and not arrived
    restrictedZonesEntered = state.IntersectedAirspace.RestrictedZone
    if exhaustedFuel or exhaustedSteps or restrictedZonesEntered:
        return True
    else:
        return False

# For each instruction, the plane moves at a time interval of (Configuration:TimeStep) hours
def runInstruction(coreFunctions, simParams, parameters, weather, airspace, state,
                   remainingSteps, instruction):
    # For each instruction, it's going step by step
    # (coreFunctions:SimulationCoreFunctions) (simParams:SimulationParameters) (parameters:FlightParameters)
    # (weather:WeatherState) (airspace:Airspace) (state:FlightState) (remainingSteps:int) (instruction:Instruction)=
    # TODO (check)
    autoLanding = (simParams['LandingMode'] == SimulationParameters.LandingMode.WhenInRange)
    instructionStatus = 'None' # defined in FlightTypes, but here we'll just use a string
    currentSteps = remainingSteps
    currentState = state
    #entries:List<FlightLogEntry> = []
    entries = []

    iter = 0
    while instructionStatus == 'None':
#        iter += 1
#        print 'wayPoint:' + str(iter)
        (reachedWaypoint, update) = stepToWaypoint(coreFunctions, simParams['TimeStep'], 
                                                   simParams['WaypointRadius'],
                                                   parameters, weather, airspace, 
                                                   currentState, instruction)
#        print 'update:'
#        print update
        updatedState = updateSimulationState(currentState, update)
#        print 'updated:'
#        print updatedState
        updatedSteps = currentSteps - 1
        instructionStatus = 'None'
        if needToAbort(parameters, updatedState, updatedSteps, reachedWaypoint):
            instructionStatus = 'Failed'
        elif autoLanding and Arrival.withinArrivalZone(parameters, updatedState):
            instructionStatus = 'Cancelled' #) // No further stepping needed
        elif reachedWaypoint:
            instructionStatus = 'Complete'
        currentSteps = updatedSteps
        currentState = updatedState
 #       print instructionStatus
        status = 'Crashed'
        if instructionStatus in ['Cancelled', 'Complete'] or instructionStatus == 'None':
            status =  'Flying'
        if simParams['RecordFlightLog']:
            weight = coreFunctions.WeightModel(parameters, currentState)
            (easting, northing, altitude) = currentState.AircraftPosition
            e = FlightTypes.FlightLogEntry(
                parameters.FlightId,
                0.0, #<Latitude> // Modified outside of the simulator
                0.0, #<Longitude>
                easting,
                northing,
                currentState.TimeElapsed,
                currentState.AirSpeed,
                currentState.GroundSpeed,
                altitude,
                currentState.FuelConsumed,
                weight,
                currentState.IntersectedAirspace.RestrictedZone,
                currentState.IntersectedAirspace.TurbulentZone,
                status)
            entries.append(e)
        
    if instructionStatus == 'Failed':
        finalState = currentState
        if currentSteps < 1:
            addMessageToState(currentState, Messages.StepLimitExceeded(
                    parameters.FlightId, currentState.AircraftPosition))
        elif currentState.FuelConsumed > parameters.InitialFuel:
            addMessageToState(currentState, Messages.FuelExhausted(
                              parameters.FlightId, currentState.AircraftPosition))
        elif currentState.IntersectedAirspace.RestrictedZone:
            addMessageToState(currentState, Messages.HitRestrictedZone(
                              parameters.FlightId, currentState.AircraftPosition))
        else:
            addMessageToState(currentState, Messages.UnknownError)
    else:
        finalState = currentState
    return (instructionStatus, currentSteps, entries, finalState)

# Moves aircraft through indicated waypoints (if they're reachable)
def runInstructions(coreFunctions, simParams, flightParams, weather, airspace, state, instructions):
#    (coreFunctions:SimulationCoreFunctions) (simParams:SimulationParameters) (flightParams : FlightParameters)
#    (weather:WeatherState) (airspace:Airspace) (state : FlightState) (instructions : Route) =
#       assertLessEqualTo "# of instructions" ((float)instructions.Length) "max # of instructions" ((float)simParams.MaxInstructions)
#        // Verify instructions meet flight rules
# for each flight
    # TODO
#    cleanInstructions = Array.map (coreFunctions.InstructionValidator simParams flightParams) instructions
# return value: instructionStatus, remainingSteps, log, endState
    # newLog:List<FlightLogEntry> = []
    newLog = []
#    // Iterate through the instructions; Stop if the previous instruction comes back Failed or Aborted
    previousState = ('Complete', simParams['MaxSteps'], newLog, state)
    for instruction in instructions:
        print instruction
        (instructionStatus, remainingSteps, log, currentState) = previousState
#        (newInstructionStatus, newRemainingSteps, newEntries, newCurrentState) = previousState
        if instructionStatus == 'Complete':
            newState = runInstruction(coreFunctions, simParams, flightParams, weather, airspace, \
                                   currentState, remainingSteps, instruction)
#            (newInstructionStatus, newRemainingSteps, newEntries, newCurrentState) = \
#                runInstruction(coreFunctions, simParams, flightParams, weather, airspace, \
#                                   currentState, remainingSteps, instruction)
            updatedLog = log + newState[2] # merge two lists
        else: 
            newState = previousState
            updatedLog=log
        previousState = newState
        (newInstructionStatus, newRemainingSteps, newEntries, newCurrentState) = newState
    return (newInstructionStatus, newRemainingSteps, updatedLog, newCurrentState)

