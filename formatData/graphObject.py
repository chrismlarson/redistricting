from geographyHelper import findDirectionOfShapeFromPoint, CardinalDirection
from operator import itemgetter


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
        return list(itemgetter(*self.__northernNeighbors)(GraphObject.graphObjectDict))

    @property
    def westernNeighbors(self):
        return list(itemgetter(*self.__westernNeighbors)(GraphObject.graphObjectDict))

    @property
    def easternNeighbors(self):
        return list(itemgetter(*self.__easternNeighbors)(GraphObject.graphObjectDict))

    @property
    def southernNeighbors(self):
        return list(itemgetter(*self.__southernNeighbors)(GraphObject.graphObjectDict))

    @property
    def allNeighbors(self):
        return self.northernNeighbors + self.westernNeighbors + self.easternNeighbors + self.southernNeighbors

    @property
    def directionSets(self):
        return [self.northernNeighbors,
                self.westernNeighbors,
                self.easternNeighbors,
                self.southernNeighbors]

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
            direction = findDirectionOfShapeFromPoint(basePoint=self.__centerOfObject,
                                                      targetShape=neighbor.geometry)
            self.addNeighbor(graphObject=neighbor, direction=direction)

    def addNeighbor(self, graphObject, direction):
        if direction == CardinalDirection.north:
            self.__northernNeighbors.append(graphObject.graphId)
        elif direction == CardinalDirection.west:
            self.__westernNeighbors.append(graphObject.graphId)
        elif direction == CardinalDirection.east:
            self.__easternNeighbors.append(graphObject.graphId)
        elif direction == CardinalDirection.south:
            self.__southernNeighbors.append(graphObject.graphId)


    def validateNeighborLists(self):
        directionSets = self.directionSets
        for directionSet in directionSets:
            if len(directionSet) != len(set(directionSet)):
                raise ValueError('Found a duplicate neighbor for GraphObject:{0}'.format(directionSet))

def getNextUniqueId():
    if GraphObject.graphObjectDict:
        return max(GraphObject.graphObjectDict.keys()) + 1
    return 0
