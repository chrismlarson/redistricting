from matplotlib import pyplot
from descartes import PolygonPatch


def plotBlocksForRedistrictingGroup(redistrictingGroup, showPopulationCounts=False):
    plotBlocksForRedistrictingGroups([redistrictingGroup], showPopulationCounts)


def plotBlocksForRedistrictingGroups(redistrictingGroups, showPopulationCounts=False):
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
        for block in redistrictingGroup.children:
            if block.isWater:
                ax.add_patch(PolygonPatch(block.geometry, fc=blueColor, ec=blueColor, alpha=0.5, zorder=2 ))
            else:
                if redistrictingGroup.isBorderBlock(block):
                    ax.add_patch(PolygonPatch(block.geometry, fc=purpleColor, ec=purpleColor, alpha=0.5, zorder=2))
                else:
                    ax.add_patch(PolygonPatch(block.geometry, fc=greenColor, ec=greenColor, alpha=0.5, zorder=2))
            centerOfBlock = block.geometry.centroid

            if showPopulationCounts:
                ax.text(x=centerOfBlock.x, y=centerOfBlock.y, s=block.population, fontdict=font)

    ax.axis('scaled')
    pyplot.show()


