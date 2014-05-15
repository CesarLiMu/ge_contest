import Units
import math
import Atmosphere
# CruiseModel is a list of 22 values
#type CruiseModel = CruiseModel of float[] with
#    member this.Parameters =
#        match this with
#        CruiseModel(p) -> p

def fuelBurn(cruiseModel, weight, altitude, airSpeed):
#(cruiseModel:CruiseModel) (weight:float<Pounds>) (altitude:float<Feet>) (airSpeed:float<Knots>) =
    #match cruiseModel with
    #CruiseModel(model) ->
    w = weight / 10000.0
    a = altitude / 10000.0
    s = airSpeed / 100.0
    model = cruiseModel
    m = airSpeed/Atmosphere.speedOfSound(altitude)
    singles = model[0] + model[1]*a + model[2]*s + model[3]*w + model[4]*m
    squares = model[5]*w*w + model[6]*a*a + model[7]*s*s + model[8]*m*m
    pairs1 = model[9]*a*s + model[10]*a*w + model[11]*a*m
    pairs2 = model[12]*s*w + model[13]*s*m + model[14]*w*m
    sqrts1 = model[15]* math.sqrt(w) + model[16]* math.sqrt(a) + \
        model[17]* math.sqrt(s) + model[18]* math.sqrt(m)
    triples = model[19]*a*s*w + model[20]*a*s*m + model[21]*a*w*m + model[22]*s*w*m
    linearCombination =singles+squares+pairs1+pairs2+sqrts1+triples
    result = math.exp(linearCombination)
    return result #result*1.0<FuelPounds/Hours>

cruiseModelMediumRange =[
    6.539592,
    0.129541,
    0.136377,
    0.069585,
    0.283615,
    0.000942,
    0.030562,
    0.011758,
    -0.299634,
    -0.405173,
    0.014788,
    1.052177,
    -0.027264,
    0.754937,
    -0.017592,
    0.082160,
    0.048971,
    0.133320,
    0.290474,
    0.001226,
    0.007830,
    -0.001579,
    -0.000626]
