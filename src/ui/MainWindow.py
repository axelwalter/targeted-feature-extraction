import os
from tkinter import *
from tkinter import filedialog as fd
from src.extraction import ffmid, feature_to_json, view_features, get_json_objects
from src.ui.VisualizationWindow import VisualizationWindow

class MainWindow(Tk):
    def __init__(self):
        super().__init__()

        self.title('Targeted Feature Extraction')
        self.geometry('970x350')
        self.mzml_files = []
        self.mzMLFilesLabel = Label(text='mzML files')
        self.mzMLFilesLabel.place(x = 10, y = 2)
        self.mzMLFilesText = Text()
        self.mzMLFilesText.config(state='disabled')
        self.mzMLFilesText.place(x = 10, y = 20, height = 190, width = 780)

        self.targetLibraryLabel = Label(text='Target Libray')
        self.targetLibraryLabel.place(x = 10, y = 210)
        self.targetLibraryText = Text()
        self.targetLibraryText.config(state='disabled')
        self.targetLibraryText.place(x = 10, y = 230, height = 25, width = 780)

        self.label = Label(text='Parameters')
        self.label.place(x = 800, y = 2)
        self.label = Label(text='m/z extraction window\nppm (> 1) or Da (< 1)')
        self.label.place(x = 800, y = 30)
        self.mzWindowText = Text()
        self.mzWindowText.place(x = 800, y = 70, height = 25, width = 60)
        self.mzWindowText.insert('end','0.04')
        self.label = Label(text='peak width (sec)')
        self.label.place(x = 800, y = 100)
        self.peakWidthText = Text()
        self.peakWidthText.place(x = 800, y = 120, height = 25, width = 60)
        self.peakWidthText.insert('end','30')
        self.label = Label(text='number of isotopes')
        self.label.place(x = 800, y = 150)
        self.numberIsotopesText = Text()
        self.numberIsotopesText.place(x = 800, y = 170, height = 25, width = 60)
        self.numberIsotopesText.insert('end','2')

        self.openFilesButton = Button(text='Open mzML Files', command=self.open_mzML)
        self.openFilesButton.place(x = 10, y = 270)

        self.clearFilesButton = Button(text='Clear mzML Files', command=self.clear_mzML_files)
        self.clearFilesButton.place(x = 10, y = 310)

        self.selectProjectButton = Button(text='Select Project Directory', command=self.select_project_dir)
        self.selectProjectButton.place(x = 180, y = 270)

        self.openTargetLibraryButton = Button(text='Open Target Library', command=self.open_target_library)
        self.openTargetLibraryButton.place(x = 570, y = 270)

        self.extractButton = Button(text='Extract Features', command=self.extract_features)
        self.extractButton.place(x = 570, y = 310)

        self.extractButton = Button(text='Data Visualization', command=self.data_visualization)
        self.extractButton.place(x = 390, y = 310)

        self.viewButton = Button(text='View Features', command=self.view_features)
        self.viewButton.place(x = 390, y = 270)

    def open_mzML(self):
        filenames = fd.askopenfilenames(filetypes=[('mzML Files', '*.mzML')])
        self.mzml_files += filenames
        self.mzMLFilesText.config(state='normal')
        self.mzMLFilesText.delete('1.0','end')
        self.mzMLFilesText.insert('end','\n'.join(self.mzml_files))
        self.mzMLFilesText.config(state='disabled')

    def open_target_library(self):
        filename = fd.askopenfilename(filetypes=[('tsv files', '*.tsv')])
        self.targetLibraryText.config(state='normal')
        self.targetLibraryText.delete('1.0','end')
        self.targetLibraryText.insert('end', filename)
        self.targetLibraryText.config(state='disabled')

    def clear_mzML_files(self):
        self.mzMLFilesText.config(state='normal')
        self.mzMLFilesText.delete('1.0','end')
        self.mzMLFilesText.config(state='disabled')
        self.mzml_files = []

    def select_project_dir(self):
        self.project_dir = fd.askdirectory()
        print('Selected project directory: '+ self.project_dir)

    def extract_features(self):
        if self.project_dir == '':
            print('Select project directory!')
            return
        if self.mzml_files == []:
            print('Open mzML files!')
            return
        if self.targetLibraryText.get('1.0','end').strip() == '':
            print('Select target library!')
            return
        if not os.path.isdir(os.path.join(self.project_dir, 'data')):
            os.mkdir(os.path.join(self.project_dir, 'data'))

        ffmid_params = {'mz_window': float(self.mzWindowText.get('1.0','end').strip()),
                        'peak_width': float(self.peakWidthText.get('1.0','end').strip()),
                        'n_isotopes': int(self.numberIsotopesText.get('1.0','end').strip())}
        for mzml_path in self.mzml_files:
            feature_path = mzml_path[:-4]+'featureXML'

            ffmid(mzml_path,
                feature_path,
                self.targetLibraryText.get('1.0','end').strip(),
                mz_window = ffmid_params['mz_window'],
                peak_width = ffmid_params['peak_width'],
                n_isotopes = ffmid_params['n_isotopes'])

            feature_to_json(feature_path, os.path.join(self.project_dir, 'data'), ffmid_params)
            os.remove(feature_path)
        print('SUCCESS: features extracted')

    def view_features(self):
        view_features(get_json_objects(self.project_dir))
    
    def data_visualization(self):
        visualization_window = VisualizationWindow(json_objects=get_json_objects(self.project_dir))
        visualization_window.mainloop()
