import Units
from collections import namedtuple

CostParameters = namedtuple('CostParameters', 
                            ['FuelCost', # float <Dolalrs/Gallons>
                             'CrewDelayCosts', # : float<Dollars/Hours>
                             'OtherHourlyCosts', # : float<Dollars / Hours>
                             'NonArrivalPenalty', # : float<Dollars>
                             'DelayCostProportion30Minutes', # : float
                             'DelayCostProportion2Hours', # : float
                             'FreeAltitudeChanges', # : int
                             'AltitudeChangeCost', # : float<Dollars>
                             'MaximumStandardPassengerDelayCost', # : float<Dollars>
                             'MaximumPremiumPassengerDelayCost', # : float<Dollars>
                             'TurbulenceCostPer6Minutes'# : float<Dollars>
                             ])
