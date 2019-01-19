from os import path, makedirs
from matplotlib import pyplot, lines, cm, colors
import matplotlib._color_data as colorData
from descartes import PolygonPatch
from shapely.geometry import LineString

blueColor = '#6699cc'
greenColor = '#66cc78'
purpleColor = '#b266cc'
yellowColor = '#e2e54b'
orangeColor = '#e0974a'
turquoiseColor = '#66ccbc'
grayColor = '#636363'
font = {'family': 'serif',
        'color': grayColor,
        'weight': 'normal',
        'size': 6,
        }


def plotBlocksForRedistrictingGroup(redistrictingGroup,
                                    showPopulationCounts=False,
                                    showBlockGraphIds=False,
                                    showDistrictNeighborConnections=False,
                                    showBlockNeighborConnections=False,
                                    showGraphHeatmap=False,
                                    showGeometryPoints=False):
    plotBlocksForRedistrictingGroups(redistrictingGroups=[redistrictingGroup],
                                     showPopulationCounts=showPopulationCounts,
                                     showBlockGraphIds=showBlockGraphIds,
                                     showDistrictNeighborConnections=showDistrictNeighborConnections,
                                     showBlockNeighborConnections=showBlockNeighborConnections,
                                     showGraphHeatmap=showGraphHeatmap,
                                     showGeometryPoints=showGeometryPoints)


def plotBlocksForRedistrictingGroups(redistrictingGroups,
                                     showPopulationCounts=False,
                                     showBlockGraphIds=False,
                                     showDistrictNeighborConnections=False,
                                     showBlockNeighborConnections=False,
                                     showGraphHeatmap=False,
                                     showGeometryPoints=False):
    fig = pyplot.figure(figsize=(8, 8))
    ax = fig.gca()

    for redistrictingGroup in redistrictingGroups:
        if showDistrictNeighborConnections:
            for neighborGroup in redistrictingGroup.allNeighbors:
                if neighborGroup in redistrictingGroups:
                    ax.add_line(getLineForPair(redistrictingGroup, neighborGroup, grayColor))

        if showGeometryPoints:
            centroid = redistrictingGroup.geometry.centroid
            ax.scatter(centroid.x, centroid.y)

        maxPopulationEnergy = max([block.populationEnergy for block in redistrictingGroup.children])
        heatMap = cm.get_cmap('hot')
        heatmapNormalizer = colors.Normalize(vmin=0.0, vmax=maxPopulationEnergy)

        for block in redistrictingGroup.children:
            if block.isWater:
                ax.add_patch(PolygonPatch(block.geometry, fc=blueColor, ec=blueColor, alpha=0.5, zorder=2))
            else:
                if showGraphHeatmap:
                    normalizedEnergy = heatmapNormalizer(block.populationEnergy)
                    heatColor = heatMap(normalizedEnergy)
                    ax.add_patch(PolygonPatch(block.geometry, fc=heatColor, ec=heatColor, alpha=0.5, zorder=2))
                else:
                    if redistrictingGroup.isBorderBlock(block):
                        if block in redistrictingGroup.northernChildBlocks:
                            borderBlockColor = purpleColor
                        elif block in redistrictingGroup.westernChildBlocks:
                            borderBlockColor = yellowColor
                        elif block in redistrictingGroup.southernChildBlocks:
                            borderBlockColor = orangeColor
                        else:
                            borderBlockColor = turquoiseColor

                        ax.add_patch(PolygonPatch(block.geometry, fc=borderBlockColor, ec=borderBlockColor,
                                                  alpha=0.5, zorder=2))
                    else:
                        ax.add_patch(PolygonPatch(block.geometry, fc=greenColor, ec=greenColor, alpha=0.5, zorder=2))
            centerOfBlock = block.geometry.centroid

            if showPopulationCounts:
                ax.text(x=centerOfBlock.x, y=centerOfBlock.y, s=block.population, fontdict=font)

            if showBlockGraphIds:
                ax.text(x=centerOfBlock.x, y=centerOfBlock.y, s=block.graphId, fontdict=font)

            if showBlockNeighborConnections:
                for neighborBlock in block.allNeighbors:
                    ax.add_line(getLineForPair(block, neighborBlock, grayColor))

    ax.axis('scaled')
    pyplot.show()


