from matplotlib import pyplot
from descartes import PolygonPatch


def plotBlocksForRedistrictingGroup(redistrictingGroup, shouldShowText=False):
    plotBlocksForRedistrictingGroups([redistrictingGroup], shouldShowText)


def plotBlocksForRedistrictingGroups(redistrictingGroups, shouldShowText=False):
    blueColor = '#6699cc'
    greenColor = '#66cc78'
    purpleColor = '#b266cc'
    fig = pyplot.figure()
    ax = fig.gca()

    font = {'family': 'serif',
            'color': 'darkred',
            'weight': 'normal',
            'size': 6,
            }
    for redistrictingGroup in redistrictingGroups:
        for block in redistrictingGroup.blocks:
            if block.isWater:
                ax.add_patch(PolygonPatch(block.geometry, fc=blueColor, ec=blueColor, alpha=0.5, zorder=2 ))
            else:
                if redistrictingGroup.isBorderBlock(block):
                    ax.add_patch(PolygonPatch(block.geometry, fc=purpleColor, ec=purpleColor, alpha=0.5, zorder=2))
                else:
                    ax.add_patch(PolygonPatch(block.geometry, fc=greenColor, ec=greenColor, alpha=0.5, zorder=2))
            centerOfBlock = block.geometry.centroid

            if shouldShowText:
                ax.text(x=centerOfBlock.x, y=centerOfBlock.y, s=block.population, fontdict=font)

    ax.axis('scaled')
    pyplot.show()


