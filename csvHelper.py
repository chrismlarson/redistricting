import sys
import csv
from tqdm import tqdm

def getNumOfCSVRows(csvPath):
    setCSVLimitToMaxAcceptable()

    tqdm.write('*** Getting total number of CSV rows for progress ***')
    totalNumberOfRows = 0
    with tqdm() as pbar:
        with open(csvPath, newline='\n') as csvFile:
            dictReader = csv.DictReader(csvFile)
            for row in dictReader:
                totalNumberOfRows += 1
                pbar.update(1)

    totalNumberOfRows -= 1 #to account for the header
    tqdm.write('Total number of CSV rows: {0}'.format(totalNumberOfRows))
    return totalNumberOfRows


def setCSVLimitToMaxAcceptable():
    decrement = True
    maxInt = sys.maxsize

    while decrement:
        # decrease the maxInt value by factor 10
        # as long as the OverflowError occurs.

        decrement = False
        try:
            csv.field_size_limit(maxInt)
        except OverflowError:
            maxInt = int(maxInt / 10)
            decrement = True