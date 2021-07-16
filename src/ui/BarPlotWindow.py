from tkinter import *
from tkinter import filedialog as fd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import cm

class BarPlotWindow(Toplevel):
    def __init__(self, df):
        super().__init__()
        self.df = df

        self.title('Heatmap')
        self.geometry('300x300')
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
        self.xrotLabel.place(x = 10, y = 90)
        self.xrotText = Text(self)
        self.xrotText.place(x = 10, y = 108, height = 25, width = 50)
        self.xrotText.insert('end','30')

        self.dpiLabel = Label(self, text='image quality (dpi)')
        self.dpiLabel.place(x = 10, y = 130)
        self.dpiText = Text(self)
        self.dpiText.place(x = 10, y = 148, height = 25, width = 50)
        self.dpiText.insert('end','300')

        self.fontSizeLabel = Label(self, text='font size')
        self.fontSizeLabel.place(x = 100, y = 130)
        self.fontSizeText = Text(self)
        self.fontSizeText.place(x = 100, y = 148, height = 25, width = 50)
        self.fontSizeText.insert('end','8') 

        self.save = BooleanVar()
        self.save.set(False)
        self.saveCheckButton = Checkbutton(self, text = "save image", variable = self.save)
        self.saveCheckButton.place(x =10, y = 170)

        self.tableButton = Button(self, text='Show Bar Plot', command=self.generate_barplot)
        self.tableButton.place(x = 50, y = 200)
    
    def generate_barplot(self):
        fig, ax = plt.subplots()
        ax.set_title(self.titleText.get('1.0','end'))
        plt.rcParams.update({'font.size': int(self.fontSizeText.get('1.0','end').strip())})
        self.df.plot.bar()
        ax.ticklabel_format(axis='y', scilimits=(0,0), style='sci', useMathText=True)
        plt.tight_layout()
        if self.save.get():
            img_path = fd.asksaveasfilename(filetypes=[('image', ['*.png','*tif'])], parent=self, fontsize=int(self.fontSizeText.get('1.0','end').strip()))
            if img_path:
                plt.savefig(img_path, format = img_path.split('.')[-1], dpi=int(self.dpiText.get('1.0','end').strip()))
        else:
            plt.show()