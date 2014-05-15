import Units
import CostParameters
import Aircraft
import Airport
import Spatial
import Airspace
# import Messages
import math

from collections import namedtuple

Instruction = namedtuple('Instruction', ['Waypoint', 'airspeed']) # Position, float<Knots>
Route = []
InstructionStatus = ('Complete', 'Failed', 'Cancelled')

FlightDirection = ('Eastbound', 'Westbound')

FlightState = namedtuple('FlightState', [
        'AircraftPosition', # : Position;
        'AirSpeed', # : float<Knots>
        'GroundSpeed', # : float<Knots>
        'TimeElapsed', # : float<Hours> // Relative to takeoff
        'FuelConsumed', # : float<FuelPounds>
        'IntersectedAirspace', # : IntersectedAirspace
        'TimeElapsedInTurbulence', #: float<Hours>
        'Messages' # : List<Message> // Messages are in reverse order
])

Payload = namedtuple('Payload', [
        'StandardPassengerCount', # : int
        'PremiumPassengerCount' # : int
        ])

FlightParameters = namedtuple('FlightParameters', [
        'FlightId', #          : int64
        'AircraftType', #             : AircraftType
        'DestinationAirport', #       : Airport
        'Direction', #                : FlightDirection
        'Payload', #                  : Payload
        'InitialFuel', # : float<FuelPounds>
        'ScheduledGateDepartureTime', # : float<Time>
        'ActualGateDepartureTime', # : float<Time>
        'ScheduledRunwayArrivalTime', #       : float<Time>
        'ScheduledGateArrivalTime'    #  : float<Time>
])

FlightStatus = ('Flying', 'Crashed', 'Landed')

FlightLogEntry = namedtuple('FlightLogEntry', [
        'FlightId', #            :int64
        'Latitude', #    :float<Latitude>
        'Longitude', #   :float<Longitude>
        'Easting', #             :float<PositionX>
        'Northing', #            :float<PositionY>
        'ElapsedTime', #         :float<Hours>
        'AirSpeed', #            :float<Knots>
        'GroundSpeed', #         :float<Knots>
        'Altitude',      #      :float<Feet>
        'FuelConsumed', #        :float<FuelPounds>
        'Weight', #              :float<Pounds>
        'InRestrictedZones', #   :bool
        'InTurbulentZones', #    :bool
        'Status' #              :FlightStatus
        ])

VerticalMovement = ('Ascent', 'Cruise', 'Descent')

def getVerticalState(currentAltitude, destinationAltitude):
    if math.fabs(currentAltitude - destinationAltitude) < 1:
        return 'Cruise'
    elif currentAltitude < destinationAltitude:
        return 'Ascent'
    else:
        return 'Descent'
