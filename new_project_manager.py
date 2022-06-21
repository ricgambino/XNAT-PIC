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

class NewProjectManager():

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

        if not self.exp_path_old:
            return
       
        self.dt.insert_row('end', [str(self.popup_prj.entry_sub.get()), str(self.exp_path_old).rsplit("/",1)[1], str(self.exp_path_old)])
        self.dt.load_table_data()

    def save_prj(self):
        save_list = self.dt.get_rows()
        if len(save_list) == 0 :
            messagebox.showerror('XNAT-PIC','No records present in the list!')
            return
        self.exp_path = filedialog.askdirectory(parent=self.popup_prj, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select the folder where to save the new project!")
        
        if not self.exp_path:
            return

        # The project already exists. Overwrite it?
        if os.path.exists((str(self.exp_path) + '//' + str(self.popup_prj.entry_prj.get())).replace('//', os.sep)):
            answer = messagebox.askyesno('XNAT-PIC', 'The project ' +(str(self.exp_path) + '//' + str(self.popup_prj.entry_prj.get())).replace('//', os.sep) +
                                        ' already exists. Overwrite it?')
            if answer is True:
                shutil.rmtree((str(self.exp_path) + '//' + str(self.popup_prj.entry_prj.get())).replace('//', os.sep))
            else:
                return

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
                
        messagebox.showinfo("XNAT-PIC", 'The new project was created!')
        self.popup_prj.destroy()



class NewSubjectManager():

    def __init__(self, root):

        # Load icon
        self.add_icon = open_image(PATH_IMAGE + "add_icon.png", 30, 30)
        
        # Define popup to create a new subject
        self.popup_sub = ttk.Toplevel()
        self.popup_sub.title("XNAT-PIC ~ Create New Subject")
        self.popup_sub.geometry("+%d+%d" % (0.5, 0.5))
        #root.eval(f'tk::PlaceWindow {str(self.popup_prj)} center')
        self.popup_sub.resizable(False, False)
        self.popup_sub.grab_set()

        # Closing window event: if it occurs, the popup must be destroyed 
        def closed_window():
            self.popup_sub.destroy()
        self.popup_sub.protocol("WM_DELETE_WINDOW", closed_window)
        
        # Select existing project 
        self.popup_sub.entry_selected_prj = ttk.Entry(self.popup_sub, state = 'disabled', width=100)
        self.popup_sub.entry_selected_prj.var = tk.StringVar()
        self.popup_sub.entry_selected_prj["textvariable"] = self.popup_sub.entry_selected_prj.var
        self.popup_sub.entry_selected_prj.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N, columnspan=2)
        
        self.popup_sub.btn_prj = ttk.Button(self.popup_sub, text = 'Select Project', command = lambda: self.select_prj(), cursor=CURSOR_HAND, style="Secondary1.TButton")
        self.popup_sub.btn_prj.grid(row=1, column=0, padx=10, pady=10, sticky=tk.N, columnspan=2)

        # Label Frame 
        self.popup_sub.frame = ttk.LabelFrame(self.popup_sub, text="New Subject", style="Popup.TLabelframe")
        self.popup_sub.frame.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

        # Existing prj      
        self.popup_sub.label_prj = ttk.Label(self.popup_sub.frame, text="Project Name")   
        self.popup_sub.label_prj.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.popup_sub.entry_prj = ttk.Entry(self.popup_sub.frame, state = tk.DISABLED, width=80)
        self.popup_sub.entry_prj.var = tk.StringVar()
        self.popup_sub.entry_prj["textvariable"] = self.popup_sub.entry_prj.var
        self.popup_sub.entry_prj.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)

        # New sub      
        self.popup_sub.label_sub = ttk.Label(self.popup_sub.frame, text="Subject Name")   
        self.popup_sub.label_sub.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.popup_sub.entry_sub = ttk.Entry(self.popup_sub.frame, width=80)
        self.popup_sub.entry_sub.var = tk.StringVar()
        self.popup_sub.entry_sub["textvariable"] = self.popup_sub.entry_sub.var
        self.popup_sub.entry_sub.grid(row=1, column=1, padx=10, pady=10, sticky=tk.N)

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
            master=self.popup_sub,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=False,
            bootstyle=PRIMARY,
            height = 10
        )
        self.dt.grid(row=3, column=0, padx=10, pady=10, sticky=tk.N, columnspan=2)

        self.popup_sub.label_add_exp = ttk.Label(self.popup_sub, text="Add New Experiment", bootstyle="inverse")   
        self.popup_sub.label_add_exp.grid(row=4, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)
        self.popup_sub.add_exp_btn = ttk.Button(self.popup_sub, image= self.add_icon, command = lambda: self.add_exp(),
                                    cursor=CURSOR_HAND, style="Popup.TButton")
        self.popup_sub.add_exp_btn.grid(row=5, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)
        ToolTip(self.popup_sub.add_exp_btn, text="Add New Experiment")
        
        # Button Save
        self.popup_sub.button_save = ttk.Button(self.popup_sub, text = 'Save', command = lambda: self.save_sub(),
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_sub.button_save.grid(row=6, column=1, padx=10, pady=5, sticky=tk.NE)

        # Button Quit
        self.popup_sub.button_quit = ttk.Button(self.popup_sub, text = 'Quit', command=closed_window, 
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_sub.button_quit.grid(row=6, column=0, padx=10, pady=5, sticky=tk.NW)

    def select_prj(self):
        self.prj_path = filedialog.askdirectory(parent=self.popup_sub, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")

        if not self.prj_path:
            return
        # Selected folder
        self.popup_sub.entry_selected_prj['state'] = 'normal'
        self.popup_sub.entry_selected_prj.delete(0, tk.END)
        self.popup_sub.entry_selected_prj.insert(0,self.prj_path)
        self.popup_sub.entry_selected_prj['state'] = 'disabled'

        # Project Name
        self.popup_sub.entry_prj['state'] = 'normal'
        self.popup_sub.entry_prj.delete(0, tk.END)
        self.popup_sub.entry_prj.insert(0,str(self.prj_path).rsplit('/', 1)[1])
        self.popup_sub.entry_prj['state'] = 'disabled'

    def add_exp(self):
        if not self.popup_sub.entry_selected_prj.get():
            messagebox.showerror('XNAT-PIC','Select a project!')
            return
        if not self.popup_sub.entry_sub.get():
            messagebox.showerror('XNAT-PIC','Insert Subject Name!')
            return
        
        self.exp_path_old = filedialog.askdirectory(parent=self.popup_sub, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select experiment directory!")

        if not self.exp_path_old:
            return
       
        self.dt.insert_row('end', [str(self.popup_sub.entry_sub.get()), str(self.exp_path_old).rsplit("/",1)[1], str(self.exp_path_old)])
        self.dt.load_table_data()

    def save_sub(self):
        save_list = self.dt.get_rows()
        if len(save_list) == 0 :
            messagebox.showerror('XNAT-PIC','No records present in the list!')
            return

        for row in save_list:
            self.exp_path_new = (str(self.prj_path) + '//' + str(row.values[0])).replace('//', os.sep)
            if os.path.exists(self.exp_path_new):
                answer = messagebox.askyesno('XNAT-PIC', 'The subject ' +  self.exp_path_new + ' already exists. Overwrite it?')

                # The subject already exists. Overwrite it?
                if answer is True:    
                    shutil.rmtree(self.exp_path_new)
                else:
                    return

            try:
                shutil.copytree(row.values[2], (self.exp_path_new + '//' + str(row.values[1])).replace('//', os.sep))
            except Exception as e:
                messagebox.showerror("XNAT-PIC", str(e))
                raise
            
            messagebox.showinfo("XNAT-PIC", 'The new subject was created!')
            self.popup_sub.destroy()


class NewExperimentManager():

    def __init__(self, root):

        # Load icon
        self.add_icon = open_image(PATH_IMAGE + "add_icon.png", 30, 30)
        
        # Define popup to create a new experiment
        self.popup_exp = ttk.Toplevel()
        self.popup_exp.title("XNAT-PIC ~ Create New Experiment")
        self.popup_exp.geometry("+%d+%d" % (0.5, 0.5))
        #root.eval(f'tk::PlaceWindow {str(self.popup_prj)} center')
        self.popup_exp.resizable(False, False)
        self.popup_exp.grab_set()

        # Closing window event: if it occurs, the popup must be destroyed 
        def closed_window():
            self.popup_exp.destroy()
        self.popup_exp.protocol("WM_DELETE_WINDOW", closed_window)
        
        # Select existing subject
        self.popup_exp.entry_selected_sub = ttk.Entry(self.popup_exp, state = 'disabled', width=100)
        self.popup_exp.entry_selected_sub.var = tk.StringVar()
        self.popup_exp.entry_selected_sub["textvariable"] = self.popup_exp.entry_selected_sub
        self.popup_exp.entry_selected_sub.grid(row=0, column=0, padx=10, pady=10, sticky=tk.N, columnspan=2)
        
        self.popup_exp.btn_sub = ttk.Button(self.popup_exp, text = 'Select Subject', command = lambda: self.select_exp(), cursor=CURSOR_HAND, style="Secondary1.TButton")
        self.popup_exp.btn_sub.grid(row=1, column=0, padx=10, pady=10, sticky=tk.N, columnspan=2)

        # Label Frame 
        self.popup_exp.frame = ttk.LabelFrame(self.popup_exp, text="New Experiment", style="Popup.TLabelframe")
        self.popup_exp.frame.grid(row=2, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

        # Existing prj      
        self.popup_exp.label_prj = ttk.Label(self.popup_exp.frame, text="Project Name")   
        self.popup_exp.label_prj.grid(row=0, column=0, padx=10, pady=10, sticky=tk.W)
        self.popup_exp.entry_prj = ttk.Entry(self.popup_exp.frame, state = tk.DISABLED, width=80)
        self.popup_exp.entry_prj.var = tk.StringVar()
        self.popup_exp.entry_prj["textvariable"] = self.popup_exp.entry_prj.var
        self.popup_exp.entry_prj.grid(row=0, column=1, padx=10, pady=10, sticky=tk.N)

        # Existing sub      
        self.popup_exp.label_sub = ttk.Label(self.popup_exp.frame, text="Subject Name")   
        self.popup_exp.label_sub.grid(row=1, column=0, padx=10, pady=10, sticky=tk.W)
        self.popup_exp.entry_sub = ttk.Entry(self.popup_exp.frame, state = tk.DISABLED, width=80)
        self.popup_exp.entry_sub.var = tk.StringVar()
        self.popup_exp.entry_sub["textvariable"] = self.popup_exp.entry_sub.var
        self.popup_exp.entry_sub.grid(row=1, column=1, padx=10, pady=10, sticky=tk.N)

        # Add the scans of the experiment
        # Listbox experiment added
        coldata = [
            {"text": "Experiment", "stretch": False},
            {"text": "Path", "stretch": False},
        ]
        rowdata = [
        ]

        self.dt = Tableview(
            master=self.popup_exp,
            coldata=coldata,
            rowdata=rowdata,
            paginated=True,
            searchable=False,
            bootstyle=PRIMARY,
            height = 10
        )
        self.dt.grid(row=3, column=0, padx=10, pady=10, sticky=tk.N, columnspan=2)

        self.popup_exp.label_add_exp = ttk.Label(self.popup_exp, text="Add New Experiment", bootstyle="inverse")   
        self.popup_exp.label_add_exp.grid(row=4, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)
        self.popup_exp.add_exp_btn = ttk.Button(self.popup_exp, image= self.add_icon, command = lambda: self.add_exp(),
                                    cursor=CURSOR_HAND, style="Popup.TButton")
        self.popup_exp.add_exp_btn.grid(row=5, column=0, padx=10, pady=5, sticky=tk.N, columnspan=2)
        ToolTip(self.popup_exp.add_exp_btn, text="Add New Experiment")
        
        # Button Save
        self.popup_exp.button_save = ttk.Button(self.popup_exp, text = 'Save', command = lambda: self.save_exp(),
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_exp.button_save.grid(row=6, column=1, padx=10, pady=5, sticky=tk.NE)

        # Button Quit
        self.popup_exp.button_quit = ttk.Button(self.popup_exp, text = 'Quit', command=closed_window, 
                                    cursor=CURSOR_HAND, style="MainPopup.TButton")
        self.popup_exp.button_quit.grid(row=6, column=0, padx=10, pady=5, sticky=tk.NW)

    def select_exp(self):
        self.sub_path = filedialog.askdirectory(parent=self.popup_exp, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select subject directory!")

        if not self.sub_path:
            return
        # Selected folder
        self.popup_exp.entry_selected_sub['state'] = 'normal'
        self.popup_exp.entry_selected_sub.delete(0, tk.END)
        self.popup_exp.entry_selected_sub.insert(0,self.sub_path)
        self.popup_exp.entry_selected_sub['state'] = 'disabled'

        # Project Name
        self.popup_exp.entry_prj['state'] = 'normal'
        self.popup_exp.entry_prj.delete(0, tk.END)
        self.popup_exp.entry_prj.insert(0,str(self.sub_path).rsplit('/', 2)[1])
        self.popup_exp.entry_prj['state'] = 'disabled'

        # Subject Name
        self.popup_exp.entry_sub['state'] = 'normal'
        self.popup_exp.entry_sub.delete(0, tk.END)
        self.popup_exp.entry_sub.insert(0,str(self.sub_path).rsplit('/', 2)[2])
        self.popup_exp.entry_sub['state'] = 'disabled'
    
    def add_exp(self):
        if not  self.popup_exp.entry_selected_sub.get():
            messagebox.showerror('XNAT-PIC','Select a subject!')
            return
        
        self.exp_path_old = filedialog.askdirectory(parent=self.popup_exp, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select experiment directory!")

        if not self.exp_path_old:
            return
       
        self.dt.insert_row('end', [str(self.exp_path_old).rsplit("/",1)[1], str(self.exp_path_old)])
        self.dt.load_table_data()

    def save_exp(self):
        save_list = self.dt.get_rows()
        if len(save_list) == 0 :
            messagebox.showerror('XNAT-PIC','No records present in the list!')
            return
        
        for row in save_list:
            self.exp_path_new = (str(self.sub_path) + '//' + str(row.values[0])).replace('//', os.sep)
            if os.path.exists(self.exp_path_new):
                answer = messagebox.askyesno('XNAT-PIC', 'The experiment ' +  self.exp_path_new + ' already exists. Overwrite it?')

                # The subject already exists. Overwrite it?
                if answer is True:    
                    shutil.rmtree(self.exp_path_new)
                else:
                    return

            try:
                shutil.copytree(row.values[1], self.exp_path_new)
            except Exception as e:
                messagebox.showerror("XNAT-PIC", str(e))
                raise
            
            messagebox.showinfo("XNAT-PIC", 'The new experiment was created!')
            self.popup_exp.destroy()

        