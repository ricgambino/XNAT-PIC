from doctest import master
from email import message
from logging import exception
from multiprocessing.sharedctypes import Value
import shutil
from sqlite3 import Row
import tkinter as tk
from tkinter import DISABLED, END, MULTIPLE, N, NE, NW, RAISED, SINGLE, W, Menu, filedialog, messagebox
from tkinter import font
from tkinter.font import Font
from turtle import bgcolor, right, width
from unicodedata import name
from unittest import result
from winreg import REG_DWORD_LITTLE_ENDIAN
from click import option
# from PIL import Image, ImageTk
#from tkinter import ttk
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
import ttkbootstrap.themes.standard 
import tkinter.simpledialog
import time, json
import os, re
import os.path
from functools import partial
import subprocess
import platform
from progress_bar import ProgressBar
from dicom_converter import Bruker2DicomConverter
from glob import glob
import xnat
from read_visupars import read_visupars_parameters
import pyAesCrypt
from tabulate import tabulate
import datetime
import threading
from dotenv import load_dotenv
from xnat_uploader import Dicom2XnatUploader, FileUploader
import datefinder
import pydicom, webbrowser
from tkcalendar import DateEntry
from accessory_functions import *
from idlelib.tooltip import Hovertip
from multiprocessing import Pool, cpu_count
from credential_manager import CredentialManager
import pandas
from layout_style import MyStyle
import babel.numbers
from multiprocessing import Process, freeze_support
from create_objects import ObjectCreator

PATH_IMAGE = "images\\"
#PATH_IMAGE = "lib\\images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
WHITE = "#ffffff"
LIGHT_GREY = "#F1FFFE"
LIGHT_GREY_DISABLED = "#91A3B1"
AZURE = "#008ad7"
AZURE_DISABLED = "#99D0EF"
DARKER_AZURE = "#006EAC"
TEXT_BTN_COLOR = "black"
TEXT_BTN_COLOR_2 = "white"
TEXT_LBL_COLOR = "black"
BG_BTN_COLOR = "#E5EAF0"
BG_LBL_COLOR = "black"
DISABLE_LBL_COLOR = '#D3D3D3'
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
SMALL_FONT_2 = ("Calibri", 10)
SMALL_FONT_3 = ("Calibri", 12)
SMALL_FONT_4 = ("Calibri", 16)
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"
BORDERWIDTH = 3

load_dotenv()
def check_credentials():
    dir = os.getcwd().replace('\\', '/')
    head, tail = os.path.split(dir)
    if os.path.isfile(head + '/.env') == False or os.environ.get('secretKey') == '':
        CredentialManager()

class SplashScreen(tk.Toplevel):
    def __init__(self, master, timeout=1000):
        """(master, image, timeout=1000) -> create a splash screen
        from specified image file.  Keep splashscreen up for timeout
        milliseconds"""
        tk.Toplevel.__init__(self, master)
        self.main = master
        self.main.withdraw()
        self.overrideredirect(1)
        im = Image.open(PATH_IMAGE + "logo-xnat-pic.png")
        self.image = ImageTk.PhotoImage(im)
        self.after_idle(self.centerOnScreen)

        self.update()
        self.after(timeout, self.destroy)

    def centerOnScreen(self):
        self.update_idletasks()
        if (platform.system()=='Linux'):
                cmd_show_screen_resolution = subprocess.Popen("xrandr --query | grep -oG 'primary [0-9]*x[0-9]*'",\
                                                            stdout=subprocess.PIPE, shell=True)
                screen_output =str(cmd_show_screen_resolution.communicate()).split()[1]
                self.screenwidth, self.root.screenheight = re.findall("[0-9]+",screen_output)
            ###
            ###
        else :
                self.screenwidth=self.winfo_screenwidth()
                self.screenheight=self.winfo_screenheight()

        # Adjust size based on screen resolution
        self.w = int(self.screenwidth/2)
        self.h = int(self.screenheight/6)
        x = int(self.screenwidth/2)-int(self.w/2)
        y =  int(self.screenheight/2)-int(self.h/2)
        self.geometry("%dx%d+%d+%d" % (self.w, self.h, x, y))
        self.createWidgets()

    def createWidgets(self):
        # Need to fill in here
        im = Image.open(PATH_IMAGE + "logo-xnat-pic.png")
        width = int(self.w)
        wpercent = (width/float(im.size[0]))
        height = int((float(im.size[1])*float(wpercent)))
        self.my_canvas = tk.Canvas(self, height=height, width=width, bg="white", highlightthickness=1, highlightbackground=LIGHT_GREY)
        self.my_canvas.pack()
    
        # Adapt the size of the logo to the size of the canvas
        im = im.resize((self.w, height), Image.ANTIALIAS)  
        self.im = ImageTk.PhotoImage(im)
        self.my_canvas.create_image(2, 0, anchor=tk.NW, image=self.im)

    def destroy(self):
        self.main.update()
        self.main.state('zoomed')
        self.main.deiconify()
        self.withdraw()

