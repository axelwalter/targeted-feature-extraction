from pyopenms import *
import matplotlib.pyplot as plt
import os
import json
import subprocess
from tkinter import *
from tkinter.ttk import *
from tkinter import filedialog as fd

mzml_files = []
project_dir = ''

def ffmid(mzML, featureXML, library, n_isotopes = 2, mz_window = 10, peak_width = 60):
    
    args = ["FeatureFinderMetaboIdent","-in",mzML,"-out",featureXML,"-id",library,
            "-extract:mz_window",str(mz_window),"-extract:n_isotopes",str(n_isotopes),
            "-detect:peak_width",str(peak_width)]
    subprocess.call(args)

def extract_features():
    if project_dir == '':
        print('Select project directory!')
        return
    if mzml_files == []:
        print('Open mzML files!')
        return
    if targetLibraryText.get('1.0','end').strip() == '':
        print('Select target library!')
        return
    if not os.path.isdir(os.path.join(project_dir, 'data')):
        os.mkdir(os.path.join(project_dir, 'data'))
    for mzml_path in mzml_files:
        feature_path = mzml_path[:-4]+'featureXML'
        ffmid(mzml_path,
              feature_path,
              targetLibraryText.get('1.0','end').strip(),
              mz_window = float(mzWindowText.get('1.0','end').strip()))
        feature_to_json(feature_path, os.path.join(project_dir, 'data'))
        os.remove(feature_path)

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

def visualize():
    if project_dir == '':
        print('Select project directory!')
        return
    json_dir = os.path.join(project_dir, 'data')
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

# visualize('tests/json')
# extract_features(feature_dir='tests/features', json_dir='tests/json')
# ffmid(mzml_dir='tests/mzML', id_path='tests/2021-06-30 Axel.tsv', mz_window=0.04)

def open_mzML():
    filenames = fd.askopenfilenames(filetypes=[('mzML Files', '*.mzML')])
    global mzml_files
    mzml_files += filenames
    mzMLFilesText.config(state='normal')
    mzMLFilesText.delete('1.0','end')
    mzMLFilesText.insert('end','\n'.join(mzml_files))
    mzMLFilesText.config(state='disabled')

def open_target_library():
    filename = fd.askopenfilename(filetypes=[('tsv files', '*.tsv')])
    targetLibraryText.config(state='normal')
    targetLibraryText.delete('1.0','end')
    targetLibraryText.insert('end', filename)
    targetLibraryText.config(state='disabled')

def clear_mzML_files():
    mzMLFilesText.config(state='normal')
    mzMLFilesText.delete('1.0','end')
    mzMLFilesText.config(state='disabled')
    global mzml_files
    mzml_files = []

def select_project_dir():
    global project_dir 
    project_dir = fd.askdirectory()
    print('Selected output directory: '+project_dir)

root = Tk(className='Targeted Feature Detection')
root.geometry('970x350')
mzMLFilesLabel = Label(text='mzML files')
mzMLFilesLabel.place(x = 10, y = 2)
mzMLFilesText = Text()
mzMLFilesText.config(state='disabled')
mzMLFilesText.place(x = 10, y = 20, height = 190, width = 780)

targetLibraryLabel = Label(text='Target Libray')
targetLibraryLabel.place(x = 10, y = 210)
targetLibraryText = Text()
targetLibraryText.config(state='disabled')
targetLibraryText.place(x = 10, y = 230, height = 25, width = 780)

parameterLabel = Label(text='Parameters\n\nm/z extraction window\nppm (> 1) or Da (< 1)\n\n\nrt window (sec)\n\n\nnumber of isotopes')
parameterLabel.place(x = 800, y = 25)
mzWindowText = Text()
mzWindowText.place(x = 800, y = 100, height = 25, width = 60)
mzWindowText.insert('end','0.4')
peakWidthText = Text()
peakWidthText.place(x = 800, y = 150, height = 25, width = 60)
peakWidthText.insert('end','60')
peakWidthText = Text()
peakWidthText.place(x = 800, y = 200, height = 25, width = 60)
peakWidthText.insert('end','2')

openFilesButton = Button(text='Open mzML Files', command=open_mzML)
openFilesButton.place(x = 10, y = 270)

clearFilesButton = Button(text='Clear mzML Files', command=clear_mzML_files)
clearFilesButton.place(x = 10, y = 310)

selectProjectButton = Button(text='Select Project Directory', command=select_project_dir)
selectProjectButton.place(x = 180, y = 270)

openTargetLibraryButton = Button(text='Open Target Library', command=open_target_library)
openTargetLibraryButton.place(x = 440, y = 270)

extractButton = Button(text='Targeted Feature Extraction', command=extract_features)
extractButton.place(x = 595, y = 270)

viewButton = Button(text='View Features', command=visualize)
viewButton.place(x = 805, y = 270)
mainloop()