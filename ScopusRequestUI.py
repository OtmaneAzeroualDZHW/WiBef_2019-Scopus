import tkinter
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import customtkinter
import pandas as pd

import ScopusRequests
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

        # tab for displaying input csv
        self.add('input file')
        self.inputSheet = tksheet.Sheet(self.tab('input file'),width=1000)
        self.inputSheet.pack(expand=True)
        self.inputSheet.enable_bindings()

        # tab to display search results
        self.add('search results')
        self.resultSheet = tksheet.Sheet(self.tab('search results'), width=1000)
        self.resultSheet.pack(expand=True)
        self.resultSheet.enable_bindings()

        # tab to display empty results
        self.add('empty results')
        self.emptyresSheet = tksheet.Sheet(self.tab('empty results'), width=1000)
        self.emptyresSheet.pack(expand=True)
        self.emptyresSheet.enable_bindings()


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

        def start_search():
            if not master.inputFrame.inst_token.get():
                master.results, master.empty = ScopusRequests.search_scopus(master.inputFrame.api_key.get(), master.to_search, master.results, master.empty, master.inputFrame.frstnm.get(), master.inputFrame.lstnm.get(), master.inputFrame.uni.get())
            else:
                master.results, master.empty = ScopusRequests.search_scopus(master.inputFrame.api_key.get(), master.to_search, master.results,
                                             master.empty, master.inputFrame.frstnm.get(),
                                             master.inputFrame.lstnm.get(), master.inputFrame.uni.get(), master.inputFrame.inst_token.get())
            master.tableFrame.resultSheet.set_header_data(master.results.columns.tolist())
            master.tableFrame.resultSheet.set_sheet_data(master.results.values.tolist(),redraw=True)
            master.tableFrame.emptyresSheet.set_header_data(master.empty.columns.tolist())
            master.tableFrame.emptyresSheet.set_sheet_data(master.empty.values.tolist())

        def save_results():
            filetypes = [('All types (*.*)', '*.*'),('csv file (*.csv)', ('*.csv'))]
            filepath = fd.asksaveasfilename(title='Save Results as .csv', initialdir='C:\\Users\\userName', filetypes=filetypes, defaultextension=filetypes)
            master.results.to_csv(filepath, sep=master.inputFrame.sep_dict[master.inputFrame.sep.get()], lineterminator=master.inputFrame.linesep_dict[master.inputFrame.linesep.get()], quotechar=master.inputFrame.quotechar_dict[master.inputFrame.quote.get()])
            showinfo(title='saved results', message='results saved to csv')
            #todo find out why it saves funny

        def save_empty():
            filetps = ('csv files', '*.csv')
            filepath = fd.asksaveasfilename(title='Save Results as .csv', initialdir='C:\\Users\\userName',
                                            filetypes=filetps)
            master.empty.to_csv(filepath, sep=master.inputFrame.sep_dict[master.inputFrame.sep.get()], lineterminator=master.inputFrame.linesep_dict[master.inputFrame.linesep.get()], quotechar=master.inputFrame.quotechar_dict[master.inputFrame.quote.get()])
            showinfo(title='saved empties', message='empty results saved to csv')

        # open file button
        self.open_button = customtkinter.CTkButton(self, text='Select a File', command=select_file)
        self.open_button.grid(column=0)

        # start search button
        self.search_button = customtkinter.CTkButton(self, text='Start Scopus Search', command=start_search)
        self.search_button.grid(column=1)

        # save results button
        self.save_results_button = customtkinter.CTkButton(self, text='Save Search Results', command=save_results)
        self.save_results_button.grid(column=2)





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



if __name__ == "__main__":
    app = App()
    app.mainloop()