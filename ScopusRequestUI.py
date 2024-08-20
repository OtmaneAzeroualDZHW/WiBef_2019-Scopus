import tkinter
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
        #api key entry field
        self.api_key = customtkinter.CTkEntry(self,placeholder_text='API Key')
        self.api_key.grid(column=1, row=0)
        #inst token entry field
        self.inst_token = customtkinter.CTkEntry(self, placeholder_text='Inst Token')
        self.inst_token.grid(column=3, row=0)


        #helper dicts for csv parameters
        self.sep_dict ={'Comma(,)':',','Semicolon (;)':';', 'Tab':'\t','Pipe (|)':'|', 'Colon (:)':':', 'Space': ' ' }
        self.linesep_dict = {'Newline (\\n)':'\n', 'Carriage Return (\\r)': '\r', 'Carriage Return + Newline (\\r\\n)':'\r\n'}
        self.quotechar_dict = {'Double Quote (")': '"', "Single Quote (')":"'", 'Backstick (`)':'`'}


        #comboboxes for selection of header names
        #todo configure placeholdertext of lable
        #todo warn user if input is longer than one char
        self.sep = customtkinter.CTkOptionMenu(self, values=list(self.sep_dict.keys()))
        self.sep.grid(column=0,row=1)

        self.linesep = customtkinter.CTkOptionMenu(self, values=list(self.linesep_dict.keys()))
        self.linesep.grid(column=2,row=1)

        self.quote = customtkinter.CTkOptionMenu(self, values=list(self.quotechar_dict.keys()))
        self.quote.grid(column=4,row=1)

        self.frstnm = customtkinter.CTkComboBox(self,state='disabled')
        self.frstnm.grid(column=0, row=2)

        self.lstnm = customtkinter.CTkComboBox(self,state='disabled')
        self.lstnm.grid(column=2, row=2)

        self.uni = customtkinter.CTkComboBox(self, state='disabled')
        self.uni.grid(column=4, row=2)






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
            master.to_search = pd.read_csv(file_path, sep=master.inputFrame.sep_dict[master.inputFrame.sep.get()], lineterminator=master.inputFrame.linesep_dict[master.inputFrame.linesep.get()], quotechar=master.inputFrame.quotechar_dict[master.inputFrame.quote.get()])
            master.tableFrame.inputSheet.set_sheet_data(master.to_search.values.tolist())
            master.tableFrame.inputSheet.set_header_data(master.to_search.columns.tolist(), redraw=True)
            master.inputFrame.frstnm.configure(state='normal', values=master.to_search.columns.tolist())
            master.inputFrame.lstnm.configure(state='normal', values=master.to_search.columns.tolist())
            master.inputFrame.uni.configure(state='normal', values=master.to_search.columns.tolist())

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

        #dataframes

        self.tosearch = pd.DataFrame()
        self.results = pd.DataFrame()
        self.empty = pd.DataFrame()

        #widgets
        self.inputFrame = InputFrame(self)
        self.inputFrame.grid(row=0, column=0)

        self.tableFrame = TableFrame(self, width=710)
        self.tableFrame.grid(row=1, column=0)

        self.buttonFrame = ButtonFrame(self)
        self.buttonFrame.grid(row=2, column=0)



app = App()
app.mainloop()