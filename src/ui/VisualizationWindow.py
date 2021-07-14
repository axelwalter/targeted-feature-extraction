
from tkinter import *
from tkinter import filedialog as fd
import pandas as pd

class VisualizationWindow(Toplevel):
    def __init__(self, json_objects):
        super().__init__()
        self.json_objects = json_objects

        self.title('Data Visualization (AUC)')
        self.geometry('970x350')
        self.samplesLabel = Label(self, text='samples')
        self.samplesLabel.place(x = 10, y = 2)
        self.samplesText = Text(self)
        self.samplesText.place(x = 10, y = 20, height = 230, width = 600)

        self.compoundsLabel = Label(self, text='compounds')
        self.compoundsLabel.place(x = 620, y = 2)
        self.compoundsText = Text(self)
        self.compoundsText.place(x = 620, y = 20, height = 230, width = 400)

        self.populate_samples_compounds()
        
        self.calc_option = StringVar(self)
        self.calc_option.set('absolute values')
        self.calcOption = OptionMenu(self, self.calc_option, 'absolute values', 'relative to first sample (%)')
        self.calcOption.place(x = 10, y = 270)
        self.viewButton = Button(self, text='Excel Table', command=self.generate_table)
        self.viewButton.place(x = 600, y = 270)

    def populate_samples_compounds(self):
        if not self.json_objects:
            print('There are no JSON files in your project directory! Forgot to select the project directory?')
            return
        compounds_tmp = []
        for sample in self.json_objects:
            self.samplesText.insert('end', sample['file']['name']+',\n')
            for key in sample['auc'].keys():
                compounds_tmp.append(key)
        for compound in set(compounds_tmp):
            self.compoundsText.insert('end', compound+'\n')
    
    def get_current_data(self):
        result = {}
        result['compounds'] = [compound.strip() for compound in self.compoundsText.get('1.0','end').split('\n') if compound]
        result['samples'] = []
        for line in self.samplesText.get('1.0','end').split('\n'):
            if ',' in line:
                file_name, custom_name = line.split(',')
                result['samples'].append((file_name.strip(), custom_name.strip()))
        return result
    
    def generate_table(self):
        print(self.calc_option.get())
        current_data = self.get_current_data()
        result = [['']+[compound for compound in current_data['compounds']]]
        for file_name, custom_name in current_data['samples']:
            data = next((json_object for json_object in self.json_objects if json_object['file']['name'] == file_name), None)
            if data:
                result.append([custom_name]+[str(data['auc'].get(compound,'NA')) for compound in current_data['compounds']])
        
        excel_path = fd.askopenfilename(filetypes=[('excel files', '*.xlsx')], parent=self)
        if excel_path:
            pd.DataFrame(result).to_excel(excel_path, index=False, header=None)
            
            