def plotBlocksWithEdgesRedistrictingGroups(redistrictingGroup, edges):
    fig = pyplot.figure()
    ax = fig.gca()

    for block in redistrictingGroup.children:
        if redistrictingGroup.isBorderBlock(block):
            if block in redistrictingGroup.northernChildBlocks:
                borderBlockColor = purpleColor
            elif block in redistrictingGroup.westernChildBlocks:
                borderBlockColor = yellowColor
            elif block in redistrictingGroup.southernChildBlocks:
                borderBlockColor = orangeColor
            else:
                borderBlockColor = turquoiseColor

            ax.add_patch(PolygonPatch(block.geometry, fc=borderBlockColor, ec=borderBlockColor,
                                      alpha=0.5, zorder=2))
        else:
            ax.add_patch(PolygonPatch(block.geometry, fc=greenColor, ec=greenColor, alpha=0.5, zorder=2))

    for edge in edges:
        if edge is LineString:
            edgeSegments = [edge]
        else:
            edgeSegments = edge

        for edgeSegment in edgeSegments:
            edgeSegmentPlotLine = lines.Line2D(xdata=edgeSegment.coords.xy[0],
                                               ydata=edgeSegment.coords.xy[1],
                                               color='red',
                                               linewidth=2)
            ax.add_line(edgeSegmentPlotLine)

    ax.axis('scaled')
    pyplot.show()


def plotRedistrictingGroups(redistrictingGroups,
                            showPopulationCounts=False,
                            showGraphIds=False,
                            showDistrictNeighborConnections=False):
    fig = pyplot.figure()
    ax = fig.gca()

    colorIndex = 0
    for redistrictingGroup in redistrictingGroups:
        if showDistrictNeighborConnections:
            for neighborGroup in redistrictingGroup.allNeighbors:
                if neighborGroup in redistrictingGroups:
                    ax.add_line(getLineForPair(redistrictingGroup, neighborGroup, grayColor))

        ax.add_patch(PolygonPatch(redistrictingGroup.geometry,
                                  fc=getColor(colorIndex),
                                  ec=getColor(colorIndex),
                                  alpha=0.5,
                                  zorder=2))

        if showPopulationCounts:
            centerOfGroup = redistrictingGroup.geometry.centroid
            ax.text(x=centerOfGroup.x, y=centerOfGroup.y, s=redistrictingGroup.population, fontdict=font)

        if showGraphIds:
            centerOfGroup = redistrictingGroup.geometry.centroid
            ax.text(x=centerOfGroup.x, y=centerOfGroup.y, s=redistrictingGroup.graphId, fontdict=font)
        colorIndex += 1

    ax.axis('scaled')
    pyplot.show()


def plotDistrict(district,
                 showPopulationCounts=False,
                 showDistrictNeighborConnections=False,
                 showDistrictEnvelope=False,
                 colorDirectionalGroups=False):
    fig = pyplot.figure()
    ax = fig.gca()

    if showDistrictEnvelope:
        ax.add_patch(PolygonPatch(district.geometry.envelope, fc=grayColor, ec=grayColor, alpha=0.2, zorder=1))

    for redistrictingGroup in district.children:
        if showDistrictNeighborConnections:
            for neighborGroup in redistrictingGroup.allNeighbors:
                ax.add_line(getLineForPair(redistrictingGroup, neighborGroup, grayColor))

        groupColor = greenColor
        if colorDirectionalGroups:
            if redistrictingGroup in district.northernChildBlocks:
                groupColor = blueColor
            elif redistrictingGroup in district.westernChildBlocks:
                groupColor = yellowColor
            elif redistrictingGroup in district.easternChildBlocks:
                groupColor = purpleColor
            elif redistrictingGroup in district.southernChildBlocks:
                groupColor = orangeColor
        ax.add_patch(PolygonPatch(redistrictingGroup.geometry, fc=groupColor, ec=groupColor, alpha=0.5, zorder=2))

        if showPopulationCounts:
            centerOfGroup = redistrictingGroup.geometry.centroid
            ax.text(x=centerOfGroup.x, y=centerOfGroup.y, s=redistrictingGroup.population, fontdict=font)

    ax.axis('scaled')
    pyplot.show()


