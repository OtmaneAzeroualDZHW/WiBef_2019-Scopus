import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter.messagebox import showinfo
import customtkinter
#from ScopusRequests import *



#helper functions
def select_file():
    filetypes=(('csv files', '*.csv'), ('All files', '*.*'))
    filename = fd.askopenfilename(title='Select File', initialdir='C:\\Users\\userName', filetypes=filetypes)
    file_path_var.set(filename)
    showinfo(title='test', message=file_path_var.get())


# system stettings
customtkinter.set_appearance_mode('System')
customtkinter.set_default_color_theme('green')

# app frame
app = customtkinter.CTk()
app.geometry('720x480')
app.title('TestAutorenPublikationen')
app.grid_columnconfigure(4,weight=1)

# global helper varaible to store filpath

file_path_var = customtkinter.StringVar()







# ui elements

## entry fields

## call entry via .get()
api_key_entry = customtkinter.CTkEntry(app, placeholder_text='Enter your API Key')
api_key_entry.grid(row=0, column=1, padx=5, pady=5)

inst_tkn_entry = customtkinter.CTkEntry(app, placeholder_text='Enter InstToken here')
inst_tkn_entry.grid(row=0, column=3, padx=5, pady=5)

frst_nm_hdr = customtkinter.CTkEntry(app, placeholder_text='first name column', font=('Helvetica', 10))
frst_nm_hdr.grid(row= 5, column=0, padx=5, pady=5)

lst_nm_hdr = customtkinter.CTkEntry(app, placeholder_text='Enter the name of your last names column here')
lst_nm_hdr.grid(row=5, column=2, padx=5, pady=5)

uni_hdr = customtkinter.CTkEntry(app, placeholder_text='Enter the name of your uni column here')
uni_hdr.grid(row=5, column=4, padx=5, pady=5)

csv_sep = customtkinter.CTkEntry(app, placeholder_text='Enter your csv seperator char')
csv_sep.grid(row=7, column=0, padx=5, pady=5)

csv_ter = customtkinter.CTkEntry(app, placeholder_text='Enter your csv lineterminator')
csv_ter.grid(row=7, column=2, padx=5, pady=5)

csv_quote = customtkinter.CTkEntry(app, placeholder_text='Enter your csv quotechar')
csv_quote.grid(row=7, column = 4, padx=5, pady=5)


# open button
open_button = customtkinter.CTkButton(app, text='Select a File', command=select_file)
open_button.grid(row=3, column=2, padx=5, pady=5)
file_path = file_path_var.get()




# run app
app.mainloop()
