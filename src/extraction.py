import subprocess
from pyopenms import *
import os
import json
import matplotlib.pyplot as plt

def ffmid(mzML, featureXML, library, n_isotopes = 2, mz_window = 10, peak_width = 60):
    args = ["FeatureFinderMetaboIdent","-in",mzML,"-out",featureXML,"-id",library,
            "-extract:mz_window",str(mz_window),"-extract:n_isotopes",str(n_isotopes),
            "-detect:peak_width",str(peak_width)]
    subprocess.call(args)

def feature_to_json(feature_path, json_dir):
    feature_map = FeatureMap()
    FeatureXMLFile().load(feature_path, feature_map)

    out = {'auc': {},
            'feature': {}}
    for feature in feature_map:
        f_id = feature.getMetaValue('PeptideRef')
        f_name = feature.getMetaValue("label")
        out['feature'][f_id] = {'name': f_name, 'iso': {}}
        for i, sub in enumerate(feature.getSubordinates()):
            out['feature'][f_id]['iso'][i+1] = {'mz': sub.getMetaValue('MZ'),
                            'rt': [float(x[0]) for x in sub.getConvexHulls()[0].getHullPoints()],
                            'i': [int(y[1]) for y in sub.getConvexHulls()[0].getHullPoints()],
                            'auc': sum([int(y[1]) for y in sub.getConvexHulls()[0].getHullPoints()]),
                            'id': sub.getMetaValue('native_id')}
            if f_name in out['auc'].keys():
                out['auc'][f_name] += out['feature'][f_id]['iso'][i+1]['auc']
            else:
                out['auc'][f_name] = out['feature'][f_id]['iso'][i+1]['auc']
    with open(os.path.join(json_dir, os.path.basename(feature_path[:-10])+'json'), "w") as f:
        json.dump(out, f, indent = 4)

def view_features(json_dir = ''):
    for file in os.listdir(json_dir):
        with open(os.path.join(json_dir, file), 'r') as f:
            data = json.load(f)
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for f_id, feature in data['feature'].items():
            color = next(ax._get_lines.prop_cycler)['color']
            for i, iso in feature['iso'].items():
                plt.plot(iso['rt'], iso['i'], color = color)
                if i == '1':
                    plt.text(iso['rt'][0], max(iso['i']), feature['name'], color = color)
        plt.title(file[:-5])
        plt.show()