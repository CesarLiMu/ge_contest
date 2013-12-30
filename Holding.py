import Units
from collections import namedtuple

HoldingModel = namedtuple('HoldingModel', ['FuelIntercept', # float
                                           'FuelWeight', # float
                                           'FuelAltitude', # float
                                           'FuelWeightAltitude2' # float
                                           ])

holdingModelMediumRange = HoldingModel(4.376e2, 1.411e-2, -1.723e-2, 2.975e-12)

def fuelBurn(model, weight, altitude):
    # Holdingmodel, float<pounds>, float<feet>
    w = weight
    a = altitude
    fuelBurn = model.FuelIntercept + model.FuelWeight * w + model.FuelAltitude * a +\
        model.FuelWeightAltitude2 * w * a * a
    return fuelBurn # FuelPounds/Hours
