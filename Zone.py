# define a zone class with name, vectors of Lat Long, and polyhedron
from collections import namedtuple

Zone = namedtuple('Zone', ['Name', 'LatLongVertices', 'Polyhedron'])
