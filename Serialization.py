# Methods to serialize/deserialize FlightQuest data objects/files

#import ParseUtilities
import InstructionParser
import Units
import FlightEntry
import FlightTypes
import SimulationParameters
import CostModel
import CostParameters
#import Weather
import Airspace
import Airport
#import Arrival
import Spatial
import Zone
import LambertConverter

import json
import csv

from collections import namedtuple

#type IDictionary<'k,'v> = System.Collections.Generic.IDictionary<'k,'v>
#type Dictionary<'k,'v> = System.Collections.Generic.Dictionary<'k,'v>

def saveConfigurationToFile(file, parameters):
    #(parameters:SimulationParameters) =
    f = open(file, 'w')
    json.dump(parameters, f)

def loadConfigurationFromFile(file):# = 
    f = open(file, 'r')
    return json.loads(f.read())

def saveProjectionToFile(file, parameters):
    f = open(file, 'w')
    json.dump(parameters, f)

def loadProjectionFromFile(file):
    f = open(file, 'r')
    project = json.loads(f.read())
    return LambertConverter.LambertProjection(**project)

RawInstruction = namedtuple('RawInstruction', [
        'Latitude', 'Longitude', 'Feet', 'Knots'
        ])

def loadInstructionsFromFile(file):
    # parse the sampleSubmission.csv
    with open(file, 'r') as csvfile:
        f = csv.reader(csvfile, delimiter=',')
        f.next()
        results = {}
        for row in f:
            flightId = int(row[0])
            waypointSequence = int(row[1])
            latitude = float(row[2])
            longitude = float(row[3])
            altitude = float(row[4])
            speed = float(row[5])
            rawInstruction = RawInstruction(latitude, longitude, altitude, speed)
            if flightId not in results:
                results[flightId] = []
            results[flightId].append(rawInstruction)
    return results


def decodeLocation(projection, latitude, longitude):
    return LambertConverter.toLambert(projection, latitude, longitude)

# what's the format of row & flight entry? flights_20130911_1824.csv
def rowToFlightEntry (row):
    id = int(row[0])
    position = Spatial.Position(float(row[1]), float(row[2]), float(row[3]))
    flightEntry = FlightEntry.FlightEntry(id, position, 
                                          row[4], row[5], 
                                          FlightTypes.Payload(int(row[6]), int(row[7])),
                                          float(row[8]), float(row[9]), float(row[10]), 
                                          float(row[11]),
                                          float(row[12]), float(row[13]))
    
    costParameters = CostParameters.CostParameters(
        float(row[14]), float(row[15]), float(row[16]), float(row[17]), 
        float(row[18]), float(row[19]), float(row[20]), float(row[21]), 
        int(row[22]), float(row[23]), float(row[24]))

    return (flightEntry,costParameters)

def loadFlightsAndCostsFromFile(file):
    f = csv.reader(open(file, 'r'), delimiter=',')
    f.next()
    res = []
    for row in f:
        res.append(rowToFlightEntry(row))
#    f.close()
    return res

def loadAirportsFromFile(file):
    f = csv.reader(open(file, 'rb'), delimiter=',')
    f.next()
    airports = {} 
    for row in f:
        code = str(row[0])
        airports[code] = Airport.Airport(
            Code=code,
            Position=Spatial.Position(float(row[1]), float(row[2]), float(row[3])),
            ArrivalDistance = float(row[4]),
            ArrivalAltitude = float(row[5]))
    return airports


def loadLandingGlmsFromFile(file):
    f = csv.reader(open(file, 'rb'), delimiter=',')
    landing = {}
    f.next()
    for row in f:
        landing[row[0]] = {
            'Intercept' : float(row[1]),
            'Dewpoint':  float(row[2]),
            'WindSpeed' : float(row[3]),
            'Visibility':  float(row[4]),
            'WindGusts' : float(row[5]),
            'Temperature':  float(row[6]),
            'UntilScheduledGateArrival' : float(row[7]),
            'UntilScheduledRunwayArrival' : float(row[8]),
            'TakeOff_0_5' : float(row[9]),
            'TakeOff_5_10' : float(row[10]),
            'TakeOff_10_15' : float(row[11]),
            'TakeOff_15_20' : float(row[12]),
            'TakeOff_20_25' : float(row[13]),
            'TakeOff_25_30' : float(row[14]),
            'TakeOff_30_35' : float(row[15]),
            'Landed_0_5' : float(row[16]),
            'Landed_5_10' : float(row[17]),
            'Landed_10_15' : float(row[18]),
            'Landed_15_20' : float(row[19]),
            'Landed_20_25' : float(row[20]),
            'Landed_25_30' : float(row[21]),
            'Landed_30_35' : float(row[22])
            }
