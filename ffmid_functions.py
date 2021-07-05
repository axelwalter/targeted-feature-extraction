import sys
sys.path.insert(1, '/home/axel/dev/OpenMS-build/pyOpenMS')

from pyopenms import *

import csv

# read an assay library (.tsv file) and return a list of FeatureFinderMetaboIdentCompound
def metaboTableFromFile(path_to_library_file):
    metaboTable = []
    with open(path_to_library_file, 'r') as tsv_file:
        tsv_reader = csv.reader(tsv_file, delimiter="\t")
        next(tsv_reader) # skip header
        for row in tsv_reader:
            metaboTable.append(FeatureFinderMetaboIdentCompound(
                row[0], # name
                row[1], # sum formula
                float(row[2]), # mass
                [int(charge) for charge in row[3].split(',')], # charges
                [float(rt) for rt in row[4].split(',')], # RTs
                [float(rt_range) for rt_range in row[5].split(',')], # RT ranges
                [float(iso_distrib) for iso_distrib in row[6].split(',')] # isotope distributions
            ))
    return metaboTable

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import axes3d

def plotDetectedFeatures3D(path_to_featureXML):
    fm = FeatureMap()
    fh = FeatureXMLFile()
    fh.load(path_to_featureXML, fm)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for feature in fm:
        color = next(ax._get_lines.prop_cycler)['color']
        for i, sub in enumerate(feature.getSubordinates()):       
            retention_times = [x[0] for x in sub.getConvexHulls()[0].getHullPoints()]
            intensities = [int(y[1]) for y in sub.getConvexHulls()[0].getHullPoints()]
            mz = sub.getMetaValue('MZ')
            ax.plot(retention_times, intensities, zs = mz, zdir = 'x', color = color)
            if i == 0:
                ax.text(mz,retention_times[0], max(intensities)*1.02, feature.getMetaValue('label'), color = color)

    ax.set_ylabel('time (s)')
    ax.set_xlabel('m/z')
    ax.set_zlabel('intensity (cps)')
    plt.show()

# plotDetectedFeatures3D('/home/axel/dev/OpenMS/src/tests/topp/FeatureFinderMetaboIdent_1_output.featureXML')


import matplotlib.pyplot as plt

def plotDetectedFeatures(path_to_featureXML):
    fm = FeatureMap()
    fh = FeatureXMLFile()
    fh.load(path_to_featureXML, fm)

    fig = plt.figure()
    ax = fig.add_subplot(111)

    for feature in fm:
        color = next(ax._get_lines.prop_cycler)['color']
        for i, sub in enumerate(feature.getSubordinates()):       
            retention_times = [x[0] for x in sub.getConvexHulls()[0].getHullPoints()]
            intensities = [int(x[1]) for x in sub.getConvexHulls()[0].getHullPoints()]
            plt.plot(retention_times, intensities, color = color)
            if i == 0:
                plt.text(retention_times[0], max(intensities)*1.02, feature.getMetaValue('label'), color = color)

    plt.xlabel('time (s)')
    plt.ylabel('intensity (cps)')
    plt.show()

# plotDetectedFeatures('/home/axel/dev/OpenMS/src/tests/topp/FeatureFinderMetaboIdent_1_output.featureXML')