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

from collections import namedtuple
#/// Prints out message at current time of stopwatch
#let inline timeStampPrint (sw:Diagnostics.Stopwatch) (message:string) = 
#    printfn "@%d ms: %s" sw.ElapsedMilliseconds message

#/// Fetches an appSetting by the given key
#let inline appSetting (key : string) =
#    ConfigurationManager.AppSettings.Item(key)

#/// Container for cached data
#type simSettings = {
simSettings = {
    'projection' :  [], #LambertProjection
   # weather: Map<String, WeatherState>
    'flights' : { }, #  Map<String, (FlightEntry*CostParameters.CostParameters)[]> 
  #  airports: Map<String, Dictionary<String,(Airport*Arrival.AirportEnvironment)>>
    'airspace': { }, #Map<String, Airspace.Airspace>
    'simulationParameters' : [] # SimulationParameters.SimulationParameters
}

DayResults = namedtuple('DayResults', [
        'date', 'flightCount', 'meanCost', 'flightLogs', 'flightCosts'
        ])

#    date: String
#    flightCount: int
#    meanCost: float
#    flightLogs: List<FlightLogEntry>[]
#    flightCosts: (int64*Option<CostModel.Costs>)[]


#/// Parses instructions, then executes FlightQuest.simulateFlights for each day
#let runRoutesOverDays (s:simSettings) (dates:string[]) (routesFile:string) =
def runRoutesOverDays(s, dates, routesFile):
    messageLimit = 10
    warningLimit = 10
    
    rawInstructions = Serialization.loadInstructionsFromFile(routesFile)
#    if Array.length parseWarnings > 0 then
#        printfn "%d instruction parse warnings" (Array.length parseWarnings)    
    routes = InstructionParser.ConvertRawInstructions(s.projection, rawInstructions)
    flightCountsAndCosts = {}

    for date in dates:
#        weather = s.weather[date]
        flights = s.flights[date]
        airports = s.airports #.[date]
        airspace = s.airspace[date]

        print "Simulating " + str(date)
#        airports = None
#        print routes
#        raw_input('routes')
        weather = None
        results = Simulator.simulateFlights(s.simulationParameters,
                                            airports,
                                            airspace,
                                            weather,
                                            flights,
                                            routes)
        # return a map of FlightId to 
     #   print results
     #   raw_input('next')
#        countArrived = [ x.ReachedDestination for x in results]
#        cost = [x.Cost for x in results]
        flightCosts = {} 
        cost = []
        countArrived = 0
        for k, v in results.iteritems():
            flightCosts[k] = v['CostDetail']
            countArrived += 1 if v['ReachedDestination'] else 0
            cost.append(v['Cost']) 
        print 'countArrived'
        print countArrived
        print 'cost'
        print cost
        flightCountsAndCosts[date] = {
            'date' : date,
            'flightCount' : countArrived,
            'meanCost' : sum(cost) / len(cost),
            #flightLogs = logs
            'flightCosts' : flightCosts
        }
    return flightCountsAndCosts


def main(argv=None):
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
   # let groundConditionPattern = basePath + appSetting "groundConditionFiles"
   # let actualTakeoffsPattern = basePath + appSetting "actualTakeoffFiles"
   # let actualLandingPattern = basePath + appSetting "actualLandingFiles"
    
   # let writeFlightLogStr = appSetting "writeFlightLog"
   # let writeFlightLog = ref false;
   # Boolean.TryParse(writeFlightLogStr, writeFlightLog) |> ignore
   # let flightLogFiles = basePath + appSetting "flightLogFiles"
   # let flightCostFile = basePath + appSetting "flightCostsFile"

    turbulentZonesPattern = basePath + config.settings["turbulentZonesFiles"]
    
    dateList = config.settings["dates"]
    dates = dateList.split(',')
 #   // Start timer
 #   let sw = Diagnostics.Stopwatch.StartNew()

 #   timeStampPrint sw "Loading configuration, projection, airports"
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

 #   print flightsDates
 #   print airspaceDates

#    raw_input("Press Enter to continue...")  
 #   timeStampPrint sw "Done with pre-simulation loads"
 #   printfn "-----------------------------------------------"
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

if __name__ == '__main__':
    main()
