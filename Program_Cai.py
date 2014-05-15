import Simulator
import Units
#import Weather
import LambertConverter
import Airport
import FlightTypes
import FlightEntry
#import ParseUtilities
import Serialization
import SimulationParameters
import InstructionParser
import config 
from Program import *
 
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
 
from collections import namedtuple
import numpy as np
import pandas as pd
from datetime import datetime
from scipy.optimize import minimize 

#  the scaling is necessary to get the right behavior of the optimizer
ALT_SCALE = 10000
SPD_SCALE = 400

# modify / update instruction's height and speed
def update_instr(hgt_spd, instruction):
    n_ins = len(instruction)
    cur_instruction = []
    for k in range(n_ins):
        position = Spatial.Position(instruction[k][0][0], instruction[k][0][1], ALT_SCALE * hgt_spd[k])
        cur_instruction.append( FlightTypes.Instruction(position, SPD_SCALE * hgt_spd[k + n_ins]) )
    return cur_instruction    

# set up a function, whose first parameter is the variable to be optimized
# here the first parameter is height and speed of the plane
# it returns the cost
def J(hgt_spd, fullCoreFunctions, simulationParameters, 
                         airportEnvironment, 
                         airspace,
                         costParameters, weather, flightState, 
                         flightParams, instruction):
    """
    hgt_spd is a list of  length twice as instruction
    first half of hgt_spd is the altitude / 10000 
    send half of hgt_spd is air speed / 400
    """
    
    if np.min(hgt_spd) < 0:
        import pdb
        pdb.set_trace()
    cur_instruction = update_instr(hgt_spd, instruction)
    result = Simulator.simulateFlight(fullCoreFunctions, simulationParameters, 
                         airportEnvironment, 
                         airspace,
                         costParameters, weather, flightState, 
                         flightParams, cur_instruction) 

    print result['Cost'] 
    return result['Cost']

 
 # // Fetch config settings
basePath = config.settings["basePath"]
configFile = basePath + config.settings["configFile"]
projectionFile = basePath + config.settings["projectionFile"]
airportsFile = basePath + config.settings["airportsFile"]
landingFile = basePath + config.settings["landingFile"]
taxiFile = basePath + config.settings["taxiFile"]
restrictedAirspaceFile = basePath + config.settings["restrictedZonesFile"]

# let weatherPattern = basePath + appSetting "weatherFiles"
flightPattern = basePath + config.settings["flightFiles"]
turbulentZonesPattern = basePath + config.settings["turbulentZonesFiles"]

dateList = config.settings["dates"]
dates = dateList.split(',')
simulationParameters = Serialization.loadConfigurationFromFile(configFile)
restrictedAirspace = Serialization.loadZonesFromFile(restrictedAirspaceFile)
projection = Serialization.loadProjectionFromFile(projectionFile)
airports = Serialization.loadAirportsFromFile(airportsFile) #, landingFile, taxiFile)

#    timeStampPrint sw "Loading date-specific info "
(flightsDates, airspaceDates) =  Serialization.loadDateMaps(
     flightPattern, restrictedAirspace, turbulentZonesPattern, dates)

#    // config contains references to pre-loaded objects/maps
configL = config.Config(projection, airports,
                        flightsDates, airspaceDates, simulationParameters)

print 'Finished pre-simulation loads'
#    let mutable moreSubmissions = true
subfiles = config.settings['submissions'].split(',')
for submission in subfiles:
    print submission
    print 'runRoutesOverDays'
    dayResults = runRoutesOverDays(configL, dates, basePath + '/' + submission)
    
    # Calculate final weighted cost
    totalFlights = 0.0
    finalScore = 0.0
    for k, day in dayResults.iteritems():
        totalFlights += day['flightCount']
        finalScore += day['flightCount'] * day['meanCost']
    print finalScore / totalFlights

 
#############################################
routesFile = basePath + '/' + submission
rawInstructions = Serialization.loadInstructionsFromFile(routesFile)
# rawInstructions is a dict
rawInstructions[308567953]

s = configL
routes = InstructionParser.ConvertRawInstructions(s.projection, rawInstructions)
date = dates[0]
flights = s.flights[date]
airports = s.airports 
airspace = s.airspace[date]

print "Simulating " + str(date)
weather = None
results = Simulator.simulateFlights(s.simulationParameters,
                                    airports,
                                    airspace,
                                    weather,
                                    flights[1048:],
                                    routes)


# specify which flight you want to optimize
k = 1048
for flightEntry, costParameters in flights[k:(k+1)]:
        print flightEntry

instruction = routes[flightEntry.Id]
(flightParams, flightState) = FlightEntry.generateParametersAndState(
    airports, flightEntry)
airportEnvironment = None
#airportEnvironment = airports[flightEntry.ArrivalAirport][1] # TODO check the snd
fullCoreFunctions = SimulationTypes.SimulationCoreFunctions(
    FuelModel.fuelBurn,
    WeightModel.grossWeight,
    AirSpeedLimiter.limitAirSpeed,
    AirSpeedLimiter.limitAltitude,
    Arrival.arrivalModel)

