from collections import namedtuple

Config = namedtuple('Config', [
       'projection',
       'airports',
 #       'weather' : weatherDates,                                                                   
       'flights',
 #       'airports' : airportsDates,                                                                 
       'airspace',
       'simulationParameters']) 

settings = {
#    'dates' : '20130911_1824',
    'dates' : '20130910_1803',
    "basePath" : "/Users/niwang/GE/FQ2PartialSimulatorData",
    "configFile" : "/Configuration.json",
    "projectionFile" : "/Projection.json",
    "airportsFile" : "/Airports.csv",
    "landingFile" : "/Landing.csv",
    "taxiFile" : "/Taxi.csv",
    "restrictedZonesFile" : "/restrictedZones.csv",

    "flightFiles" : "/flights_",  # *.csv"
    "turbulentZonesFiles" : "/turbulentZones_", # *.cs
#    "submissions" : 'sampleSubmission1.csv'
    "submissions" : 'sampleSubmissionk10.csv'
#    "submissions" : 'sampleTest.csv'
}
  
