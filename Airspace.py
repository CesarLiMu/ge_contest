import Units
import Spatial
import Zone
import Aircraft
import CollisionDetection

from collections import namedtuple

# define Restricted Zones & TurbulentZones
# TODO

Airspace = namedtuple('Airspace', ['RestrictedZones', # Zone[]
                                   'TurbulentZones' # Zone[]
                                   ])

IntersectAirspace = namedtuple('IntersectAirsplace',
                               ['RestrictedZone', # bool
                                'TurbulentZone' # bool
                                ])
                                
emptyAirspace = Airspace([], [])
emptyIntersection = IntersectAirspace(False, False)

def aircraftInAirspace(airspace, previousPosition, currentPosition):
    lineSegment = Spatial.LineSegment(previousPosition, currentPosition)
    altitude = currentPosition.Feet
    # check whether it cross with the restrictedZone or turbulentZones
    crossRestricted = False
    crossTurbulent = False
    for res in airspace.RestrictedZones:
#        print res
        if CollisionDetection.detect3DCollision(lineSegment, altitude, res.Polyhedron):
            crossRestricted = True
    for turb in airspace.TurbulentZones:
        if CollisionDetection.detect3DCollision(lineSegment, altitude, res.Polyhedron):
            crossTurbulent=True
    return IntersectAirspace(crossRestricted, crossTurbulent)
