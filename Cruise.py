from collections import namedtuple
import numpy as np
import Atmosphere

#  in cruise model, the plane burns fuel at a constant rate to maintain a constant airspeed and altitude

class Cruise:
    def __init__(self):
        self.model = [6.539592,
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


    def fuelBurn(self, weight, altitude, airSpeed):
        # weight: pounds
        # altitue: Feet
        # airSpeed: Knots
          w =  weight / 10000.0
          a =  altitude / 10000.0
          s =  airSpeed / 100.0
          m = airSpeed/Atmosphere.speedOfSound(altitude)
          singles = self.model[0] + self.model[1]*a + self.model[2]*s + self.model[3]*w + self.model[4]*m
          squares = self.model[5]*w*w + self.model[6]*a*a + self.model[7]*s*s + self.model[8]*m*m
          pairs1 = self.model[9]*a*s + self.model[10]*a*w + self.model[11]*a*m
          pairs2 = self.model[12]*s*w + self.model[13]*s*m + self.model[14]*w*m
          sqrts1 = self.model[15]*np.sqrt(w) + self.model[16]*np.sqrt(a) + self.model[17]*np.sqrt(s) + self.model[18]*np.sqrt(m)
          triples = self.model[19]*a*s*w + self.model[20]*a*s*m + self.model[21]*a*w*m + self.model[22]*s*w*m
          linearCombination =singles+squares+pairs1+pairs2+sqrts1+triples
          result = exp(linearCombination)
          return result # <FuelPounds/Hours>
        

