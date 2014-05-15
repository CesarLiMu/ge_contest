import Units

#from enum import Enum
from collections import namedtuple

class LandingMode:
    NoLanding = 1
    AfterWaypoints = 2
    WhenInRange = 3

SimulationParameters = namedtuple('SimulationParameters', [
        'TimeStep', # : float<Hours>
        'MaxSteps', # : int
        'MaxInstructions', # : int
        'WaypointRadius', # : float<NauticalMiles>
        'MinimumAltitude', # : float<Feet>
        'LandingMode', # : LandingMode
        'RecordFlightLog' # : bool
        ])

