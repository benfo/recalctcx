import os
import argparse
import math
import xml.etree.ElementTree as ET

def main():
    # Commandline arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--in", dest="inputfile", required=True)
    parser.add_argument("-o", "--out", dest="outputfile", default="")
    args = parser.parse_args()

    # Validate input and output files
    inputfilename = os.path.realpath(args.inputfile)    
    inputfilenameParts = os.path.splitext(os.path.basename(args.inputfile))    
    inputpath = os.path.split(inputfilename)[0]
    
    inputfileExists = os.path.exists(inputfilename) and os.access(inputfilename, os.R_OK)
    if not inputfileExists:
        print "The input file '%s' does not exist." % args.inputfile
        return

    outputfilename = args.outputfile
    if outputfilename == "":
        outputfilename = os.path.join(inputpath, inputfilenameParts[0] + "-recalculated" + inputfilenameParts[1])
    
    # Recalculate distance
    print "Recalculating distance..."
    recalculate(inputfilename, outputfilename)
    print "Done."

def distance(origin, destination):
    # using the Haversine formula:
    # http://en.wikipedia.org/wiki/Haversine_formula
    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371000 # meters

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2) * math.sin(dlat / 2) + math.cos(math.radians(lat1)) \
        * math.cos(math.radians(lat2)) * math.sin(dlon / 2) * math.sin(dlon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

def recalculate(inputfile, outputfile):
    ET.register_namespace("", "http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2")
    tree = ET.parse(inputfile)
    root = tree.getroot()

    for lap in root.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Lap"):
        totalDistance = 0
        fromPosition = None

        for trackpoint in lap.iter("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Trackpoint"):
            lat = float(trackpoint.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position/{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LatitudeDegrees").text)
            lon = float(trackpoint.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}Position/{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}LongitudeDegrees").text)
    
            if fromPosition is None:
                fromPosition = [lat, lon]
                continue
            toPosition = [lat, lon]

            dist = distance(fromPosition, toPosition)
            totalDistance += dist
            fromPosition = toPosition

            distMeters = trackpoint.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters")
            distMeters.text = str(round(totalDistance, 2))

        lapDistMeters = lap.find("{http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2}DistanceMeters")
        lapDistMeters.text = str(round(totalDistance, 2))

    tree.write(outputfile)

if __name__ == "__main__":
    main()