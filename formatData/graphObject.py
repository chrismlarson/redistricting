from geographyHelper import findDirectionOfShapeFromPoint, CardinalDirection, intersectingGeometries

_nextGraphId = -1


class GraphObject:
    def __init__(self, centerOfObject):
        self.graphId = getNextUniqueId()
        GraphObject.graphObjectDict[self.graphId] = self
        self.__northernNeighbors = []
        self.__westernNeighbors = []
        self.__easternNeighbors = []
        self.__southernNeighbors = []
        self.__allNeighborIds = set()
        self._neighborsCache = None
        self.populationEnergy = 0
        self.updateCenterOfObject(centerOfObject)

    graphObjectDict = {}


    def __setstate__(self, state):
        GraphObject.graphObjectDict[state['graphId']] = self
        self.__dict__ = state
        if '_neighborsCache' not in self.__dict__:
            self._neighborsCache = None
        if '_GraphObject__allNeighborIds' not in self.__dict__:
            self.__allNeighborIds = set(
                self.__northernNeighbors + self.__westernNeighbors +
                self.__easternNeighbors + self.__southernNeighbors
            )


    @property
    def hasNeighbors(self):
        return bool(self.northernNeighbors or self.westernNeighbors or
                    self.easternNeighbors or self.southernNeighbors)


    @property
    def northernNeighbors(self):
        return [GraphObject.graphObjectDict[_] for _ in self.__northernNeighbors]

    @property
    def westernNeighbors(self):
        return [GraphObject.graphObjectDict[_] for _ in self.__westernNeighbors]

    @property
    def easternNeighbors(self):
        return [GraphObject.graphObjectDict[_] for _ in self.__easternNeighbors]

    @property
    def southernNeighbors(self):
        return [GraphObject.graphObjectDict[_] for _ in self.__southernNeighbors]

    @property
    def allNeighbors(self):
        if self._neighborsCache is None:
            self._neighborsCache = (self.northernNeighbors + self.westernNeighbors +
                                    self.easternNeighbors + self.southernNeighbors)
        return self._neighborsCache

    def updateCenterOfObject(self, center):
        self.__centerOfObject = center

    def isNeighbor(self, graphObject):
        return (graphObject in self.northernNeighbors or graphObject in self.westernNeighbors or
                graphObject in self.easternNeighbors or graphObject in self.southernNeighbors)

    def clearNeighborGraphObjects(self):
        self.__northernNeighbors = []
        self.__westernNeighbors = []
        self.__easternNeighbors = []
        self.__southernNeighbors = []
        self.__allNeighborIds = set()
        self._neighborsCache = None

    def addNeighbors(self, neighbors):
        for neighbor in neighbors:
            self.addNeighbor(graphObject=neighbor)

    def addNeighbor(self, graphObject, direction=None):
        if direction is None:
            direction = findDirectionOfShapeFromPoint(basePoint=self.__centerOfObject,
                                                      targetShape=graphObject.geometry)
        if graphObject.graphId not in self.__allNeighborIds:
            if direction == CardinalDirection.north:
                self.__northernNeighbors.append(graphObject.graphId)
            elif direction == CardinalDirection.west:
                self.__westernNeighbors.append(graphObject.graphId)
            elif direction == CardinalDirection.east:
                self.__easternNeighbors.append(graphObject.graphId)
            elif direction == CardinalDirection.south:
                self.__southernNeighbors.append(graphObject.graphId)
            self.__allNeighborIds.add(graphObject.graphId)
            self._neighborsCache = None

    def removeNeighbors(self, neighbors):
        for neighbor in neighbors:
            self.removeNeighbor(neighbor)

    def removeNeighbor(self, neighbor):
        nid = neighbor.graphId
        if nid not in self.__allNeighborIds:
            return
        for lst in (self.__northernNeighbors, self.__westernNeighbors,
                    self.__easternNeighbors, self.__southernNeighbors):
            if nid in lst:
                lst.remove(nid)
                break
        self.__allNeighborIds.discard(nid)
        self._neighborsCache = None

    def removeNonIntersectingNeighbors(self):
        for neighbor in self.allNeighbors:
            if not intersectingGeometries(self, neighbor):
                self.removeNeighbor(neighbor)

    def removeNeighborConnections(self):
        for neighbor in self.allNeighbors:
            neighbor.removeNeighbor(self)
        self.clearNeighborGraphObjects()

    def validateNeighborLists(self):
        if len(self.allNeighbors) != len(set(self.allNeighbors)):
            raise ValueError(f'Found a duplicate neighbor for GraphObject:{self.graphId}')

def getNextUniqueId():
    global _nextGraphId
    _nextGraphId += 1
    return _nextGraphId
