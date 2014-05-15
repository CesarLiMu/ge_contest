import Spatial
import Zone

#type Message = string

def flightDescription(id, position):
    return 'Flight' + str(id) + str(position.PositionX) + ',' + str(position.PositionY) \
        + str(position.Feet)
#(id:int64) ((xf,yf,zf):Position) = sprintf "Flight %d at (%.1f, %.1f, %.0f)" id (float xf) (float yf) (float zf)
def StepLimitExceeded(id, position):
    return flightDescription(id, position) + 'exceed maximum steps'
# (id:int64) (position:Position) = (flightDescription id position) + " exceeded maximum steps"

def FuelExhausted(id, position):
    return flightDescription(id, position) + " exhausted fuel tank"

def HitRestrictedZone(id, position):
    return flightDescription(id, position) + " hit restricted zone"

def CannotLand(id, position, airportCode):
# ((xa,ya,za):Position) =
    return flightDescription(id, position) + 'cant land at ' + airportCode

NoInstructions = "No instructions found for flight"
MissingAirport = "Airport missing"
UnknownError = "Unknown error"

def BadInstruction(n):
    return "Bad instruction on line" + str(n)