class xnat_pic_gui():

    def __init__(self):
                   
        self.root = tk.Tk()
        self.root.state('zoomed') # The root widget is adapted to the screen size
        self.root.minsize(width=1000, height=500) # Set the minimum size of the working window
        # Define the style of the root widget
        # self.style = ttk.Style('cerculean')
        self.style_label = tk.StringVar()
        self.style_label.set('cerculean')
        self.style = MyStyle(self.style_label.get()).get_style()
        # Get the screen resolution
        if (platform.system()=='Linux'):
            cmd_show_screen_resolution = subprocess.Popen("xrandr --query | grep -oG 'primary [0-9]*x[0-9]*'",\
                                                          stdout=subprocess.PIPE, shell=True)
            screen_output =str(cmd_show_screen_resolution.communicate()).split()[1]
            self.root.screenwidth, self.root.screenheight = re.findall("[0-9]+",screen_output)
        else :
            self.root.screenwidth=self.root.winfo_screenwidth()
            self.root.screenheight=self.root.winfo_screenheight()

        # Toolbar Menu
        self.toolbar_menu = ttk.Menu(self.root)
        fileMenu = ttk.Menu(self.toolbar_menu, tearoff=0)
        fileMenu.add_separator()
        fileMenu.add_command(label="Exit", command=lambda: self.root.destroy())
        def change_theme(*args):
            self.style = MyStyle(self.style_label.get()).get_style()
            self.frame.update()

        optionMenu = ttk.Menu(self.toolbar_menu, tearoff=0)
        themes = ["lumen", "pulse", "yeti", "cerculean", "darkly", "solar", "superhero", "cyborg"]
        themeMenu = ttk.Menu(optionMenu, tearoff=0)
        themeMenu.add_command(label=themes[0], command=lambda: self.style_label.set(themes[0]))
        themeMenu.add_command(label=themes[1], command=lambda: self.style_label.set(themes[1]))
        themeMenu.add_command(label=themes[2], command=lambda: self.style_label.set(themes[2]))
        themeMenu.add_command(label=themes[3], command=lambda: self.style_label.set(themes[3]))
        themeMenu.add_command(label=themes[4], command=lambda: self.style_label.set(themes[4]))
        themeMenu.add_command(label=themes[5], command=lambda: self.style_label.set(themes[5]))
        themeMenu.add_command(label=themes[6], command=lambda: self.style_label.set(themes[6]))
        themeMenu.add_command(label=themes[7], command=lambda: self.style_label.set(themes[7]))

        optionMenu.add_cascade(label="Themes", menu=themeMenu)
        
        self.toolbar_menu.add_cascade(label="File", menu=fileMenu)
        self.toolbar_menu.add_cascade(label="Edit")
        self.toolbar_menu.add_cascade(label="Options", menu=optionMenu)
        self.root.config(menu=self.toolbar_menu)
        self.style_label.trace('w', change_theme)

        # Adjust size based on screen resolution
        self.width = self.root.screenwidth
        self.height = self.root.screenheight
        self.root.geometry("%dx%d+0+0" % (self.width, self.height))
        self.root.title("   XNAT-PIC   ~   Molecular Imaging Center   ~   University of Torino   ")
        # If you want the logo 
        self.root.iconbitmap(PATH_IMAGE + "logo3.ico")

        # Initialize the Frame widget which parent is the root widget
        self.frame = ttk.Frame(self.root)
        self.frame.pack(fill='both', expand=1)
        self.frame_label = tk.StringVar()
        self.frame_label.set('Enter')
        # Initialize the working area size
        self.my_width = int(self.width*PERCENTAGE_SCREEN)
        self.my_height = int(self.height*PERCENTAGE_SCREEN)

        # Load Accept icon
        self.logo_accept = open_image(PATH_IMAGE + "Done.png", 15, 15)
        # Load Delete icon
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 15, 15)
        # Load Edit icon
        self.logo_edit = open_image(PATH_IMAGE + "Edit.png", 15, 15)
        # Load Clear icon
        self.logo_clear = open_image(PATH_IMAGE + "delete.png", 15, 15)
        # Load open eye
        self.open_eye = open_image(PATH_IMAGE + "open_eye.png", 15, 15)
        # Load closed eye
        self.closed_eye = open_image(PATH_IMAGE + "closed_eye.png", 15, 15)

        def resize_window(*args):
            # Get the current window size
            self.width = self.root.winfo_width()
            self.height = self.root.winfo_height()
            # Update the working area size
            self.my_width = int(self.width*PERCENTAGE_SCREEN)
            self.my_height = int(self.height*PERCENTAGE_SCREEN)
            # Load Side Logo Panel
            self.panel_img = open_image(PATH_IMAGE + "logo-panel.png", self.my_width/5, self.my_height)
            self.panel_img.label = ttk.Label(self.frame, image=self.panel_img)
            self.panel_img.label.place(x=0, y=0, anchor=tk.NW, relheight=1, relwidth=0.2)
            # Load XNAT-PIC Logo
            if self.frame_label.get() in ["Enter", "Main"]:
                self.xnat_pic_logo = open_image(PATH_IMAGE + "XNAT-PIC-logo.png", 3*self.my_width/5, self.my_height/3)
                self.xnat_pic_logo.label= ttk.Label(self.frame, image=self.xnat_pic_logo)
                self.xnat_pic_logo.label.place(relx=0.3, rely=0, anchor=tk.NW, relheight=0.3, relwidth=0.8)
            # Change font according to window size
            if self.width > 1700:
                self.style.configure('TButton', font = LARGE_FONT)
                
            elif self.width > 1000 and self.width < 1700:
                self.style.configure('TButton', font = SMALL_FONT)
            
            elif self.width < 1000:
                self.style.configure('TButton', font = SMALL_FONT_2)
            # Update the frame widget
            self.frame.update()

        # Enter button handler method
        def enter_handler(*args):
            self.enter_btn.destroy() # Destroy the enter button and keep the Frame alive
            xnat_pic_gui.choose_your_action(self)
        # Enter button widget
        self.enter_btn = ttk.Button(self.frame, text="ENTER",
                             command=enter_handler,
                            cursor=CURSOR_HAND, bootstyle="primary")
        self.enter_btn.place(relx=0.6, rely=0.6, anchor=tk.CENTER, relwidth=0.2)
        
        # Call the resize_window method if the window size is changed by the user
        self.frame.bind("<Configure>", resize_window)
        self.root.mainloop()
            
    # Choose to upload files, fill in the info, convert files, process images
    def choose_your_action(self):
        
        if self.xnat_pic_logo.label.winfo_exists() == 0:
            self.xnat_pic_logo.label= ttk.Label(self.frame, image=self.xnat_pic_logo)
            self.xnat_pic_logo.label.place(relx=0.3, rely=0, anchor=tk.NW, relheight=0.3, relwidth=0.8)

        self.frame_label.set("Main")
        # Action buttons           
        # Convert files Bruker2DICOM
        self.convert_btn = ttk.Button(self.frame, text="DICOM Converter",
                                    command=partial(self.bruker2dicom_conversion, self), cursor=CURSOR_HAND)
        self.convert_btn.place(relx=0.6, rely=0.5, anchor=tk.CENTER, relwidth=0.2)
        Hovertip(self.convert_btn,'Convert images from Bruker ParaVision format to DICOM standard')
        
        # Fill in the info
        self.info_btn = ttk.Button(self.frame, text="Project Data", 
                                    command=partial(self.metadata, self), cursor=CURSOR_HAND)
        self.info_btn.place(relx=0.6, rely=0.6, anchor=tk.CENTER, relwidth=0.2)
        Hovertip(self.info_btn,'Fill in the information about the acquisition')

        # Upload files
        def upload_callback(*args):
            self.XNATUploader(self)
        self.upload_btn = ttk.Button(self.frame, text="Uploader",
                                        command=upload_callback, cursor=CURSOR_HAND)
        self.upload_btn.place(relx=0.6, rely=0.7, anchor=tk.CENTER, relwidth=0.2)
        Hovertip(self.upload_btn,'Upload DICOM images to XNAT')

        # Close button
        def close_window(*args):
            ans = messagebox.askyesno("XNAT-PIC", "The XNAT-PIC software will be closed. Are you sure?")
            if ans:
                self.root.destroy()

        self.close_btn = ttk.Button(self.frame, text="Quit", command=close_window,
                                        cursor=CURSOR_HAND)
        self.close_btn.place(relx=0.95, rely=0.9, anchor=tk.NE, relwidth=0.1)
        

    class bruker2dicom_conversion():
        
        def __init__(self, master):

            self.params = {}

            try:
                destroy_widgets([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo.label])
            except:
                pass

            # Create new frame
            master.frame_label.set("Converter")
            # Frame Title
            self.frame_title = ttk.Label(master.frame, text="XNAT-PIC Converter", style="Title.TLabel")
            self.frame_title.place(relx=0.6, rely=0.05, anchor=tk.CENTER, relwidth=0.4)

            # Label Frame for Select Converter
            self.conv_selection = ttk.LabelFrame(master.frame, text="Converter Selection")
            self.conv_selection.place(relx=0.25, rely=0.15, anchor=tk.NW)

            self.conv_flag = tk.IntVar()
            self.folder_to_convert = tk.StringVar()
            self.converted_folder = tk.StringVar()

            self.convertion_state = tk.IntVar()

            def select_folder(*args):
                # Disable the buttons
                disable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn])
                # Ask for project directory
                self.folder_to_convert.set(filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), 
                                                                title="XNAT-PIC: Select directory in Bruker ParaVision format"))
                if self.folder_to_convert.get() == '':
                    messagebox.showerror("XNAT-PIC Converter", "Please select a folder.")
                    enable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn])
                    return
                # Reset convertion_state parameter
                self.convertion_state.set(0)
                # Enable the buttons
                enable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn, self.next_btn])

            # Convert Project
            def prj_conv_handler(*args):
                self.conv_flag.set(0)
                select_folder()
            self.prj_conv_btn = ttk.Button(self.conv_selection, text="Convert Project", width=21, 
                                            command=prj_conv_handler, cursor=CURSOR_HAND)
            self.prj_conv_btn.grid(row=0, column=0, sticky=tk.NW, padx=10, pady=10)
            Hovertip(self.prj_conv_btn, "Convert a project from Bruker format to DICOM standard")

            # Convert Subject
            def sbj_conv_handler(*args):
                self.conv_flag.set(1)
                select_folder()
            self.sbj_conv_btn = ttk.Button(self.conv_selection, text="Convert Subject", width=21,
                                            command=sbj_conv_handler, cursor=CURSOR_HAND)
            self.sbj_conv_btn.grid(row=0, column=1, sticky=tk.NW, padx=10, pady=10)
            Hovertip(self.sbj_conv_btn, "Convert a subject from Bruker format to DICOM standard")

            # Convert Experiment
            def exp_conv_handler(*args):
                self.conv_flag.set(2)
                select_folder()
            self.exp_conv_btn = ttk.Button(self.conv_selection, text="Convert Experiment", width=21,
                                            command=exp_conv_handler, cursor=CURSOR_HAND)
            self.exp_conv_btn.grid(row=0, column=2, sticky=tk.NW, padx=10, pady=10)
            Hovertip(self.exp_conv_btn, "Convert an experiment from Bruker format to DICOM standard")

            # Label Frame for Checkbuttons
            self.label_frame_checkbtn = ttk.LabelFrame(master.frame, text="Options")
            self.label_frame_checkbtn.place(relx=0.95, rely=0.15, anchor=tk.NE)
            # Overwrite button
            self.overwrite_flag = tk.IntVar()
            self.btn_overwrite = ttk.Checkbutton(self.label_frame_checkbtn, text="Overwrite existing folders",                               
                                onvalue=1, offvalue=0, variable=self.overwrite_flag, style="Mini.TCheckbutton")
            self.btn_overwrite.grid(row=1, column=1, sticky=tk.NW, padx=5, pady=5)
            Hovertip(self.btn_overwrite, "Overwrite already existent folders if they occur")

            # Results button
            def add_results_handler(*args):
                self.params['results_flag'] = self.results_flag.get()
            self.results_flag = tk.IntVar()
            self.btn_results = ttk.Checkbutton(self.label_frame_checkbtn, text='Copy additional files', variable=self.results_flag,
                                onvalue=1, offvalue=0, command=add_results_handler, style="Mini.TCheckbutton")
            self.btn_results.grid(row=2, column=1, sticky=tk.NW, padx=5, pady=5)
            Hovertip(self.btn_results, "Copy additional files (results, parametric maps, graphs, ...)\ninto converted folders")

            def display_folder_tree(*args):

                if self.folder_to_convert.get() != '':
                    
                    if self.tree_to_convert.exists(0):
                        self.tree_to_convert.delete(*self.tree_to_convert.get_children())
                    main_folder = self.tree_to_convert.insert("", "end", iid=0, text=self.folder_to_convert.get().split('/')[-1], 
                                                            values=("", "", "Folder"), open=True)
                    subdir = os.listdir(self.folder_to_convert.get())
                    subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                    total_weight = 0
                    last_edit_time = ''
                    j = 1
                    for sub in subdirectories:
                        
                        if os.path.isfile(os.path.join(self.folder_to_convert.get(), sub)):
                            # Check for last edit time
                            edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_convert.get(), sub)))))
                            if last_edit_time == '' or edit_time > last_edit_time:
                                # Update the last edit time
                                last_edit_time = edit_time
                            # Check for file dimension
                            file_weight = round(os.path.getsize(os.path.join(self.folder_to_convert.get(), sub))/1024, 2)
                            total_weight += round(file_weight/1024, 2)
                            # Add the item like a file
                            self.tree_to_convert.insert(main_folder, "end", iid=j, text=sub, values=(edit_time, str(file_weight) + "KB", "File"))
                            # Update the j counter
                            j += 1

                        elif os.path.isdir(os.path.join(self.folder_to_convert.get(), sub)):
                            current_weight = 0
                            last_edit_time_lev2 = ''
                            branch_idx = j
                            level2_folder = self.tree_to_convert.insert(main_folder, "end", iid=branch_idx, text=sub, values=("", "", "Folder"), open=False)
                            j += 1
                            # Scansiona le directory interne per ottenere il tree CHIUSO
                            sub_level2 = os.listdir(os.path.join(self.folder_to_convert.get(), sub))
                            subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                            for sub2 in subdirectories2:
                                if os.path.isfile(os.path.join(self.folder_to_convert.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_convert.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2
                                    # Check for file dimension
                                    file_weight = round(os.path.getsize(os.path.join(self.folder_to_convert.get(), sub, sub2))/1024, 2)
                                    current_weight += round(file_weight/1024, 2)
                                    # Add the item like a file
                                    self.tree_to_convert.insert(level2_folder, "end", iid=j, text=sub2, values=(edit_time, str(file_weight) + "KB", "File"))
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.folder_to_convert.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_convert.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2

                                    folder_size = round(get_dir_size(os.path.join(self.folder_to_convert.get(), sub, sub2))/1024/1024, 2)
                                    current_weight += folder_size
                                    self.tree_to_convert.insert(level2_folder, "end", iid=j, text=sub2, values=(edit_time, str(folder_size) + 'MB', "Folder"))
                                    j += 1
                                
                            total_weight += current_weight
                            self.tree_to_convert.set(branch_idx, column="#1", value=last_edit_time_lev2)
                            self.tree_to_convert.set(branch_idx, column="#2", value=str(round(current_weight, 2)) + "MB")

                    # Update the fields of the parent object
                    self.tree_to_convert.set(0, column="#1", value=last_edit_time)
                    self.tree_to_convert.set(0, column="#2", value=str(round(total_weight/1024, 2)) + "GB")
            
            # Treeview Label Frame pre_convertion
            self.tree_labelframe = ttk.LabelFrame(master.frame, text="Folder to Convert")
            self.tree_labelframe.place(relx=0.25, rely=0.25, anchor=tk.NW)

            # Clear Tree buttons
            def clear_tree(*args):
                if self.tree_to_convert.exists(0):
                    self.tree_to_convert.delete(*self.tree_to_convert.get_children())
                if self.tree_converted.exists(0):
                    self.tree_converted.delete(*self.tree_converted.get_children())

            self.clear_tree_btn = ttk.Button(self.tree_labelframe, image=master.logo_clear,
                                    cursor=CURSOR_HAND, command=clear_tree, style="WithoutBack.TButton")
            self.clear_tree_btn.grid(row=0, column=1, sticky=tk.NW, padx=5, pady=5)

            # Treeview widget pre_convertion
            self.tree_to_convert = ttk.Treeview(self.tree_labelframe, selectmode='none', bootstyle='primary')
            self.tree_to_convert.grid(row=1, column=0, padx=5, pady=10, sticky=tk.NW)
            self.tree_scrollbar = ttk.Scrollbar(self.tree_labelframe, orient='vertical', command=self.tree_to_convert.yview)
            self.tree_scrollbar.grid(row=1, column=1, padx=0, pady=10, sticky=tk.NS)
            self.tree_to_convert.configure(yscrollcommand=self.tree_scrollbar.set)
            self.tree_to_convert["columns"] = ("#1", "#2", "#3")
            self.tree_to_convert.heading("#0", text="Selected folder", anchor=tk.NW)
            self.tree_to_convert.heading("#1", text="Last Update", anchor=tk.NW)
            self.tree_to_convert.heading("#2", text="Size", anchor=tk.NW)
            self.tree_to_convert.heading("#3", text="Type", anchor=tk.NW)
            self.tree_to_convert.column("#0", stretch=tk.YES, width=150)
            self.tree_to_convert.column("#1", stretch=tk.YES, width=150)
            self.tree_to_convert.column("#2", stretch=tk.YES, width=100)
            self.tree_to_convert.column("#3", stretch=tk.YES, width=100)

            def tree_thread(*args):
                progressbar_tree = ProgressBar("XNAT-PIC Converter")
                progressbar_tree.start_indeterminate_bar()
                if self.convertion_state.get() == 0:
                    t = threading.Thread(target=display_folder_tree, args=())
                elif self.convertion_state.get() == 1:
                    t = threading.Thread(target=display_converted_folder_tree, args=())
                t.start()
                while t.is_alive():
                    progressbar_tree.update_bar()
                progressbar_tree.stop_progress_bar()

            def display_converted_folder_tree(*args):

                if self.converted_folder.get() != '' and self.convertion_state.get() == 1:
                    progressbar_tree = ProgressBar("XNAT-PIC Converter")
                    progressbar_tree.start_indeterminate_bar()
                    if self.tree_converted.exists(0):
                        self.tree_converted.delete(*self.tree_converted.get_children())
                    head, tail = os.path.split(self.converted_folder.get())
                    main_folder = self.tree_converted.insert("", "end", iid=0, text=tail, 
                                                            values=("", "", "Folder"), open=True)
                    subdir = os.listdir(self.converted_folder.get())
                    subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                    total_weight = 0
                    last_edit_time = ''
                    j = 1
                    for sub in subdirectories:
                        
                        if os.path.isfile(os.path.join(self.converted_folder.get(), sub)):
                            # Check for last edit time
                            edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.converted_folder.get(), sub)))))
                            if last_edit_time == '' or edit_time > last_edit_time:
                                # Update the last edit time
                                last_edit_time = edit_time
                            # Check for file dimension
                            file_weight = round(os.path.getsize(os.path.join(self.converted_folder.get(), sub))/1024, 2)
                            total_weight += round(file_weight/1024, 2)
                            # Add the item like a file
                            self.tree_converted.insert(main_folder, "end", iid=j, text=sub, values=(edit_time, str(file_weight) + "KB", "File"))
                            # Update the j counter
                            j += 1

                        elif os.path.isdir(os.path.join(self.converted_folder.get(), sub)):
                            current_weight = 0
                            last_edit_time_lev2 = ''
                            branch_idx = j
                            level2_folder = self.tree_converted.insert(main_folder, "end", iid=branch_idx, text=sub, values=("", "", "Folder"), open=False)
                            j += 1
                            # Scansiona le directory interne per ottenere il tree CHIUSO
                            sub_level2 = os.listdir(os.path.join(self.converted_folder.get(), sub))
                            subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                            for sub2 in subdirectories2:
                                if os.path.isfile(os.path.join(self.converted_folder.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.converted_folder.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2
                                    # Check for file dimension
                                    file_weight = round(os.path.getsize(os.path.join(self.converted_folder.get(), sub, sub2))/1024, 2)
                                    current_weight += round(file_weight/1024, 2)
                                    # Add the item like a file
                                    self.tree_converted.insert(level2_folder, "end", iid=j, text=sub2, values=(edit_time, str(file_weight) + "KB", "File"))
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.converted_folder.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.converted_folder.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2

                                    folder_size = round(get_dir_size(os.path.join(self.converted_folder.get(), sub, sub2))/1024/1024, 2)
                                    current_weight += folder_size
                                    self.tree_converted.insert(level2_folder, "end", iid=j, text=sub2, values=(edit_time, str(folder_size) + 'MB', "Folder"))
                                    j += 1
                                
                            total_weight += current_weight
                            self.tree_converted.set(branch_idx, column="#1", value=last_edit_time_lev2)
                            self.tree_converted.set(branch_idx, column="#2", value=str(round(current_weight, 2)) + "MB")

                    # Update the fields of the parent object
                    self.tree_converted.set(0, column="#1", value=last_edit_time)
                    self.tree_converted.set(0, column="#2", value=str(round(total_weight/1024, 2)) + "GB")

                    progressbar_tree.stop_progress_bar()
                    enable_buttons([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn])

            # Treeview Label Frame post_convertion
            self.tree_labelframe_post = ttk.LabelFrame(master.frame, text="Converted Folder")
            self.tree_labelframe_post.place(relx=0.95, rely=0.25, anchor=tk.NE)

            self.clear_tree_btn_post = ttk.Button(self.tree_labelframe_post, image=master.logo_clear,
                                    cursor=CURSOR_HAND, command=clear_tree, style="WithoutBack.TButton")
            self.clear_tree_btn_post.grid(row=0, column=1, sticky=tk.NW, padx=5, pady=5)

            # Treeview widget post_convertion
            self.tree_converted = ttk.Treeview(self.tree_labelframe_post, selectmode='none', bootstyle='primary')
            self.tree_converted.grid(row=1, column=0, padx=5, pady=5, sticky=tk.NW)
            self.tree_scrollbarconverted = ttk.Scrollbar(self.tree_labelframe_post, orient='vertical', command=self.tree_converted.yview)
            self.tree_scrollbarconverted.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NS)
            self.tree_converted.configure(yscrollcommand=self.tree_scrollbarconverted.set)
            self.tree_converted["columns"] = ("#1", "#2", "#3")
            self.tree_converted.heading("#0", text="Selected folder", anchor=tk.NW)
            self.tree_converted.heading("#1", text="Last Update", anchor=tk.NW)
            self.tree_converted.heading("#2", text="Size", anchor=tk.NW)
            self.tree_converted.heading("#3", text="Type", anchor=tk.NW)
            self.tree_converted.column("#0", stretch=tk.YES, width=150)
            self.tree_converted.column("#1", stretch=tk.YES, width=150)
            self.tree_converted.column("#2", stretch=tk.YES, width=100)
            self.tree_converted.column("#3", stretch=tk.YES, width=100)

            self.convertion_state.trace('w', tree_thread)

            # EXIT Button 
            def exit_converter():
                result = messagebox.askquestion("XNAT-PIC Converter", "Do you want to exit?", icon='warning')
                if result == 'yes':
                    # Destroy all the existent widgets (Button, Checkbutton, ...)
                    destroy_widgets([self.conv_selection, self.exit_btn, self.label_frame_checkbtn, self.next_btn, 
                                    self.tree_labelframe, self.tree_labelframe_post, self.frame_title])
                    # Restore the main frame
                    xnat_pic_gui.choose_your_action(master)

            self.exit_btn = ttk.Button(master.frame, cursor=CURSOR_HAND,
                                     text="Back", command=exit_converter)
            # self.exit_btn.configure(command=exit_converter)
            self.exit_btn.place(relx=0.25, rely=0.9, anchor=tk.NW, relwidth=0.1)

            # NEXT Button
            def next_btn_handler(*args):
                if self.conv_flag.get() == 0:
                    self.converted_folder.set(self.folder_to_convert.get() + '_dcm')
                    self.prj_convertion(master)
     
                elif self.conv_flag.get() == 1:
                    self.converted_folder.set(os.path.join('/'.join(self.folder_to_convert.get().split('/')[:-1])  + '_dcm', 
                                                self.folder_to_convert.get().split('/')[-1]))
                    self.sbj_convertion(master)
    
                elif self.conv_flag.get() == 2:
                    self.converted_folder.set(os.path.join('/'.join(self.folder_to_convert.get().split('/')[:-2])  + '_dcm', 
                                                self.folder_to_convert.get().split('/')[-2:]))
                    self.exp_convertion(master)
                       
                else:
                    self.converted_folder.set('')

            self.next_btn = ttk.Button(master.frame, text="Next", cursor=CURSOR_HAND, command=next_btn_handler,
                                    state='disabled')
            self.next_btn.place(relx=0.95, rely=0.9, anchor=tk.NE, relwidth=0.1)
            
        def prj_convertion(self, master):

            # Check for the chosen directory
            if not self.folder_to_convert.get():
                messagebox.showerror("XNAT-PIC Converter", "The selected folder does not exists. Please select an other one.")
                return

            if glob(self.folder_to_convert.get() + '/**/**/**/**/**/2dseq', recursive=False) == []:
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not project related")
                return
            
            master.root.deiconify()
            master.root.update()
            # Define the project destination folder
            # self.prj_dst = self.folder_to_convert.get() + '_dcm'
            self.prj_dst = self.converted_folder.get()

            # Initialize converter class
            self.converter = Bruker2DicomConverter(self.params)

            def prj_converter():

                # Get the list of the subject into the project
                list_sub = os.listdir(self.folder_to_convert.get())
                # Clear list_sub from configuration files (e.g. desktop.ini)
                list_sub = [sub for sub in list_sub if sub.endswith('.ini')==False]
                # Initialize the list of conversion errors
                self.conversion_err = []
                # Loop over subjects
                for j, dir in enumerate(list_sub, 0):
                    # Show the current step on the progress bar
                    progressbar.show_step(j + 1, len(list_sub))
                    # Define the current subject path 
                    current_folder = os.path.join(self.folder_to_convert.get(), dir).replace('\\', '/')

                    if os.path.isdir(current_folder):
                        current_dst = os.path.join(self.prj_dst, dir).replace('\\', '/')
                        # Check if the current subject folder already exists
                        if os.path.isdir(current_dst):
                            # Case 1 --> The directory already exists
                            if self.overwrite_flag.get() == 1:
                                # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                                shutil.rmtree(current_dst)
                                os.makedirs(current_dst)
                            else:
                                # Existent folder without overwriting flag set to 0 --> ignore folder
                                self.conversion_err.append(current_folder.split('/')[-1])
                                continue
                        else:
                            # Case 2 --> The directory does not exist
                            if current_dst.split('/')[-1].count('_dcm') >= 1:
                                # Check to avoid already converted folders
                                self.conversion_err.append(current_folder.split('/')[-1])
                                continue
                            else:
                                # Create the new destination folder
                                os.makedirs(current_dst)

                        # Set progress bar caption to the current scan folder
                        progressbar.set_caption('Converting ' + str(current_folder.split('/')[-1]) + ' ...')

                        # Get the list of the experiments into the subject
                        list_exp = os.listdir(current_folder)
                        # Clear list_exp from configuration files (e.g. desktop.ini)
                        list_exp = [exp for exp in list_exp if exp.endswith('.ini')==False]

                        for k, exp in enumerate(list_exp):
                            print('Converting ' + str(exp))
                            exp_folder = os.path.join(current_folder, exp).replace('\\', '/')
                            exp_dst = os.path.join(current_dst, exp).replace('\\','/')
                            list_scans = self.converter.get_list_of_folders(exp_folder, exp_dst)

                            # Start the multiprocessing conversion: one pool per each scan folder
                            with Pool(processes=int(cpu_count() - 1)) as pool:
                                pool.map(self.converter.convert, list_scans)

                    # Update the current step of the progress bar
                    progressbar.update_progressbar(j, len(list_sub))
                    # Set progress bar caption 'done' to the current folder
                    progressbar.set_caption('Converting ' + str(current_folder.split('/')[-1]) + ' ...done!')
            
            start_time = time.time()

            # Start the progress bar
            progressbar = ProgressBar(bar_title='XNAT-PIC Project Converter')
            progressbar.start_determinate_bar()

            # Perform DICOM convertion through separate thread (different from the main thread)
            tp = threading.Thread(target=prj_converter, args=())
            tp.start()
            while tp.is_alive() == True:
                progressbar.update_bar(0.00001)
            else:
                progressbar.stop_progress_bar()
            
            end_time = time.time()
            print('Total elapsed time: ' + str(end_time - start_time) + ' s')

            messagebox.showinfo("XNAT-PIC Converter","The conversion of the project is done!\n\n\n\n"
                                "Exceptions:\n\n" +
                                str([str(x) for x in self.conversion_err])[1:-1])

            self.convertion_state.set(1)      
                
        def sbj_convertion(self, master):

            # Check for chosen directory
            if not self.folder_to_convert.get():
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            if glob(self.folder_to_convert.get() + '/**/**/**/**/2dseq', recursive=False) == []:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not subject related")
                return

            master.root.deiconify()
            master.root.update()
            # head, tail = os.path.split(self.folder_to_convert.get())
            # head = head + '_dcm'
            # project_foldername = tail.split('.',1)[0]
            # self.sub_dst = os.path.join(head, project_foldername).replace('\\', '/')
            self.sub_dst = self.converted_folder.get()
            print(self.converted_folder.get())

            # Start converter
            self.converter = Bruker2DicomConverter(self.params)

            # If the destination folder already exists throw exception, otherwise create the new folder
            if os.path.isdir(self.sub_dst):
                # Case 1 --> The directory already exists
                if self.overwrite_flag.get() == 1:
                    # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                    shutil.rmtree(self.sub_dst)
                    os.makedirs(self.sub_dst)
                else:
                    # Existent folder without overwriting flag set to 0 --> ignore folder
                    messagebox.showerror("XNAT-PIC Converter", "Destination folder %s already exists" % self.sub_dst)
                    self.converted_folder.set(self.sub_dst)
                    return
            else:
                # Case 2 --> The directory does not exist
                if self.sub_dst.split('/')[-1].count('_dcm') >= 1:
                    # Check to avoid already converted folders
                    messagebox.showerror("XNAT-PIC Converter", "Chosen folder %s already converted" % self.sub_dst)
                    self.converted_folder.set(os.path.join(self.folder_to_convert.get().split('/')[:-2], self.sub_dst))
                    return
                else:
                    # Create the new destination folder
                    os.makedirs(self.sub_dst)

            def sbj_converter():

                list_exp = os.listdir(self.folder_to_convert.get())
                list_exp = [exp for exp in list_exp if exp.endswith('.ini') == False]
                for k, exp in enumerate(list_exp):
                    print('Converting ' + str(exp))
                    progressbar.show_step(k + 1, len(list_exp))
                    progressbar.update_progressbar(k, len(list_exp))
                    exp_folder = os.path.join(self.folder_to_convert.get(), exp).replace('\\','/')
                    exp_dst = os.path.join(self.sub_dst, exp).replace('\\','/')

                    list_scans = self.converter.get_list_of_folders(exp_folder, exp_dst)
        
                    progressbar.set_caption('Converting ' + str(exp_folder.split('/')[-1]) + ' ...')
                    with Pool(processes=int(cpu_count() - 1)) as pool:
                        pool.map(self.converter.convert, list_scans)
                    progressbar.set_caption('Converting ' + str(exp_folder.split('/')[-1]) + ' ...done!')

            start_time = time.time()

            # Start the progress bar
            progressbar = ProgressBar(bar_title='XNAT-PIC Subject Converter')
            progressbar.start_determinate_bar()

            # Initialize and start convertion thread
            tp = threading.Thread(target=sbj_converter, args=())
            tp.start()
            while tp.is_alive() == True:
                # As long as the thread is working, update the progress bar
                progressbar.update_bar(0.0001)
            progressbar.stop_progress_bar()

            end_time = time.time()
            print('Total elapsed time: ' + str(end_time - start_time) + ' s')

            messagebox.showinfo("XNAT-PIC Converter","Done! Your subject is successfully converted.")
            self.convertion_state.set(1)  

        def exp_convertion(self, master):

            # Check for chosen directory
            if not self.folder_to_convert.get():
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            if glob(self.folder_to_convert.get() + '/**/**/**/2dseq', recursive=False) == []:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not experiment related")
                return

            master.root.deiconify()
            master.root.update()
            # head, tail = os.path.split(self.folder_to_convert.get())
            # head2, tail2 = os.path.split(head)
            # head2 = head2 + '_dcm'
            # self.exp_dst = os.path.join(head2, tail2, tail).replace('\\', '/')
            self.exp_dst = self.converted_folder.get()

            # Initialize converter class
            self.converter = Bruker2DicomConverter(self.params)

            def exp_converter():
                list_scans = self.converter.get_list_of_folders(self.folder_to_convert.get(), self.exp_dst)
    
                progressbar.set_caption('Converting ' + str(self.folder_to_convert.get().split('/')[-1]) + ' ...')
                with Pool(processes=int(cpu_count() - 1)) as pool:
                    pool.map(self.converter.convert, list_scans)
                progressbar.set_caption('Converting ' + str(self.folder_to_convert.get().split('/')[-1]) + ' ...done!')

            start_time = time.time()

            # Start the progress bar
            progressbar = ProgressBar(bar_title='XNAT-PIC Experiment Converter')
            progressbar.start_indeterminate_bar()

            # Initialize and start convertion thread
            tp = threading.Thread(target=exp_converter, args=())
            tp.start()
            while tp.is_alive() == True:
                # As long as the thread is working, update the progress bar
                progressbar.update_bar()
            progressbar.stop_progress_bar()

            end_time = time.time()
            print('Total elapsed time: ' + str(end_time - start_time) + ' s')

            messagebox.showinfo("XNAT-PIC Converter","Done! Your experiment is successfully converted.")
            self.convertion_state.set(1)
                 
    # Fill in information
    class metadata():

        def __init__(self, master):

            # Disable all buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
            
            # Choose your directory
            messagebox.showinfo("Metadata", "Select project directory!")
            self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")
            
            # If there is no folder selected, re-enable the buttons and return
            if not self.information_folder:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                return
            master.frame_label.set("Metadata")         
            self.layout_metadata(master) 

        def select_folder(self, master): 
            # Choose your directory
            self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")
            
            # If there is no folder selected, re-enable the buttons and return
            if not self.information_folder:
                return

            destroy_widgets([self.menu, self.notebook, self.label_frame_ID, self.label_frame_CV, self.modify_btn,
            self.confirm_btn, self.multiple_confirm_btn, self.hscrollbar, self.my_xscrollbar, self.my_yscrollbar, self.my_listbox, self.canvas_notebook, self.frame_title, self.name_selected_project])  

            self.layout_metadata(master)  

        def layout_metadata(self, master): 
            self.project_name = (self.information_folder.rsplit("/",1)[1])
            self.tmp_dict = {}
            self.results_dict = {}
 
            # Load the acq. date from visu_pars file for Bruker file or from DICOM files
            def read_acq_date(path): 
                match_date = ''
                for dirpath, dirnames, filenames in os.walk(path.replace('\\', '/')):
                    # Check if the visu pars file is in the scans
                    for filename in [f for f in filenames if f.startswith("visu_pars")]:
                        acq_date = read_visupars_parameters((dirpath + "\\" + filename).replace('\\', '/'))["VisuAcqDate"]
                        # Read the date
                        matches = datefinder.find_dates(str(acq_date))
                        for match in matches:
                            match_date = match.strftime('%Y-%m-%d')
                            return match_date
                    # Check if the DICOM is in the scans
                    for filename in [f for f in filenames if f.endswith(".dcm")]:
                        dataset = pydicom.dcmread((dirpath + "\\" + filename).replace('\\', '/'))
                        match_date = datetime.datetime.strptime(dataset.AcquisitionDate, '%Y%m%d').strftime('%Y-%m-%d')
                        return match_date
                return match_date
            
            # Get a list of workbook paths 
            self.path_list = []
            self.todos = {}
            todos_tmp = {}
            exp = []
            # Scan all files contained in the folder that the user has provided
            for item in os.listdir(self.information_folder):
                path = str(self.information_folder + "\\" + item).replace('\\', '/')
                # Check if the content of the project is a folder and therefore a patient or a file not to be considered
                if os.path.isdir(path):
                    # Architecture of the project: project-subject-experiment
                    for item2 in os.listdir(path):
                        path1 = str(path + "\\" + item2).replace('\\', '/')
                        if os.path.isdir(path1):
                            self.path_list.append(path1)
                            exp.append(str(item2))
                    todos_tmp = {item: exp}
                    exp = []
                self.todos.update(todos_tmp)
                todos_tmp = {}

            # Scan all files contained in the folder that the user has provided
            for path in self.path_list:
                exp = str(path).rsplit("/",3)[3]
                sub = str(path).rsplit("/",3)[2]
                prj = str(path).rsplit("/",3)[1]
                name = exp + "_" + "Custom_Variables.txt"
                keys = sub + "#" + exp
                # Check if the txt file is in folder of the patient
                # If the file exists, read le info
                if os.path.exists((path + "\\" + name).replace('\\', '/')):
                    subject_data = read_table((path + "\\" + name).replace('\\', '/'))
                    tmp_dict = {keys: subject_data}
                else:
                # If the txt file do not exist, load default value
                # Project: name of main folder
                # Subject: name of internal folders
                # Acq date: from visu_pars file for BRUKER, from DICOM from DICOM file
                #
                # Load the acq. date for BRUKER file
                    try:
                        tmp_acq_date = read_acq_date(path)
                    except Exception as e:
                        tmp_acq_date = ''
                    
                    subject_data = {"Project": prj,
                                "Subject": sub,
                                "Experiment": exp,
                                "Acquisition_date": tmp_acq_date,
                                "C_V": "",
                                "Group": "",
                                "Timepoint":"",
                                "Dose":""
                                }
                    tmp_dict = {keys: subject_data}

                self.results_dict.update(tmp_dict)

            #################### Update the frame ####################
            destroy_widgets([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo.label])
            self.frame_metadata = ttk.Frame(master.frame)
            self.frame_metadata.place(relx = 0.2, rely= 0, relheight=1, relwidth=0.8, anchor=tk.NW)
            self.frame_metadata.update()
            w_frame_old = self.frame_metadata.winfo_width()
            print(w_frame_old)
            h_frame_old = self.frame_metadata.winfo_height()
            print(h_frame_old)
            # Frame Title
            self.frame_title = ttk.Label(self.frame_metadata, text="XNAT-PIC Project Data", style='Title.TLabel')
            self.frame_title.pack(side=TOP, anchor=CENTER)
            #################### Menu ###########################
            self.menu = ttk.Menu(master.root)
            file_menu = ttk.Menu(self.menu, tearoff=0)
            file_menu.add_command(label="Select Folder", command = lambda: self.select_folder(master))
            file_menu.add_separator()
            file_menu.add_command(label="Add ID", command = lambda: self.add_ID(master))
            file_menu.add_command(label="Add Custom Variables", command = lambda: self.add_custom_variable(master))
            file_menu.add_command(label="Clear Custom Variables", command = lambda: self.clear_metadata())
            file_menu.add_separator()
            file_menu.add_command(label="Save All", command = lambda: self.save_metadata())

            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_command(label="About", command = lambda: messagebox.showinfo("XNAT-PIC","Help"))
            self.menu.add_command(label="Exit", command = lambda: self.exit_metadata(master))
            master.root.config(menu=self.menu)

            #################### Folder list #################### 
            ### Selected folder label
            self.name_selected_project = ttk.Label(self.frame_metadata, text='Selected Project: ' + self.project_name, style = "UnderTitle.TLabel")
            self.name_selected_project.pack(side=TOP, anchor=CENTER)
            self.empty_row = ttk.Label(self.frame_metadata, text='\n')
            self.empty_row.pack(side=TOP, anchor=CENTER)
            # ### Tab Notebook
            # self.canvas_notebook = tk.Canvas(self.frame_metadata)
            # h_canvas_old = int (h_frame_old/16)
            # w_canvas_old = int(w_frame_old/5)
            # self.canvas_notebook.config(height= h_canvas_old, width=w_canvas_old)
            # self.canvas_notebook.pack(side=TOP, anchor=NW, padx=20)
                       
            # self.frame_nb = ttk.LabelFrame(master.frame, text = 'Subjects')
            #self.canvas_notebook.create_window((0,0), window=self.frame_nb, anchor="nw", tags="frame")

            # # Create an object of horizontal scrollbar to scroll tab
            self.hscrollbar = ttk.Scrollbar(self.frame_metadata, orient="horizontal", command=self.canvas_notebook.xview)
            self.hscrollbar.pack(side=TOP, anchor=NW, padx=20)

            self.notebook = ttk.Notebook(master.frame) 
            self.notebook.pack()
            
            ### Tab Content is a listbox
            self.my_listbox = tk.Listbox(self.frame_metadata,selectbackground = AZURE, relief=tk.FLAT, font=SMALL_FONT_3, selectmode=SINGLE, takefocus = 0)
            self.my_listbox.place(relwidth=0.3, relheight=0.25)
            self.my_listbox.pack(side=TOP, anchor=NW, padx=20)
            
            # Yscrollbar for listbox
            self.my_yscrollbar = ttk.Scrollbar(self.my_listbox, orient="vertical")
            self.my_listbox.config(yscrollcommand = self.my_yscrollbar.set)
            self.my_yscrollbar.config(command = self.my_listbox.yview)
            self.my_yscrollbar.pack(side="right", fill="y")

            # Xscrollbar for listbox
            self.my_xscrollbar = ttk.Scrollbar(self.my_listbox, orient="horizontal")
            self.my_listbox.config(xscrollcommand = self.my_xscrollbar.set)
            self.my_xscrollbar.config(command = self.my_listbox.xview)
            self.my_xscrollbar.pack(side="bottom", fill="x")

            # Sorts the tabs first by length and then alphabetically
            for key in sorted(self.todos, key=len):
                self.notebook.add(tk.Frame(self.notebook, background="#99D0EF"), text=key, underline=0, sticky=tk.NE + tk.SW)

            self.notebook.enable_traversal()
            
            # def frame_configure(event):
            #     self.canvas_notebook.configure(scrollregion=self.canvas_notebook.bbox("all"))
            
            self.frame_nb.update()
            if self.frame_nb.winfo_reqwidth() < self.canvas_notebook.winfo_reqwidth():
                self.hscrollbar.destroy()

            #self.frame_nb.bind("<Configure>", frame_configure)
            
            #def on_resize(event):
                # self.frame_metadata.update()
                # w_frame_new = self.frame_metadata.winfo_width()
                # h_frame_new = self.frame_metadata.winfo_height()
                # h_canvas_new = int(h_frame_new/16)
                # w_canvas_new = int(w_frame_new/5)
                # self.canvas_notebook.config(height = h_canvas_old, width = w_canvas_new)


            #self.frame_metadata.bind("<Configure>", on_resize)
        #     #################### Subject form ####################
        #     # ID
        #     # Label frame for ID: folder selected, project, subject, exp and acq. date
        #     self.label_frame_ID = ttk.LabelFrame(master.frame, text="ID", padding=5)
        #     #
        #     # Scroll bar in the Label frame ID
        #     self.canvas_ID = tk.Canvas(self.label_frame_ID)
        #     self.frame_ID = tk.Frame(self.canvas_ID)

        #     self.vsb_ID = ttk.Scrollbar(self.label_frame_ID, orient="vertical", command=self.canvas_ID.yview)
        #     self.canvas_ID.configure(yscrollcommand=self.vsb_ID.set)  

        #     self.hsb_ID = ttk.Scrollbar(self.label_frame_ID, orient="horizontal", command=self.canvas_ID.xview)
        #     self.canvas_ID.configure(xscrollcommand=self.hsb_ID.set)     

        #     self.vsb_ID.pack(side="right", fill="y")
        #     self.hsb_ID.pack(side="bottom", fill="x")

        #     self.canvas_ID.pack(side="left", fill="both", expand=True)
        #     self.canvas_ID.create_window((0,0), window=self.frame_ID, anchor="nw")

        #     # Be sure that we call OnFrameConfigure on the right canvas
        #     self.frame_ID.bind("<Configure>", lambda event, canvas=self.canvas_ID: OnFrameConfigure(canvas))
        #     self.label_frame_ID.place(relx=0.50, rely=0.25, anchor=tk.NW, relwidth=0.3, relheight=0.25)
        #     def OnFrameConfigure(canvas):
        #             canvas.configure(scrollregion=canvas.bbox("all"))

        #     keys_ID = ["Folder", "Project", "Subject", "Experiment", "Acq. date"]
        #     # Entry ID 
        #     self.entries_variable_ID = []  
        #     self.entries_value_ID = []          
        #     count = 0
        #     for key in keys_ID:
        #         # Variable
        #         self.entries_variable_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=15))
        #         self.entries_variable_ID[-1].insert(0, key)
        #         self.entries_variable_ID[-1]['state'] = 'disabled'
        #         self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
        #         # Value
        #         if key == "Acq. date":
        #             self.entries_value_ID.append(ttk.Entry(self.frame_ID, state='disabled', takefocus = 0, width=20))
        #             self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=NW)
        #         else:
        #             self.entries_value_ID.append(ttk.Entry(self.frame_ID, state='disabled', takefocus = 0, width=44))
        #             self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
        #         count += 1

        #     # Calendar for acq. date
        #     self.datevar = ttk.IntVar()
        #     self.cal = ttk.DateEntry(self.frame_ID, dateformat = '%Y-%m-%d')
        #     self.cal.entry.configure(width=10)
        #     self.cal.entry['state'] = 'normal'
        #     self.cal.entry.delete(0, tk.END)
        #     self.cal.entry['state'] = 'disabled'
        #     self.cal.button['state'] = 'disabled'
        #     self.cal.grid(row=4, column=1, padx = 5, pady = 5, sticky=NE)

        #     ####################################################################
        #     # Custom Variables (CV)
        #     # Label frame for Custom Variables: group, dose, timepoint
        #     self.label_frame_CV = ttk.LabelFrame(master.frame, text="Custom Variables")
            
        #     # Scroll bar in the Label frame CV
        #     self.canvas_CV = tk.Canvas(self.label_frame_CV)
        #     self.frame_CV = tk.Frame(self.canvas_CV)

        #     self.vsb_CV = ttk.Scrollbar(self.label_frame_CV, orient="vertical", command=self.canvas_CV.yview)
        #     self.canvas_CV.configure(yscrollcommand=self.vsb_CV.set)  
        #     self.hsb_CV = ttk.Scrollbar(self.label_frame_CV, orient="horizontal", command=self.canvas_CV.xview)
        #     self.canvas_CV.configure(xscrollcommand=self.hsb_CV.set)     

        #     self.vsb_CV.pack(side="right", fill="y")     
        #     self.hsb_CV.pack(side="bottom", fill="x")
        #     self.canvas_CV.pack(side="left", fill="both", expand=True)
        #     self.canvas_CV.create_window((0,0), window=self.frame_CV, anchor="nw")

        #     # Be sure that we call OnFrameConfigure on the right canvas
        #     self.frame_CV.bind("<Configure>", lambda event, canvas=self.canvas_CV: OnFrameConfigure(canvas))
        #     self.label_frame_CV.place(relx=0.50, rely=0.52, anchor=tk.NW, relwidth=0.35, relheight=0.2)
            
        #     def OnFrameConfigure(canvas):
        #             canvas.configure(scrollregion=canvas.bbox("all"))

        #     keys_CV = ["Group", "Timepoint", "Dose"]
        #     # Entry CV  
        #     self.entries_variable_CV = []  
        #     self.entries_value_CV = []          
        #     count = 0
        #     for key in keys_CV:
        #         # Variable
        #         self.entries_variable_CV.append(ttk.Entry(self.frame_CV, takefocus = 0, width=15))
        #         self.entries_variable_CV[-1].insert(0, key)
        #         self.entries_variable_CV[-1]['state'] = 'disabled'
        #         self.entries_variable_CV[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
        #         # Value
        #         self.entries_value_CV.append(ttk.Entry(self.frame_CV, state='disabled', takefocus = 0, width=25))
        #         self.entries_value_CV[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
        #         count += 1

        #     # Group Menu
        #     OPTIONS = ["untreated", "treated"]
        #     self.selected_group = tk.StringVar()
        #     self.group_menu = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_group, width=10)
        #     self.group_menu['values'] = OPTIONS
        #     self.group_menu['state'] = 'disabled'
        #     self.group_menu.grid(row=0, column=2, padx = 5, pady = 5, sticky=W)
            
        #     # UM for dose
        #     self.OPTIONS_UM = ["Mg", "kg", "mg", "µg", "ng"]
        #     self.selected_dose = tk.StringVar()
        #     self.dose_menu = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_dose, width=10)
        #     self.dose_menu['values'] = self.OPTIONS_UM
        #     self.dose_menu['state'] = 'disabled'
        #     self.dose_menu.grid(row=2, column=2, padx = 5, pady = 5, sticky=W)

        #     # Timepoint
        #     self.OPTIONS = ["pre", "post"]
        #     self.selected_timepoint = tk.StringVar()
        #     self.timepoint_menu = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_timepoint, width=10)
        #     self.timepoint_menu['values'] = self.OPTIONS
        #     self.timepoint_menu['state'] = 'disabled'
        #     self.timepoint_menu.grid(row=1, column=2, padx = 5, pady = 5, sticky=W)

        #     self.time_entry = ttk.Entry(self.frame_CV, state='disabled', takefocus = 0, width=5)
        #     self.time_entry.grid(row=1, column=3, padx = 5, pady = 5, sticky=W)

        #     self.OPTIONS1 = ["seconds", "minutes", "hours", "days", "weeks", "months", "years"]
        #     self.selected_timepoint1 = tk.StringVar()
        #     self.timepoint_menu1 = ttk.Combobox(self.frame_CV, takefocus = 0, textvariable=self.selected_timepoint1, width=7)
        #     self.timepoint_menu1['values'] = self.OPTIONS1
        #     self.timepoint_menu1['state'] = 'disabled'
        #     self.timepoint_menu1.grid(row=1, column=4, padx = 5, pady = 5, sticky=W)

        #     #################### Load the info about the selected subject ####################
        #     def select_tab(event):
        #        tab_id = self.notebook.select()
        #        try:
        #           self.tab_name = self.notebook.tab(tab_id, "text")
        #        except:
        #            pass
        #        # Update the listbox
        #        self.my_listbox.delete(0, END)
        #        self.my_listbox.insert(tk.END, *self.todos[self.tab_name])
        #        self.load_info(master)

        #     self.notebook.bind("<<NotebookTabChanged>>", select_tab)
        #     #################### Modify the metadata ####################
        #     self.modify_btn = ttk.Button(master.frame, text="Modify", command = lambda: self.modify_metadata(), cursor=CURSOR_HAND, takefocus = 0)
        #     self.modify_btn.place(relx=0.25, rely=0.8, anchor=tk.NW, relwidth=0.18)

        #     #################### Confirm the metadata ####################
        #     self.confirm_btn = ttk.Button(master.frame, text="Confirm", command = lambda: self.confirm_metadata(), cursor=CURSOR_HAND, takefocus = 0)
        #     self.confirm_btn.place(relx=0.50, rely=0.8, anchor=tk.NW, relwidth=0.18)

        #     #################### Confirm multiple metadata ####################
        #     self.multiple_confirm_btn = ttk.Button(master.frame, text="Multiple Confirm", command = lambda: self.confirm_multiple_metadata(master), cursor=CURSOR_HAND, takefocus = 0)
        #     self.multiple_confirm_btn.place(relx=0.75, rely=0.8, anchor=tk.NW, relwidth=0.18)
                       
        # def load_info(self, master):

        #     def items_selected(event):
        #         # Clear all the combobox and the entry
        #         self.selected_group.set('')
        #         self.selected_timepoint.set('')
        #         self.selected_timepoint1.set('')
        #         self.dose_menu.set('')
        #         self.time_entry.delete(0, tk.END)

        #         disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1])

        #         # Delete entries
        #         for i in range(0, len(self.entries_value_ID)):
        #             self.entries_variable_ID[i].destroy()
        #             self.entries_value_ID[i].destroy()

        #         for i in range(0, len(self.entries_value_CV)):
        #             self.entries_variable_CV[i].destroy()
        #             self.entries_value_CV[i].destroy()
        #         """ handle item selected event
        #         """
        #         # Get selected index
        #         self.selected_index = self.my_listbox.curselection()
        #         self.selected_folder = self.tab_name + '#' + self.my_listbox.get(self.selected_index)

        #         # Load the info (ID + CV)
        #         ID = True
        #         count = 1
        #         self.entries_variable_ID = []
        #         self.entries_variable_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=15))
        #         self.entries_variable_ID[-1].insert(0, "Folder")
        #         self.entries_variable_ID[-1]['state'] = 'disabled'
        #         self.entries_variable_ID[-1].grid(row=0, column=0, padx = 5, pady = 5, sticky=W)
        #         self.entries_variable_CV = []
        #         self.entries_value_ID = []
        #         self.entries_value_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=44))
        #         self.entries_value_ID[-1].insert(0, self.selected_folder)
        #         self.entries_value_ID[-1]['state'] = 'disabled'
        #         self.entries_value_ID[-1].grid(row=0, column=1, padx = 5, pady = 5, sticky=W)
        #         self.entries_value_CV = []
        #         for k, v in dict(self.results_dict[self.selected_folder]).items():
        #             if v is None:
        #                 v = ''
        #             if k == "C_V":
        #                 ID = False
        #                 count = 0
        #             if ID:
        #                 self.entries_variable_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=15))
        #                 self.entries_variable_ID[-1].insert(0, k)
        #                 self.entries_variable_ID[-1]['state'] = 'disabled'
        #                 self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
        #                 # Value
        #                 if k == "Acquisition_date":
        #                     self.entries_value_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=20))
        #                     self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=NW)
        #                 else:
        #                     self.entries_value_ID.append(ttk.Entry(self.frame_ID, takefocus = 0, width=44))
        #                     self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
        #                 self.entries_value_ID[-1].insert(0, v)
        #                 self.entries_value_ID[-1]['state'] = 'disabled'
    
        #                 count += 1
                        
        #             else:
        #                 if k != "C_V":
        #                     self.entries_variable_CV.append(ttk.Entry(self.frame_CV, takefocus = 0, width=15))
        #                     self.entries_variable_CV[-1].insert(0, k)
        #                     self.entries_variable_CV[-1]['state'] = 'disabled'
        #                     self.entries_variable_CV[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
        #                     # Value
        #                     self.entries_value_CV.append(ttk.Entry(self.frame_CV, takefocus = 0, width=25))
        #                     self.entries_value_CV[-1].insert(0, v)
        #                     self.entries_value_CV[-1]['state'] = 'disabled'
        #                     self.entries_value_CV[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
        #                     count += 1
                
        #         self.cal.entry['state'] = 'normal'
        #         self.cal.entry.delete(0, tk.END)
        #         self.cal.entry.insert(0, self.entries_value_ID[4].get())
        #         self.cal.entry['state'] = 'disabled'
        #         self.cal.button['state'] = 'disabled'

        #     self.my_listbox.bind('<Tab>', items_selected)

        # def modify_metadata(self):
        #         # Check before confirming the data
        #     try:
        #         self.selected_folder
        #         pass
        #     except Exception as e:
        #             messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
        #             raise 

        #     # Normal entry
        #     for i in range(1, len(self.entries_value_ID)):
        #         self.entries_value_ID[i]['state'] = 'normal'

        #     for i in range(0, len(self.entries_value_CV)):
        #         self.entries_value_CV[i]['state'] = 'normal'
            
        #     self.cal.entry['state'] = 'normal'
        #     self.cal.button['state'] = 'normal'
        #     # Acquisition date has a default format in entry but you can modify date with the calendar
        #     #self.cal.configure(state="normal")
            
        #     def date_entry_selected(event):
        #         self.entries_value_ID[4]['state'] = tk.NORMAL
        #         self.entries_value_ID[4].delete(0, tk.END)
        #         self.entries_value_ID[4].insert(0, str(self.cal.entry.get()))
        #         self.entries_value_ID[4]['state'] = tk.DISABLED
        #         self.my_listbox.selection_set(self.selected_index)
            
        #     self.cal.entry.bind("<FocusOut>", date_entry_selected)

        #     #self.cal.entry.bind("<Return>", date_entry_selected)
        #     # Option menu for the group
        #     self.group_menu['state'] = 'readonly'

        #     def group_changed(event):
        #         """ handle the group changed event """
        #         self.entries_value_CV[0].delete(0, tk.END)
        #         self.entries_value_CV[0].insert(0, str(self.selected_group.get()))                    
        #         self.my_listbox.selection_set(self.selected_index)

        #     self.group_menu.bind("<<ComboboxSelected>>", group_changed)

        #     # Option menu for the dose
        #     self.dose_menu['state'] = 'readonly'

        #     def dose_changed(event):
        #         """ handle the dose changed event """
        #         dose_str = ''
        #         if self.entries_value_CV[2].get():
        #             for word in filter(str(self.entries_value_CV[2].get()).__contains__, self.OPTIONS_UM):
        #                 # If a unit of measurement is already present, replace it
        #                 dose_str = str(self.entries_value_CV[2].get()).replace(word, str(self.selected_dose.get()))
        #                 self.entries_value_CV[2].delete(0, tk.END)     
        #                 self.entries_value_CV[2].insert(0, dose_str)                    
        #                 self.my_listbox.selection_set(self.selected_index)
        #                 return
        #                     # If only the number is present, add the unit of measure
        #             dose_str = str(self.entries_value_CV[2].get()) + "-" + str(self.selected_dose.get())
        #         else:
        #             # If the entry is empty, enter only the unit of measure
        #             dose_str = str(self.selected_dose.get())

        #         self.entries_value_CV[2].delete(0, tk.END)     
        #         self.entries_value_CV[2].insert(0, dose_str)                    
        #         self.my_listbox.selection_set(self.selected_index)

        #     self.dose_menu.bind("<<ComboboxSelected>>", dose_changed)
            
        #     # Option menu for the timepoint
        #     self.timepoint_menu1['state'] = 'readonly'
        #     self.time_entry['state'] = 'normal'
        #     self.timepoint_menu['state'] = 'readonly'

        #     def timepoint_changed(event):
        #         self.entries_value_CV[1].config(state=tk.NORMAL)
        #         """ handle the timepoint changed event """
        #         if str(self.time_entry.get()) or str(self.selected_timepoint1.get()):
        #             timepoint_str = str(self.selected_timepoint.get()) + "-" + str(self.time_entry.get()) + "-" + str(self.selected_timepoint1.get())
        #         else:
        #             timepoint_str = str(self.selected_timepoint.get()) 

        #         self.my_listbox.selection_set(self.selected_index)

        #         if self.time_entry.get():
        #             try:
        #                 float(self.time_entry.get())
        #             except Exception as e: 
        #                 messagebox.showerror("XNAT-PIC", "Insert a number in the timepoint entry")

        #         self.entries_value_CV[1].delete(0, tk.END)
        #         self.entries_value_CV[1].insert(0, timepoint_str)
        #         self.entries_value_CV[1].config(state=tk.DISABLED)

        #     self.timepoint_menu.bind("<<ComboboxSelected>>", timepoint_changed)
        #     self.time_entry.bind("<<FocusOut>>", timepoint_changed)
        #     self.timepoint_menu1.bind("<<ComboboxSelected>>", timepoint_changed)

        # def check_entries(self):
        #     # Check before confirming the data
        #     try:
        #         self.selected_folder
        #         pass
        #     except Exception as e:
        #             messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
        #             raise 

        #     if not self.entries_value_ID[1].get():
        #         messagebox.showerror("XNAT-PIC", "Insert the name of the project")
        #         raise 

        #     if not self.entries_value_ID[2].get():
        #         messagebox.showerror("XNAT-PIC", "Insert the name of the subject")
        #         raise

        #     if self.entries_value_ID[4].get():
        #         try:
        #             datetime.datetime.strptime(self.entries_value_ID[4].get(), '%Y-%m-%d')
        #         except Exception as e:
        #             messagebox.showerror("XNAT-PIC", "Incorrect data format in acquisition date, should be YYYY-MM-DD")
        #             raise

        #     if self.entries_value_CV[1].get() and '-' in  self.entries_value_CV[1].get(): 
        #         if not str(self.entries_value_CV[1].get()).split('-')[0] in self.OPTIONS:
        #             messagebox.showerror("XNAT-PIC", "Select pre/post in timepoint")
        #             raise
        #         if not str(self.entries_value_CV[1].get()).split('-')[2] in self.OPTIONS1:
        #             messagebox.showerror("XNAT-PIC", "Select seconds, minutes, hours, days, weeks, months, years in timepoint")
        #             raise

        #         input_num = str(self.entries_value_CV[1].get()).split('-')[1]
        #         try:
        #             float(input_num)
        #         except Exception as e: 
        #             messagebox.showerror("XNAT-PIC", "Insert a number in timepoint between pre/post and seconds, minutes, hours..")  
        #             raise
        # # Update the values and save the values in a txt file        
        # def save_entries(self, my_key, multiple):
            
        #     if multiple == 0:
        #     # Single confirm
        #         array_ID = range(1, len(self.entries_variable_ID))
        #         array_CV = range(0, len(self.entries_variable_CV))
        #     elif multiple ==1:
        #     # Multple confirm
        #         array_ID = self.list_ID
        #         array_CV = self.list_CV
                
        #     tmp_ID = {}
        #     # Update the info in the txt file ID
        #     for i in array_ID:
        #         tmp_ID.update({self.entries_variable_ID[i].get() : self.entries_value_ID[i].get()})     
        #         self.entries_variable_ID[i]['state'] = tk.DISABLED
        #         self.entries_value_ID[i]['state'] = tk.DISABLED 
            
        #     tmp_ID.update({"C_V" : ""}) 

        #     # Update the info in the txt file CV
        #     for i in array_CV:
        #         tmp_ID.update({self.entries_variable_CV[i].get() : self.entries_value_CV[i].get()})     
        #         self.entries_variable_CV[i]['state'] = tk.DISABLED
        #         self.entries_value_CV[i]['state'] = tk.DISABLED 

        #     self.results_dict[my_key].update(tmp_ID)
           
        #     # Clear all 
        #     self.selected_group.set('')
        #     self.selected_dose.set('')
        #     self.selected_timepoint.set('')
        #     self.selected_timepoint1.set('')
        #     self.time_entry.delete(0, tk.END)
        #     self.cal.entry.delete(0, tk.END)
        #     disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.cal])
        #     # Saves the changes made by the user in the txt file
        #     substring = str(my_key).replace('#','/')
        #     index = [i for i, s in enumerate(self.path_list) if substring in s]
        #     name_txt = str(my_key).rsplit('#', 1)[1] + "_" + "Custom_Variables.txt"
        #     tmp_path = self.path_list[index[0]] + "\\" + name_txt
        #     try:
        #         with open(tmp_path.replace('\\', '/'), 'w+') as meta_file:
        #             meta_file.write(tabulate(self.results_dict[my_key].items(), headers=['Variable', 'Value']))
        #     except Exception as e: 
        #             messagebox.showerror("XNAT-PIC", "Confirmation failed: " + str(e))  
        #             raise    
        # def confirm_metadata(self):
        #     try:
        #         self.check_entries()
        #     except Exception as e: 
        #         messagebox.showerror("XNAT-PIC", "Error in checking fields" + str(e))  
        #         raise

        #     try:
        #         self.save_entries(self.selected_folder, multiple=0)
        #     except Exception as e: 
        #         messagebox.showerror("XNAT-PIC", "Error in saving" + str(e))  
        #         raise

        # # #################### Confirm multiple metadata ####################
        # def confirm_multiple_metadata(self, master):

        #     disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.my_listbox])
        #     tab_names = [self.notebook.tab(i, state='disable') for i in self.notebook.tabs()]  
                     
        #     try:
        #         self.selected_folder
        #         pass
        #     except Exception as e:
        #         enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn, self.my_listbox])
        #         messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
        #         raise

        #     messagebox.showinfo("Project Data","Select the ID fields you want to copy.")

        #     # Select the fields that you want to copy
        #     self.list_ID = []
        #     # Confirm ID
        #     def multiple_confirm_ID(row):
        #         self.list_ID.append(row)
        #         btn_multiple_confirm_ID[row].destroy()
        #         btn_multiple_delete_ID[row].destroy()
        #         count_list.pop()
        #         # If the user has finished all the selections of the ID, he moves on to the selection of CV
        #         if len(count_list) == 1:
        #             self.select_CV(master)

        #     # Delete ID
        #     def multiple_delete_ID(row):
        #         btn_multiple_confirm_ID[row].destroy()
        #         btn_multiple_delete_ID[row].destroy()
        #         count_list.pop()
        #         # If the user has finished all the selections of the ID, he moves on to the selection of CV
        #         if len(count_list) == 1:
        #             self.select_CV(master)

        #     btn_multiple_confirm_ID = []
        #     btn_multiple_delete_ID = []
        #     count_list = []
        #     for i in range(0, len(self.entries_variable_ID)):
        #         btn_multiple_confirm_ID.append(ttk.Button(self.frame_ID, image = master.logo_accept, 
        #                                         command=lambda row=i: multiple_confirm_ID(row), cursor=CURSOR_HAND))
        #         btn_multiple_confirm_ID[-1].grid(row=i, column=2, padx = 5, pady = 5, sticky=NW)
        #         btn_multiple_confirm_ID[0].destroy()
        #         btn_multiple_delete_ID.append(ttk.Button(self.frame_ID, image = master.logo_delete, 
        #                                         command=lambda row=i: multiple_delete_ID(row), cursor=CURSOR_HAND))
        #         btn_multiple_delete_ID[-1].grid(row=i, column=3, padx = 5, pady = 5, sticky=NW)
        #         btn_multiple_delete_ID[0].destroy()
        #         count_list = btn_multiple_confirm_ID.copy()
            
        # def select_CV(self, master):
        #     messagebox.showinfo("Project Data","Select the Custom Variables you want to copy.")

        #     # Select the fields that you want to copy
        #     self.list_CV = []
        #     # Confirm ID
        #     def multiple_confirm_CV(row):
        #         self.list_CV.append(row)
        #         btn_multiple_confirm_CV[row].destroy()
        #         btn_multiple_delete_CV[row].destroy()
        #         count_list.pop()
        #         # If the user has finished all the selections of the CV, he moves on to the selection of experiments
        #         if len(count_list) == 0:
        #             self.select_exp(master)

        #     # Delete ID
        #     def multiple_delete_CV(row):
        #         btn_multiple_confirm_CV[row].destroy()
        #         btn_multiple_delete_CV[row].destroy()
        #         count_list.pop()
        #         # If the user has finished all the selections of the CV, he moves on to the selection of experiments
        #         if len(count_list) == 0:
        #             self.select_exp(master)

        #     btn_multiple_confirm_CV = []
        #     btn_multiple_delete_CV = []
        #     count_list = []
        #     for i in range(0, len(self.entries_variable_CV)):
        #         btn_multiple_confirm_CV.append(ttk.Button(self.frame_CV, image = master.logo_accept, 
        #                                         command=lambda row=i: multiple_confirm_CV(row), cursor=CURSOR_HAND))
        #         btn_multiple_confirm_CV[-1].grid(row=i, column=5, padx = 5, pady = 5, sticky=NW)
        #         btn_multiple_delete_CV.append(ttk.Button(self.frame_CV, image = master.logo_delete, 
        #                                         command=lambda row=i: multiple_delete_CV(row), cursor=CURSOR_HAND))
        #         btn_multiple_delete_CV[-1].grid(row=i, column=6, padx = 5, pady = 5, sticky=NW)
        #         count_list = btn_multiple_confirm_CV.copy()
            
        # def select_exp(self, master):
        #     messagebox.showinfo("Metadata","1. Select the folders from the box on the left for which to copy the info!\n 2. Always remaining in the box on the left, press ENTER to confirm or ESC to cancel!")
        #     enable_buttons([self.my_listbox])
        #     tab_names = [self.notebook.tab(i, state='normal') for i in self.notebook.tabs()]
        #     self.my_listbox.selection_set(self.selected_index)    
        #     self.my_listbox['selectmode'] = MULTIPLE
            
        #     # Obtain the subject-experiment list to be modified
        #     self.list_tab_listbox = []
        #     def select_listbox(event):
        #         self.seltext = [self.tab_name + '#' + self.my_listbox.get(index) for index in self.my_listbox.curselection()]
        #     self.my_listbox.bind("<<ListboxSelect>>", select_listbox)

        #     def select_tab_listbox(event):
        #         tab_id = self.notebook.select()
        #         self.tab_name = self.notebook.tab(tab_id, "text")
        #         # Update the listbox
        #         self.my_listbox.delete(0, END)
        #         self.my_listbox.insert(tk.END, *self.todos[self.tab_name])
        #         self.list_tab_listbox.append(self.seltext)
                
        #     self.notebook.bind("<<NotebookTabChanged>>", select_tab_listbox)  

        #     # The user presses 'enter' to confirm 
        #     def items_selected2(event):
        #         self.list_tab_listbox.append(self.seltext)
        #         result = messagebox.askquestion("Multiple Confirm", "Are you sure you want to save data for the selected folders?\n", icon='warning')
                
        #         if result == 'yes':
        #             try:
        #                 self.check_entries()
        #             except Exception as e: 
        #                 messagebox.showerror("XNAT-PIC", "Error in checking fields" + str(e))  
        #                 raise
                
        #         for x in range(len(self.list_tab_listbox)):
        #             for y in range(len(self.list_tab_listbox[x])):
        #                 try:
        #                     self.save_entries(self.list_tab_listbox[x][y], multiple=1)
        #                 except Exception as e: 
        #                     messagebox.showerror("XNAT-PIC", "Error in saving" + str(e))  
        #                     raise
                
        #         # Clear all 
        #         self.selected_group.set('')
        #         self.selected_dose.set('')
        #         self.selected_timepoint.set('')
        #         self.selected_timepoint1.set('')
        #         self.time_entry.delete(0, tk.END)
        #         self.cal.entry.delete(0, tk.END)
        #         disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.cal])
        #         # Clear the focus and the select mode of the listbox is single
        #         enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
        #         self.my_listbox.selection_clear(0, 'end')
        #         self.my_listbox['selectmode'] = SINGLE
                

        #     self.my_listbox.bind("<Return>", items_selected2)
            
        #     # The user presses 'esc' to cancel
        #     def items_cancel(event):
        #             # Clear the focus and the select mode of the listbox is single
        #         messagebox.showinfo("Metadata","The information was not saved for the selected folders!")
        #         enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
        #         self.my_listbox.selection_clear(0, 'end')
        #         self.my_listbox['selectmode'] = SINGLE
        #     self.my_listbox.bind("<Escape>", items_cancel)
                
        # # #################### Add ID #################
        # def add_ID(self, master):
        #      # Check before confirming the data
        #     try:
        #         self.selected_folder
        #         pass
        #     except Exception as e:
        #             messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
        #             raise 
        #     # Disable btns
        #     disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
        #     # I use len(all_entries) to get nuber of next free row
        #     next_row = len(self.entries_variable_ID)
            
        #     # Add entry variable ID
        #     ent_variable = ttk.Entry(self.frame_ID, takefocus = 0, width=15)
        #     ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
        #     self.entries_variable_ID.append(ent_variable)                 

        #     # Add entry value ID in second col
        #     ent_value = ttk.Entry(self.frame_ID, takefocus = 0, width=44)
        #     ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
        #     self.entries_value_ID.append(ent_value)

        #     # Confirm
        #     def confirm_ID(next_row):
        #         pos = list(self.results_dict[self.selected_folder].keys()).index('C_V')
        #         items = list(self.results_dict[self.selected_folder].items())
        #         items.insert(pos, (self.entries_variable_ID[next_row].get(), self.entries_value_ID[next_row].get()))
        #         self.results_dict[self.selected_folder] = dict(items)
        #         state = self.entries_value_ID[1]['state']
        #         self.entries_variable_ID[next_row]['state'] = tk.DISABLED
        #         self.entries_value_ID[next_row]['state'] = state
        #         enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
        #         btn_confirm_ID.destroy()
        #         btn_reject_ID.destroy()
                 
        #     btn_confirm_ID = ttk.Button(self.frame_ID, image = master.logo_accept, 
        #                                     command=lambda: confirm_ID(next_row), cursor=CURSOR_HAND)
        #     btn_confirm_ID.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=NW)

        #     # Delete
        #     def reject_ID(next_row):
        #         enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
        #         self.entries_variable_ID[next_row].destroy()
        #         self.entries_value_ID[next_row].destroy()
        #         btn_confirm_ID.destroy()
        #         btn_reject_ID.destroy()
        #     btn_reject_ID = ttk.Button(self.frame_ID, image = master.logo_delete,  
        #                                     command=lambda: reject_ID(next_row), cursor=CURSOR_HAND)
        #     btn_reject_ID.grid(row=next_row, column=3, padx = 5, pady = 5, sticky=NW)


        # # #################### Add Custom Variable #################
        # def add_custom_variable(self, master):
        #      # Check before confirming the data
        #     try:
        #         self.selected_folder
        #         pass
        #     except Exception as e:
        #             messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
        #             raise 
        #     # Disable btns
        #     disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
        #     # I get number of next free row
        #     next_row = len(self.entries_variable_CV)
            
        #     # Add entry variable CV
        #     ent_variable = ttk.Entry(self.frame_CV, takefocus = 0, width=15)
        #     ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
        #     self.entries_variable_CV.append(ent_variable)                 

        #     # Add entry value in second col
        #     ent_value = ttk.Entry(self.frame_CV, takefocus = 0, width=25)
        #     ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
        #     self.entries_value_CV.append(ent_value)
            
        #     # Confirm
        #     def confirm_CV(next_row):
        #         if self.entries_variable_CV[next_row].get():
        #             tmp_CV = {self.entries_variable_CV[next_row].get() : self.entries_value_CV[next_row].get()}
        #             self.results_dict[self.selected_folder].update(tmp_CV) 
        #             state = self.entries_value_ID[1]['state']    
        #             self.entries_variable_CV[next_row]['state'] = tk.DISABLED
        #             self.entries_value_CV[next_row]['state'] = state
        #             enable_buttons([self.modify_btn, self.confirm_btn])
        #             btn_confirm_CV.destroy()
        #             btn_reject_CV.destroy()
        #         else:
        #             messagebox.showerror("XNAT-PIC", "Insert Custom Variable")
                     
        #     btn_confirm_CV = ttk.Button(self.frame_CV, image = master.logo_accept, 
        #                                     command=lambda: confirm_CV(next_row), cursor=CURSOR_HAND)
        #     btn_confirm_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=tk.NW)

        #     # Delete
        #     def reject_CV(next_row):
        #         self.entries_variable_CV[next_row].destroy()
        #         self.entries_value_CV[next_row].destroy()
        #         enable_buttons([self.modify_btn, self.confirm_btn])
        #         btn_confirm_CV.destroy()
        #         btn_reject_CV.destroy()
        #     btn_reject_CV = ttk.Button(self.frame_CV, image = master.logo_delete, 
        #                                     command=lambda: reject_CV(next_row), cursor=CURSOR_HAND)
        #     btn_reject_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=tk.NE)

        # # #################### Clear the metadata ####################              
        # def clear_metadata(self):
        #     # Clear all the combobox and the entry
        #     self.selected_dose.set('')
        #     self.selected_group.set('')
        #     self.selected_timepoint.set('')
        #     self.selected_timepoint1.set('')
        #     self.cal.entry.delete(0, tk.END)
        #     self.time_entry.delete(0, tk.END)

        #     state = self.entries_value_ID[1]['state']
        #     # Set empty string in all the entries
        #     for i in range(0, len(self.entries_variable_CV)):
        #             self.entries_value_CV[i]['state'] = tk.NORMAL
        #             self.entries_value_CV[i].delete(0, tk.END)
        #             self.entries_value_CV[i]['state'] = state

        # # #################### Save all the metadata ####################
        # def save_metadata(self):
        #     tmp_global_path = str(self.information_folder) + "\\" + self.project_name + '_' + 'Custom_Variables.xlsx'
        #     try:
        #         df = pandas.DataFrame.from_dict(self.results_dict, orient='index')
        #         writer = pandas.ExcelWriter(tmp_global_path.replace('\\', '/'), engine='xlsxwriter')
        #         df.to_excel(writer, sheet_name='Sheet1')
        #         writer.save()
        #         messagebox.showinfo("XNAT-PIC", "File saved successfully")
        #     except Exception as e: 
        #             messagebox.showerror("XNAT-PIC", "Save failed: " + str(e))  
        #             raise
            
        # # #################### Exit the metadata ####################
        # def exit_metadata(self, master):
        #     result = messagebox.askquestion("Exit", "Do you want to exit?", icon='warning')
        #     if result == 'yes':
        #         destroy_widgets([self.menu, self.notebook, self.label_frame_ID, self.label_frame_CV, self.modify_btn,
        #         self.confirm_btn, self.multiple_confirm_btn, self.hscrollbar, self.my_xscrollbar, self.my_yscrollbar, self.my_listbox, self.canvas_notebook, self.frame_title, self.name_selected_project])

        #         xnat_pic_gui.choose_your_action(master)
    
    class XNATUploader():

        def __init__(self, master):
            
            # Disable main frame buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

            # Start with a popup to get credentials
            login_popup = tk.Toplevel(background=WHITE)
            login_popup.title("XNAT-PIC ~ Login")
            login_popup.geometry("%dx%d+%d+%d" % (410, 240, master.my_width/3, master.my_height/4))
            login_popup.resizable(False, False)

            # Closing window event: if it occurs, the popup must be destroyed and the main frame buttons must be enabled
            def closed_window():
                login_popup.destroy()
                #Enable all buttons
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
            login_popup.protocol("WM_DELETE_WINDOW", closed_window)

            # Credentials Label Frame
            login_popup.cred_frame = ttk.LabelFrame(login_popup, text="Credentials", style="Popup.TLabelframe")
            login_popup.cred_frame.grid(row=1, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)

            # XNAT ADDRESS      
            login_popup.label_address = ttk.Label(login_popup.cred_frame, text="XNAT web address")   
            login_popup.label_address.grid(row=1, column=0, padx=2, pady=2, sticky=tk.E)
            login_popup.entry_address = ttk.Entry(login_popup.cred_frame, width=25)
            login_popup.entry_address.var = tk.StringVar()
            login_popup.entry_address["textvariable"] = login_popup.entry_address.var
            login_popup.entry_address.grid(row=1, column=1, padx=2, pady=2)

            def enable_address_modification(*args):
                if login_popup.modify_address_flag.get() == 1:
                    login_popup.entry_address.configure(state='normal')
                else:
                    login_popup.entry_address.configure(state='disabled')
            login_popup.modify_address_flag = tk.IntVar()
            login_popup.modify_address_btn = ttk.Checkbutton(login_popup.cred_frame, text="Change address", state='disabled', 
                                                            style="Popup.TCheckbutton",
                                                            onvalue=1, offvalue=0, variable=login_popup.modify_address_flag)
            login_popup.modify_address_btn.grid(row=1, column=2, padx=2, pady=2, sticky=tk.W)
            login_popup.modify_address_flag.trace('w', enable_address_modification)
           
            # XNAT USER 
            login_popup.label_user = ttk.Label(login_popup.cred_frame, text="Username")
            login_popup.label_user.grid(row=2, column=0, padx=1, ipadx=1, sticky=tk.E)

            def get_list_of_users():
                # Get the list of registered and stored users
                try:
                    home = os.path.expanduser("~")
                    # Define the encrypted file path
                    encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                    # Define the decrypted file path
                    decrypted_file = os.path.join(home, "Documents", ".XNAT_login_file00000.txt")
                    # Decrypt the encrypted file
                    pyAesCrypt.decryptFile(encrypted_file, decrypted_file, os.environ.get('secretKey'), 
                                            int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
                    # Open the decrypted file
                    with open(decrypted_file, 'r') as credentials_file:
                        # Read the data
                        data = json.load(credentials_file)
                        # Get the list of users
                        list_of_users = list(data.keys())
                    # Clear the 'data' variable
                    data = ''
                    # Remove the decrypted file
                    os.remove(decrypted_file)
                    return list_of_users
                except Exception as error:
                    return []

            def get_credentials(*args):
                if login_popup.entry_user.get() != '':
                    if login_popup.entry_user.get() in login_popup.combo_user['values']:
                        # Load stored credentials
                        self.load_saved_credentials(login_popup)
                        # Disable the button to modify the web address
                        login_popup.entry_address.configure(state='disabled')
                        # Enable the 'Change address' button
                        login_popup.modify_address_btn.configure(state='normal')
                        # Enable the 'Remember me' button
                        login_popup.btn_remember.configure(state='normal')
                        # Enable the 'Show password' toggle button
                        login_popup.toggle_btn.configure(state='normal')
                    else:
                        # Enable the 'Remember me' button
                        login_popup.btn_remember.configure(state='normal')
                else:
                    # Disable the 'Remember me' button
                    login_popup.btn_remember.configure(state='disabled')
                    # Reset 'Remember me' button
                    login_popup.remember.set(0)
                    # Disable the 'Show password' toggle button
                    login_popup.toggle_btn.configure(state='disabled')
                    # # Reset address and password fields
                    # login_popup.entry_psw.var.set('')
                    # login_popup.entry_address.var.set('')

            login_popup.entry_user = tk.StringVar()
            login_popup.combo_user = ttk.Combobox(login_popup.cred_frame, font=SMALL_FONT_2, takefocus=0, textvariable=login_popup.entry_user, 
                                                    state='normal', width=19, style="Popup.TCombobox")
            login_popup.combo_user['values'] = get_list_of_users()
            login_popup.entry_user.trace('w', get_credentials)
            login_popup.combo_user.grid(row=2, column=1, padx=2, pady=2)

            # XNAT PASSWORD 
            login_popup.label_psw = ttk.Label(login_popup.cred_frame, text="Password")
            login_popup.label_psw.grid(row=3, column=0, padx=1, ipadx=1, sticky=tk.E)

            # Show/Hide the password
            def toggle_password():
                if login_popup.entry_psw.cget('show') == '':
                    login_popup.entry_psw.config(show='*')
                    login_popup.toggle_btn.config(image=master.open_eye)
                else:
                    if tkinter.simpledialog.askstring("PIN", "Enter PIN: ", show='*', parent=login_popup.cred_frame) == os.environ.get('secretPIN'):
                        login_popup.entry_psw.config(show='')
                        login_popup.toggle_btn.config(image=master.closed_eye)
                    else:
                        messagebox.showerror("XNAT-PIC Uploader", "Error! The PIN code does not correspond")
                        enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
            
            login_popup.entry_psw = ttk.Entry(login_popup.cred_frame, show="*", width=25)
            login_popup.entry_psw.var = tk.StringVar()
            login_popup.entry_psw["textvariable"] = login_popup.entry_psw.var
            login_popup.entry_psw.grid(row=3, column=1, padx=2, pady=2)
            login_popup.toggle_btn = ttk.Button(login_popup.cred_frame, image= master.open_eye,
                                                command=toggle_password, state='disabled', 
                                                cursor=CURSOR_HAND, style="Popup.TButton")
            login_popup.toggle_btn.grid(row=3, column=2, padx=2, pady=2, sticky=tk.W)

            # Forgot password button
            def forgot_psw(*args):
                webbrowser.open("http://130.192.212.48:8080/app/template/ForgotLogin.vm#!", new=1)

            login_popup.forgot_psw = ttk.Label(login_popup.cred_frame, text="Forgot password", style="Popup.TLabel", 
                                            cursor=CURSOR_HAND)
            login_popup.forgot_psw.grid(row=4, column=1, padx=1, ipadx=1)
            login_popup.forgot_psw.bind("<Button-1>", forgot_psw)

            # Register button
            def register(*args):
                webbrowser.open("http://130.192.212.48:8080/app/template/Register.vm#!", new=1)

            login_popup.register_btn = ttk.Label(login_popup.cred_frame, text="Register", style="Popup.TLabel",
                                            cursor=CURSOR_HAND)
            login_popup.register_btn.grid(row=4, column=2, padx=2, pady=2, sticky=tk.W)
            login_popup.register_btn.bind("<Button-1>", register)

            # Label Frame for HTTP buttons
            login_popup.label_frame_http = ttk.LabelFrame(login_popup, text="Options", style="Popup.TLabelframe")
            login_popup.label_frame_http.grid(row=0, column=0, padx=10, pady=5, sticky=tk.E+tk.W+tk.N+tk.S, columnspan=2)
            
            # HTTP/HTTPS 
            login_popup.http = tk.StringVar()
            login_popup.button_http = ttk.Radiobutton(login_popup.label_frame_http, text=" http:// ", variable=login_popup.http, 
                                                        value="http://", style="Popup.TRadiobutton")
            login_popup.button_http.grid(row=1, column=0, sticky=tk.E, padx=2, pady=2)
            login_popup.button_https = ttk.Radiobutton(login_popup.label_frame_http, text=" https:// ", variable=login_popup.http, 
                                                        value="https://", style="Popup.TRadiobutton")
            login_popup.button_https.grid(row=1, column=1, padx=2, pady=2, sticky=tk.E)
            login_popup.http.set("http://")

            # SAVE CREDENTIALS CHECKBUTTON
            login_popup.remember = tk.IntVar()
            login_popup.btn_remember = ttk.Checkbutton(login_popup.cred_frame, text="Remember me", variable=login_popup.remember, state='disabled',
                                                        onvalue=1, offvalue=0, style="Popup.TCheckbutton")
            login_popup.btn_remember.grid(row=2, column=2, padx=2, pady=2, sticky=tk.W)

            # CONNECTION
            login_popup.button_connect = ttk.Button(login_popup, text="Login", style="MainPopup.TButton",
                                                    command=partial(self.login, login_popup, master))
            login_popup.button_connect.grid(row=2, column=1, padx=5, pady=5, sticky=tk.E)

            # QUIT button
            def quit_event():
                login_popup.destroy()
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

            login_popup.button_quit = ttk.Button(login_popup, text='Quit', command=quit_event, style="MainPopup.TButton")
            login_popup.button_quit.grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)

        def load_saved_credentials(self, popup):
            # REMEMBER CREDENTIALS
            try:
                home = os.path.expanduser("~")
                # Define the encrypted file path
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                # Define the decrypted file path
                decrypted_file = os.path.join(home, "Documents", ".XNAT_login_file00000.txt")
                # Decrypt the file
                pyAesCrypt.decryptFile(encrypted_file, decrypted_file, os.environ.get('secretKey'), 
                                        int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
                # Open the decrypted file in 'read' mode
                with open(decrypted_file, 'r') as credentials_file:
                    # Read the data
                    data = json.load(credentials_file)
                    # Fill the empty fields
                    popup.entry_address.var.set(data[popup.entry_user.get()]['Address'])
                    popup.entry_user.set(data[popup.entry_user.get()]['Username'])
                    popup.entry_psw.var.set(data[popup.entry_user.get()]['Password'])
                # Clear the 'data' variable
                data = ''
                # Remove the decrypted file
                os.remove(decrypted_file)
                # Check the 'Remember me' button
                popup.btn_remember.config(state='normal')
                popup.remember.set(1)
            except Exception as error:
                messagebox.showerror("XNAT-PIC Login", "Error! The user information is not available, or you don't have access to it.")

        def login(self, popup, master):

            # Retireve the complete address
            popup.entry_address_complete = popup.http.get() + popup.entry_address.var.get()

            home = os.path.expanduser("~")
            try:
                # Start a new xnat session
                self.session = xnat.connect(
                    popup.entry_address_complete,
                    popup.entry_user.get(),
                    popup.entry_psw.var.get(),
                )
                # Check if the 'Remember Button' is checked
                if popup.remember.get() == True:
                    # Save credentials
                    self.save_credentials(popup)
                else:
                    # Try to remove the existent encrypted file
                    try:
                        os.remove(
                            os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                        )
                    except FileNotFoundError:
                        pass
                popup.destroy()
                # Go to the overall uploader
                self.overall_uploader(master)

            except Exception as error:
                messagebox.showerror("Error!", error)
                popup.destroy()
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

        def save_credentials(self, popup):

            home = os.path.expanduser("~")

            if os.path.exists(os.path.join(home, "Documents")):
                
                # Define the path of the encrypted file
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                # Define the path of the decrypted file
                decrypted_file = os.path.join(home, "Documents", ".XNAT_login_file00000.txt")

                if os.path.isfile(encrypted_file):

                    # Decrypt the encrypted file exploiting the secret key
                    pyAesCrypt.decryptFile(encrypted_file, decrypted_file, os.environ.get('secretKey'), 
                                            int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
                    # Open decrypted file and read the data stored
                    with open(decrypted_file, 'r') as credentials_file:
                        data = json.load(credentials_file)
                    # Update the already stored data with the current session parameters
                    data[str(popup.entry_user.get())] = {
                                "Address": popup.entry_address.var.get(),
                                "Username": popup.entry_user.get(),
                                "Password": popup.entry_psw.var.get(),
                                "HTTP": popup.http.get()
                        }
                    # Remove the decrypted file
                    os.remove(decrypted_file)
                
                else:
                    # Define empty dictionary for credentials
                    data = {}
                    # Add the current credentials to the dictionary
                    data[str(popup.entry_user.get())] = {
                                "Address": popup.entry_address.var.get(),
                                "Username": popup.entry_user.get(),
                                "Password": popup.entry_psw.var.get(),
                                "HTTP": popup.http.get()
                        }

                # Define the path of the file
                file = os.path.join(home, "Documents", ".XNAT_login_file.txt")
                # Open the file to write in the data to be stored
                with open(file, 'w+') as login_file:
                    json.dump(data, login_file)
                # Clear data variable
                data = {}
                # Encrypt the file
                pyAesCrypt.encryptFile(file, encrypted_file, os.environ.get('secretKey'), 
                                        int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2')))
                # Remove the file
                os.remove(file)

        def check_project_name(self, *args):

            if self.entry_prjname.get() != '':
                # Method to check about project name
                if self.entry_prjname.get() in self.OPTIONS:
                    # Case 1 --> The project already exists
                    messagebox.showerror(
                        "XNAT-PIC Uploader",
                        "Project ID %s already exists! Please, enter a different project ID."
                        % self.entry_prjname.get(),
                    )
                else:
                    # Case 2 --> The project does not exist yet
                    result = messagebox.askyesno("XNAT-PIC Uploader", "A new project will be created. Are you sure?")
                    if result is False:
                            return
                    self.prj.set(self.entry_prjname.get())
                    disable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])
                    try:
                        project = self.session.classes.ProjectData(
                                       name=self.prj.get(), parent=self.session)
                    except exception as e:
                        messagebox.showerror("Error!", str(e))
                        
                    self.session.clearcache()
                    # Refresh the list of projects
                    self.OPTIONS = self.session.projects
                    messagebox.showinfo('XNAT-PIC Uploader', 'A new project is created.')                 
                    
            else:
                messagebox.showerror("XNAT-PIC Uploader", "Please enter a project ID.")

        def check_subject_name(self, *args):

            if self.entry_subname.get() != '':
                # Check if the project already exists
                if self.prj.get() in self.OPTIONS:
                    # Method to check about project name
                    if self.entry_subname.get() in self.OPTIONS2:
                        # Case 1 --> The project already exists
                        messagebox.showerror(
                            "XNAT-PIC Uploader!",
                            "Subject %s already exists! Please, enter a different subject ID"
                            % self.entry_subname.get(),
                        )
                    else:
                        # Case 2 --> The project does not exist yet
                        try:
                            result = messagebox.askyesno("XNAT-PIC Uploader", "A new subject will be created into %s. Are you sure?"
                                                        % self.prj.get())
                            if result is False:
                                return
                            self.sub.set(self.entry_subname.get())
                            disable_buttons([self.entry_subname, self.confirm_new_sub, self.reject_new_sub])

                            try:
                                # Try to retrieve the project
                                project = self.session.projects[self.prj.get()]
                            except:
                                # otherwise a new one will be created
                                messagebox.showwarning('XNAT-PIC Uploader', 'The project you are trying to retrieve does not exist.'
                                                                            'A new project will be created.')
                                project = self.session.classes.ProjectData(
                                                    name=self.prj.get(), parent=self.session)
                                # Clear cache to refresh the catalog
                                self.session.clearcache()
                            # Create new subject   
                            subject = self.session.classes.SubjectData(parent=project, label=self.sub.get())
                            # Clear cache to refresh the catalog
                            self.session.clearcache()
                            # Refresh the list of subjects
                            self.OPTIONS2 = self.session.projects[self.prj.get()].subjects
                            messagebox.showinfo('XNAT-PIC Uploader', 'A new subject is created.')                 
                        except exception as e:
                            messagebox.showerror("Error!", str(e))
                else:
                    messagebox.showerror('XNAT-PIC Uploader', 'The current project does not exist in XNAT platform.'
                                                            '\nPlease select an other project or create a new one.')
            else:
                messagebox.showerror("XNAT-PIC Uploader", "Please enter a subject ID.")

        def check_experiment_name(self, *args):

            if self.entry_expname.get() != '':
                if self.prj.get() in self.OPTIONS:
                    if self.sub.get() in self.OPTIONS2:

                        if self.entry_expname.get() in self.OPTIONS3:
                            # Case 1 --> The experiment already exists
                            messagebox.showerror(
                                "XNAT-PIC Uploader!",
                                "Experiment %s already exists! Please, enter a different experiment ID"
                                % self.entry_expname.get(),
                            )
                        else:
                            # Case 2 --> The experiment does not exist yet
                            try:
                                result = messagebox.askyesno("XNAT-PIC Uploader", "A new experiment will be created into %s. Are you sure?"
                                                            % self.sub.get())
                                if result is False:
                                    return
                                self.exp.set(self.entry_expname.get())
                                disable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])

                                try:
                                    # Try to retrieve the subject
                                    subject = self.session.projects[self.prj.get()].subjects[self.sub.get()]
                                except:
                                    # otherwise a new one will be created
                                    messagebox.showwarning('XNAT-PIC Uploader', 'The subject you are trying to retrieve does not exist.'
                                                                                'A new project will be created.')
                                    subject = self.session.classes.SubjectData(parent=self.prj.get(), label=self.sub.get())
                                    # Clear cache to refresh the catalog
                                    self.session.clearcache()
                                # Create new experiment

                                ...

                                # Clear cache to refresh the catalog
                                # os.remove(str(self.exp.get()))
                                self.session.clearcache()
                                # Refresh the list of projects and subjects
                                self.OPTIONS2 = self.session.projects[self.prj.get()].subjects
                                self.OPTIONS3 = self.session.projects[self.prj.get()].subjects[self.sub.get()]
                                messagebox.showinfo('XNAT-PIC Uploader', 'A new experiment is created.')                 
                            except exception as e:
                                messagebox.showerror("Error!", str(e))
                    else:
                        messagebox.showerror('XNAT-PIC Uploader', 'The current subject does not exist in XNAT platform.'
                                                                '\nPlease select an other subject or create a new one.')
                else:
                    messagebox.showerror('XNAT-PIC Uploader', 'The current project does not exist in XNAT platform.'
                                                            '\nPlease select an other project or create a new one.')
            else:
                messagebox.showerror("XNAT-PIC Uploader", "Please enter a experiment ID.")

        def overall_uploader(self, master):
                           
            #################### Update the frame ####################
            try:
                destroy_widgets([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn, master.xnat_pic_logo.label])
                
            except:
                pass
            #################### Create the new frame ####################
            master.frame_label.set("Uploader")
            #############################################
            ################ Main Buttons ###############
            self.label_frame_main = ttk.LabelFrame(master.frame, text="", style="Hidden.TLabelframe")
            self.label_frame_main.place(relx=0.2, rely=0, anchor=tk.NW, relwidth=0.8, relheight=1)

            # Frame Title
            self.frame_title = ttk.Label(self.label_frame_main, text="XNAT-PIC Uploader", style="Title.TLabel", anchor=tk.CENTER)
            self.frame_title.pack(fill='x', padx=25, pady=10, anchor=tk.NW)

            # Label Frame Uploader Selection
            self.label_frame_uploader = ttk.LabelFrame(self.label_frame_main, text="Uploader Selection")
            self.label_frame_uploader.pack(fill='x', padx=25, pady=10, anchor=tk.NW)

            self.conv_type = tk.IntVar()

            # Upload project
            def project_handler(*args):
                self.conv_type.set(0)
                self.uploader_data.config(text="Project Uploader")
                self.check_buttons(master, press_btn=0)
            self.prj_btn = ttk.Button(self.label_frame_uploader, text="Upload Project",
                                    command=project_handler, cursor=CURSOR_HAND, width=20)
            self.prj_btn.pack(side='left', expand=True, pady=10)
            
            # Upload subject
            def subject_handler(*args):
                self.conv_type.set(1)
                self.uploader_data.config(text="Subject Uploader")
                self.check_buttons(master, press_btn=1)
            self.sub_btn = ttk.Button(self.label_frame_uploader, text="Upload Subject",
                                    command=subject_handler, cursor=CURSOR_HAND, width=20)
            self.sub_btn.pack(side='left', expand=True, pady=10)

            # Upload experiment
            def experiment_handler(*args):
                self.conv_type.set(2)
                self.uploader_data.config(text="Experiment Uploader")
                self.check_buttons(master, press_btn=2)
            self.exp_btn = ttk.Button(self.label_frame_uploader, text="Upload Experiment", 
                                    command=experiment_handler, cursor=CURSOR_HAND, width=20)
            self.exp_btn.pack(side='left', expand=True, pady=10)   
            
            # Upload file
            def file_handler(*args):
                self.conv_type.set(3)
                self.uploader_data.config(text="File Uploader")
                self.check_buttons(master, press_btn=3)
            self.file_btn = ttk.Button(self.label_frame_uploader, text="Upload File",
                                    command=file_handler, cursor=CURSOR_HAND, width=20)
            self.file_btn.pack(side='left', expand=True, pady=10)

            # Define the central label frame
            self.central_label_frame = ttk.LabelFrame(self.label_frame_main, text="", style="Hidden.TLabelframe")
            self.central_label_frame.pack(fill='x', padx=25, pady=10, anchor=tk.NW)

            # Label Frame for folder selection
            self.folder_selection_label_frame = ttk.Labelframe(self.central_label_frame, text="Folder Selection")
            self.folder_selection_label_frame.pack(side='left', anchor=tk.NW)
            
            # Define a string variable in order to check the current selected item of the Treeview widget
            self.selected_item_path = tk.StringVar()
            
            def select_folder(*args):
                # Define the initial directory
                init_dir = os.path.expanduser("~").replace('\\', '/') + '/Desktop/Dataset'
                # Ask the user to insert the desired directory
                self.folder_to_upload.set(filedialog.askdirectory(parent=master.frame, initialdir=init_dir, 
                                                        title="XNAT-PIC Uploader: Select directory in DICOM format to upload"))
                # Reset and clear the selected_item_path defined from Treeview widget selection
                self.selected_item_path.set('')

            def folder_selected_handler(*args):
                if self.folder_to_upload.get() != '':

                    # Check for pre-existent tree
                    if self.tree.exists(0):
                        # # Check for the name of the previous tree
                        # if self.tree.item(0)['text'] != self.folder_to_upload.get().split('/')[-1]:
                        # If the folder name is changed, then delete the previous tree
                        self.tree.delete(*self.tree.get_children())

                    # Define the main folder into the Treeview object
                    main_folder = self.tree.insert("", "end", iid=0, text=self.folder_to_upload.get().split('/')[-1], values=("", "", "Folder"), open=True)
                    # Scan the folder to get its tree
                    subdir = os.listdir(self.folder_to_upload.get())
                    # Check for OS configuration files and remove them
                    subdirectories = [x for x in subdir if x.endswith('.ini') == False]
                    total_weight = 0
                    last_edit_time = ''
                    j = 1
                    for sub in subdirectories:
                        
                        if os.path.isfile(os.path.join(self.folder_to_upload.get(), sub)):
                            # Check for last edit time
                            edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_upload.get(), sub)))))
                            if last_edit_time == '' or edit_time > last_edit_time:
                                # Update the last edit time
                                last_edit_time = edit_time
                            # Check for file dimension
                            file_weight = round(os.path.getsize(os.path.join(self.folder_to_upload.get(), sub))/1024, 2)
                            total_weight += round(file_weight/1024, 2)
                            # Add the item like a file
                            self.tree.insert(main_folder, "end", iid=j, text=sub, values=(edit_time, str(file_weight) + "KB", "File"))
                            # Update the j counter
                            j += 1

                        elif os.path.isdir(os.path.join(self.folder_to_upload.get(), sub)):
                            current_weight = 0
                            last_edit_time_lev2 = ''
                            branch_idx = j
                            level2_folder = self.tree.insert(main_folder, "end", iid=branch_idx, text=sub, values=("", "", "Folder"), open=False)
                            j += 1
                            # Scansiona le directory interne per ottenere il tree CHIUSO
                            sub_level2 = os.listdir(os.path.join(self.folder_to_upload.get(), sub))
                            subdirectories2 = [x for x in sub_level2 if x.endswith('.ini') == False]
                            for sub2 in subdirectories2:
                                if os.path.isfile(os.path.join(self.folder_to_upload.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_upload.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2
                                    # Check for file dimension
                                    file_weight = round(os.path.getsize(os.path.join(self.folder_to_upload.get(), sub, sub2))/1024, 2)
                                    current_weight += round(file_weight/1024, 2)
                                    # Add the item like a file
                                    self.tree.insert(level2_folder, "end", iid=j, text=sub2, values=(edit_time, str(file_weight) + "KB", "File"))
                                    # Update the j counter
                                    j += 1

                                elif os.path.isdir(os.path.join(self.folder_to_upload.get(), sub, sub2)):
                                    # Check for last edit time
                                    edit_time = str(time.strftime("%d/%m/%Y,%H:%M:%S", time.localtime(os.path.getmtime(os.path.join(self.folder_to_upload.get(), sub, sub2)))))
                                    if last_edit_time_lev2 == '' or edit_time > last_edit_time_lev2:
                                        # Update the last edit time
                                        last_edit_time_lev2 = edit_time
                                    if last_edit_time_lev2 > last_edit_time:
                                        last_edit_time = last_edit_time_lev2

                                    folder_size = round(get_dir_size(os.path.join(self.folder_to_upload.get(), sub, sub2))/1024/1024, 2)
                                    current_weight += folder_size
                                    self.tree.insert(level2_folder, "end", iid=j, text=sub2, values=(edit_time, str(folder_size) + 'MB', "Folder"))
                                    j += 1
                                
                            total_weight += current_weight
                            self.tree.set(branch_idx, column="#1", value=last_edit_time_lev2)
                            self.tree.set(branch_idx, column="#2", value=str(round(current_weight, 2)) + "MB")

                    # Update the fields of the parent object
                    self.tree.set(0, column="#1", value=last_edit_time)
                    self.tree.set(0, column="#2", value=str(round(total_weight/1024, 2)) + "GB")

            # Initialize the folder_to_upload path
            self.folder_to_upload = tk.StringVar()
            self.select_folder_button = ttk.Button(self.folder_selection_label_frame, text="Select folder", style="TButton",
                                                    state='disabled', cursor=CURSOR_HAND, width=20, command=select_folder)
            self.select_folder_button.grid(row=0, column=0, sticky=tk.NW, padx=10, pady=10)

            # Upload additional files
            self.add_file_flag = tk.IntVar()
            self.add_file_btn = ttk.Checkbutton(self.folder_selection_label_frame, variable=self.add_file_flag, onvalue=1, offvalue=0, 
                                text="Additional Files", state='disabled', style="WithoutBack.TCheckbutton")
            self.add_file_btn.grid(row=0, column=1, padx=10, pady=10, sticky=tk.E)

            # Treeview for folder visualization
            def get_selected_item(*args):
                selected_item = self.tree.selection()[0]
                
                if self.folder_to_upload.get().split('/')[-1] == self.tree.item(selected_item, "text"):
                    self.selected_item_path.set(self.folder_to_upload.get())
                else:
                    parent_item = self.tree.parent(selected_item)
                    if self.folder_to_upload.get().split('/')[-1] == self.tree.item(parent_item, "text"):
                        self.selected_item_path.set('/'.join([self.folder_to_upload.get(), 
                                self.tree.item(selected_item, "text")]))
                    else:
                        higher_parent_item = self.tree.parent(parent_item)
                        if self.folder_to_upload.get().split('/')[-1] == self.tree.item(higher_parent_item, "text"):
                            self.selected_item_path.set('/'.join([self.folder_to_upload.get(), self.tree.item(parent_item, "text"),
                                self.tree.item(selected_item, "text")]))

            self.tree = ttk.Treeview(self.folder_selection_label_frame, selectmode='browse', bootstyle='primary')
            self.tree.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NW, columnspan=2)
            self.tree.bind("<ButtonRelease-1>", get_selected_item)

            # Scrollbar for Treeview widget
            self.tree_scrollbar = ttk.Scrollbar(self.folder_selection_label_frame, orient='vertical', command=self.tree.yview)
            self.tree_scrollbar.grid(row=1, column=2, padx=0, pady=10, sticky=tk.NS)
            self.tree.configure(yscrollcommand=self.tree_scrollbar.set)
            self.tree["columns"] = ("#1", "#2", "#3")
            self.tree.heading("#0", text="Selected folder", anchor=tk.NW)
            self.tree.heading("#1", text="Last Update", anchor=tk.NW)
            self.tree.heading("#2", text="Size", anchor=tk.NW)
            self.tree.heading("#3", text="Type", anchor=tk.NW)
            self.tree.column("#0", stretch=tk.YES, width=150)
            self.tree.column("#1", stretch=tk.YES, width=150)
            self.tree.column("#2", stretch=tk.YES, width=100)
            self.tree.column("#3", stretch=tk.YES, width=100)

            def load_tree(*args):
                progressbar_tree = ProgressBar("XNAT-PIC Uploader")
                progressbar_tree.start_indeterminate_bar()
                t = threading.Thread(target=folder_selected_handler, args=())
                t.start()
                while t.is_alive() == True:
                    progressbar_tree.update_bar()
                progressbar_tree.stop_progress_bar()

            self.folder_to_upload.trace('w', load_tree)

            # Label Frame Uploader Custom Variables
            self.custom_var_labelframe = ttk.LabelFrame(self.central_label_frame, text="Custom Variables")
            self.custom_var_labelframe.pack(side='left', padx=10, anchor=tk.NW)

            # Custom Variables
            self.n_custom_var = tk.IntVar()
            self.n_custom_var.set(3)
            custom_var_options = list(range(0, 4))
            self.custom_var_list = ttk.OptionMenu(self.custom_var_labelframe, self.n_custom_var, 0, *custom_var_options)
            self.custom_var_list.config(width=2)
            self.custom_var_list.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NW)
            self.custom_var_label = ttk.Label(self.custom_var_labelframe, text="Custom Variables")
            self.custom_var_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.NW)

            # Show Custom Variables
            def display_custom_var(*args):
                for widget in self.custom_var_labelframe.winfo_children():
                    if widget.grid_info()['row'] > 0:
                        widget.destroy()

                if self.selected_item_path.get() != '':
                    if self.n_custom_var.get() != 0:
                        try:
                            list_of_files = glob(self.selected_item_path.get() + '/**/*.txt', recursive=False)
                            custom_file = [x for x in list_of_files if 'Custom' in x]
                            custom_variables = read_table(custom_file[0])
                            info = {}
                            custom_vars = [(key, custom_variables[key]) for key in custom_variables.keys() 
                                                if key not in ['Project', 'Subject', 'Experiment', 'Acquisition_date', 'C_V']]
                        except:
                            info = {"Project": self.selected_item_path.get().split('/')[-3], 
                                    "Subject": self.selected_item_path.get().split('/')[-2], 
                                    "Experiment": self.selected_item_path.get().split('/')[-1], 
                                    "Acquisition_date": "", 
                                    "C_V": ""}
                            custom_vars = [("Group", ""), ("Timepoint", ""), ("Dose", "")]
                            custom_file = [os.path.join(self.selected_item_path.get(), 'MR', self.selected_item_path.get().split('/')[-1] + "_Custom_Variables.txt")]
                        label_list = []
                        entry_list = []
                        for x in range(1, self.n_custom_var.get() + 1):
                            # Custom Variable Label
                            label_n = ttk.Label(self.custom_var_labelframe, text=custom_vars[x-1][0])
                            label_n.grid(row=x, column=0, padx=10, pady=10, sticky=tk.NW)
                            label_list.append(label_n)
                            # Custom Variable Entry
                            entry_n = ttk.Entry(self.custom_var_labelframe, show='', state='disabled')
                            entry_n.var = tk.StringVar()
                            entry_n.var.set(custom_vars[x-1][1])
                            entry_n["textvariable"] = entry_n.var
                            entry_n.grid(row=x, column=1, padx=10, pady=10, sticky=tk.NW)
                            entry_list.append(entry_n)

                        # Button to modify the entry of the custom variable
                        def edit_handler(*args):
                            enable_buttons(entry_list)
                            enable_buttons([confirm_button, reject_button])
                             
                        edit_button = ttk.Button(self.custom_var_labelframe, image=master.logo_edit, command=edit_handler,
                                                    style="WithoutBack.TButton", cursor=CURSOR_HAND)
                        edit_button.grid(row=1, column=2, padx=10, pady=10, sticky=tk.NW)

                        # Button to confirm changes
                        def accept_changes(*args):
                            # Save change on .txt file
                            data = {}
                            data.update(info)
                            for e in range(len(entry_list)):
                                data[label_list[e]["text"]] = entry_list[e].var.get()
                            write_table(custom_file[0], data)
                            display_custom_var()

                        confirm_button = ttk.Button(self.custom_var_labelframe, image=master.logo_accept, command=accept_changes,
                                                    state='disabled', style="WithoutBack.TButton", cursor=CURSOR_HAND)
                        confirm_button.grid(row=1, column=3, padx=10, pady=10, sticky=tk.NW)

                        # Button to abort changes
                        def reject_changes(*args):
                            # disable_buttons(entry_list)
                            display_custom_var()
                        reject_button = ttk.Button(self.custom_var_labelframe, image=master.logo_delete, command=reject_changes,
                                                    state='disabled', style="WithoutBack.TButton", cursor=CURSOR_HAND)
                        reject_button.grid(row=1, column=4, padx=10, pady=10, sticky=tk.NW)

            self.n_custom_var.trace('w', display_custom_var)
            self.selected_item_path.trace('w', display_custom_var)
            #############################################

            # Label Frame for Uploader Data
            self.uploader_data = ttk.LabelFrame(self.label_frame_main, text="")
            self.uploader_data.pack(fill='x', expand=True, padx=25, pady=10, anchor=tk.NW)

            #############################################
            ################# Project ###################
            # Menu
            def get_subjects(*args):
                if self.prj.get() != '--' and self.prj.get() in self.OPTIONS:
                    self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
                else:
                    self.OPTIONS2 = []
                self.sub.set(default_value)
                self.exp.set(default_value)
                self.subject_list['menu'].delete(0, 'end')
                for key in self.OPTIONS2:
                    self.subject_list['menu'].add_command(label=key, command=lambda var=key:self.sub.set(var))
            
            def reject_project(*args):
                self.entry_prjname.delete(0,tk.END)
                disable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])

            self.project_list_label = ttk.Label(self.uploader_data, text="Select Project")
            self.project_list_label.grid(row=0, column=0, padx=10, pady=10, sticky=tk.NW)
            self.OPTIONS = list(self.session.projects)
            self.prj = tk.StringVar()
            default_value = "--"
            self.project_list = ttk.OptionMenu(self.uploader_data, self.prj, default_value, *self.OPTIONS)
            self.project_list.configure(state="disabled", width=30)
            self.prj.trace('w', get_subjects)
            self.prj.trace('w', reject_project)
            self.project_list.grid(row=0, column=1, padx=2, pady=10, sticky=tk.NW)
            
            # Button to add a new project
            def add_project():
                object_creator = ObjectCreator(self.session).add_project_popup()
                enable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])
                self.entry_prjname.delete(0,tk.END)
            self.new_prj_btn = ttk.Button(self.uploader_data, state=tk.DISABLED, width=20, style="Secondary.TButton",
                                        command=add_project, cursor=CURSOR_HAND, text="Add New Project")
            self.new_prj_btn.grid(row=0, column=2, padx=20, pady=10, sticky=tk.NW)
            
            # Entry to write a new project
            self.entry_prjname = ttk.Entry(self.uploader_data)
            self.entry_prjname.configure(state="disabled", width=30)
            self.entry_prjname.grid(row=0, column=3, padx=2, pady=10, sticky=tk.NW)

            # Button to confirm new project
            self.confirm_new_prj = ttk.Button(self.uploader_data, image=master.logo_accept, style="WithoutBack.TButton",
                                            command=self.check_project_name, cursor=CURSOR_HAND, state='disabled')
            self.confirm_new_prj.grid(row=0, column=4, padx=10, pady=10, sticky=tk.NW)

            # Button to reject new project
            self.reject_new_prj = ttk.Button(self.uploader_data, image=master.logo_delete, style="WithoutBack.TButton",
                                            command=reject_project, cursor=CURSOR_HAND, state='disabled')
            self.reject_new_prj.grid(row=0, column=5, padx=2, pady=10, sticky=tk.NW)
            
            #############################################

            #############################################
            ################# Subject ###################
            # Menu
            def get_experiments(*args):
                if self.prj.get() != '--' and self.sub.get() != '--' and self.prj.get() in self.OPTIONS and self.sub.get() in self.OPTIONS2:
                    self.OPTIONS3 = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
                else:
                    self.OPTIONS3 = []
                self.exp.set(default_value)
                self.experiment_list['menu'].delete(0, 'end')
                for key in self.OPTIONS3:
                    self.experiment_list['menu'].add_command(label=key, command=lambda var=key:self.exp.set(var))

            def reject_subject(*args):
                self.entry_subname.delete(0,tk.END)
                disable_buttons([self.entry_subname, self.confirm_new_sub, self.reject_new_sub])

            if self.prj.get() != '--':
                self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
            else:
                self.OPTIONS2 = []
            self.subject_list_label = ttk.Label(self.uploader_data, text="Select Subject")
            self.subject_list_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.NW)
            self.sub = tk.StringVar()
            self.subject_list = ttk.OptionMenu(self.uploader_data, self.sub, default_value, *self.OPTIONS2)
            self.subject_list.configure(state="disabled", width=30)
            self.sub.trace('w', get_experiments)
            self.sub.trace('w', reject_subject)
            self.subject_list.grid(row=1, column=1, padx=2, pady=5, sticky=tk.NW)
            
            # Button to add a new subject
            def add_subject():
                object_creator = ObjectCreator(self.session).add_subject_popup()
                enable_buttons([self.entry_subname, self.confirm_new_sub, self.reject_new_sub])
                self.entry_subname.delete(0,tk.END)
            self.new_sub_btn = ttk.Button(self.uploader_data, state=tk.DISABLED, width=20, style="Secondary.TButton",
                                        command=add_subject, cursor=CURSOR_HAND, text="Add New Subject")
            self.new_sub_btn.grid(row=1, column=2, padx=20, pady=10, sticky=tk.NW)

            # Entry to write a new subject
            self.entry_subname = ttk.Entry(self.uploader_data)
            self.entry_subname.configure(state="disabled", width=30)
            self.entry_subname.grid(row=1, column=3, padx=2, pady=10, sticky=tk.NW)

            # Button to confirm new subject
            self.confirm_new_sub = ttk.Button(self.uploader_data, image=master.logo_accept, style="WithoutBack.TButton",
                                            command=self.check_subject_name, cursor=CURSOR_HAND, state='disabled')
            self.confirm_new_sub.grid(row=1, column=4, padx=10, pady=10, sticky=tk.NW)

            # Button to reject new subject
            self.reject_new_sub = ttk.Button(self.uploader_data, image = master.logo_delete, style="WithoutBack.TButton",
                                            command=reject_subject, cursor=CURSOR_HAND, state='disabled')
            self.reject_new_sub.grid(row=1, column=5, padx=2, pady=10, sticky=tk.NW)
            #############################################

            #############################################
            ################# Experiment ################
            def reject_experiment(*args):
                self.entry_expname.delete(0,tk.END)
                disable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])
            
            # Menu
            if self.prj.get() != '--' and self.sub.get() != '--':
                self.OPTIONS3 = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
            else:
                self.OPTIONS3 = []
            self.experiment_list_label = ttk.Label(self.uploader_data, text="Select Experiment")
            self.experiment_list_label.grid(row=2, column=0, padx=10, pady=10, sticky=tk.NW)
            self.exp = tk.StringVar()
            self.experiment_list = ttk.OptionMenu(self.uploader_data, self.exp, default_value, *self.OPTIONS3)
            self.experiment_list.configure(state="disabled", width=30)
            self.exp.trace('w', reject_experiment)
            self.experiment_list.grid(row=2, column=1, padx=2, pady=10, sticky=tk.NW)
            
            # Button to add a new experiment
            def add_experiment():
                enable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])
                self.entry_expname.delete(0,tk.END)
            self.new_exp_btn = ttk.Button(self.uploader_data, state=tk.DISABLED, style="Secondary.TButton", 
                                        text="Add New Experiment", command=add_experiment, cursor=CURSOR_HAND, width=20)
            self.new_exp_btn.grid(row=2, column=2, padx=20, pady=10, sticky=tk.NW)

            # Entry to write a new experiment
            self.entry_expname = ttk.Entry(self.uploader_data)
            self.entry_expname.config(state='disabled', width=30)
            self.entry_expname.grid(row=2, column=3, padx=2, pady=10, sticky=tk.NW)

            # Button to confirm new experiment
            self.confirm_new_exp = ttk.Button(self.uploader_data, image = master.logo_accept, style="WithoutBack.TButton",
                                            command=self.check_experiment_name, cursor=CURSOR_HAND, state='disabled')
            self.confirm_new_exp.grid(row=2, column=4, padx=10, pady=10, sticky=tk.NW)

            # Button to reject new experiment
            self.reject_new_exp = ttk.Button(self.uploader_data, image = master.logo_delete, style="WithoutBack.TButton",
                                            command=reject_experiment, cursor=CURSOR_HAND, state='disabled')
            self.reject_new_exp.grid(row=2, column=5, padx=2, pady=10, sticky=tk.NW)
            #############################################

            self.bottom_label_frame = ttk.Labelframe(self.label_frame_main, text="", style="Hidden.TLabelframe")
            self.bottom_label_frame.pack(side='bottom', padx=25, pady=25, fill='x')

            #############################################
            ################ EXIT Button ################
            def exit_uploader():
                result = messagebox.askquestion("XNAT-PIC Uploader", "Do you want to exit?", icon='warning')
                if result == 'yes':
                    # Destroy all the existent widgets (Button, OptionMenu, ...)
                    destroy_widgets([self.uploader_data, self.custom_var_labelframe, self.label_frame_uploader, self.exit_btn,
                                    self.next_btn, self.folder_selection_label_frame, self.frame_title])
                    # Perform disconnection of the session if it is alive
                    try:
                        self.session.disconnect()
                        self.session = ''
                    except:
                        pass
                    # Restore the main frame
                    xnat_pic_gui.choose_your_action(master)

            self.exit_text = tk.StringVar() 
            self.exit_btn = ttk.Button(self.bottom_label_frame, textvariable=self.exit_text)
            self.exit_btn.configure(command=exit_uploader)
            self.exit_text.set("Exit")
            self.exit_btn.pack(side='left', padx=25, pady=25, anchor=tk.NW)
            #############################################

            #############################################
            ################ NEXT Button ################
            def next():
                if self.press_btn == 0:
                    self.project_uploader(master)
                elif self.press_btn == 1:
                    self.subject_uploader(master)
                elif self.press_btn == 2:
                    self.experiment_uploader(master)
                elif self.press_btn == 3:
                    self.file_uploader(master)
                else:
                    pass

            self.next_text = tk.StringVar() 
            self.next_btn = ttk.Button(self.bottom_label_frame, textvariable=self.next_text, state='disabled',
                                        command=next)
            self.next_text.set("Next")
            self.next_btn.pack(side='right', padx=25, pady=25, anchor=tk.NE)
            #############################################

        def check_buttons(self, master, press_btn=0):

            def back():
                destroy_widgets([self.label_frame_uploader, self.uploader_data, self.custom_var_labelframe,
                                self.exit_btn, self.next_btn, self.folder_selection_label_frame, self.frame_title])
                self.overall_uploader(master)

            # Initialize the press button value
            self.press_btn = press_btn

            # Change the EXIT button into BACK button and modify the command associated with it
            self.exit_text.set("Back")
            self.exit_btn.configure(command=back)

            if press_btn == 0:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button, self.add_file_btn])
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                self.prj.trace('w', enable_next)
                
            elif press_btn == 1:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button, self.add_file_btn])
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                self.prj.trace('w', enable_next)
                
            elif press_btn == 2:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button,
                                self.subject_list, self.new_sub_btn, self.add_file_btn])
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                self.sub.trace('w', enable_next)

            elif press_btn == 3:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.select_folder_button,
                                self.subject_list, self.new_sub_btn,
                                self.experiment_list, self.new_exp_btn, self.add_file_btn])
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--' and self.exp.get() != '--' and self.folder_to_upload.get() != '':
                        enable_buttons([self.next_btn])
                self.exp.trace('w', enable_next)
            else:
                pass

        def project_uploader(self, master):

            project_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), 
                                                        title="XNAT-PIC Project Uploader: Select project directory in DICOM format to upload")
            # Check for empty selected folder
            if os.path.isdir(project_to_upload) == False:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder does not exist!')
            elif os.listdir(project_to_upload) == []:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder is empty!')
            else:
                # Start progress bar
                progressbar = ProgressBar(bar_title='XNAT-PIC Uploader')
                progressbar.start_indeterminate_bar()

                list_dirs = os.listdir(project_to_upload)

                start_time = time.time()

                def upload_thread():

                    for sub in list_dirs:
                        sub = os.path.join(project_to_upload, sub)

                        list_dirs_exp = os.listdir(sub)
                        for exp in list_dirs_exp:
                            exp = os.path.join(sub, exp)
                            # Check if 'MR' folder is already into the folder_to_upload path
                            if 'MR' != os.path.basename(exp):
                                exp = os.path.join(exp, 'MR').replace('\\', '/')
                            else:
                                exp = exp.replace('\\', '/')
                            params = {}
                            params['folder_to_upload'] = exp
                            params['project_id'] = self.prj.get()
                            params['custom_var_flag'] = self.n_custom_var.get()
                            # Check for existing custom variables file
                            
                            try:
                                # If the custom variables file is available
                                text_file = [os.path.join(exp, f) for f in os.listdir(exp) if f.endswith('.txt') and 'Custom' in f]
                                subject_data = read_table(text_file[0])
                                
                                # Define the subject_id and the experiment_id
                                # Controllo su stringa vuota
                                self.sub.set(subject_data['Subject'])
                                if self.sub.get() != subject_data['Subject']:
                                    ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", 
                                                            "The subject you are trying to retrieve does not match with the custom variables."
                                                            "\n Would you like to continue?")
                                    if ans != True:
                                        return
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], 
                                                        subject_data['Timepoint']]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()
                                for var in subject_data.keys():
                                    if var not in ['Project', 'Subject', 'AcquisitionDate']:
                                        params[var] = subject_data[var]
                            except:
                                # Define the subject_id and the experiment_id if the custom variables file is not available
                                self.sub.set(exp.split('/')[-2].replace('.','_'))
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([exp.split('/')[-3].replace('_dcm', ''), exp.split('/')[-2].replace('.', '_')]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()

                            progressbar.set_caption('Uploading ' + str(self.sub.get()) + ' ...')

                            self.uploader.upload(params)
                            # Check for Results folder
                            if self.add_file_flag.get() == 1:
                                # self.session.clearcache()
                                self.uploader_file = FileUploader(self.session)
                                progressbar.set_caption('Uploading files to ' + str(self.exp.get()) + ' ...')
                                for sub_dir in os.listdir(exp):
                                    if 'Results' in sub_dir:
                                        vars = {}
                                        vars['project_id'] = self.prj.get()
                                        vars['subject_id'] = self.sub.get()
                                        vars['experiment_id'] = self.exp.get()
                                        vars['folder_name'] = sub_dir
                                        list_of_files = os.scandir(os.path.join(exp, sub_dir))
                                        file_paths = []
                                        for file in list_of_files:
                                            if file.is_file():
                                                file_paths.append(file.path)
                                        self.uploader_file.upload(file_paths, vars)

                self.uploader = Dicom2XnatUploader(self.session)

                t = threading.Thread(target=upload_thread, args=())
                t.start()
                
                while t.is_alive() == True:
                    progressbar.update_bar()
                
                # Stop the progress bar and close the popup
                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Elapsed time: ' + str(end_time-start_time) + ' seconds')

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your subject is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn, self.custom_var_list,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
            # Delete all widgets that cannot be destroyed
            delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.check_add_files,
                                                    self.check_n_custom_var, self.subtitle])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)

        def subject_uploader(self, master):

            subject_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), 
                                                        title="XNAT-PIC Subject Uploader: Select subject directory in DICOM format to upload")
            # Check for empty selected folder
            if os.path.isdir(subject_to_upload) == False:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder does not exist!')
            elif os.listdir(subject_to_upload) == []:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder is empty!')
            else:
                list_dirs = os.listdir(subject_to_upload)
                self.uploader = Dicom2XnatUploader(self.session)

                # Start progress bar
                progressbar = ProgressBar(bar_title='XNAT-PIC Uploader')
                progressbar.start_indeterminate_bar()

                start_time = time.time()

                for exp in list_dirs:
                    exp = os.path.join(subject_to_upload, exp)
                    
                    # Check if 'MR' folder is already into the folder_to_upload path
                    if 'MR' != os.path.basename(exp):
                        exp = os.path.join(exp, 'MR').replace('\\', '/')
                    else:
                        exp = exp.replace('\\', '/')

                    params = {}
                    params['folder_to_upload'] = exp
                    params['project_id'] = self.prj.get()
                    params['custom_var_flag'] = self.n_custom_var.get()
                    # Check for existing custom variables file
                    try:
                        # If the custom variables file is available
                        text_file = [os.path.join(exp, f) for f in os.listdir(exp) if f.endswith('.txt') and 'Custom' in f]
                        subject_data = read_table(text_file[0])
                        
                        # Define the subject_id and the experiment_id
                        if self.sub.get() == '--':
                            self.sub.set(subject_data['Subject'])
                        if self.sub.get() != subject_data['Subject']:
                            ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", 
                                                    "The subject you are trying to retrieve does not match with the custom variables."
                                                    "\n Would you like to continue?")
                            if ans != True:
                                return
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], 
                                                    subject_data['Timepoint']]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                        for var in subject_data.keys():
                            if var not in ['Project', 'Subject', 'AcquisitionDate']:
                                params[var] = subject_data[var]
                    except:
                        # Define the subject_id and the experiment_id if the custom variables file is not available
                        if self.sub.get() == '--':
                            self.sub.set(exp.split('/')[-2].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([exp.split('/')[-3].replace('_dcm',''), exp.split('/')[-2].replace('.','_')]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()

                    progressbar.set_caption('Uploading ' + str(self.sub.get()) + ' ...')

                    t = threading.Thread(target=self.uploader.upload, args=(params, ))
                    t.start()

                    while t.is_alive() == True:
                        progressbar.update_bar()
                    else:
                        # Check for Results folder
                        if self.add_file_flag.get() == 1:
                            self.session.clearcache()
                            self.uploader_file = FileUploader(self.session)
                            for sub_dir in os.listdir(exp):
                                if 'Results' in sub_dir:
                                    vars = {}
                                    vars['project_id'] = self.prj.get()
                                    vars['subject_id'] = self.sub.get()
                                    vars['experiment_id'] = self.exp.get()
                                    vars['folder_name'] = sub_dir
                                    list_of_files = os.scandir(os.path.join(exp, sub_dir))
                                    file_paths = []
                                    for file in list_of_files:
                                        if file.is_file():
                                            file_paths.append(file.path)
                                    progressbar.set_caption('Uploading files on ' + str(self.exp.get()) + ' ...')
                                    ft = threading.Thread(target=self.uploader_file.upload, args=(file_paths, vars, ))
                                    ft.start()
                                    while ft.is_alive() == True:
                                        progressbar.update_bar()

                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Elapsed time: ' + str(end_time-start_time) + ' seconds')

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your subject is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn, self.custom_var_list,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
            # Delete all widgets that cannot be destroyed
            delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.check_add_files,
                                                    self.check_n_custom_var, self.subtitle])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)

        def experiment_uploader(self, master):

            experiment_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), 
                                                            title="XNAT-PIC Experiment Uploader: Select experiment directory in DICOM format to upload")
            # Check for empty selected folder
            if os.path.isdir(experiment_to_upload) == False:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder does not exist!')
            elif os.listdir(experiment_to_upload) == []:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder is empty!')
            else:
                try:
                    self.uploader = Dicom2XnatUploader(self.session)
                    # Start progress bar
                    progressbar = ProgressBar(bar_title='XNAT-PIC Uploader')
                    progressbar.start_indeterminate_bar()

                    start_time = time.time()
                    # Check if 'MR' folder is already into the folder_to_upload path
                    if 'MR' != os.path.basename(experiment_to_upload):
                        experiment_to_upload = os.path.join(experiment_to_upload, 'MR').replace('\\', '/')
                    else:
                        experiment_to_upload = experiment_to_upload.replace('\\', '/')

                    params = {}
                    params['folder_to_upload'] = experiment_to_upload
                    params['project_id'] = self.prj.get()
                    params['custom_var_flag'] = self.n_custom_var.get()
                    # Check for existing custom variables file
                    try:
                        # If the custom variables file is available
                        text_file = [os.path.join(experiment_to_upload, f) for f in os.listdir(experiment_to_upload) if f.endswith('.txt') 
                                                                                                                        and 'Custom' in f]
                        subject_data = read_table(text_file[0])
                        
                        # Define the subject_id and the experiment_id
                        if self.sub.get() == '--':
                            self.sub.set(subject_data['Subject'])
                        if self.sub.get() != subject_data['Subject']:
                            ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", 
                                                    "The subject you are trying to retrieve does not match with the custom variables."
                                                    "\n Would you like to continue?")
                            if ans != True:
                                return
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], 
                                                    subject_data['Timepoint']]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                        for var in subject_data.keys():
                            if var not in ['Project', 'Subject', 'AcquisitionDate']:
                                params[var] = subject_data[var]
                    except:
                        # Define the subject_id and the experiment_id if the custom variables file is not available
                        if self.sub.get() == '--':
                            self.sub.set(experiment_to_upload.split('/')[-2].replace('.','_'))
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([experiment_to_upload.split('/')[-3].replace('_dcm', ''), 
                                                    experiment_to_upload.split('/')[-2].replace('.','_')]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()

                    progressbar.set_caption('Uploading ' + str(self.exp.get()) + ' ...')

                    t = threading.Thread(target=self.uploader.upload, args=(params, ))
                    t.start()

                    while t.is_alive() == True:
                        progressbar.update_bar()
                    else:
                        # Check for Results folder
                        if self.add_file_flag.get() == 1:
                            self.session.clearcache()
                            self.uploader_file = FileUploader(self.session)
                            for sub_dir in os.listdir(experiment_to_upload):
                                if 'Results' in sub_dir:
                                    vars = {}
                                    vars['project_id'] = self.prj.get()
                                    vars['subject_id'] = self.sub.get()
                                    vars['experiment_id'] = self.exp.get()
                                    vars['folder_name'] = sub_dir
                                    list_of_files = os.scandir(os.path.join(experiment_to_upload, sub_dir))
                                    file_paths = []
                                    for file in list_of_files:
                                        if file.is_file():
                                            file_paths.append(file.path)
                                    progressbar.set_caption('Uploading files on ' + str(self.exp.get()) + ' ...')
                                    ft = threading.Thread(target=self.uploader_file.upload, args=(file_paths, vars, ))
                                    ft.start()
                                    while ft.is_alive() == True:
                                        progressbar.update_bar()

                        progressbar.stop_progress_bar()

                        end_time = time.time()
                        print('Elapsed time: ' + str(end_time-start_time) + ' seconds')

                except Exception as e: 
                    messagebox.showerror("XNAT-PIC Uploader", e)

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your subject is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn, self.custom_var_list,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
            # Delete all widgets that cannot be destroyed
            delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.check_add_files,
                                                    self.check_n_custom_var, self.subtitle])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)

        def file_uploader(self, master):

            files_to_upload = filedialog.askopenfilenames(parent=master.root, initialdir=os.path.expanduser("~"), 
                                                        title="XNAT-PIC File Uploader: Select file to upload")
            
            if files_to_upload == [] or files_to_upload == '':
                messagebox.showerror('XNAT-PIC Uploader', 'Error! No files selected!')
            else:
                vars = {}
                vars['project_id'] = self.prj.get()
                vars['subject_id'] = self.sub.get()
                vars['experiment_id'] = self.exp.get()
                vars['folder_name'] = files_to_upload[0].split('/')[-2]

                progressbar = ProgressBar('XNAT-PIC File Uploader')
                progressbar.start_indeterminate_bar()

                file_paths = []
                for file in files_to_upload:
                    if file.is_file():
                        file_paths.append(file.path)
                        
                progressbar.set_caption('Uploading files on ' + str(self.exp.get()) + ' ...')
                ft = threading.Thread(target=self.uploader_file.upload, args=(file_paths, vars, ))
                ft.start()
                while ft.is_alive() == True:
                    progressbar.update_bar()

                progressbar.stop_progress_bar()
                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your file is uploaded on XNAT platform.")

            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn, self.custom_var_list,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
            # Delete all widgets that cannot be destroyed
            delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.check_add_files,
                                                    self.check_n_custom_var, self.subtitle])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)


if __name__ == "__main__":
    
    freeze_support()
    check_credentials()

    # root = tk.Tk()
    app = xnat_pic_gui()
    # s = SplashScreen(root, timeout=5000)
    # root.mainloop()

           