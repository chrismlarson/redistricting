from geographyHelper import findDirectionOfShapeFromPoint, CardinalDirection


class GraphObject:
    def __init__(self, centerOfObject):
        self.__northernNeighbors = []
        self.__westernNeighbors = []
        self.__easternNeighbors = []
        self.__southernNeighbors = []
        self.updateCenterOfObject(centerOfObject)

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
        return self.__northernNeighbors

    @property
    def westernNeighbors(self):
        return self.__westernNeighbors

    @property
    def easternNeighbors(self):
        return self.__easternNeighbors

    @property
    def southernNeighbors(self):
        return self.__southernNeighbors

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
            self.__northernNeighbors.append(graphObject)
        elif direction == CardinalDirection.west:
            self.__westernNeighbors.append(graphObject)
        elif direction == CardinalDirection.east:
            self.__easternNeighbors.append(graphObject)
        elif direction == CardinalDirection.south:
            self.__southernNeighbors.append(graphObject)
