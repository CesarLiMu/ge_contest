import Simulator
import Units
import LambertConverter
import Airport
import FlightTypes
import FlightEntry
import Serialization
import SimulationParameters
import InstructionParser
import config 
from Program import *
import Atmosphere 
import Units
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
from scipy.optimize import minimize 
import itertools

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

def bulk_hgt_spd (hgt_spd, li):
    """ if li >7 then hgt_spd should have len 14
        else hgt_spd should have length li * 2
     """
    
    if li > 7:
        hgt_spd = list(hgt_spd)
        hgt_spd =list(itertools.chain( * [hgt_spd[:3], hgt_spd[3:4] * (li -6) , hgt_spd[4:7], 
                   hgt_spd[7:10], hgt_spd[10:11] * (li -6), hgt_spd[11 :]]))
    return np.array(hgt_spd)    

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
    hgt_spd = bulk_hgt_spd (hgt_spd, len(instruction))
    
    hgt_spd = [np.max([1e-2,ii]) for ii in  hgt_spd]
    cur_instruction = update_instr(hgt_spd, instruction)
    result = Simulator.simulateFlight(fullCoreFunctions, simulationParameters, 
                         airportEnvironment, 
                         airspace,
                         costParameters, weather, flightState, 
                         flightParams, cur_instruction) 

    return result['Cost']

def writeInstr(output_file, instruction_opt, raw_instr):    
        with open(output_file, "a") as f:
            for kk in range(len(raw_instr)):
                c_feet = instruction_opt[kk].Waypoint.Feet
                c_feet = int(min(46000, max(c_feet, 2000)))
                
                c_speed = instruction_opt[kk].airspeed
                c_speed = int(min(650, max(c_speed, 150)))
                
                str_list = ",".join( [str(flightEntry.Id),
                            str(kk +1), 
                            str(raw_instr[kk].Latitude),
                            str(raw_instr[kk].Longitude),
                            str(c_feet),
                            str(c_speed)])
                f.write(str_list + "\n")
 
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
#dates = dateList.split(',')
dates = dateList
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

submission = config.settings['submissions']
print submission
routesFile = basePath + '/' + submission
rawInstructions = Serialization.loadInstructionsFromFile(routesFile)
# rawInstructions is a dict
routes = InstructionParser.ConvertRawInstructions(configL.projection, rawInstructions)
weather = None
airports = configL.airports 
airportEnvironment = None
fullCoreFunctions = SimulationTypes.SimulationCoreFunctions(
    FuelModel.fuelBurn,
    WeightModel.grossWeight,
    AirSpeedLimiter.limitAirSpeed,
    AirSpeedLimiter.limitAltitude,
    Arrival.arrivalModel)

output_file = basePath + "USTC9600_final_submission.csv'
with open(output_file, "w") as f:
    f.write("FlightId,Ordinal,Latitude,Longitude,Altitude,AirSpeed\n")

count_miss =0
count_skip = 0 
count_opt = 0
for date in dates:
    print "Simulating " + str(date)
    flights = configL.flights[date]
    airspace = configL.airspace[date]
    
    for flightEntry, costParameters in flights:
        print flightEntry.Id

        if flightEntry.Id not in rawInstructions.keys():
            print flightEntry.Id, " not in instructions."
            count_miss +=1
            continue
        
        raw_instr = rawInstructions[flightEntry.Id]
        instruction = routes[flightEntry.Id]
        n_ins = len(instruction)
        print n_ins
        
        count_opt +=1
        (flightParams, flightState) = FlightEntry.generateParametersAndState(
            airports, flightEntry)
        
        if n_ins <=7:
            init_hgt_spd = [0] * 2 * n_ins 
            for k in range(len(instruction)):
                init_hgt_spd[k] = instruction[k][0][2] / ALT_SCALE # height
                init_hgt_spd[k + n_ins] = instruction[k][1] / SPD_SCALE # air-speed
        else:
            init_hgt_spd = [0] * 2 * 7 
            for k in range(4):
                init_hgt_spd[k] = instruction[k][0][2] / ALT_SCALE # height
                init_hgt_spd[k + 7] = instruction[k][1] / SPD_SCALE # air-speed
            for k in range(4,7):
                init_hgt_spd[k] = instruction[n_ins + k - 7][0][2] / ALT_SCALE # height
                init_hgt_spd[k + 7] = instruction[n_ins + k - 7][1] / SPD_SCALE # air-speed
    
        args=(fullCoreFunctions, simulationParameters, 
                             airportEnvironment,  airspace,
                             costParameters, weather, flightState, 
                             flightParams, instruction)
    
        # this bounds should depend on the weight of plane, which needs to be calculated.
        weight = WeightModel.grossWeight(flightParams, flightState)
        max_altitude = AirSpeedLimiter.calculateMaximumAltitude(weight)
        max_speed = Atmosphere.speedOfSound(max_altitude) * flightParams.AircraftType.MaximumMachSpeed
        
        bnds = [(0.2, max_altitude / ALT_SCALE)] * min(n_ins,7)
        bnds.extend([(150.0/SPD_SCALE, max_speed / SPD_SCALE)]* min(n_ins, 7))        
    
        res2 = minimize(J, init_hgt_spd, 
            args=args, 
            tol = 0.05,
            method = 'SLSQP',
            bounds=bnds
            )
        print "number of iters",  res2['nit']
        # construct the optimized instruction
        new_hgt_spd = bulk_hgt_spd(res2['x'], len(instruction))
        instruction_opt = update_instr(new_hgt_spd, instruction)
        writeInstr(output_file, instruction_opt, raw_instr)





     
    

