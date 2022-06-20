import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import ttkbootstrap as ttk
from accessory_functions import *
from ttkbootstrap.tableview import Tableview
from ttkbootstrap.constants import *
from ttkbootstrap.tooltip import ToolTip
import shutil

PATH_IMAGE = "images\\"
CURSOR_HAND = "hand2"
SMALL_FONT_2 = ("Calibri", 10)

class ProjectManager():

    def __init__(self, root):

        # Load icon
        self.add_icon = open_image(PATH_IMAGE + "add_icon.png", 30, 30)
        
        # Define popup to create a new project
        self.popup_prj = ttk.Toplevel()
        self.popup_prj.title("XNAT-PIC ~ Create New Project")
        self.popup_prj.geometry("+%d+%d" % (0.5, 0.5))
        #root.eval(f'tk::PlaceWindow {str(self.popup_prj)} center')
        self.popup_prj.resizable(False, False)
        self.popup_prj.grab_set()

        # Closing window event: if it occurs, the popup must be destroyed 
        def closed_window():
            self.popup_prj.destroy()
        self.popup_prj.protocol("WM_DELETE_WINDOW", closed_window)

        # Label Frame
        self.popup_prj.frame = ttk.LabelFrame(self.popup_prj, text="New Project", style="Popup.TLabelframe")
        self.popup_prj.frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

         # New prj      
        self.popup_prj.label_prj = ttk.Label(self.popup_prj.frame, text="Project Name")   
        self.popup_prj.label_prj.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.popup_prj.entry_prj = ttk.Entry(self.popup_prj.frame, width=80)
        self.popup_prj.entry_prj.var = tk.StringVar()
        self.popup_prj.entry_prj["textvariable"] = self.popup_prj.entry_prj.var
        self.popup_prj.entry_prj.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)

        # New sub      
        self.popup_prj.label_sub = ttk.Label(self.popup_prj.frame, text="Subject Name")   
        self.popup_prj.label_sub.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.popup_prj.entry_sub = ttk.Entry(self.popup_prj.frame, width=80)
        self.popup_prj.entry_sub.var = tk.StringVar()
        self.popup_prj.entry_sub["textvariable"] = self.popup_prj.entry_sub.var
        self.popup_prj.entry_sub.grid(row=1, column=1, padx=10, pady=10, sticky=tk.N)

        # Add the scans of the experiment
        # Listbox experiment added
        coldata = [
            {"text": "Subject", "stretch": False},
            {"text": "Experiment", "stretch": False},
            {"text": "Path", "stretch": False},
        ]
        rowdata = [
        ]

        self.dt = Tableview(
            master=self.popup_prj,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=False,
            bootstyle=PRIMARY,
            height = 10
        )
        self.dt.grid(row=2, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)

        self.popup_prj.label_add_exp = ttk.Label(self.popup_prj, text="Add New Experiment", bootstyle="inverse")   
        self.popup_prj.label_add_exp.grid(row=3, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)
        self.popup_prj.add_exp_btn = ttk.Button(self.popup_prj, image= self.add_icon, command = lambda: self.add_exp(),
                                    cursor=CURSOR_HAND, style="Popup.TButton")
        self.popup_prj.add_exp_btn.grid(row=4, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)
        ToolTip(self.popup_prj.add_exp_btn, text="Add New Experiment")
        
        # Button Save
        self.popup_prj.button_save = ttk.Button(self.popup_prj, text = 'Save', command = lambda: self.save_prj(), 
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_prj.button_save.grid(row=5, column=1, padx=10, pady=5, sticky=tk.NE)

        # Button Quit
        self.popup_prj.button_quit = ttk.Button(self.popup_prj, text = 'Quit', command=closed_window, 
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_prj.button_quit.grid(row=5, column=0, padx=10, pady=5, sticky=tk.NW)
    
    def add_exp(self):
        if not self.popup_prj.entry_prj.get():
            messagebox.showerror('XNAT-PIC','Insert Project Name!')
            return
        if not self.popup_prj.entry_sub.get():
            messagebox.showerror('XNAT-PIC','Insert Subject Name!')
            return
        
        self.exp_path_old = filedialog.askdirectory(parent=self.popup_prj, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select experiment directory!")
       
        self.dt.insert_row('end', [str(self.popup_prj.entry_sub.get()), str(self.exp_path_old).rsplit("/",1)[1], str(self.exp_path_old)])
        self.dt.load_table_data()

    def save_prj(self):
        save_list = self.dt.get_rows()
        if len(save_list) == 0 :
            messagebox.showerror('XNAT-PIC','No records present in the list!')
            return
        self.exp_path = filedialog.askdirectory(parent=self.popup_prj, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select the folder where to save the new project!")
        for row in save_list:
            self.exp_path_new = (str(self.exp_path) + '//' + str(self.popup_prj.entry_prj.get()) + '//' + str(row.values[0]) + '//' + str(row.values[1])).replace('//', os.sep)
            if not os.path.exists(self.exp_path_new):
                try:
                  shutil.copytree(row.values[2], self.exp_path_new)
                except Exception as e:
                    messagebox.showerror("XNAT-PIC", str(e))
                    raise
            else:
                messagebox.showerror("XNAT-PIC", 'The path: ' + self.exp_path_new + ' already exists!')
                return
                
        messagebox.showinfo("XNAT-PIC", 'The project was created!')
        self.popup_prj.destroy()



        