import subprocess
from pyopenms import *
import os
import json
import matplotlib.pyplot as plt
import pandas as pd

def ffmid(mzML, featureXML, library, n_isotopes = 2, mz_window = 10, peak_width = 60):
    args = ["FeatureFinderMetaboIdent","-in",mzML,"-out",featureXML,"-id",library,
            "-extract:mz_window",str(mz_window),"-extract:n_isotopes",str(n_isotopes),
            "-detect:peak_width",str(peak_width)]
    subprocess.call(args)

def feature_to_json(feature_path, json_dir, ffmid_params):
    feature_map = FeatureMap()
    FeatureXMLFile().load(feature_path, feature_map)

    out = {'file': {'name':os.path.basename(feature_path[:-11])},
           'params': ffmid_params,
           'auc': {},
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

def view_features(json_objects = []):
    for data in json_objects:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        for f_id, feature in data['feature'].items():
            color = next(ax._get_lines.prop_cycler)['color']
            for i, iso in feature['iso'].items():
                plt.plot(iso['rt'], iso['i'], color = color)
                if i == '1':
                    plt.text(iso['rt'][0], max(iso['i']), feature['name'], color = color)
        ax.ticklabel_format(axis='y', style='sci', scilimits=(0,0), useMathText=True)
        ax.set_ylabel('intensity (cps)')
        ax.set_xlabel('time (s)')
        plt.title(data['file']['name'])
        plt.show()
    
def get_json_objects(project_dir):
        if project_dir == '':
            print('Select project directory!')
            return
        json_dir = os.path.join(project_dir, 'data')
        json_objects = []
        for file in os.listdir(json_dir):
            with open(os.path.join(json_dir, file),'r') as f:
                json_objects.append(json.load(f))
        return json_objects

def maximum_absolute_scaling(df):
    # copy the dataframe
    df_scaled = df.copy()
    # apply maximum absolute scaling
    for column in df_scaled.columns[1:]:
        column_values = pd.to_numeric(df_scaled[column])
        df_scaled[column] = column_values  / column_values.abs().max()
    return df_scaled

def result_to_df(result):
        df = pd.DataFrame(result)
        df = df.replace('NA', np.nan)
        new_header = df.iloc[0]
        df = df[1:]
        df.columns = new_header
        return df