result = Simulator.simulateFlight(fullCoreFunctions, simulationParameters, 
                         airportEnvironment, 
                         airspace,
                         costParameters, weather, flightState, 
                         flightParams, instruction) 

# run optimizer



###########################################

n_ins = len(instruction)
init_hgt_spd = [0] * 2 * n_ins 
for k in range(len(instruction)):
    init_hgt_spd[k] = instruction[k][0][2] / ALT_SCALE # height
    init_hgt_spd[k + n_ins] = instruction[k][1] / SPD_SCALE # air-speed

J(init_hgt_spd, fullCoreFunctions, simulationParameters, 
                         airportEnvironment, 
                         airspace,
                         costParameters, weather, flightState, 
                         flightParams, instruction)

args=(fullCoreFunctions, simulationParameters, 
                         airportEnvironment,  airspace,
                         costParameters, weather, flightState, 
                         flightParams, instruction)
     

hgt_spd2 = [ 28501.47937479,  25500.50739136,  22500.66545314,  25500.86582939,
        25500.12154325,  13501.491974  ,  13501.16120649,   13501.4928488 ,
         4500.2763054 ,   1499.55715489,    566.36522868,    492.59284645,
          488.28880921,    480.63440249,    469.3154134 ,    450.56865523,
          433.26620162,    525.        ,    535.        ,    545.        ]

hgt_spd2[:n_ins] = [ x / ALT_SCALE for x in hgt_spd2[:n_ins]]
hgt_spd2[n_ins:] = [ x / SPD_SCALE for x in hgt_spd2[n_ins:]]

# this bounds should depend on the weight of plane, which needs to be calculated.


bnds = [(0.2, 8)] *n_ins
bnds.extend([(150.0/400.0, 1.75)]*n_ins)        
 
# different numerical method to choose
# 'COBYLA' 3623  failed but fast
# 'L-BFGS-B'    4153  time: 18.35
# SLSQP  3657  this is the best choice
# TNC  3650
mthd = 'SLSQP'

t1 = datetime.now()
res2 = minimize(J, hgt_spd2, 
                args=args, 
                tol = 0.05,
                method = mthd,
                bounds=bnds
                #constraints=cons
                #options = {'maxiter': 40}
                )
t2 = datetime.now()
tt = t2 -t1
tt.total_seconds()

#res = minimize(J, hgt_spd2, args=args, tol = 0.05, options = {'maxiter': 40})

# construct the optimized instruction
instruction_opt = update_instr(res2['x'], instruction)

# try a different init value
res2 = minimize(J, init_hgt_spd, 
                args=args, 
                tol = 0.05,
                method = mthd,
                bounds=bnds
                #constraints=cons
                #options = {'maxiter': 40}
                )

#  improvement
# make sure the optimizer could find the cruise mode where


