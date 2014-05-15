# define a Aircraft class
from collections import namedtuple

AircraftType = namedtuple('AircraftType', 
                          ['ServiceCeiling', # feet
                           'OperatingEmptyWeight', # pounds
                           'FuelCapacity', # gallons 
                           'MaximumTakeOffWeight', # pounds
                           'MaximumMachSpeed',
                           'MinimumAirSpeed', # knots
                           'TaxiFuelBurn' # FuelPounds/Hours
                           ])

mediumRange = AircraftType(41000.0, 91108.0, 7837.0, 174200.0, 0.82,
                           150.0, 1984.158)


        
