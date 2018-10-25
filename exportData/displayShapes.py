from matplotlib import pyplot
from descartes import PolygonPatch


def plotBlocksFromRedistrictingGroup(redistrictingGroup):
    blueColor = '#6699cc'
    greenColor = '#66cc78'
    fig = pyplot.figure()
    ax = fig.gca()

    font = {'family': 'serif',
            'color': 'darkred',
            'weight': 'normal',
            'size': 6,
            }
    for block in redistrictingGroup.blocks:
        if block.isWater:
            ax.add_patch(PolygonPatch(block.geometry, fc=blueColor, ec=blueColor, alpha=0.5, zorder=2 ))
        else:
            ax.add_patch(PolygonPatch(block.geometry, fc=greenColor, ec=greenColor, alpha=0.5, zorder=2))
        #todo: add text for poplation size
        centerOfBlock = block.geometry.centroid
        ax.text(x=centerOfBlock.x, y=centerOfBlock.y, s=block.population, fontdict=font)
        # ax.text()
        # https://matplotlib.org/api/pyplot_api.html#matplotlib.pyplot.text

    ax.axis('scaled')
    pyplot.show()


