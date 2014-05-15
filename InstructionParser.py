import Units
#import Assertions
import FlightTypes
#import ParseUtilities
import LambertConverter
import Spatial

from collections import namedtuple

import csv

RawInstruction = namedtuple('RawInstruction', [
        'Latitude', 'Longitude', 'Feet', 'Knots'
        ])

def ConvertRawInstruction(projection, raw): #:RawInstruction) 
    lambertCoordinates = (raw.Latitude, raw.Longitude)
    (easting,northing) = LambertConverter.toLambert(projection, lambertCoordinates)
    position = Spatial.Position(easting, northing, raw.Feet)
    return FlightTypes.Instruction(position, raw.Knots) # instruction

def ConvertRawInstructions(projection, rawInstructions): # what's the format of rawInstructions?
    # it's a map of flightId * to array of instructions
    instructionTable = {}
    for k,vs in rawInstructions.iteritems():
        instructions = [ConvertRawInstruction(projection, v) for v in vs]
        instructionTable[k] = instructions
    return instructionTable
