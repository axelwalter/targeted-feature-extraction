from tkinter import *
from tkinter import filedialog as fd
import matplotlib.pyplot as plt

class BarPlotWindow(Toplevel):
    def __init__(self, df):
        super().__init__()
        self.df = df

        self.title('Bar Plot')
        self.geometry('300x270')
        self.titleLabel = Label(self, text='title')
        self.titleLabel.place(x = 10, y = 2)
        self.titleText = Text(self)
        self.titleText.place(x = 10, y = 20, height = 25, width = 280)

        self.cmapLabel = Label(self, text='color map')
        self.cmapLabel.place(x = 10, y = 50)
        self.cmapText = Text(self)
        self.cmapText.place(x = 10, y = 68, height = 25, width = 200)
        self.cmapText.insert('end','bwr')

        self.xrotLabel = Label(self, text='x label rotation')
        self.xrotLabel.place(x = 10, y = 100)
        self.xrotText = Text(self)
        self.xrotText.place(x = 10, y = 118, height = 25, width = 50)
        self.xrotText.insert('end','30')

        self.dpiLabel = Label(self, text='image quality (dpi)')
        self.dpiLabel.place(x = 10, y = 150)
        self.dpiText = Text(self)
        self.dpiText.place(x = 10, y = 168, height = 25, width = 50)
        self.dpiText.insert('end','300')

        self.fontSizeLabel = Label(self, text='font size')
        self.fontSizeLabel.place(x = 100, y = 150)
        self.fontSizeText = Text(self)
        self.fontSizeText.place(x = 100, y = 168, height = 25, width = 50)
        self.fontSizeText.insert('end','8')

        self.save = BooleanVar()
        self.save.set(False)
        self.saveCheckButton = Checkbutton(self, text = "save image", variable = self.save)
        self.saveCheckButton.place(x =10, y = 200)

        self.tableButton = Button(self, text='Generate Bar Plot', command=self.generate_barplot)
        self.tableButton.place(x = 150, y = 230)
    
    def generate_barplot(self):
        plt.rcParams.update({'font.size': int(self.fontSizeText.get('1.0','end').strip())})
        bar = self.df.plot.bar(title=self.titleText.get('1.0','end'), rot=int(self.xrotText.get('1.0','end').strip()), ylabel='intensity AUC')
        plt.ticklabel_format(axis='y', scilimits=(0,0), style='sci', useMathText=True)
        plt.tight_layout()
        if self.save.get():
            img_path = fd.asksaveasfilename(filetypes=[('PNG', ['*.png']),('TIF', ['*.tif','*.tiff'])], parent=self)
            if img_path:
                plt.savefig(img_path, format = img_path.split('.')[-1], dpi=int(self.dpiText.get('1.0','end').strip()))
                print('SUCCESS: saved bar plot in image file: '+img_path)
        else:
            plt.show()