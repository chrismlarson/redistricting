from matplotlib import pyplot, lines
import matplotlib._color_data as colorData
from descartes import PolygonPatch

blueColor = '#6699cc'
greenColor = '#66cc78'
purpleColor = '#b266cc'
grayColor = '#636363'
font = {'family': 'serif',
            'color': grayColor,
            'weight': 'normal',
            'size': 6,
            }

def plotBlocksForRedistrictingGroup(redistrictingGroup, showPopulationCounts=False):
    plotBlocksForRedistrictingGroups([redistrictingGroup], showPopulationCounts)


def plotBlocksForRedistrictingGroups(redistrictingGroups,
                                     showPopulationCounts=False,
                                     showDistrictNeighborConnections=False,
                                     showBlockNeighborConnections=False):
    fig = pyplot.figure()
    ax = fig.gca()

    for redistrictingGroup in redistrictingGroups:
        if showDistrictNeighborConnections:
            for neighborGroup in redistrictingGroup.allNeighbors:
                if neighborGroup in redistrictingGroups:
                    ax.add_line(getLineForPair(redistrictingGroup, neighborGroup, grayColor))

        for block in redistrictingGroup.children:
            if block.isWater:
                ax.add_patch(PolygonPatch(block.geometry, fc=blueColor, ec=blueColor, alpha=0.5, zorder=2))
            else:
                if redistrictingGroup.isBorderBlock(block):
                    ax.add_patch(PolygonPatch(block.geometry, fc=purpleColor, ec=purpleColor, alpha=0.5, zorder=2))
                else:
                    ax.add_patch(PolygonPatch(block.geometry, fc=greenColor, ec=greenColor, alpha=0.5, zorder=2))
            centerOfBlock = block.geometry.centroid

            if showPopulationCounts:
                ax.text(x=centerOfBlock.x, y=centerOfBlock.y, s=block.population, fontdict=font)

            if showBlockNeighborConnections:
                for neighborBlock in redistrictingGroup.children:
                    if neighborBlock in redistrictingGroups:
                        ax.add_line(getLineForPair(block, neighborBlock, grayColor))

    ax.axis('scaled')
    pyplot.show()

def plotRedistrictingGroups(redistrictingGroups,
                                     showPopulationCounts=False,
                                     showDistrictNeighborConnections=False):
    fig = pyplot.figure()
    ax = fig.gca()

    colorIndex = 0
    for redistrictingGroup in redistrictingGroups:
        if showDistrictNeighborConnections:
            for neighborGroup in redistrictingGroup.allNeighbors:
                if neighborGroup in redistrictingGroups:
                    ax.add_line(getLineForPair(redistrictingGroup, neighborGroup, grayColor))

        ax.add_patch(PolygonPatch(redistrictingGroup.geometry, fc=getColor(colorIndex), ec=greenColor, alpha=0.5, zorder=2))

        if showPopulationCounts:
            centerOfGroup = redistrictingGroup.geometry.centroid
            ax.text(x=centerOfGroup.x, y=centerOfGroup.y, s=redistrictingGroup.population, fontdict=font)
        colorIndex += 1

    ax.axis('scaled')
    pyplot.show()


def getColor(index):
    colorList = list(colorData.XKCD_COLORS.values())
    if index >= len(colorList):
        index -= len(colorList)
    return colorList[index]


def getLineForPair(a, b, color):
    aCenter = a.geometry.centroid
    bCenter = b.geometry.centroid
    return lines.Line2D(xdata=[aCenter.x, bCenter.x],
                             ydata=[aCenter.y, bCenter.y],
                             color=color,
                             linewidth=0.5)