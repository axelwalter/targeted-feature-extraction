from tkinter import *
from tkinter import filedialog as fd
from src.extraction import maximum_absolute_scaling, result_to_df
from src.ui.HeatMapWindow import HeatMapWindow
from src.ui.BarPlotWindow import BarPlotWindow

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
        self.calcOption = OptionMenu(self, self.calc_option, 'absolute values', 'relative to first sample (%)',
                                     'relative to first sample (absolute values)')
        self.calcOption.place(x = 10, y = 270)


        self.normalize = BooleanVar()
        self.normalize.set(False)
        self.normalizeCheckButton = Checkbutton(self, text = "normalize values (-1 to 1)", variable = self.normalize)
        self.normalizeCheckButton.place(x = 10, y = 310)

        self.tableButton = Button(self, text='Export Table', command=self.generate_table)
        self.tableButton.place(x = 300, y = 270)

        self.heatmapButton = Button(self, text='Heatmap', command=self.generate_heatmap)
        self.heatmapButton.place(x = 450, y = 270)

        self.tableButton = Button(self, text='Bar Plot', command=self.generate_barplot)
        self.tableButton.place(x = 600, y = 270)

    def populate_samples_compounds(self):
        if not self.json_objects:
            print('There are no JSON files in your project directory! Forgot to select the project directory?')
            return
        compounds_tmp = []
        for sample in self.json_objects:
            self.samplesText.insert('end', sample['file']['name']+' =\n')
            for key in sample['auc'].keys():
                compounds_tmp.append(key)
        for compound in set(compounds_tmp):
            self.compoundsText.insert('end', compound+' =\n')
    
    def get_current_data(self):
        result = {}
        result['compounds'] = []
        for line in self.compoundsText.get('1.0','end').split('\n'):
            if '=' in line:
                name, custom_name = line.split('=')
                if custom_name == '':
                    custom_name = name
                result['compounds'].append((name.strip(), custom_name.strip()))

        result['samples'] = []
        for line in self.samplesText.get('1.0','end').split('\n'):
            if '=' in line:
                name, custom_name = line.split('=')
                if custom_name == '':
                    custom_name = name
                result['samples'].append((name.strip(), custom_name.strip()))
        return result
    
    def generate_table(self):
        df = self.calculate_df()
        file_path = fd.asksaveasfilename(filetypes=[('excel files', '*.xlsx'), ('tab separated value', '*.tsv')], parent=self)
        if file_path.endswith('.xlsx'):
            df.to_excel(file_path, index=False)
        elif file_path.endswith('.tsv'):
            df.to_csv(file_path, sep='\t', index=True)
    
    def generate_heatmap(self):
        visualization_window = HeatMapWindow(df=self.calculate_df())
        visualization_window.mainloop()

    def generate_barplot(self):
        visualization_window = BarPlotWindow(df=self.calculate_df())
        visualization_window.mainloop()

    def calculate_df(self):
        current_data = self.get_current_data()
        option = self.calc_option.get()
        result = []
        columns = [compound[1] for compound in current_data['compounds']]
        indices = []
        if option == 'absolute values':
            for file_name, custom_name in current_data['samples']:
                data = next((json_object for json_object in self.json_objects if json_object['file']['name'] == file_name), None)
                if data:
                    result.append([data['auc'].get(compound[0],'NA') for compound in current_data['compounds']]) 
                    indices.append(custom_name)
        else:   
            first_sample_data = next((json_object for json_object in self.json_objects if json_object['file']['name'] == current_data['samples'][0][0]), None)
            if first_sample_data:
                first_sample_aucs = [first_sample_data['auc'].get(compound[0],'NA') for compound in current_data['compounds']]
                for file_name, custom_name in current_data['samples'][1:]:
                    data = next((json_object for json_object in self.json_objects if json_object['file']['name'] == file_name), None)
                    if data:
                        tmp_result = []
                        sample_aucs = [data['auc'].get(compound[0],'NA') for compound in current_data['compounds']]
                        for reference, value in zip(first_sample_aucs, sample_aucs):
                            if isinstance(reference, int) and isinstance(value, int):
                                if option == 'relative to first sample (%)':
                                    tmp_result.append(round(value/reference*100,1))
                                elif option == 'relative to first sample (absolute values)':
                                    tmp_result.append(value-reference)
                            else:
                                tmp_result.append('NA')
                        indices.append(custom_name)
                    result.append(tmp_result)
        df = result_to_df(result, columns=columns, index=indices)
        if self.normalize.get():
            df = maximum_absolute_scaling(df)
        print('\n'+option+', normalize: '+str(self.normalize.get()))
        print(df.to_string())
        return df