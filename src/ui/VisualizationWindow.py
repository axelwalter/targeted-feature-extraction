from tkinter import *
from tkinter import filedialog as fd
from src.extraction import maximum_absolute_scaling, result_to_df
import matplotlib.pyplot as plt
import seaborn as sns

class VisualizationWindow(Toplevel):
    def __init__(self, json_objects):
        super().__init__()
        self.json_objects = json_objects

        self.title('Data Visualization (AUC)')
        self.geometry('970x530')
        self.samplesLabel = Label(self, text='samples')
        self.samplesLabel.place(x = 10, y = 2)
        self.samplesText = Text(self)
        self.samplesText.place(x = 10, y = 20, height = 230, width = 600)

        self.compoundsLabel = Label(self, text='compounds')
        self.compoundsLabel.place(x = 620, y = 2)
        self.compoundsText = Text(self)
        self.compoundsText.place(x = 620, y = 20, height = 230, width = 340)

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
        self.tableButton.place(x = 500, y = 410+40)

        self.heatmapButton = Button(self, text='Heatmap', command=self.generate_heatmap)
        self.heatmapButton.place(x = 500, y = 270+40)

        self.tableButton = Button(self, text='Bar Plot', command=self.generate_barplot)
        self.tableButton.place(x = 500, y = 340+40)

        self.titleLabel = Label(self, text='title')
        self.titleLabel.place(x = 10+650, y = 2+270)
        self.titleText = Text(self)
        self.titleText.place(x = 10+650, y = 20+270, height = 25, width = 280)

        self.cmapLabel = Label(self, text='color map')
        self.cmapLabel.place(x = 10+650, y = 50+270)
        self.cmapText = Text(self)
        self.cmapText.place(x = 10+650, y = 68+270, height = 25, width = 200)
        self.cmapText.insert('end','bwr')

        self.xrotLabel = Label(self, text='x label rotation')
        self.xrotLabel.place(x = 10+650, y = 100+270)
        self.xrotText = Text(self)
        self.xrotText.place(x = 10+650, y = 118+270, height = 25, width = 50)
        self.xrotText.insert('end','30')

        self.yrotLabel = Label(self, text='y label rotation')
        self.yrotLabel.place(x = 100+700, y = 100+270)
        self.yrotText = Text(self)
        self.yrotText.place(x = 100+700, y = 118+270, height = 25, width = 50)
        self.yrotText.insert('end','360')

        self.dpiLabel = Label(self, text='image quality (dpi)')
        self.dpiLabel.place(x = 10+650, y = 150+270)
        self.dpiText = Text(self)
        self.dpiText.place(x = 10+650, y = 168+270, height = 25, width = 50)
        self.dpiText.insert('end','300')

        self.fontSizeLabel = Label(self, text='font size')
        self.fontSizeLabel.place(x = 100+700, y = 150+270)
        self.fontSizeText = Text(self)
        self.fontSizeText.place(x = 100+700, y = 168+270, height = 25, width = 50)
        self.fontSizeText.insert('end','8') 

        self.annotate = BooleanVar()
        self.annotate.set(False)
        self.annotateCheckButton = Checkbutton(self, text = "annotate values", variable = self.annotate)
        self.annotateCheckButton.place(x =10+650, y = 200+270)

        self.save = BooleanVar()
        self.save.set(False)
        self.saveCheckButton = Checkbutton(self, text = "save image", variable = self.save)
        self.saveCheckButton.place(x =10+650, y = 230+270)

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
        plt.rcParams.update({'font.size': int(self.fontSizeText.get('1.0','end').strip())})
        heat = sns.heatmap(self.calculate_df(), cmap=self.cmapText.get('1.0','end').strip(), annot=self.annotate.get(), square=True)
        heat.set_xticklabels(heat.get_xticklabels(), rotation = int(self.xrotText.get('1.0','end').strip()), fontsize=int(self.fontSizeText.get('1.0','end').strip()))
        heat.set_yticklabels(heat.get_yticklabels(), rotation = int(self.yrotText.get('1.0','end').strip()), fontsize=int(self.fontSizeText.get('1.0','end').strip()))
        plt.tight_layout()
        if self.save.get():
            img_path = fd.asksaveasfilename(filetypes=[('PNG', ['*.png']),('TIF', ['*.tif','*.tiff'])], parent=self)
            if img_path:
                plt.savefig(img_path, format = img_path.split('.')[-1], dpi=int(self.dpiText.get('1.0','end').strip()))
                print('SUCCESS: saved heatmap in image file: '+img_path)
        else:
            plt.show()

    def generate_barplot(self):
        plt.rcParams.update({'font.size': int(self.fontSizeText.get('1.0','end').strip())})
        bar = self.calculate_df().plot.bar(title=self.titleText.get('1.0','end'), rot=int(self.xrotText.get('1.0','end').strip()), ylabel='intensity AUC')
        plt.ticklabel_format(axis='y', scilimits=(0,0), style='sci', useMathText=True)
        plt.tight_layout()
        if self.save.get():
            img_path = fd.asksaveasfilename(filetypes=[('PNG', ['*.png']),('TIF', ['*.tif','*.tiff'])], parent=self)
            if img_path:
                plt.savefig(img_path, format = img_path.split('.')[-1], dpi=int(self.dpiText.get('1.0','end').strip()))
                print('SUCCESS: saved bar plot in image file: '+img_path)
        else:
            plt.show()

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
