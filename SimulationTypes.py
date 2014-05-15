import Units
import Aircraft
# import Arrival
import FlightTypes
import SimulationParameters
import Spatial
#import Messages
import CostModel

from collections import namedtuple
#type FuelModel =
#    FuelModel.FlightFunctions -> float<Pounds> -> float<Feet> -> float<Knots> ->
#        VerticalMovement -> (float<FuelPounds/Hours> * float<FuelPounds/Hours> * float<Feet/Hours>)

#type AirSpeedLimiter = float -> float<Pounds> -> float<Feet> -> float<Knots> -> float<Knots>

#type AltitudeLimiter = float<Pounds> -> float<Feet> -> float<Feet>

#let NoAirSpeedLimiter _ _ _ x = x

#type WeightModel = FlightParameters -> FlightState -> float<Pounds>

#type ArrivalModel = AirportEnvironment -> FuelModel.FlightFunctions -> FlightParameters -> Position -> float<Pounds> -> float<Time> -> FlightState

#type InstructionValidator = SimulationParameters -> FlightParameters -> Instruction -> Instruction

SimulationCoreFunctions = namedtuple('SimulationCoreFunctions', [
        'FuelModel', # : FuelModel
        'WeightModel', # : WeightModel
        'AirSpeedLimiter', # : AirSpeedLimiter
        'AltitudeLimiter', 'ArrivalModel'])#  # : AltitudeLimiter
#        'ArrivalModel', # : ArrivalModel
#        'InstructionValidator' # : InstructionValidator
#        ])

# /// Container for results of simulation
SimulationResult = namedtuple('SimulationResult', [
        'FlightId', #            : int64
        'Duration', #            : float<Hours>
        'FuelBurned', #          : float<FuelPounds>
        'Messages', #            : Message[]
        'ReachedDestination', #  : bool
        'Log', #                 : List<FlightLogEntry>
        'CostDetail', #          : Option<Costs>
        'Cost' #                : float<Dollars>
        ])