def plotGraphObjectGroups(graphObjectGroups,
                          showPopulationCounts=False,
                          showGraphIds=False,
                          showDistrictNeighborConnections=False,
                          showGraphHeatmapForFirstGroup=False,
                          saveImages=False,
                          saveDescription='Temp'):
    fig = pyplot.figure(figsize=(8, 8))
    ax = fig.gca()

    if showGraphHeatmapForFirstGroup:
        count = -1
    else:
        count = 0
    for graphObjectGroup in graphObjectGroups:
        if len(graphObjectGroup) is not 0:
            maxPopulation = max([block.population for block in graphObjectGroup])
            heatMap = cm.get_cmap('Reds')
            heatmapNormalizer = colors.LogNorm(vmin=0.1, vmax=maxPopulation, clip=True)

            for graphObject in graphObjectGroup:
                if showDistrictNeighborConnections:
                    for neighborGroup in graphObject.allNeighbors:
                        ax.add_line(getLineForPair(graphObject, neighborGroup, grayColor))
                if showGraphHeatmapForFirstGroup and graphObjectGroups.index(graphObjectGroup) is 0:
                    normalizedEnergy = heatmapNormalizer(graphObject.population)
                    heatColor = heatMap(normalizedEnergy)
                    ax.add_patch(PolygonPatch(graphObject.geometry, fc=heatColor, ec=(0,0,0,0), zorder=1))
                else:
                    ax.add_patch(
                        PolygonPatch(graphObject.geometry, fc=getColor(count), ec=getColor(count), alpha=0.5,
                                     zorder=2))

                if showPopulationCounts:
                    centerOfGroup = graphObject.geometry.centroid
                    ax.text(x=centerOfGroup.x, y=centerOfGroup.y, s=graphObject.population, fontdict=font)

                if showGraphIds:
                    centerOfGroup = graphObject.geometry.centroid
                    ax.text(x=centerOfGroup.x, y=centerOfGroup.y, s=graphObject.graphId, fontdict=font)

        count += 1

    ax.axis('scaled')

    if saveImages:
        directoryPath = path.expanduser('~/Documents/RedistrictingImages')
        if not path.exists(directoryPath):
            makedirs(directoryPath)
        filePath = path.expanduser('{0}/{1}.png'.format(directoryPath, saveDescription))
        pyplot.savefig(filePath)
    pyplot.show()


def plotPolygons(polygons, title=None):
    fig = pyplot.figure(figsize=(8, 8))
    ax = fig.gca()

    count = 0
    for polygon in polygons:
        if polygon is not None:
            ax.add_patch(PolygonPatch(polygon, fc=getColor(count), ec=getColor(count), alpha=0.5, zorder=2))
        count += 1

    if title is not None:
        fig.suptitle(title, fontsize=16)

    ax.axis('scaled')
    pyplot.show()


def plotDistricts(districts,
                  showPopulationCounts=False,
                  showDistrictNeighborConnections=False,
                  saveImages=False,
                  saveDescription='Temp'):
    fig = pyplot.figure()
    ax = fig.gca()

    colorIndex = 0
    for district in districts:
        for redistrictingGroup in district.children:
            if showDistrictNeighborConnections:
                for neighborGroup in redistrictingGroup.allNeighbors:
                    ax.add_line(getLineForPair(redistrictingGroup, neighborGroup, grayColor))

            ax.add_patch(
                PolygonPatch(redistrictingGroup.geometry, fc=getColor(colorIndex), ec=getColor(colorIndex), alpha=0.5,
                             zorder=2))

            if showPopulationCounts:
                centerOfGroup = redistrictingGroup.geometry.centroid
                ax.text(x=centerOfGroup.x, y=centerOfGroup.y, s=redistrictingGroup.population, fontdict=font)
        colorIndex += 1

    ax.axis('scaled')

    if saveImages:
        directoryPath = path.expanduser('~/Documents/RedistrictingImages')
        if not path.exists(directoryPath):
            makedirs(directoryPath)
        filePath = path.expanduser('{0}/{1}.png'.format(directoryPath, saveDescription))
        pyplot.savefig(filePath)
    pyplot.show()


def getColor(index):
    if index >= len(distinctColors):
        index -= len(distinctColors)
    return distinctColors[index]


def getLineForPair(a, b, color):
    aCenter = a.geometry.centroid
    bCenter = b.geometry.centroid
    return lines.Line2D(xdata=[aCenter.x, bCenter.x],
                        ydata=[aCenter.y, bCenter.y],
                        color=color,
                        linewidth=0.5)


startingColors = [colorData.XKCD_COLORS['xkcd:cloudy blue'],
                  colorData.XKCD_COLORS['xkcd:dark pastel green'],
                  colorData.XKCD_COLORS['xkcd:liliac'],
                  colorData.XKCD_COLORS['xkcd:saffron'],
                  colorData.XKCD_COLORS['xkcd:light red'],
                  colorData.XKCD_COLORS['xkcd:tan'],
                  colorData.XKCD_COLORS['xkcd:cool blue'],
                  colorData.XKCD_COLORS['xkcd:lime green'],
                  colorData.XKCD_COLORS['xkcd:purple'],
                  colorData.XKCD_COLORS['xkcd:orange'],
                  colorData.XKCD_COLORS['xkcd:deep pink'],
                  colorData.XKCD_COLORS['xkcd:pale pink'],
                  colorData.XKCD_COLORS['xkcd:twilight']]
distinctColors = startingColors + [color for color in list(colorData.XKCD_COLORS.values()) if
                                   color not in startingColors]
