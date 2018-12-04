from geographyHelper import findDirectionOfShapeFromPoint, CardinalDirection, intersectingGeometries


class GraphObject:
    def __init__(self, centerOfObject):
        self.graphId = getNextUniqueId()
        GraphObject.graphObjectDict[self.graphId] = self
        self.__northernNeighbors = []
        self.__westernNeighbors = []
        self.__easternNeighbors = []
        self.__southernNeighbors = []
        self.populationEnergy = 0
        self.updateCenterOfObject(centerOfObject)

    graphObjectDict = {}


    def __setstate__(self, state):
        GraphObject.graphObjectDict[state['graphId']] = self
        self.__dict__ = state


    @property
    def hasNeighbors(self):
        if self.northernNeighbors or \
                self.westernNeighbors or \
                self.easternNeighbors or \
                self.southernNeighbors:
            return True
        else:
            return False


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
        return self.northernNeighbors + self.westernNeighbors + self.easternNeighbors + self.southernNeighbors

    def updateCenterOfObject(self, center):
        self.__centerOfObject = center

    def isNeighbor(self, graphObject):
        if graphObject in self.northernNeighbors or \
                graphObject in self.westernNeighbors or \
                graphObject in self.easternNeighbors or \
                graphObject in self.southernNeighbors:
            return True
        else:
            return False

    def clearNeighborGraphObjects(self):
        self.__northernNeighbors = []
        self.__westernNeighbors = []
        self.__easternNeighbors = []
        self.__southernNeighbors = []

    def addNeighbors(self, neighbors):
        for neighbor in neighbors:
            self.addNeighbor(graphObject=neighbor)

    def addNeighbor(self, graphObject, direction=None):
        if direction is None:
            direction = findDirectionOfShapeFromPoint(basePoint=self.__centerOfObject,
                                                      targetShape=graphObject.geometry)
        if graphObject not in self.allNeighbors:
            if direction == CardinalDirection.north:
                self.__northernNeighbors.append(graphObject.graphId)
            elif direction == CardinalDirection.west:
                self.__westernNeighbors.append(graphObject.graphId)
            elif direction == CardinalDirection.east:
                self.__easternNeighbors.append(graphObject.graphId)
            elif direction == CardinalDirection.south:
                self.__southernNeighbors.append(graphObject.graphId)

    def removeNeighbors(self, neighbors):
        for neighbor in neighbors:
            self.removeNeighbor(neighbor)

    def removeNeighbor(self, neighbor):
        for northernNeighbor in self.northernNeighbors:
            if neighbor is northernNeighbor:
                self.__northernNeighbors.remove(neighbor.graphId)
        for westernNeighbor in self.westernNeighbors:
            if neighbor is westernNeighbor:
                self.__westernNeighbors.remove(neighbor.graphId)
        for easternNeighbor in self.easternNeighbors:
            if neighbor is easternNeighbor:
                self.__easternNeighbors.remove(neighbor.graphId)
        for southernNeighbor in self.southernNeighbors:
            if neighbor is southernNeighbor:
                self.__southernNeighbors.remove(neighbor.graphId)

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
            raise ValueError('Found a duplicate neighbor for GraphObject:{0}'.format(self.graphId))

def getNextUniqueId():
    if GraphObject.graphObjectDict:
        return max(GraphObject.graphObjectDict.keys()) + 1
    return 0