######## some optimization result #################################################
# TNC  3736  time: 170.4
[Instruction(Waypoint=Position(PositionX=64.04603838937774, PositionY=718.9058665781738, Feet=40000.0), airspeed=566.36522867999997),
 Instruction(Waypoint=Position(PositionX=93.86034403277743, PositionY=755.1875263088633, Feet=30597.217350000807), airspeed=492.59284645000002),
 Instruction(Waypoint=Position(PositionX=123.6807717158874, PositionY=791.470305178194, Feet=20702.323232985844), airspeed=510.94534320419285),
 Instruction(Waypoint=Position(PositionX=153.5073612504056, PositionY=827.7541800722473, Feet=32132.177229537709), airspeed=531.23411835385093),
 Instruction(Waypoint=Position(PositionX=183.34015266996724, PositionY=864.03912723579, Feet=25828.04329399181), airspeed=543.02688825125267),
 Instruction(Waypoint=Position(PositionX=213.1791862245686, PositionY=900.3251222583041, Feet=40000.0), airspeed=546.38711372515525),
 Instruction(Waypoint=Position(PositionX=243.02450237451012, PositionY=936.612140059848, Feet=30925.823697397289), airspeed=573.69070581720166),
 Instruction(Waypoint=Position(PositionX=272.8761417839651, PositionY=972.9001548767028, Feet=19736.113040290169), airspeed=525.0),
 Instruction(Waypoint=Position(PositionX=302.7341453141201, PositionY=1009.1891402468178, Feet=5000.0), airspeed=535.0),
 Instruction(Waypoint=Position(PositionX=332.59855401584906, PositionY=1045.4790689950985, Feet=5000.0), airspeed=545.0)] 
 
 # TNC 3650 time 232
 [Instruction(Waypoint=Position(PositionX=64.04603838937774, PositionY=718.9058665781738, Feet=47999.556347380851), airspeed=566.36522867999997),
 Instruction(Waypoint=Position(PositionX=93.86034403277743, PositionY=755.1875263088633, Feet=35184.845724673702), airspeed=492.59284645000002),
 Instruction(Waypoint=Position(PositionX=123.6807717158874, PositionY=791.470305178194, Feet=25743.090565319901), airspeed=581.95396358325684),
 Instruction(Waypoint=Position(PositionX=153.5073612504056, PositionY=827.7541800722473, Feet=43177.700941833711), airspeed=598.23522660360777),
 Instruction(Waypoint=Position(PositionX=183.34015266996724, PositionY=864.03912723579, Feet=32759.096717545795), airspeed=516.64951691015017),
 Instruction(Waypoint=Position(PositionX=213.1791862245686, PositionY=900.3251222583041, Feet=17340.69019695148), airspeed=559.35205265968011),
 Instruction(Waypoint=Position(PositionX=243.02450237451012, PositionY=936.612140059848, Feet=59500.348057926603), airspeed=700.0),
 Instruction(Waypoint=Position(PositionX=272.8761417839651, PositionY=972.9001548767028, Feet=22018.692843906651), airspeed=525.0),
 Instruction(Waypoint=Position(PositionX=302.7341453141201, PositionY=1009.1891402468178, Feet=2000.0000000000018), airspeed=535.0),
 Instruction(Waypoint=Position(PositionX=332.59855401584906, PositionY=1045.4790689950985, Feet=2000.0000000000018), airspeed=545.0)]
 
 # SLSQP  3657  time: 61.7 seconds
 [Instruction(Waypoint=Position(PositionX=64.04603838937774, PositionY=718.9058665781738, Feet=39999.99997215136), airspeed=566.36522867999997),
 Instruction(Waypoint=Position(PositionX=93.86034403277743, PositionY=755.1875263088633, Feet=39999.752647635018), airspeed=485.36648118942026),
 Instruction(Waypoint=Position(PositionX=123.6807717158874, PositionY=791.470305178194, Feet=39999.816069748922), airspeed=687.42502079312499),
 Instruction(Waypoint=Position(PositionX=153.5073612504056, PositionY=827.7541800722473, Feet=39999.951794953507), airspeed=477.2359424617357),
 Instruction(Waypoint=Position(PositionX=183.34015266996724, PositionY=864.03912723579, Feet=40000.000018263934), airspeed=586.36747013777585),
 Instruction(Waypoint=Position(PositionX=213.1791862245686, PositionY=900.3251222583041, Feet=39079.202056862589), airspeed=500.18220496536941),
 Instruction(Waypoint=Position(PositionX=243.02450237451012, PositionY=936.612140059848, Feet=32435.226477110984), airspeed=660.52528369536174),
 Instruction(Waypoint=Position(PositionX=272.8761417839651, PositionY=972.9001548767028, Feet=19653.555423179499), airspeed=525.0),
 Instruction(Waypoint=Position(PositionX=302.7341453141201, PositionY=1009.1891402468178, Feet=5000.0000087955295), airspeed=535.0),
 Instruction(Waypoint=Position(PositionX=332.59855401584906, PositionY=1045.4790689950985, Feet=4999.9999964894714), airspeed=545.0)]
 
 # SLSQP 3565 time 19
 [Instruction(Waypoint=Position(PositionX=64.04603838937774, PositionY=718.9058665781738, Feet=79999.999865281075), airspeed=566.36522867999997),
 Instruction(Waypoint=Position(PositionX=93.86034403277743, PositionY=755.1875263088633, Feet=79999.999866531318), airspeed=492.59284645000002),
 Instruction(Waypoint=Position(PositionX=123.6807717158874, PositionY=791.470305178194, Feet=79999.999973905055), airspeed=699.99999944876481),
 Instruction(Waypoint=Position(PositionX=153.5073612504056, PositionY=827.7541800722473, Feet=79999.999863635865), airspeed=699.99999925540146),
 Instruction(Waypoint=Position(PositionX=183.34015266996724, PositionY=864.03912723579, Feet=79999.999994907615), airspeed=699.99999912581336),
 Instruction(Waypoint=Position(PositionX=213.1791862245686, PositionY=900.3251222583041, Feet=79999.999816680007), airspeed=699.99999898294641),
 Instruction(Waypoint=Position(PositionX=243.02450237451012, PositionY=936.612140059848, Feet=79999.99990180532), airspeed=699.99999254566524),
 Instruction(Waypoint=Position(PositionX=272.8761417839651, PositionY=972.9001548767028, Feet=18421.924138601291), airspeed=525.0),
 Instruction(Waypoint=Position(PositionX=302.7341453141201, PositionY=1009.1891402468178, Feet=1999.9999978692549), airspeed=535.0),
 Instruction(Waypoint=Position(PositionX=332.59855401584906, PositionY=1045.4790689950985, Feet=2000.0000273875012), airspeed=545.0)]
 
 