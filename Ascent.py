from collections import namedtuple
import numpy as np

AscentModel = namedtuple('AscentModel',
                          ['DistanceIntercept',
                            'DistanceAltitude',
                            'DistanceWeight',
                            'DistanceAltitudeWeight',
                            'TimeAltitudePower',
                            'TimeIntercept',
                            'TimeAltitude',
                            'TimeWeight',
                            'TimeAltitudeWeight',
                            'FuelIntercept',
                            'FuelAltitude',
                            'FuelAltitudeSqrt ',
                            'FuelWeight',
                            'FuelAltitudeWeight',
                            'FuelAltitudeSqrtWeight',
                            'MaximumRateOfAscent'   # <Feet/Hours>
                            ])


class Descent:
    def __init__(self):
        self.model = DescentModel(1.062,
                                  5.224e-5,
                                  5.215e-6,
                                  2.029e-10,
                                  1.2,
                                  -3.775229,
                                  3.226931e-06,
                                  5.633243e-06,
                                    2.077038e-11,
                                    3.985,
                                    -5.179e-05,
                                    2.366e-02,
                                    1.463e-05,
                                    4.899e-10,
                                   -1.121e-07,
                                   240000.0)

    def caculateTime(self, altitude, weight):
        # altitude: feet, weight: pound
        
        a =  altitude * 1.0
        w =  weight * 1.0
        aTime = a**self.model.TimeAltitudePower
        result =
            pd.exp(self.model.TimeIntercept + self.model.TimeAltitude*aTime + self.model.TimeWeight*w + self.model.TimeAltitudeWeight*aTime*w)
        return result*1. # 0<Hours>

            
    def altitudeDerivativeWrtTime(self, altitude, weight):
        a = max(altitude, 1.0)
        w = 1.0 * weight
        time = self.calculateTime(altitude, weight)
        multiplicand =
            (self.model.TimeAltitude + self.model.TimeAltitudeWeight*w) * \
            self.model.TimeAltitudePower * a**(self.model.TimeAltitudePower-1.0)
        dtda = time * multiplicand / 1.0 #<Feet>
        dadt = 1.0/dtda
        return min( self.model.MaximumRateOfAscent, dadt)

    def calculateFule(self, altitude, weight):
        a = 1.0 * altitude
        w = 1.0 * weight
        aFuel = np.sqrt (a)
        result =
            exp(
                self.model.FuelIntercept + self.model.FuelAltitude*a + self.model.FuelAltitudeSqrt*aFuel + self.model.FuelWeight*w +
                self.model.FuelAltitudeWeight*a*w + self.model.FuelAltitudeSqrtWeight*aFuel*w)
        return result    


    def fuelDerivativeWrtAltitude(self, altitude, weight):
        a = 1.0 * altitude
        w = 1.0 * weight
        aFuelDerivative = 0.5/np.sqrt( a)
        fuel = self.calculateFuel( altitude, weight)
        multiplicand =
            self.model.FuelAltitude + self.model.FuelAltitudeSqrt*aFuelDerivative + \
            self.model.FuelAltitudeWeight*w + self.model.FuelAltitudeSqrtWeight*w*aFuelDerivative
        dfda = fuel*multiplicand
        return dfda * 1.0 # <FuelPounds/Feet>

    def calculateRates(self, altitude, weight):
         dAltitudeDTime = self.altitudeDerivativeWrtTime( altitude, weight)
         dFuelDAltitude = self.fuelDerivativeWrtAltitude( altitude, weight)
         dFuelDTime = dFuelDAltitude*dAltitudeDTime
         return (dAltitudeDTime, dFuelDTime)

    def calculateTimeFuelDistance(model, altitude, weight):
         a = 1.0 * altitude
         w = 1.0 * weight
         time = self.calculateTime ( altitude, weight)
         fuel = self.calculateFuel ( altitude, weight)
         distance = np.exp(self.model.DistanceIntercept+self.model.DistanceAltitude*a+self.model.DistanceWeight*w+self.model.DistanceAltitudeWeight*a*w)
         return (time,fuel*1.0,distance*1.0)  # <FuelPounds>, <NauticalMiles>  







