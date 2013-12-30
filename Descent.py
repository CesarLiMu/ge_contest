from collections import namedtuple

DescentModel = namedtuple('DescentModel',
                          ['TimeIntercept',  
                            'TimeAltitude',
                            'TimePower',
                            'FuelIntercept',
                            'FuelAltitule',
                            'FuelPower',
                            'DistanceIntercept',
                            'DistanceAltitule',
                            'DistancealtituleWeight',
                            'MaximumRateOfDescent'   # Feet/hour
                            ])


class Descent:
    def __init__(self, time):
        self.time = time
        self.descentMediumRange = DescentModel(0.0242256,
                                       0.0002435,
                                       0.7,
                                       44.24,
                                       10.22,
                                       0.4,
                                       6.807,
                                       1.135e-3,
                                       1.414e-8,
                                       -240000.0)

    def caculateTime(self, altitude):
        aTime = altitude ** self.descentMediumRange.TimePower
        time = self.descentMediumRange.TimeIntercept + self.descentMediumRange.TimeAltitude*aTime
        maxDescent = abs(altitude * 1.0 / self.descentMediumRange.MaximumRateOfDescent)
        return  max( maxDescent, time)   # in hour
 
    def altitudeDerivativeWrtTime(self, altitude):
        dtda = self.descentMediumRange.TimeAltitude * self.descentMediumRange.TimePower * altitude **(self.descentMediumRange.TimePower-1.0)
        dadt = -1.0/dtda   #<Feet/Hours>
        return  max(self.descentMediumRange.MaximumRateOfDescent, dadt)  # Feet/Hours

    def calculateFuel(self, altitude):
        aFuel =  altitude ** self.descentMediumRange.FuelPower
        result = self.descentMediumRange.FuelIntercept + self.descentMediumRange.FuelAltitude*aFuel
        return result * 1.0  # <FuelPounds>

    def fuelDerivativeWrtAltitude(self, altitude):
        dfda = self.descentMediumRange.FuelAltitude*self.descentMediumRange.FuelPower*  altitude **(self.descentMediumRange.FuelPower-1.0)
        return dfda * 1.0  # <FuelPounds/Feet>

    def calculateRates(self, altitude, weight):
        dAltitudeDTime = self.altitudeDerivativeWrtTime(altitude)
        dFuelDAltitude = self.fuelDerivativeWrtAltitude(altitude)
        dFuelDTime = abs( dAltitudeDTime * dFuelDAltitude)
        return (dAltitudeDTime, dFuelDTime)

    def calculateDistance(self, altitude, weight):
        a =  altitude * 1.0
        w =  weight * 1.0
        distance = self.descentMediumRange.DistanceIntercept+self.descentMediumRange.DistanceAltitude*a+self.descentMediumRange.DistanceAltitudeWeight*a*w
        return distance*1.0 # <NauticalMiles>

    def calculateTimeFuelDistance(self, altitude, weight):
        time = self.calculateTime(altitude)
        fuel = self.calculateFuel ( altitude)
        distance = self.calculateDistance ( altitude, weight)
        return (time,fuel,distance)
