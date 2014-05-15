#import Assertions
import FlightTypes
import Airport
import Airspace
import Units
import Aircraft

from collections import namedtuple

FlightEntry = namedtuple('FlightEntry', [
        'Id',
        'Position', # : Spatial.Position
        'DepartureAirport', # : string
        'ArrivalAirport', # : string
        'Payload', # : Payload
        'InitialFuel', # : float<FuelPounds>
        'ConsumedFuel', # : float<FuelPounds>
        'ScheduledGateDepartureTime', # : float<Time>
        'ActualGateDepartureTime', # : float<Time>
        'ScheduledRunwayArrivalTime', # : float<Time>
        'ScheduledGateArrivalTime' #: float<Time>
        ])

FlightParameters = namedtuple('FlightParameters', [
        'FlightId',
        'Direction',
        'AircraftType',
        'DestinationAirport',
        'Payload',
        'InitialFuel',
        'ScheduledGateDepartureTime',
        'ActualGateDepartureTime',
        'ScheduledGateArrivalTime',
        'ScheduledRunwayArrivalTime'
        ])

FlightState = namedtuple('FlightState', [
        'AircraftPosition',
        'AirSpeed',
        'GroundSpeed',
        'TimeElapsed',
        'FuelConsumed',
        'IntersectedAirspace',
        'TimeElapsedInTurbulence',
        'Messages'
        ])

def generateParametersAndState(airports, entry):
    # TODO (niwang)
    # airports: a dict of AirportID to Airport object
    # the original list of Airport is a tuple of Airport and Environment, now we only keep
    # the Airport Object
    # entry: FlightEntry
    aircraftType = Aircraft.mediumRange
    departureAirport = airports[entry.DepartureAirport] #['Airport.Code']
    arrivalAirport = airports[entry.ArrivalAirport] #['Airport.Code']
    timeElapsed = Units.timeDifference(0.0, entry.ActualGateDepartureTime)
    maximumFuel = Units.fuelGallonsToFuelPounds(aircraftType.FuelCapacity)
    initialFuel = entry.InitialFuel
    fuelConsumed = entry.ConsumedFuel

    flightParameters = FlightParameters(
        entry.Id,
        'Eastbound' if departureAirport.Position.PositionX < \
            arrivalAirport.Position.PositionX else 'Westbound',
        aircraftType,
        arrivalAirport,
        entry.Payload,
        initialFuel,
        entry.ScheduledGateDepartureTime,
        entry.ActualGateDepartureTime,
        entry.ScheduledGateArrivalTime,
        entry.ScheduledRunwayArrivalTime)

    flightState = FlightState(
        entry.Position,
        0.0,
        0.0,
        timeElapsed,
        fuelConsumed,
        Airspace.emptyIntersection,
        0.0,
        [])
    return (flightParameters, flightState)

