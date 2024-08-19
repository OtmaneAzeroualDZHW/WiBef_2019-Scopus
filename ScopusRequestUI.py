import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import customtkinter
import pandas as pd
from ScopusRequests import *
import tksheet


#todo: add start search button
#todo add third tab for rejects
#todo add tables for second and third tab
#todo make widget scaling dynamic to widowsize?
class InputFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        customtkinter.CTkLabel(self,text='Entry Fields planned here' ,fg_color='red').grid(column=0, sticky='ew')

class TableFrame(customtkinter.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)


        self.add('input file')
        self.inputSheet = tksheet.Sheet(self.tab('input file'),width=1000)
        self.inputSheet.pack(expand=True)
        self.inputSheet.enable_bindings()
        self.add('search results')


class ButtonFrame(customtkinter.CTkFrame):
    def __init__(self, master):
        super().__init__(master)

        def select_file():
            filetypes = (('csv files', '*.csv'), ('All files', '*.*'))
            file_path = fd.askopenfilename(title='Select File', initialdir='C:\\Users\\userName', filetypes=filetypes)
            df = pd.read_csv(file_path, sep=';')
            master.tableFrame.inputSheet.set_sheet_data(df.values.tolist())
            master.tableFrame.inputSheet.set_header_data(df.columns.tolist(), redraw=True)

            #add redraw

        self.open_button = customtkinter.CTkButton(self, text='Select a File', command=select_file)
        self.open_button.grid(column=0, padx=5, pady=5)


class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        #appframe
        self.title('testing class based approach and pandastable')
        self.geometry('720x480')
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        #widgets
        self.inputFrame = InputFrame(self)
        self.inputFrame.grid(row=0, column=0)

        self.tableFrame = TableFrame(self, width=710)
        self.tableFrame.grid(row=1, column=0)

        self.buttonFrame = ButtonFrame(self)
        self.buttonFrame.grid(row=2, column=0)



app = App()
app.mainloop()