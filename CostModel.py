from collections import namedtuple
import numpy as np

Costs = namedtuple('Costs',
                          ['FuelCost',
                            'DelayCost',
                            'TurbulenceCost',
                            'OscilateCost'])

class Inner:
    def __init__(self):
        self.delayReference30Minutes = 0.5
        self.delayReference2Hours = 2.0

    def altitudeOscillationCost(self, costParams, instructions):
        """
        costParams: namedtuple of CostParameters
        instructions: list of namedtuple of Instruction 
        """
        if len(instructions) <=1:
            return 0.0
        
        changeCount = 0
        previousAltitude = instructions[1].Waypoint.Feet
        
        altDalta = previousAltitude - instructions[0].Waypoint.Feet
        
        if  altDalta > 1e-6:
            direction = Direction.Ascending
        elif altDalto < -1e-6 :
            direction = Direction.Descending
        else:
            direction = Direction.Cruise
    
        for instr in instructions[2:]:
            newAltitude = instr.Waypoint.Feet
            if (newAltitude - previousAltitude > 1e-6) and (direction == Direction.Descending):
                direction = Direction.Ascending
                changeCount += 1
                previousAltitude = newAltitude
            elif (newAltitude - previousAltitude < -1e-6 ) and (direction == Direction.Ascending) : 
                direction = Direction.Descending
                changeCount += 1
                previousAltitude = newAltitude
                
        oscillationCost = np.max(0, (changeCount - costParams.FreeAltitudeChanges)) * costParams.AltitudeChangeCost
        return  oscillationCost
    
        
    def perPassengerRelativeDelayCost(self, costParams, timeDelayed):
        # timeDelayed is in hours
        t1 = self.delayReference30Minutes
        t2 = self.delayReference2Hours
        eb = np.log( 1.0/costParams.DelayCostProportion30Minutes-1.0)
        fb = log(1.0/costParams.DelayCostProportion2Hours-1.0)
        adr = 1.0/(t2-t1)  # reciprocal of determinant
        timeScaleFactor = adr*eb - adr*fb
        timeOffset = t2*adr*eb - t1*adr*fb
        return 1.0 / (1.0 + np.exp(- timeScaleFactor * timeDelayed + timeOffset))
    
    def passengerDelayCost(self, costParams, payload, timeDelayed):
        # payload is namedtuple of Payload
        relativeDelayCost = self.perPassengerRelativeDelayCost (costParams, timeDelayed)
        weightedPassengerAsymptote =
            payload.StandardPassengerCount * costParams.MaximumStandardPassengerDelayCost +
            payload.PremiumPassengerCount * costParams.MaximumPremiumPassengerDelayCost
        return relativeDelayCost * weightedPassengerAsymptote

    def delayCost(costParams, payload, maybeTimeDelayed):
        """
         maybeTimeDelayed is real value or nan
         instead of Option object in F# to simplify the code
         output:  <Dollars>
        """
        if np.isnan(maybeTimeDelayed):
            return costParams.NonArrivalPenalty
        else
            # Total delay cost is sum of crew, otherHourlyCosts and passenger dissatisfaction
            timeDelayed = maybeTimeDelayed
            hourlyCost = timeDelayed * (costParams.CrewDelayCosts + costParams.OtherHourlyCosts)
            dissatisfactionCost = passengerDelayCost( costParams, payload, timeDelayed)
            result = dissatisfactionCost + hourlyCost
            return np.max (0.0,  result)

    
    def turbulenceCost(costParams, timeInTurbulence):
        """
        timeInTurbulence : number of hours
        costParams: namedtuple of CostParameters
        output: dollar amount
        """
        return timeInTurbulence / 0.1  * costParams.TurbulenceCostPer6Minutes


def flightCost( costParams, instructions, payload, fuelBurned, maybeTimeDelayed, turbulence):
    """
    instructions: list of namedtuple Instruction
    payload:
    fuelBurned:  in gallon
    maybeTimeDelayed: real value in hours
    turbulence: hours in turbulence
    output: namedtuple Costs
    """
    inner = Inner()
    altitudeChangeCost = inner.altitudeOscillationCost( costParams , instructions)
    fuelCost = fuelBurned * costParams.FuelCost
    delayCost = inner.delayCost( costParams, payload, maybeTimeDelayed)
    turbulenceCost = inner.turbulenceCost( costParams, turbulence)
    return Costs(fuelCost,
                 delayCost,
                 turbulenceCost,
                 altitudeChangeCost
                 )