#    f.close()
    return landing

def loadTaxiGlmsFromFile (file):
    f = csv.reader(open(file, 'rb'), delimiter=',')
    taxi = {}
    f.next()
    for row in f:
        taxi[row[0]] = {
            'Intercept' :  float(row[1]),
            'Dewpoint' : float(row[2]),
            'WindSpeed' : float(row[3]),
            'Visibility' : float(row[4]),
            'WindGusts' : float(row[5]),
            'Temperature' : float(row[6]),
            'UntilScheduledGateArrival' : float(row[7]),
            'ScheduledTaxiTime' : float(row[8]),
            'TakeOff_0_5' : float(row[9]),
            'TakeOff_5_10' : float(row[10]),
            'TakeOff_10_15' : float(row[11]),
            'Landed_0_5' : float(row[12]),
            'Landed_5_10' : float(row[13]),
            'Landed_10_15' : float(row[14])
            }
#    f.close()
    return taxi

# what do we do with all the information like airport conditions, airport events?
# actual actual takeoff, actual landing?
#    (basicData:Stream) (landingGlms:Stream) (taxiGlms:Stream) (airportConditions:Stream)
#    (actualTakeoffs:Stream) (actualLandings:Stream) =

def saveFlightLogToFile(file, logs):
    # logs [ FlightLogEntry] 
    f = open(file, 'w')
    headers = ["FlightId", "Latitude", "Longitude", "Easting", "Northing", 
               "ElapsedTime", "AirSpeed", "GroundSpeed", "Altitude", "FuelConsumed", 
               "InRestrictedZones", "InTurbulentZones", "Weight", "Status"]
    f.write(','.join(headers))
    f.write('\n')

    for e in logs:
        status = e.Status # Flying, Crashed, Landed

        s = [str(e.FlightId), str(e.Latitude), 
             str(e.Longitude), str(e.Easting), str(e.Northing), str(e.ElapsedTime), 
             str(e.AirSpeed), 
             str(e.GroundSpeed), str(e.Altitude), str(e.FuelConsumed),
             str(e.InRestrictedZones), str(e.InTurbulentZones), 
             str(e.Weight), str(status)]
        f.write(','.join(s))
        f.write('\n')
    f.close()

def loadZonesFromFile(file):
    f = csv.reader(open(file, 'rb'), delimiter=',')
    taxi = {}
    f.next()
    zones = []
    for row in f:
        latlongVertStrings = row[3]
        lambertVertStrings = row[4]
        llArray = []
        lamArray = []
        for latlong in latlongVertStrings.split(' '):
            vs = [float(v) for v in latlong.split(':')]
            llArray.append(Spatial.Location(vs[0], vs[1]))
        for lambert in lambertVertStrings.split(' '):
            vs = [float(v) for v in lambert.split(':')]
            lamArray.append(Spatial.Location(vs[0], vs[1]))
        zones.append(Zone.Zone(row[0],
                               llArray,
                               Spatial.Polyhedron(lamArray, float(row[1]), float(row[2]))
                               ))
    return zones

def saveFlightCostsToFile(file, flightCosts):
#let saveFlightCostsToFile (filePath:string) (flightCosts:(Int64*Option<Costs>)[]) =
    f = open(file, 'w')
    headers = ["FlightId", "DelayCost", "FuelCost", "TurbulenceCost", "OscillationCost"]
    f.write(','.join(headers))
    f.write('\n')
    writer.WriteLine(String.Join(",", headers))

    for cost in flightCosts:
        id = cost[0]
        c = cost[1].value
        f.write(','.join([id, str(c.DelayCost), str(c.FuelCost),
                          str(c.TurbulenceCost), str(c.OscillationCost)]))
        f.write('\n')
    
#/// Loads weather, flights, and airport conditions for each day into a map with date as the key
def loadDateMaps(flightPattern, restrictedZones, turbulentZonesPattern, dates):
    flights = {}
    airspaces = {}
    for day in dates:
        flights[day] = loadFlightsAndCostsFromFile(flightPattern + day + '.csv')
        airspace = Airspace.Airspace(
            RestrictedZones = restrictedZones,
            TurbulentZones = loadZonesFromFile(turbulentZonesPattern + day + '.csv')
        )
        airspaces[day] = airspace
    return flights, airspaces    
# ((Map.ofArray weather), (Map.ofArray flights), (Map.ofArray airports), (Map.ofArray airspaces))

