from matplotlib import pyplot, lines
from descartes import PolygonPatch


def plotBlocksForRedistrictingGroup(redistrictingGroup, showPopulationCounts=False):
    plotBlocksForRedistrictingGroups([redistrictingGroup], showPopulationCounts)


def plotBlocksForRedistrictingGroups(redistrictingGroups,
                                     showPopulationCounts=False,
                                     showDistrictNeighborConnections=False,
                                     showBlockNeighborConnections=False):
    blueColor = '#6699cc'
    greenColor = '#66cc78'
    purpleColor = '#b266cc'
    grayColor = '#636363'
    fig = pyplot.figure()
    ax = fig.gca()

    font = {'family': 'serif',
            'color': grayColor,
            'weight': 'normal',
            'size': 6,
            }
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


def getLineForPair(a, b, color):
    aCenter = a.geometry.centroid
    bCenter = b.geometry.centroid
    return lines.Line2D(xdata=[aCenter.x, bCenter.x],
                             ydata=[aCenter.y, bCenter.y],
                             color=color,
                             linewidth=0.5)