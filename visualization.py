from pyopenms import *
import matplotlib.pyplot as plt
import os
from featureDetectionFunctions import featureFinderMetaboIdent

for file in os.listdir('tests/mzML'):
    mzml_path = os.path.join('tests/mzML', file)
    feature_path = os.path.join('tests/features', file[:-4]+'featureXML')
    img_path = os.path.join('tests/img', file[:-4]+'png')
    
    featureFinderMetaboIdent(mzml_path, feature_path, 'tests/2021-06-30 Axel.tsv', mz_window=0.04)

    fm = FeatureMap()
    fh = FeatureXMLFile()
    fh.load(feature_path, fm)


    fig = plt.figure()
    ax = fig.add_subplot(111)

    for feature in fm:
        sub = feature.getSubordinates()[0]
        retention_times = [x[0] for x in sub.getConvexHulls()[0].getHullPoints()]
        intensities = [int(y[1]) for y in sub.getConvexHulls()[0].getHullPoints()]
        ax.plot(retention_times, intensities, label = sub.getMetaValue('MZ'))

    ax.legend()
    ax.set_ylabel('intensity')
    ax.set_xlabel('time (s)')
    ax.set_title(os.path.basename(file)[:-11])
    plt.savefig(img_path, format='png')

