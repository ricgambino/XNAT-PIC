from doctest import master
from logging import exception
import shutil
import tkinter as tk
from tkinter import DISABLED, END, MULTIPLE, N, NE, NW, RAISED, SINGLE, W, Menu, filedialog, messagebox
from tkinter.font import Font
from turtle import bgcolor, width
from unicodedata import name
from unittest import result
from PIL import Image, ImageTk
from tkinter import ttk
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
from xnat_uploader import Dicom2XnatUploader, FileUploader, read_table
import datefinder
import pydicom, webbrowser
from tkcalendar import DateEntry
from accessory_functions import *
from idlelib.tooltip import Hovertip
from multiprocessing import Pool, cpu_count
from credential_manager import CredentialManager
from win32api import GetMonitorInfo, MonitorFromPoint
import pandas

PATH_IMAGE = "images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
BACKGROUND_COLOR = "#ffffff"
THEME_COLOR = "#E5EAF0"
THEME_COLOR_2 = '#0070C0'
TEXT_BTN_COLOR = "black"
TEXT_BTN_COLOR_2 = "white"
TEXT_LBL_COLOR = "black"
BG_BTN_COLOR = "#E5EAF0"
BG_BTN_COLOR_2 = '#0070C0'
BG_LBL_COLOR = "black"
DISABLE_LBL_COLOR = '#D3D3D3'
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
SMALL_FONT_2 = ("Calibri", 10)
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
        self.my_canvas = tk.Canvas(self, height=height, width=width, bg="white", highlightthickness=1, highlightbackground=THEME_COLOR)
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
        self.root.state('zoomed')
        # self.root = master
        # Define the style of the root screen
        self.style = ttk.Style(self.root)
        self.root.tk.call('source', 'azure/azure.tcl')
        self.style.theme_use('azure')
        self.style.configure("Accentbutton", font=("Calibri", 20, "bold"), foreground='white')
        self.style.configure("Togglebutton", foreground='white')
        #self.root.state('zoomed')
        ### GET PRIMARY SCREEN RESOLUTION
        ### MADE FOR MULTISCREEN ENVIRONMENTS
        if (platform.system()=='Linux'):
            cmd_show_screen_resolution = subprocess.Popen("xrandr --query | grep -oG 'primary [0-9]*x[0-9]*'",\
                                                          stdout=subprocess.PIPE, shell=True)
            screen_output =str(cmd_show_screen_resolution.communicate()).split()[1]
            self.root.screenwidth, self.root.screenheight = re.findall("[0-9]+",screen_output)
        ###
        ###
        else :
            self.root.screenwidth=self.root.winfo_screenwidth()
            self.root.screenheight=self.root.winfo_screenheight()

        # Adjust size based on screen resolution
        w = self.root.screenwidth
        h = self.root.screenheight
        monitor_info = GetMonitorInfo(MonitorFromPoint((0,0)))
        work_area = monitor_info.get("Work")
        work_height = work_area[3]
        self.root.geometry("%dx%d+0+0" % (w, h))
        self.root.title("   XNAT-PIC   ~   Molecular Imaging Center   ~   University of Torino   ")
        # If you want the logo 
        #self.root.iconbitmap(r"logo3.ico")

        # Define Canvas and logo in background
        global my_width
        global my_height
        my_width = int(w*PERCENTAGE_SCREEN)
        my_height = int(work_height*PERCENTAGE_SCREEN)
        self.my_canvas = tk.Canvas(self.root, width=my_width, height=my_height, bg=BACKGROUND_COLOR, highlightthickness=0, 
                                    highlightbackground=THEME_COLOR)
        self.my_canvas.place(x=0, y=0, anchor=tk.NW)

        # Logo Panel
        panel = Image.open(PATH_IMAGE + "logo-panel.png").convert("RGBA")
        panel = panel.resize((int(my_width/5), my_height), Image.ANTIALIAS)
        self.panel = ImageTk.PhotoImage(panel)
        self.panel_image = tk.Button(self.my_canvas, image=self.panel, bg=BG_BTN_COLOR, borderwidth=0, 
                                    activebackground=BG_BTN_COLOR)
        self.img1 = self.my_canvas.create_window(0, 0, anchor=tk.NW, window=self.panel_image)

        # XNAT-PIC Logo
        logo = Image.open(PATH_IMAGE + "XNAT-PIC-logo.png").convert("RGBA")
        logo = logo.resize((int(logo.size[0]/3), int(logo.size[1]/3)), Image.ANTIALIAS)
        self.logo = ImageTk.PhotoImage(logo)
        self.logo_img = tk.Button(self.my_canvas, image=self.logo, background=BACKGROUND_COLOR, borderwidth=0)
        self.img2 = self.my_canvas.create_window(int(my_width/5 + ((4*my_width/5)/2)), int(my_height*10/100), 
                                                anchor=tk.CENTER, window=self.logo_img)
        
        # Open the image for the logo
        logo_info = Image.open(PATH_IMAGE + "info.png")
        self.logo_info = ImageTk.PhotoImage(logo_info)
        width_logo, height_logo = logo_info.size

        # Open the image for the accept icon
        logo_accept = Image.open(PATH_IMAGE + "accept.png")
        logo_accept = logo_accept.resize((width_logo, height_logo), Image.ANTIALIAS)
        self.logo_accept = ImageTk.PhotoImage(logo_accept)

        # Open the image for the delete icon
        logo_delete = Image.open(PATH_IMAGE + "delete.png")
        logo_delete = logo_delete.resize((width_logo, height_logo), Image.ANTIALIAS)
        self.logo_delete = ImageTk.PhotoImage(logo_delete)

        # Button to enter
        def enter_handler(*args):
            self.enter_btn.destroy()
            xnat_pic_gui.choose_your_action(self)

        # enter_text = tk.StringVar()
        self.enter_btn = ttk.Button(self.my_canvas, text="ENTER", style="Accentbutton",
                                    command=enter_handler, 
                                    cursor=CURSOR_HAND)
        # enter_text.set("ENTER")
        self.my_canvas.create_window(int(my_width/5 + ((4*my_width/5)/2)), int(my_height*70/100), width = int(logo.size[0]/2), 
                                    anchor=tk.CENTER, window = self.enter_btn)
        self.root.mainloop()
            
    # Choose to upload files, fill in the info, convert files, process images
    def choose_your_action(self):

        if hasattr(xnat_pic_gui, 'img2') == False:
            self.img2 = self.my_canvas.create_window(int(my_width/5 + ((4*my_width/5)/2)), int(my_height*10/100), 
                                                anchor=tk.CENTER, window=self.logo_img)

        # Action buttons           
        # Positions for action button parametric with respect to the size of the canvas
        x_btn = int(my_width/5)
        y_btn = int(my_height)
        width_btn = int(my_width/5)

        # Convert files Bruker2DICOM
        self.convert_btn = ttk.Button(self.my_canvas, text="DICOM Converter", style="Accentbutton",
                                    command=partial(self.bruker2dicom_conversion, self), cursor=CURSOR_HAND)

        self.my_canvas.create_window(3*x_btn, y_btn*50/100, width = width_btn, anchor = tk.CENTER, window=self.convert_btn)
        Hovertip(self.convert_btn,'Convert images from Bruker ParaVision format to DICOM standard')
        
        # Fill in the info
        self.info_btn = ttk.Button(self.my_canvas, text="Project Data", style="Accentbutton", 
                                    command=partial(self.metadata, self), cursor=CURSOR_HAND)
        self.my_canvas.create_window(3*x_btn, y_btn*60/100, width = width_btn, anchor = tk.CENTER, window=self.info_btn)
        Hovertip(self.info_btn,'Fill in the information about the acquisition')

        # Upload files
        def upload_callback(*args):
            self.XNATUploader(self)
        self.upload_btn = ttk.Button(self.my_canvas, text="Uploader", style="Accentbutton", 
                                        command=upload_callback, cursor=CURSOR_HAND)
        self.my_canvas.create_window(3*x_btn, y_btn*70/100, width = width_btn, anchor = tk.CENTER, window=self.upload_btn)
        Hovertip(self.upload_btn,'Upload DICOM images to XNAT')

        # Close button
        def close_window(*args):
            self.root.destroy()
        self.close_btn = ttk.Button(self.my_canvas, text="Quit", style="Accentbutton", command=close_window,
                                        cursor=CURSOR_HAND)
        self.my_canvas.create_window(4*x_btn + x_btn/2, y_btn*90/100, width = width_btn/2, anchor=tk.CENTER, window=self.close_btn)

    def get_page(self):
        return self.root   

    class bruker2dicom_conversion():
        
        def __init__(self, master):

            self.params = {}

            try:
                destroy_widgets([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
                master.my_canvas.delete(master.img2)
            except:
                pass

            # Create new frame
            x_btn = int(my_width/5)
            y_btn = int(my_height)
            width_btn = int(my_width/5)

            # Frame Title
            self.frame_title = master.my_canvas.create_text(3*x_btn, int(y_btn*0.1), anchor=tk.CENTER, fill='black', font=("Ink Free", 36, "bold"),
                                         text="XNAT-PIC Converter")

            # Convert Project
            def convert_project_handler(*args):
                self.prj_convertion(master)
            self.prj_conv_btn = ttk.Button(master.my_canvas, text="Convert Project", style="Accentbutton",
                                        command=convert_project_handler, cursor=CURSOR_HAND)
            master.my_canvas.create_window(3*x_btn, int(y_btn*0.5), width=width_btn, anchor=tk.CENTER, window=self.prj_conv_btn)
            Hovertip(self.prj_conv_btn, "Convert a project from Bruker format to DICOM standard")

            # Convert Subject
            def convert_subject_handler(*args):
                self.sbj_convertion(master)
            self.sbj_conv_btn = ttk.Button(master.my_canvas, text="Convert Subject", style="Accentbutton",
                                         command=convert_subject_handler, cursor=CURSOR_HAND)
            master.my_canvas.create_window(3*x_btn, int(y_btn*0.6), width=width_btn, anchor=tk.CENTER, window=self.sbj_conv_btn)
            Hovertip(self.sbj_conv_btn, "Convert a subject from Bruker format to DICOM standard")

            # Convert Experiment
            def convert_experiment_handler(*args):
                self.experiment_convertion(master)
            self.exp_conv_btn = ttk.Button(master.my_canvas, text="Convert Experiment", style="Accentbutton",
                                         command=convert_experiment_handler, cursor=CURSOR_HAND)
            master.my_canvas.create_window(3*x_btn, int(y_btn*0.7), width=width_btn, anchor=tk.CENTER, window=self.exp_conv_btn)
            Hovertip(self.exp_conv_btn, "Convert an experiment from Bruker format to DICOM standard")

            # Label Frame for Checkbuttons
            self.label_frame_checkbtn = ttk.LabelFrame(master.my_canvas, text="Options")
            master.my_canvas.create_window(4*x_btn, int(y_btn*0.5), anchor=tk.W, window=self.label_frame_checkbtn)

            # Overwrite button
            self.overwrite_flag = tk.IntVar()
            self.btn_overwrite = ttk.Checkbutton(self.label_frame_checkbtn, text="Overwrite existing folders", variable=self.overwrite_flag,
                                onvalue=1, offvalue=0, style="Switch")
            self.btn_overwrite.grid(row=1, column=1, sticky=tk.W, padx=10, pady=10)
            Hovertip(self.btn_overwrite, "Overwrite already existent folders if they occur")

            # Results button
            def add_results_handler(*args):
                self.params['results_flag'] = self.results_flag.get()
            self.results_flag = tk.IntVar()
            self.btn_results = ttk.Checkbutton(self.label_frame_checkbtn, text='Copy additional files', variable=self.results_flag,
                                onvalue=1, offvalue=0, style="Switch", command=add_results_handler)
            self.btn_results.grid(row=2, column=1, sticky=tk.W, padx=10, pady=10)
            Hovertip(self.btn_results, "Copy additional files (results, parametric maps, graphs, ...)\ninto converted folders")

            # EXIT Button 
            def exit_converter():
                result = messagebox.askquestion("XNAT-PIC Converter", "Do you want to exit?", icon='warning')
                if result == 'yes':
                    # Destroy all the existent widgets (Button, Checkbutton, ...)
                    destroy_widgets([self.prj_conv_btn, self.sbj_conv_btn, self.exp_conv_btn, self.exit_btn,
                                        self.label_frame_checkbtn])
                    delete_widgets(master.my_canvas, [self.frame_title])
                    # Restore the main frame
                    xnat_pic_gui.choose_your_action(master)

            self.exit_btn = ttk.Button(master.my_canvas, text="Exit", style="Accentbutton", cursor=CURSOR_HAND)
            self.exit_btn.configure(command=exit_converter)
            master.my_canvas.create_window(4*x_btn + x_btn/2, y_btn*0.9, anchor=tk.CENTER, width=int(width_btn/2), window=self.exit_btn)
            
        def prj_convertion(self, master):

            # Disable the buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

            # Ask for project directory
            init_dir = os.path.expanduser("~").replace('\\', '/') + '/Desktop/Dataset'
            self.project_to_convert = filedialog.askdirectory(parent=master.root, initialdir=init_dir, 
                                                            title="XNAT-PIC: Select project directory in Bruker ParaVision format")
            # Check for the chosen directory
            if not self.project_to_convert:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder does not exists. Please select an other one.")
                return

            if glob(self.project_to_convert + '/**/**/**/**/**/2dseq', recursive=False) == []:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not project related")
                return
            
            master.root.deiconify()
            master.root.update()
            # Define the project destination folder
            self.prj_dst = self.project_to_convert + '_dcm'

            # Initialize converter class
            self.converter = Bruker2DicomConverter(self.params)

            def prj_converter():

                # Get the list of the subject into the project
                list_sub_init = os.listdir(self.project_to_convert)
                list_sub = [dir for dir in list_sub_init if os.path.isdir(os.path.join(self.project_to_convert, dir).replace('\\', '/'))]
                # Initialize the list of conversion errors
                self.conversion_err = []
                # Loop over subjects
                for j, dir in enumerate(list_sub, 0):
                    # Define the current subject path 
                    current_folder = os.path.join(self.project_to_convert, dir).replace('\\', '/')
                    if os.path.isdir(current_folder):
                        # Show the current step on the progress bar
                        progressbar.show_step(j + 1, len(list_sub))
                        # Update the current step of the progress bar
                        progressbar.update_progressbar(j, len(list_sub))

                        current_dst = os.path.join(self.prj_dst, dir).replace('\\', '/')
                        # Check if the current subject folder already exists
                        if os.path.isdir(current_dst):
                            # Case 1 --> The directory already exists
                            if self.overwrite_flag == 1:
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

                        for k, exp in enumerate(list_exp):
                            exp_folder = os.path.join(current_folder, exp).replace('\\', '/')
                            if os.path.isdir(exp_folder):
                                print('Converting ' + str(exp))
                                exp_dst = os.path.join(current_dst, exp).replace('\\','/')
                                list_scans = self.converter.get_list_of_folders(exp_folder, exp_dst)

                                # Start the multiprocessing conversion: one pool per each scan folder
                                with Pool(processes=int(cpu_count() - 1)) as pool:
                                    pool.map(self.converter.convert, list_scans)

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
                progressbar.update_bar(0.000001)
            else:
                progressbar.stop_progress_bar()
            
            end_time = time.time()
            print('Total elapsed time: ' + str(end_time - start_time) + ' s')

            messagebox.showinfo("XNAT-PIC Converter","The conversion of the project is done!\n\n\n\n"
                                "Exceptions:\n\n" +
                                str([str(x) for x in self.conversion_err])[1:-1])
            enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])        
                
        def sbj_convertion(self, master):

            # Convert from bruker to DICOM and disable the buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

            # Ask for subject directory
            self.subject_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), 
                                                            title="XNAT-PIC: Select subject directory in Bruker ParaVision format")
            # Check for chosen directory
            if not self.subject_to_convert:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            if glob(self.subject_to_convert + '/**/**/**/**/2dseq', recursive=False) == []:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not subject related")
                return

            master.root.deiconify()
            master.root.update()
            head, tail = os.path.split(self.subject_to_convert)
            head = head + '_dcm'
            project_foldername = tail.split('.',1)[0]
            self.sub_dst = os.path.join(head, project_foldername).replace('\\', '/')

            # Start converter
            self.converter = Bruker2DicomConverter(self.params)

            # If the destination folder already exists throw exception, otherwise create the new folder
            if os.path.isdir(self.sub_dst):
                # Case 1 --> The directory already exists
                if self.overwrite_flag == 1:
                    # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                    shutil.rmtree(self.sub_dst)
                    os.makedirs(self.sub_dst)
                else:
                    # Existent folder without overwriting flag set to 0 --> ignore folder
                    messagebox.showerror("XNAT-PIC Converter", "Destination folder %s already exists" % self.sub_dst)
                    return
            else:
                # Case 2 --> The directory does not exist
                if self.sub_dst.split('/')[-1].count('_dcm') >= 1:
                    # Check to avoid already converted folders
                    messagebox.showerror("XNAT-PIC Converter", "Chosen folder %s already converted" % self.sub_dst)
                    return
                else:
                    # Create the new destination folder
                    os.makedirs(self.sub_dst)

            def sbj_converter():

                list_exp = os.listdir(self.subject_to_convert)
                for k, exp in enumerate(list_exp):
                    progressbar.show_step(k + 1, len(list_exp))
                    progressbar.update_progressbar(k + 1, len(list_exp))
                    print('Converting ' + str(exp))
                    exp_folder = os.path.join(self.subject_to_convert, exp).replace('\\','/')
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
            enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])   

        def experiment_convertion(self, master):

            # Convert from bruker to DICOM and disable the buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

            # Ask for subject directory
            self.experiment_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), 
                                                            title="XNAT-PIC: Select experiment directory in Bruker ParaVision format")
            # Check for chosen directory
            if not self.experiment_to_convert:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            if glob(self.experiment_to_convert + '/**/**/**/2dseq', recursive=False) == []:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                messagebox.showerror("XNAT-PIC Converter", "The selected folder is not experiment related")
                return

            master.root.deiconify()
            master.root.update()
            head, tail = os.path.split(self.experiment_to_convert)
            head2, tail2 = os.path.split(head)
            head2 = head2 + '_dcm'
            self.exp_dst = os.path.join(head2, tail2, tail).replace('\\', '/')

            # Initialize converter class
            self.converter = Bruker2DicomConverter(self.params)

            def exp_converter():
                list_scans = self.converter.get_list_of_folders(self.experiment_to_convert, self.exp_dst)
    
                progressbar.set_caption('Converting ' + str(self.experiment_to_convert.split('/')[-1]) + ' ...')
                with Pool(processes=int(cpu_count() - 1)) as pool:
                    pool.map(self.converter.convert, list_scans)
                progressbar.set_caption('Converting ' + str(self.experiment_to_convert.split('/')[-1]) + ' ...done!')

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
            enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                 
    # Fill in information
    class metadata():

        def __init__(self, master):

            # Disable all buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

            # Choose your directory
            self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")
            
            # If there is no folder selected, re-enable the buttons and return
            if not self.information_folder:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                return
            
            self.project_name = (self.information_folder.rsplit("/",1)[1])
            self.tmp_dict = {}
            self.results_dict = {}
            
        # Scommenta per la gestione dei due progetti
            self.frame_metadata(master)
        #     # Ask about the architecture of the project
        #     self.my_popup = tk.Toplevel()
        #     self.my_popup.title("XNAT-PIC ~ Metadata")
        #     self.my_popup.geometry("%dx%d+%d+%d" % (550, 200, my_width/3, my_height/4))

        #    # Closing window event: if it occurs, the popup must be destroyed and the main frame buttons must be enabled
        #     def closed_window():
        #         self.my_popup.destroy()
        #         #Enable all buttons
        #         enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
        #     self.my_popup.protocol("WM_DELETE_WINDOW", closed_window)

        #     self.radioValue = tk.IntVar() 
        #     rdioOne = tk.Radiobutton(self.my_popup, text='P-S', variable=self.radioValue, value=0) 
        #     rdioTwo = tk.Radiobutton(self.my_popup, text='P-S-E', variable=self.radioValue, value=1)
        #     next_btn = tk.Button(self.my_popup, text="Next", font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH,  command=partial(self.frame_metadata, master), cursor=CURSOR_HAND, takefocus = 0) 
        #     rdioOne.grid(column=0, row=0, sticky="W")
        #     rdioTwo.grid(column=0, row=1, sticky="W")
        #     next_btn.grid(column=0, row=2, sticky="W")
        
        def frame_metadata(self, master):   
            #flag = self.radioValue.get()
            #self.my_popup.destroy()
            flag = 1
             
            # Load the acq. date from visu_pars file for Bruker file or from DICOM
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
                    # Architecture of the project: project-subject
                    if flag == 0:
                        self.path_list.append(path)
                    # Architecture of the project: project-subject-experiment
                    elif flag==1:
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
                if flag == 0:
                    prj = str(path).rsplit("/",2)[2]
                    sub = str(path).rsplit("/",2)[1]
                    exp = prj
                    name = exp + "_" + "Custom_Variables.txt"
                    keys =  exp
                elif flag ==1:
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
            #master.process_btn.destroy()
            destroy_widgets([master.convert_btn.destroy(), master.info_btn.destroy(), master.upload_btn.destroy()])
            #################### Menu ###########################
            self.menu = tk.Menu(master.root)
            file_menu = tk.Menu(self.menu, tearoff=0)
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
            x_folder_list = int(my_width*23/100)
            y_folder_list = int(my_height*5/100)
            self.label = tk.Label(master.my_canvas, text='Selected Project: ' + self.project_name, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR, font = LARGE_FONT)
            master.my_canvas.create_window(x_folder_list, y_folder_list, width = int(my_width*75/100), height = int(my_height*7/100), anchor=tk.NW, window=self.label)
            
            # self.my_listbox = tk.Listbox(master.my_canvas, selectmode=SINGLE, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, font=SMALL_FONT, takefocus = 0)
            # master.my_canvas.create_window(x_folder_list, y_folder_list1, width = int(my_width*25/100), height = int(my_height*40/100) ,anchor = tk.NW, window = self.my_listbox)

            # # List of subject in the project in the listbox
            # self.my_listbox.insert(tk.END, *self.results_dict.keys())

            # # Attach listbox to x and y scrollbar ()
            # x_folder_scrollbar = int(my_width*8/100)
            # self.my_yscrollbar = tk.Scrollbar(master.my_canvas, orient="vertical")
            # self.my_listbox.config(yscrollcommand = self.my_yscrollbar.set)
            # self.my_yscrollbar.config(command = self.my_listbox.yview)
            # master.my_canvas.create_window(x_folder_scrollbar, y_folder_list1, height = int(my_height*40/100), anchor = tk.NW, window = self.my_yscrollbar)
            
            # y_folder_scrollbar = int(my_height*66/100)
            # self.my_xscrollbar = tk.Scrollbar(master.my_canvas, orient="horizontal")
            # self.my_listbox.config(xscrollcommand = self.my_xscrollbar.set)
            # self.my_xscrollbar.config(command = self.my_listbox.xview)
            # master.my_canvas.create_window(x_folder_list, y_folder_scrollbar, width = int(my_width*25/100), anchor = tk.NW, window = self.my_xscrollbar)
            
            y_folder_list1 = int(my_height*15/100)
            h_notebook = int(my_height*55/100)
            SMALL_FONT_3 = ("Calibri", 12)
            self.my_listbox = []
            style = ttk.Style()

            try:
                style.theme_create( "dummy", parent="clam", settings={
                "TNotebook": {
                    "configure": {"tabmargins": [2, 5, 2, 0] ,
                                "background": THEME_COLOR }},
                "TNotebook.Tab": {
                    "configure": {"padding": [5, 1], "background": THEME_COLOR, "font" : SMALL_FONT_3},
                    "map":       {"background": [("selected", BG_BTN_COLOR_2)],
                                "foreground": [("selected", "white")],
                                "expand": [("selected", [1, 1, 1, 0])] } } } )
            except:
                pass
            style.theme_use("dummy")
            self.notebook = ttk.Notebook(master.my_canvas)
            master.my_canvas.create_window(x_folder_list, y_folder_list1,width = int(my_width*20.9/100), height = h_notebook ,anchor = tk.NW, window=self.notebook)
            for key, value in self.todos.items():
                frame = ttk.Frame(self.notebook)
                self.notebook.add(frame, text=key, underline=0, sticky=tk.NE + tk.SW)
                self.my_listbox.append(tk.Listbox(frame, font=SMALL_FONT_3, selectmode=SINGLE, takefocus = 0))
                self.my_listbox[-1].insert(tk.END, *value)
                self.my_listbox[-1].pack(fill='both', expand=1)
                # Yscrollbar
                self.my_yscrollbar = tk.Scrollbar(self.my_listbox[-1], orient="vertical")
                self.my_listbox[-1].config(yscrollcommand = self.my_yscrollbar.set)
                self.my_yscrollbar.config(command = self.my_listbox[-1].yview)
                self.my_yscrollbar.pack(fill='y', side='right')
                # Xscrollbar
                self.my_xscrollbar = tk.Scrollbar(self.my_listbox[-1], orient="horizontal")
                self.my_listbox[-1].config(xscrollcommand = self.my_xscrollbar.set)
                self.my_xscrollbar.config(command = self.my_listbox[-1].xview)
                self.my_xscrollbar.pack(fill='x', side='bottom')
            self.notebook.enable_traversal()

            #self.notebook.bind("<<NotebookTabChanged>>", self.select_tab)
                    
            # y_folder_scrollbar = int(my_height*66/100)
            # self.my_xscrollbar = tk.Scrollbar(master.my_canvas, orient="horizontal")
            # self.notebook.config(xscrollcommand = self.my_xscrollbar.set)
            # self.my_xscrollbar.config(command = self.notebook.xview)
            # self.my_xscrollbar.pack(fill='x')
            # master.my_canvas.create_window(x_folder_list, y_folder_scrollbar, width = int(my_width*25/100), anchor = tk.NW, window = self.my_xscrollbar)
  
            #################### Subject form ####################
            # ID
            # Label frame for ID: folder selected, project, subject and acq. date
            self.label_frame_ID = tk.LabelFrame(master.my_canvas, background = BACKGROUND_COLOR, borderwidth=5, font=SMALL_FONT, relief='solid', text="ID")

            #
            x_lbl_ID = int(my_width*44/100)
            y_lbl_ID = y_folder_list1
            w_lbl_ID = int(my_width*51/100)
            h_lbl_ID = int(my_height*32/100)
            #
            # Scroll bar in the Label frame ID
            self.canvas_ID = tk.Canvas(self.label_frame_ID, borderwidth=0, bg=BACKGROUND_COLOR, highlightbackground=BACKGROUND_COLOR)
            self.frame_ID = tk.Frame(self.canvas_ID, bg=BACKGROUND_COLOR)
            self.vsb_ID = tk.Scrollbar(self.label_frame_ID, orient="vertical", command=self.canvas_ID.yview)
            self.canvas_ID.configure(yscrollcommand=self.vsb_ID.set, width=w_lbl_ID, height=h_lbl_ID)       

            self.vsb_ID.pack(side="right", fill="y")
            self.canvas_ID.pack(side="left", fill="both", expand=True)
            self.canvas_ID.create_window((0,0), window=self.frame_ID, anchor="nw")

            # Be sure that we call OnFrameConfigure on the right canvas
            self.frame_ID.bind("<Configure>", lambda event, canvas=self.canvas_ID: OnFrameConfigure(canvas))
            master.my_canvas.create_window(x_lbl_ID, y_lbl_ID, anchor='nw', height = h_lbl_ID, window=self.label_frame_ID)
            
            def OnFrameConfigure(canvas):
                    canvas.configure(scrollregion=canvas.bbox("all"))

            keys_ID = ["Folder", "Project", "Subject", "Experiment", "Acq. date"]
            # Entry ID 
            self.entries_variable_ID = []  
            self.entries_value_ID = []          
            count = 0
            for key in keys_ID:
                # Variable
                self.entries_variable_ID.append(tk.Entry(self.frame_ID, disabledbackground= BACKGROUND_COLOR, disabledforeground= "black",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                self.entries_variable_ID[-1].insert(0, key)
                self.entries_variable_ID[-1]['state'] = 'disabled'
                self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                # Value
                if key == "Acq. date":
                    self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, state='disabled', takefocus = 0, width=20))
                    self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=NW)
                else:
                    self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, state='disabled', takefocus = 0, width=44))
                    self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                count += 1

            # Calendar for acq. date
            self.cal = DateEntry(self.frame_ID, state = tk.DISABLED, width=11, font = SMALL_FONT_3, background=BG_BTN_COLOR_2, date_pattern = 'y-mm-dd', foreground='white', borderwidth=0, selectbackground = BG_BTN_COLOR_2, selectforeground = "black")
            self.cal.delete(0, tk.END)
            self.cal.grid(row=4, column=1, padx = 5, pady = 5, sticky=NE)

            ####################################################################
            # Custom Variables (CV)
            # Label frame for Custom Variables: group, dose, timepoint
            self.label_frame_CV = tk.LabelFrame(master.my_canvas, background = BACKGROUND_COLOR, borderwidth=5, font=SMALL_FONT, relief='solid', text="Custom Variables")
            x_lbl_CV = x_lbl_ID
            y_lbl_CV = int(my_height*50/100)
            h_lbl_CV = int(my_height*20/100)
            w_lbl_CV = int(my_width*53/100)

            # Scroll bar in the Label frame CV
            self.canvas_CV = tk.Canvas(self.label_frame_CV, borderwidth=0, bg=BACKGROUND_COLOR, highlightbackground=BACKGROUND_COLOR)
            self.frame_CV = tk.Frame(self.canvas_CV, bg=BACKGROUND_COLOR)
            self.vsb_CV = tk.Scrollbar(self.label_frame_CV, orient="vertical", command=self.canvas_CV.yview)
            self.canvas_CV.configure(yscrollcommand=self.vsb_CV.set, width=w_lbl_CV, height=h_lbl_CV)       

            self.vsb_CV.pack(side="right", fill="y")
            self.canvas_CV.pack(side="left", fill="both", expand=True)
            self.canvas_CV.create_window((0,0), window=self.frame_CV, anchor="nw")

            # Be sure that we call OnFrameConfigure on the right canvas
            self.frame_CV.bind("<Configure>", lambda event, canvas=self.canvas_CV: OnFrameConfigure(canvas))
            
            master.my_canvas.create_window(x_lbl_CV, y_lbl_CV, height = h_lbl_CV, width=w_lbl_CV, window=self.label_frame_CV, anchor='nw')
            def OnFrameConfigure(canvas):
                    canvas.configure(scrollregion=canvas.bbox("all"))

            keys_CV = ["Group", "Timepoint", "Dose",]
            # Entry CV  
            self.entries_variable_CV = []  
            self.entries_value_CV = []          
            count = 0
            for key in keys_CV:
                # Variable
                self.entries_variable_CV.append(tk.Entry(self.frame_CV, disabledbackground= BACKGROUND_COLOR, disabledforeground= "black",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                self.entries_variable_CV[-1].insert(0, key)
                self.entries_variable_CV[-1]['state'] = 'disabled'
                self.entries_variable_CV[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                # Value
                self.entries_value_CV.append(tk.Entry(self.frame_CV, font=SMALL_FONT, state='disabled', takefocus = 0, width=25))
                self.entries_value_CV[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                count += 1

            # Group Menu
            OPTIONS = ["untreated", "treated"]
            self.selected_group = tk.StringVar()
            self.group_menu = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_group, width=10)
            self.group_menu['values'] = OPTIONS
            self.group_menu['state'] = 'disabled'
            self.group_menu.grid(row=0, column=2, padx = 5, pady = 5, sticky=W)
            
            # UM for dose
            self.OPTIONS_UM = ["Mg", "kg", "mg", "µg", "ng"]
            self.selected_dose = tk.StringVar()
            self.dose_menu = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_dose, width=10)
            self.dose_menu['values'] = self.OPTIONS_UM
            self.dose_menu['state'] = 'disabled'
            self.dose_menu.grid(row=2, column=2, padx = 5, pady = 5, sticky=W)

            # Timepoint
            self.OPTIONS = ["pre", "post"]
            self.selected_timepoint = tk.StringVar()
            self.timepoint_menu = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_timepoint, width=10)
            self.timepoint_menu['values'] = self.OPTIONS
            self.timepoint_menu['state'] = 'disabled'
            self.timepoint_menu.grid(row=1, column=2, padx = 5, pady = 5, sticky=W)

            self.time_entry = tk.Entry(self.frame_CV, font = SMALL_FONT, state='disabled', takefocus = 0, width=5)
            self.time_entry.grid(row=1, column=3, padx = 5, pady = 5, sticky=W)

            self.OPTIONS1 = ["seconds", "minutes", "hours", "days", "weeks", "months", "years"]
            self.selected_timepoint1 = tk.StringVar()
            self.timepoint_menu1 = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_timepoint1, width=7)
            self.timepoint_menu1['values'] = self.OPTIONS1
            self.timepoint_menu1['state'] = 'disabled'
            self.timepoint_menu1.grid(row=1, column=4, padx = 5, pady = 5, sticky=W)

            #################### Load the info about the selected subject ####################
            def select_tab(event):
               tab_id = self.notebook.select()
               self.tab_name = self.notebook.tab(tab_id, "text")
               self.load_info(master)

            self.notebook.bind("<<NotebookTabChanged>>", select_tab)  
            #################### Modify the metadata ####################
            modify_text = tk.StringVar() 
            self.modify_btn = tk.Button(master.my_canvas, textvariable=modify_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, borderwidth=BORDERWIDTH, command = lambda: self.modify_metadata(), cursor=CURSOR_HAND, takefocus = 0)
            modify_text.set("Modify")
            #x_lbl =x_folder_list
            x_lbl = int(my_width*35/100)
            y_btn = int(my_height*78/100)
            width_btn = int(my_width*16/100)
            master.my_canvas.create_window(x_lbl, y_btn, anchor = tk.NW, width = width_btn, window = self.modify_btn)

            #################### Confirm the metadata ####################
            confirm_text = tk.StringVar() 
            self.confirm_btn = tk.Button(master.my_canvas, textvariable=confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, borderwidth=BORDERWIDTH, command = lambda: self.confirm_metadata(), cursor=CURSOR_HAND, takefocus = 0)
            confirm_text.set("Confirm")
            #x_conf_btn = int(my_width*52/100)
            x_conf_btn = int(my_width*65/100)
            master.my_canvas.create_window(x_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = self.confirm_btn)

            #################### Confirm multiple metadata ####################
            # multiple_confirm_text = tk.StringVar() 
            # self.multiple_confirm_btn = tk.Button(master.my_canvas, textvariable=multiple_confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: self.confirm_multiple_metadata(), cursor=CURSOR_HAND, takefocus = 0)
            # multiple_confirm_text.set("Multiple Confirm")
            # x_multiple_conf_btn = int(my_width*81/100)
            # master.my_canvas.create_window(x_multiple_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = self.multiple_confirm_btn)
                       
        def load_info(self, master):

            def items_selected(event):
                # Clear all the combobox and the entry
                self.selected_group.set('')
                self.selected_timepoint.set('')
                self.selected_timepoint1.set('')
                self.dose_menu.set('')
                self.time_entry.delete(0, tk.END)
                self.cal.delete(0, tk.END)
                disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.cal])

                # Delete entries
                for i in range(0, len(self.entries_value_ID)):
                    self.entries_variable_ID[i].destroy()
                    self.entries_value_ID[i].destroy()

                for i in range(0, len(self.entries_value_CV)):
                    self.entries_variable_CV[i].destroy()
                    self.entries_value_CV[i].destroy()
                """ handle item selected event
                """
                # Get selected index
                self.selected_index = self.my_listbox[self.index_tab].curselection()
                self.selected_folder_tmp = self.my_listbox[self.index_tab].get(self.selected_index)
                self.selected_folder = self.tab_name + '#' +self.selected_folder_tmp
                ID = True
                count = 1
                self.entries_variable_ID = []
                self.entries_variable_ID.append(tk.Entry(self.frame_ID, disabledbackground= BACKGROUND_COLOR, disabledforeground= "black",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                self.entries_variable_ID[-1].insert(0, "Folder")
                self.entries_variable_ID[-1]['state'] = 'disabled'
                self.entries_variable_ID[-1].grid(row=0, column=0, padx = 5, pady = 5, sticky=W)
                self.entries_variable_CV = []
                self.entries_value_ID = []
                self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, takefocus = 0, width=44))
                self.entries_value_ID[-1].insert(0, self.selected_folder)
                self.entries_value_ID[-1]['state'] = 'disabled'
                self.entries_value_ID[-1].grid(row=0, column=1, padx = 5, pady = 5, sticky=W)
                self.entries_value_CV = []
                for k, v in dict(self.results_dict[self.selected_folder]).items():
                    if v is None:
                        v = ''
                    if k == "C_V":
                        ID = False
                        count = 0
                    if ID:
                        self.entries_variable_ID.append(tk.Entry(self.frame_ID, disabledbackground= BACKGROUND_COLOR, disabledforeground= "black",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                        self.entries_variable_ID[-1].insert(0, k)
                        self.entries_variable_ID[-1]['state'] = 'disabled'
                        self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                        # Value
                        if k == "Acquisition_date":
                            self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, takefocus = 0, width=20))
                            self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=NW)
                        else:
                            self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, takefocus = 0, width=44))
                            self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                        self.entries_value_ID[-1].insert(0, v)
                        self.entries_value_ID[-1]['state'] = 'disabled'
    
                        count += 1
                        
                    else:
                        if k != "C_V":
                            self.entries_variable_CV.append(tk.Entry(self.frame_CV, disabledbackground= BACKGROUND_COLOR, disabledforeground= "black",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                            self.entries_variable_CV[-1].insert(0, k)
                            self.entries_variable_CV[-1]['state'] = 'disabled'
                            self.entries_variable_CV[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                            # Value
                            self.entries_value_CV.append(tk.Entry(self.frame_CV, font=SMALL_FONT, takefocus = 0, width=25))
                            self.entries_value_CV[-1].insert(0, v)
                            self.entries_value_CV[-1]['state'] = 'disabled'
                            self.entries_value_CV[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                            count += 1

            self.index_tab = list(self.todos).index(self.tab_name)
            self.my_listbox[self.index_tab].bind('<Tab>', items_selected)

        def modify_metadata(self):
                # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 

            # Normal entry
            for i in range(1, len(self.entries_value_ID)):
                self.entries_value_ID[i]['state'] = 'normal'

            for i in range(0, len(self.entries_value_CV)):
                self.entries_value_CV[i]['state'] = 'normal'
            # Acquisition date has a default format in entry but you can modify date with the calendar
            self.cal['state'] = 'normal'
            
            def date_entry_selected(event):
                w = event.widget
                self.entries_value_ID[4]['state'] = tk.NORMAL
                self.entries_value_ID[4].delete(0, tk.END)
                self.entries_value_ID[4].insert(0, str(w.get_date()))
                self.entries_value_ID[4]['state'] = tk.DISABLED
                self.my_listbox[self.index_tab].selection_set(self.selected_index)

            self.cal.bind("<<DateEntrySelected>>", date_entry_selected)

            # Option menu for the group
            self.group_menu['state'] = 'readonly'

            def group_changed(event):
                """ handle the group changed event """
                self.entries_value_CV[0].delete(0, tk.END)
                self.entries_value_CV[0].insert(0, str(self.selected_group.get()))                    
                self.my_listbox[self.index_tab].selection_set(self.selected_index)

            self.group_menu.bind("<<ComboboxSelected>>", group_changed)

            # Option menu for the dose
            self.dose_menu['state'] = 'readonly'

            def dose_changed(event):
                """ handle the dose changed event """
                dose_str = ''
                if self.entries_value_CV[2].get():
                    for word in filter(str(self.entries_value_CV[2].get()).__contains__, self.OPTIONS_UM):
                        # If a unit of measurement is already present, replace it
                        dose_str = str(self.entries_value_CV[2].get()).replace(word, str(self.selected_dose.get()))
                        self.entries_value_CV[2].delete(0, tk.END)     
                        self.entries_value_CV[2].insert(0, dose_str)                    
                        self.my_listbox[self.index_tab].selection_set(self.selected_index)
                        return
                            # If only the number is present, add the unit of measure
                    dose_str = str(self.entries_value_CV[2].get()) + "-" + str(self.selected_dose.get())
                else:
                    # If the entry is empty, enter only the unit of measure
                    dose_str = str(self.selected_dose.get())

                self.entries_value_CV[2].delete(0, tk.END)     
                self.entries_value_CV[2].insert(0, dose_str)                    
                self.my_listbox[self.index_tab].selection_set(self.selected_index)

            self.dose_menu.bind("<<ComboboxSelected>>", dose_changed)
            
            # Option menu for the timepoint
            self.timepoint_menu1['state'] = 'readonly'
            self.time_entry['state'] = 'normal'
            self.timepoint_menu['state'] = 'readonly'

            def timepoint_changed(event):
                self.entries_value_CV[1].config(state=tk.NORMAL)
                """ handle the timepoint changed event """
                if str(self.time_entry.get()) or str(self.selected_timepoint1.get()):
                    timepoint_str = str(self.selected_timepoint.get()) + "-" + str(self.time_entry.get()) + "-" + str(self.selected_timepoint1.get())
                else:
                    timepoint_str = str(self.selected_timepoint.get()) 

                self.my_listbox[self.index_tab].selection_set(self.selected_index)

                if self.time_entry.get():
                    try:
                        float(self.time_entry.get())
                    except Exception as e: 
                        messagebox.showerror("XNAT-PIC", "Insert a number in the timepoint entry")

                self.entries_value_CV[1].delete(0, tk.END)
                self.entries_value_CV[1].insert(0, timepoint_str)
                self.entries_value_CV[1].config(state=tk.DISABLED)

            self.timepoint_menu.bind("<<ComboboxSelected>>", timepoint_changed)
            self.time_entry.bind("<Return>", timepoint_changed)
            self.timepoint_menu1.bind("<<ComboboxSelected>>", timepoint_changed)

        def check_entries(self):
            # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 

            if not self.entries_value_ID[1].get():
                messagebox.showerror("XNAT-PIC", "Insert the name of the project")
                raise 

            if not self.entries_value_ID[2].get():
                messagebox.showerror("XNAT-PIC", "Insert the name of the subject")
                raise

            if self.entries_value_ID[3].get():
                try:
                    datetime.datetime.strptime(self.entries_value_ID[4].get(), '%Y-%m-%d')
                except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Incorrect data format in acquisition date, should be YYYY-MM-DD")
                    raise

            if self.entries_value_CV[1].get() and '-' in  self.entries_value_CV[1].get(): 
                if not str(self.entries_value_CV[1].get()).split('-')[0] in self.OPTIONS:
                    messagebox.showerror("XNAT-PIC", "Select pre/post in timepoint")
                    raise
                if not str(self.entries_value_CV[1].get()).split('-')[2] in self.OPTIONS1:
                    messagebox.showerror("XNAT-PIC", "Select seconds, minutes, hours, days, weeks, months, years in timepoint")
                    raise

                input_num = str(self.entries_value_CV[1].get()).split('-')[1]
                try:
                    float(input_num)
                except Exception as e: 
                    messagebox.showerror("XNAT-PIC", "Insert a number in timepoint between pre/post and seconds, minutes, hours..")  
                    raise

        def confirm_metadata(self):
            self.check_entries()
            
            tmp_ID = {}
            # Update the info in the txt file ID
            for i in range(1, len(self.entries_variable_ID)):
                tmp_ID.update({self.entries_variable_ID[i].get() : self.entries_value_ID[i].get()})     
                self.entries_variable_ID[i]['state'] = tk.DISABLED
                self.entries_value_ID[i]['state'] = tk.DISABLED 
            
            tmp_ID.update({"C_V" : ""}) 

            # Update the info in the txt file CV
            for i in range(0, len(self.entries_variable_CV)):
                tmp_ID.update({self.entries_variable_CV[i].get() : self.entries_value_CV[i].get()})     
                self.entries_variable_CV[i]['state'] = tk.DISABLED
                self.entries_value_CV[i]['state'] = tk.DISABLED 

            self.results_dict[self.selected_folder].update(tmp_ID)
            
            # Clear all 
            self.selected_group.set('')
            self.selected_dose.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.time_entry.delete(0, tk.END)
            self.cal.delete(0, tk.END)
            disable_buttons([self.dose_menu, self.group_menu, self.timepoint_menu, self.time_entry, self.timepoint_menu1, self.cal])
            # Saves the changes made by the user in the txt file
            substring = str(self.selected_folder).replace('#','/')
            index = [i for i, s in enumerate(self.path_list) if substring in s]
            name_txt = str(self.selected_folder).rsplit('#', 1)[1] + "_" + "Custom_Variables.txt"
            tmp_path = self.path_list[index[0]] + "\\" + name_txt
            try:
                with open(tmp_path.replace('\\', '/'), 'w+') as meta_file:
                    meta_file.write(tabulate(self.results_dict[self.selected_folder].items(), headers=['Variable', 'Value']))
            except Exception as e: 
                    messagebox.showerror("XNAT-PIC", "Confirmation failed: " + str(e))  
                    raise    
            #################### Confirm multiple metadata ####################
            # def normal_button():
            #     #clear_btn["state"] = tk.NORMAL
            #     #save_btn["state"] = tk.NORMAL
            #     enable_buttons([modify_btn, confirm_btn, multiple_confirm_btn])

        def confirm_multiple_metadata(self):
            #clear_btn["state"] = tk.DISABLED
            print("TODO")
            #disable_buttons([modify_btn, confirm_btn, multiple_confirm_btn])
            #save_btn["state"] = tk.DISABLED
            
            # try:
            #     self.selected_folder
            #     pass
            # except Exception as e:
            #         normal_button()
            #         messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
            #         raise

            # messagebox.showinfo("Metadata","1. Select the folders from the box on the left for which to copy the info entered!\n 2. Always remaining in the box on the left, press ENTER to confirm or ESC to cancel!")

            # my_listbox.selection_set(self.selected_folder)    
            # my_listbox['selectmode'] = MULTIPLE
            
            # # The user presses 'enter' to confirm 
            # def items_selected2(event):
                
            #     seltext = [my_listbox.get(index) for index in my_listbox.curselection()]
            #     result = messagebox.askquestion("Multiple Confirm", "Are you sure you want to save data for the following folders?\n" + '\n'.join(seltext), icon='warning')
            #     if result == 'yes':
            #        confirm_metadata(self)
            #     # Get indexes of selected folders
            #     selected_text_list = my_listbox.curselection()
                
            #     # Update the list of results
            #     max_lim = len(fields)
            #     for i in range(0, len(selected_text_list)):
            #             for j in range(0, max_lim):
            #                 results[selected_text_list[i]*max_lim+j] =  entries[j].get()

            #     # Update the txt file
            #     for i in range(0, len(selected_text_list)):
            #             with open(path_list[selected_text_list[i]], 'w+') as meta_file:
            #                                 meta_file.write(tabulate([['Project', str(results[self.selected_folder*max_lim+0])], ['Subject', str(results[self.selected_folder*max_lim+1])], ['Acquisition_date', str(results[self.selected_folder*max_lim+2])], 
                
            #                                 ['Group', str(results[self.selected_folder*max_lim+3])], ['Dose', str(results[self.selected_folder*max_lim+4])], ['Timepoint', str(results[self.selected_folder*max_lim+5])]], headers=['Variable', 'Value']))
                
            #     messagebox.showinfo("Metadata","The information has been saved for the selected folders!")

            #     # Clear the focus and the select mode of the listbox is single
            #     normal_button()
            #     my_listbox.selection_clear(0, 'end')
            #     my_listbox['selectmode'] = SINGLE
                

            # my_listbox.bind("<Return>", items_selected2)
            
            # # The user presses 'esc' to cancel
            # def items_cancel(event):
            #         # Clear the focus and the select mode of the listbox is single
            #     messagebox.showinfo("Metadata","The information was not saved for the selected folders!")
            #     normal_button()
            #     my_listbox.selection_clear(0, 'end')
            #     my_listbox['selectmode'] = SINGLE
            # my_listbox.bind("<Escape>", items_cancel)
                
        #################### Add ID #################
        def add_ID(self, master):
             # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 
            # Disable btns
            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
            # I use len(all_entries) to get nuber of next free row
            next_row = len(self.entries_variable_ID)
            
            # Add entry variable ID
            ent_variable = tk.Entry(self.frame_ID, bg="white", borderwidth=0, disabledbackground= BACKGROUND_COLOR, disabledforeground= "black", highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15)
            ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
            self.entries_variable_ID.append(ent_variable)                 

            # Add entry value ID in second col
            ent_value = tk.Entry(self.frame_ID, font=SMALL_FONT, takefocus = 0, width=44)
            ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
            self.entries_value_ID.append(ent_value)

            # Confirm
            def confirm_ID(next_row):
                pos = list(self.results_dict[self.selected_folder].keys()).index('C_V')
                items = list(self.results_dict[self.selected_folder].items())
                items.insert(pos, (self.entries_variable_ID[next_row].get(), self.entries_value_ID[next_row].get()))
                self.results_dict[self.selected_folder] = dict(items)
                state = self.entries_value_ID[1]['state']
                self.entries_variable_ID[next_row]['state'] = tk.DISABLED
                self.entries_value_ID[next_row]['state'] = state
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
                btn_confirm_ID.destroy()
                btn_reject_ID.destroy()
                 
            btn_confirm_ID = tk.Button(self.frame_ID, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=lambda: confirm_ID(next_row), cursor=CURSOR_HAND)
            btn_confirm_ID.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=NW)

            # Delete
            def reject_ID(next_row):
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
                self.entries_variable_ID[next_row].destroy()
                self.entries_value_ID[next_row].destroy()
                btn_confirm_ID.destroy()
                btn_reject_ID.destroy()
            btn_reject_ID = tk.Button(self.frame_ID, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=lambda: reject_ID(next_row), cursor=CURSOR_HAND)
            btn_reject_ID.grid(row=next_row, column=3, padx = 5, pady = 5, sticky=NW)


        #################### Add Custom Variable #################
        def add_custom_variable(self, master):
             # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 
            # Disable btns
            disable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
            # I get number of next free row
            next_row = len(self.entries_variable_CV)
            
            # Add entry variable CV
            ent_variable = tk.Entry(self.frame_CV, bg="white", borderwidth=0, disabledbackground= BACKGROUND_COLOR, disabledforeground= "black", highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15)
            ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
            self.entries_variable_CV.append(ent_variable)                 

            # add entry value in second col
            ent_value = tk.Entry(self.frame_CV, font=SMALL_FONT, takefocus = 0, width=25)
            ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
            self.entries_value_CV.append(ent_value)
            
            # Confirm
            def confirm_CV(next_row):
                if self.entries_variable_CV[next_row].get():
                    tmp_CV = {self.entries_variable_CV[next_row].get() : self.entries_value_CV[next_row].get()}
                    self.results_dict[self.selected_folder].update(tmp_CV) 
                    state = self.entries_value_ID[1]['state']    
                    self.entries_variable_CV[next_row]['state'] = tk.DISABLED
                    self.entries_value_CV[next_row]['state'] = state
                    enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
                    btn_confirm_CV.destroy()
                    btn_reject_CV.destroy()
                else:
                    messagebox.showerror("XNAT-PIC", "Insert Custom Variable")
                     
            btn_confirm_CV = tk.Button(self.frame_CV, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=lambda: confirm_CV(next_row), cursor=CURSOR_HAND)
            btn_confirm_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=tk.NW)

            # Delete
            def reject_CV(next_row):
                self.entries_variable_CV[next_row].destroy()
                self.entries_value_CV[next_row].destroy()
                enable_buttons([self.modify_btn, self.confirm_btn, self.multiple_confirm_btn])
                btn_confirm_CV.destroy()
                btn_reject_CV.destroy()
            btn_reject_CV = tk.Button(self.frame_CV, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=lambda: reject_CV(next_row), cursor=CURSOR_HAND)
            btn_reject_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=tk.N)

        #################### Clear the metadata ####################              
        def clear_metadata(self):
            # Clear all the combobox and the entry
            self.selected_dose.set('')
            self.selected_group.set('')
            self.selected_timepoint.set('')
            self.selected_timepoint1.set('')
            self.cal.delete(0, tk.END)
            self.time_entry.delete(0, tk.END)

            state = self.entries_value_ID[1]['state']
            # Set empty string in all the entries
            for i in range(0, len(self.entries_variable_CV)):
                    self.entries_value_CV[i]['state'] = tk.NORMAL
                    self.entries_value_CV[i].delete(0, tk.END)
                    self.entries_value_CV[i]['state'] = state

        #################### Save all the metadata ####################
        def save_metadata(self):
            tmp_global_path = str(self.information_folder) + "\\" + self.project_name + '_' + 'Custom_Variables.xlsx'
            try:
                df = pandas.DataFrame.from_dict(self.results_dict, orient='index')
                writer = pandas.ExcelWriter(tmp_global_path.replace('\\', '/'), engine='xlsxwriter')
                df.to_excel(writer, sheet_name='Sheet1')
                writer.save()
                messagebox.showinfo("XNAT-PIC", "File saved successfully")
            except Exception as e: 
                    messagebox.showerror("XNAT-PIC", "Save failed: " + str(e))  
                    raise
            
        #################### Exit the metadata ####################
        def exit_metadata(self, master):
            result = messagebox.askquestion("Exit", "Do you want to exit?", icon='warning')
            if result == 'yes':
                destroy_widgets([self.menu, self.label, self.notebook, self.label_frame_ID, self.label_frame_CV, self.modify_btn,
                self.confirm_btn, self.multiple_confirm_btn])
                xnat_pic_gui.choose_your_action(master)
    
    class XNATUploader():

        def __init__(self, master):
            
            # Disable main frame buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])

            # Start with a popup to get credentials
            login_popup = tk.Toplevel()
            login_popup.title("XNAT-PIC ~ Login")
            login_popup.geometry("%dx%d+%d+%d" % (540, 220, my_width/3, my_height/4))

            # Closing window event: if it occurs, the popup must be destroyed and the main frame buttons must be enabled
            def closed_window():
                login_popup.destroy()
                #Enable all buttons
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
            login_popup.protocol("WM_DELETE_WINDOW", closed_window)

            # XNAT ADDRESS      
            login_popup.label_address = tk.Label(login_popup, text="XNAT web address", font=SMALL_FONT_2)   
            login_popup.label_address.grid(row=1, column=0, padx=1, ipadx=1, sticky=tk.E)
            login_popup.entry_address = ttk.Entry(login_popup, width=25)
            login_popup.entry_address.var = tk.StringVar()
            login_popup.entry_address["textvariable"] = login_popup.entry_address.var
            login_popup.entry_address.grid(row=1, column=1, padx=1, ipadx=1, pady=10)

            def enable_address_modification(*args):
                login_popup.entry_address.configure(state='normal')

            login_popup.modify_address_btn = ttk.Radiobutton(login_popup, text="Change address", command=enable_address_modification, 
                                                            state='disabled')
            login_popup.modify_address_btn.grid(row=1, column=2, padx=1, ipadx=1, sticky=tk.W)
           
            # XNAT USER 
            login_popup.label_user = tk.Label(login_popup, text="Username", font=SMALL_FONT_2)
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
                    else:
                        # Enable the 'Remember me' button
                        login_popup.btn_remember.configure(state='normal')
                else:
                    # Disable the 'Remember me' button
                    login_popup.btn_remember.configure(state='disabled')
                    # Reset 'Remember me' button
                    login_popup.remember.set(0)
                    # Reset address and password fields
                    login_popup.entry_psw.var.set('')
                    login_popup.entry_address.var.set('')

            login_popup.entry_user = tk.StringVar()
            login_popup.combo_user = ttk.Combobox(login_popup, font=("Calibri", 10), takefocus=0, textvariable=login_popup.entry_user, 
                                                    state='normal', width=19)
            login_popup.combo_user['values'] = get_list_of_users()
            login_popup.entry_user.trace('w', get_credentials)
            login_popup.combo_user.grid(row=2, column=1, padx=1, ipadx=1)

            # XNAT PASSWORD 
            login_popup.label_psw = tk.Label(login_popup, text="Password", font=SMALL_FONT_2)
            login_popup.label_psw.grid(row=3, column=0, padx=1, ipadx=1, sticky=tk.E)

            # Show/Hide the password
            def toggle_password():
                if login_popup.entry_psw.cget('show') == '':
                    login_popup.entry_psw.config(show='*')
                    login_popup.toggle_btn.config(text='Show Password')
                else:
                    if tkinter.simpledialog.askstring("PIN", "Enter PIN: ", show='*', parent=login_popup) == os.environ.get('secretPIN'):
                        login_popup.entry_psw.config(show='')
                        login_popup.toggle_btn.config(text='Hide Password')
                    else:
                        messagebox.showerror("XNAT-PIC Uploader", "Error! The PIN code does not correspond")
            
            login_popup.entry_psw = ttk.Entry(login_popup, show="*", width=25)
            login_popup.entry_psw.var = tk.StringVar()
            login_popup.entry_psw["textvariable"] = login_popup.entry_psw.var
            login_popup.entry_psw.grid(row=3, column=1, padx=1, ipadx=1)
            login_popup.toggle_btn = ttk.Button(login_popup, text='Show Password', command=toggle_password, style="Togglebutton")
            login_popup.toggle_btn.grid(row=3, column=2)

            # Forgot password button
            def forgot_psw(*args):
                webbrowser.open("http://130.192.212.48:8080/app/template/ForgotLogin.vm#!", new=1)

            login_popup.forgot_psw = tk.Label(login_popup, text="Forgot password", font=("Calibri", 8, "underline"), fg='blue')
            login_popup.forgot_psw.grid(row=4, column=1, padx=1, ipadx=1)
            login_popup.forgot_psw.bind("<Button-1>", forgot_psw)

            # Register button
            def register(*args):
                webbrowser.open("http://130.192.212.48:8080/app/template/Register.vm#!", new=1)

            login_popup.register_btn = tk.Label(login_popup, text="Register", font=("Calibri", 8, "underline"), fg='blue')
            login_popup.register_btn.grid(row=4, column=2, padx=1, ipadx=1)
            login_popup.register_btn.bind("<Button-1>", register)

            # Label Frame for HTTP buttons

            # HTTP/HTTPS 
            login_popup.http = tk.StringVar()
            login_popup.button_http = ttk.Radiobutton(login_popup, text=" http:// ", variable=login_popup.http, value="http://")
            login_popup.button_http.grid(row=5, column=0, sticky=tk.E)
            login_popup.http.set("http://")
            login_popup.button_https = ttk.Radiobutton(login_popup, text=" https:// ", variable=login_popup.http, value="https://")
            login_popup.button_https.grid(row=5, column=1)

            # SAVE CREDENTIALS CHECKBUTTON
            login_popup.remember = tk.IntVar()
            login_popup.btn_remember = ttk.Checkbutton(login_popup, text="Remember me", variable=login_popup.remember, state='disabled')
            login_popup.btn_remember.grid(row=5, column=2, padx=1, ipadx=1, sticky=tk.W)

            # CONNECTION
            login_popup.button_connect = ttk.Button(login_popup, text="Login", style="Accentbutton",
                                                    command=partial(self.login, login_popup, master))
            login_popup.button_connect.grid(row=6, column=2, padx=1, ipadx=1, sticky=tk.W)

            # QUIT button
            def quit_event():
                login_popup.destroy()
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

            login_popup.button_quit = ttk.Button(login_popup, text='Quit', style="Accentbutton", command=quit_event)
            login_popup.button_quit.grid(row=6, column=0, padx=10, ipadx=1, sticky=tk.E)

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
                popup.btn_remember.select()
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
                # Start a thread to keep updated the current session
                # self.session_thread = threading.Thread(target=self.refresh_session, args=())
                # self.session_thread.start()

                # Go to the overall uploader
                self.overall_uploader(master)

            except Exception as error:
                messagebox.showerror("Error!", error)
                popup.destroy()
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

        def refresh_session(self):
            # Keep updated the current session
            while self.session != '':
                self.session.clearcache()
                print('Session updated')
                time.sleep(60)
            print('Refresh thread stopped')

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
                destroy_widgets([master.convert_btn, master.info_btn, master.upload_btn, master.close_btn])
                master.my_canvas.delete(master.img2)
            except:
                pass
            #################### Create the new frame ####################

            #############################################
            ################ Main Buttons ###############
            x_btn = int(my_width/5)
            y_btn = int(my_height)
            width_btn = int(my_width/5)-30

            # Frame Title
            self.frame_title = master.my_canvas.create_text(3*x_btn, int(y_btn*0.1), anchor=tk.CENTER, fill='black', font=("Ink Free", 36, "bold"),
                                         text="XNAT-PIC Uploader")

            # Upload project
            prj_text = tk.StringVar()
            self.prj_btn = tk.Button(master.my_canvas, textvariable=prj_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, 
                                    borderwidth=BORDERWIDTH, command=partial(self.check_buttons, master, press_btn=0), cursor=CURSOR_HAND)
            prj_text.set("Upload Project")
            master.my_canvas.create_window(x_btn + x_btn/2, int(y_btn*0.2), width = width_btn, anchor = tk.CENTER, window = self.prj_btn)
            
            # Upload subject
            sub_text = tk.StringVar()
            self.sub_btn = tk.Button(master.my_canvas, textvariable=sub_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, 
                                    borderwidth=BORDERWIDTH, command=partial(self.check_buttons, master, press_btn=1), cursor=CURSOR_HAND)
            sub_text.set("Upload Subject")
            master.my_canvas.create_window(2*x_btn + x_btn/2, int(y_btn*0.2), width = width_btn, anchor = tk.CENTER, window = self.sub_btn)

            # Upload experiment
            exp_text = tk.StringVar()
            self.exp_btn = tk.Button(master.my_canvas, textvariable=exp_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, 
                                    borderwidth=BORDERWIDTH, command=partial(self.check_buttons, master, press_btn=2), cursor=CURSOR_HAND)
            exp_text.set("Upload Experiment")
            master.my_canvas.create_window(3*x_btn + x_btn/2, int(y_btn*0.2), width = width_btn, anchor = tk.CENTER, window = self.exp_btn)       
            
            # Upload file
            file_text = tk.StringVar()
            self.file_btn = tk.Button(master.my_canvas, textvariable=file_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, 
                                    borderwidth=BORDERWIDTH, command=partial(self.check_buttons, master, press_btn=3), cursor=CURSOR_HAND)
            file_text.set("Upload File")
            master.my_canvas.create_window(4*x_btn + x_btn/2, int(y_btn*0.2), width = width_btn, anchor = tk.CENTER, window = self.file_btn) 

            # Upload additional files
            self.add_file_flag = tk.IntVar()
            self.add_file_btn = tk.Checkbutton(master.my_canvas, variable=self.add_file_flag, onvalue=1, offvalue=0, anchor=tk.CENTER, 
                                                background=BACKGROUND_COLOR, highlightthickness=0)
            y_ck_btn = int(my_height*30/100)
            self.check_add_files = master.my_canvas.create_text(4*x_btn + x_btn/2, int(my_height*30/100), anchor=tk.CENTER, 
                                                            width=width_btn/2, fill='black', font=SMALL_FONT_2, text="Additional Files")
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/2, y_ck_btn, anchor=tk.E, window=self.add_file_btn)

            # Custom Variables
            self.n_custom_var = tk.IntVar()
            custom_var_options = list(range(0, 5))
            self.custom_var_list = ttk.OptionMenu(master.my_canvas, self.n_custom_var, 0, *custom_var_options)
            self.check_n_custom_var = master.my_canvas.create_text(4*x_btn + x_btn/2, int(my_height*33/100), anchor = tk.CENTER, width=width_btn, 
                                                            fill='black', font=SMALL_FONT_2, 
                                                            text="Custom Variables")
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/2, int(my_height*33/100), anchor=tk.E, width=width_btn/5, 
                                            window=self.custom_var_list)
            #############################################

            #############################################
            ################# Project ###################
            width_menu = int(my_width/5)
            y_prj = int(my_height*40/100)
            # Label
            self.select_prj = master.my_canvas.create_text(x_btn + x_btn/2, y_prj, anchor=tk.CENTER, width=width_menu, fill=DISABLE_LBL_COLOR, 
                                                            font=LARGE_FONT, text="Select Project")
            
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

            self.OPTIONS = list(self.session.projects)
            self.prj = tk.StringVar()
            default_value = "--"
            self.project_list = ttk.OptionMenu(master.my_canvas, self.prj, default_value, *self.OPTIONS)
            self.project_list.configure(state="disabled")
            self.prj.trace('w', get_subjects)
            self.prj.trace('w', reject_project)
            master.my_canvas.create_window(2*x_btn + x_btn/2 + width_btn/2, y_prj, anchor=tk.E, width=width_menu, window=self.project_list)
            
            # Button to add a new project
            def add_project():
                enable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])
                self.entry_prjname.delete(0,tk.END)
            new_prj_text = tk.StringVar()
            self.new_prj_btn = tk.Button(master.my_canvas, textvariable=new_prj_text, state=tk.DISABLED, font=SMALL_FONT_2, bg=BG_BTN_COLOR, 
                                        fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_project, cursor=CURSOR_HAND)
            new_prj_text.set("Add New Project")
            master.my_canvas.create_window(3*x_btn + x_btn/2, y_prj, width=width_btn/2, anchor=tk.W, window=self.new_prj_btn)
            
            # Entry to write a new project
            self.entry_prjname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn + x_btn/2 - width_btn/2, y_prj, width=int(width_btn/2), anchor = tk.W, 
                                            window=self.entry_prjname)

            # Button to confirm new project
            self.confirm_new_prj = tk.Button(master.my_canvas, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=self.check_project_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/3 -10, y_prj, anchor=tk.E, window=self.confirm_new_prj)

            # Button to reject new project
            self.reject_new_prj = tk.Button(master.my_canvas, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=reject_project, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/3 +10, y_prj, anchor=tk.W, window=self.reject_new_prj)
            #############################################

            #############################################
            ################# Subject ###################
            # Label
            y_sub = int(my_height*50/100)
            self.select_sub = master.my_canvas.create_text(x_btn + x_btn/2, y_sub, anchor=tk.CENTER, width=width_menu, fill=DISABLE_LBL_COLOR, 
                                                            font=LARGE_FONT, text = "Select Subject")
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
            self.sub = tk.StringVar()
            self.subject_list = ttk.OptionMenu(master.my_canvas, self.sub, default_value, *self.OPTIONS2)
            self.subject_list.configure(state="disabled")
            self.sub.trace('w', get_experiments)
            self.sub.trace('w', reject_subject)
            master.my_canvas.create_window(2*x_btn + x_btn/2 + width_btn/2, y_sub, anchor=tk.E, width = width_menu, window = self.subject_list)
            
            # Button to add a new subject
            def add_subject():
                enable_buttons([self.entry_subname, self.confirm_new_sub, self.reject_new_sub])
                self.entry_subname.delete(0,tk.END)
            new_sub_text = tk.StringVar()
            self.new_sub_btn = tk.Button(master.my_canvas, textvariable=new_sub_text, state=tk.DISABLED, font=SMALL_FONT_2, bg=BG_BTN_COLOR, 
                                        fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_subject, cursor=CURSOR_HAND)
            new_sub_text.set("Add New Subject")
            master.my_canvas.create_window(3*x_btn + x_btn/2, y_sub, width=int(width_btn/2), anchor=tk.W, window = self.new_sub_btn)

            # Entry to write a new subject
            self.entry_subname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn + x_btn/2 - width_btn/2, y_sub, width=int(width_btn/2), anchor=tk.W, window=self.entry_subname)

            # Button to confirm new subject
            self.confirm_new_sub = tk.Button(master.my_canvas, image=master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=self.check_subject_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/3 -10, y_sub, anchor=tk.E, window=self.confirm_new_sub)

            # Button to reject new subject
            self.reject_new_sub = tk.Button(master.my_canvas, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=reject_subject, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/3 +10, y_sub, anchor=tk.W, window=self.reject_new_sub)
            #############################################

            #############################################
            ################# Experiment ################
            def reject_experiment(*args):
                self.entry_expname.delete(0,tk.END)
                disable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])
            # Label
            y_exp = int(my_height*60/100)
            self.select_exp = master.my_canvas.create_text(x_btn + x_btn/2, y_exp, anchor=tk.CENTER, width=width_menu, fill=DISABLE_LBL_COLOR, font=LARGE_FONT, 
                                                            text="Select Experiment")
            
            # Menu
            if self.prj.get() != '--' and self.sub.get() != '--':
                self.OPTIONS3 = list(self.session.projects[self.prj.get()].subjects[self.sub.get()].experiments.key_map.keys())
            else:
                self.OPTIONS3 = []
            self.exp = tk.StringVar()
            self.experiment_list = ttk.OptionMenu(master.my_canvas, self.exp, default_value, *self.OPTIONS3)
            self.experiment_list.configure(state="disabled")
            self.exp.trace('w', reject_experiment)
            master.my_canvas.create_window(2*x_btn + x_btn/2 + width_btn/2, y_exp, anchor=tk.E, width=width_menu, window=self.experiment_list)
            
            # Button to add a new experiment
            def add_experiment():
                enable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])
                self.entry_expname.delete(0,tk.END)
            new_exp_text = tk.StringVar()
            self.new_exp_btn = tk.Button(master.my_canvas, textvariable=new_exp_text, state=tk.DISABLED, font=SMALL_FONT_2, bg=BG_BTN_COLOR, 
                                        fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_experiment, cursor=CURSOR_HAND)
            new_exp_text.set("Add New Experiment")
            master.my_canvas.create_window(3*x_btn + x_btn/2, y_exp, width=int(width_btn/2), anchor=tk.W, window=self.new_exp_btn)

            # Entry to write a new experiment
            self.entry_expname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn + x_btn/2 - width_btn/2, y_exp, width=int(width_btn/2), anchor=tk.W, window=self.entry_expname)

            # Button to confirm new experiment
            self.confirm_new_exp = tk.Button(master.my_canvas, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=self.check_experiment_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/3 -10, y_exp, anchor=tk.E, window=self.confirm_new_exp)

            # Button to reject new experiment
            self.reject_new_exp = tk.Button(master.my_canvas, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=reject_experiment, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(4*x_btn + x_btn/2 + width_btn/3 +10, y_exp, anchor=tk.W, window=self.reject_new_exp)
            #############################################

            #############################################
            ################ EXIT Button ################
            def exit_uploader():
                result = messagebox.askquestion("XNAT-PIC Uploader", "Do you want to exit?", icon='warning')
                if result == 'yes':
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
                                                    self.check_n_custom_var, self.frame_title])
                    # Perform disconnection of the session if it is alive
                    try:
                        self.session.disconnect()
                        self.session = ''
                    except:
                        pass
                    # Restore the main frame
                    xnat_pic_gui.choose_your_action(master)

            self.exit_text = tk.StringVar() 
            self.exit_btn = tk.Button(master.my_canvas, textvariable=self.exit_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, 
                                    borderwidth=BORDERWIDTH, cursor=CURSOR_HAND, takefocus=0)
            self.exit_btn.configure(command=exit_uploader)
            self.exit_text.set("Exit")
            y_exit_btn = int(my_height*80/100)
            master.my_canvas.create_window(x_btn + x_btn/2, y_exit_btn, anchor=tk.CENTER, width=int(width_btn/2), window=self.exit_btn)
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
            self.next_btn = tk.Button(master.my_canvas, textvariable=self.next_text, font=LARGE_FONT, bg=BG_BTN_COLOR_2, fg=TEXT_BTN_COLOR_2, 
                                    borderwidth=BORDERWIDTH, command=next, cursor=CURSOR_HAND, takefocus=0, state='disabled')
            self.next_text.set("Next")
            master.my_canvas.create_window(4*x_btn + x_btn/2, y_exit_btn, anchor=tk.CENTER, width=int(width_btn/2), window=self.next_btn)
            #############################################

        def check_buttons(self, master, press_btn=0):

            def back():
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
                self.overall_uploader(master)

            # Initialize the press button value
            self.press_btn = press_btn

            # Change the EXIT button into BACK button and modify the command associated with it
            self.exit_text.set("Back")
            self.exit_btn.configure(command=back)

            x_btn = int(my_width/5)

            if press_btn == 0:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn])
                # Insert subtitle
                self.subtitle = master.my_canvas.create_text(3*x_btn, int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/5), fill='red', 
                                                            font=LARGE_FONT, text="Project Uploader")
                # Highlight the field name
                master.my_canvas.itemconfig(self.select_prj, fill=TEXT_LBL_COLOR)
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--':
                        enable_buttons([self.next_btn])
                self.prj.trace('w', enable_next)
                
            elif press_btn == 1:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn])
                # Insert subtitle
                self.subtitle = master.my_canvas.create_text(3*x_btn, int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/5), fill='red', 
                                                            font=LARGE_FONT, text="Subject Uploader")
                # Highlight the field name
                master.my_canvas.itemconfig(self.select_prj, fill=TEXT_LBL_COLOR)
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--':
                        enable_buttons([self.next_btn])
                self.prj.trace('w', enable_next)
                
            elif press_btn == 2:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn, self.subject_list, self.new_sub_btn])
                # Insert subtitle
                self.subtitle = master.my_canvas.create_text(3*x_btn, int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/5), fill='red', 
                                                            font=LARGE_FONT, text="Experiment Uploader")
                # Highlight the field names
                master.my_canvas.itemconfig(self.select_prj, fill=TEXT_LBL_COLOR)
                master.my_canvas.itemconfig(self.select_sub, fill=TEXT_LBL_COLOR)
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--':
                        enable_buttons([self.next_btn])
                self.sub.trace('w', enable_next)

            elif press_btn == 3:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn, self.add_file_btn, self.custom_var_list])
                enable_buttons([self.project_list, self.new_prj_btn, self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn])
                # Insert subtitle
                self.subtitle = master.my_canvas.create_text(3*x_btn, int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/5), fill='red', 
                                                            font=LARGE_FONT, text="File Uploader")
                # Highlight the field names
                master.my_canvas.itemconfig(self.select_prj, fill=TEXT_LBL_COLOR)
                master.my_canvas.itemconfig(self.select_sub, fill=TEXT_LBL_COLOR)
                master.my_canvas.itemconfig(self.select_exp, fill=TEXT_LBL_COLOR)
                # Enable NEXT button only if all the requested fields are filled
                def enable_next(*args):
                    if self.prj.get() != '--' and self.sub.get() != '--' and self.exp.get() != '--':
                        enable_buttons([self.next_btn])
                self.exp.trace('w', enable_next)
            else:
                pass

        def project_uploader(self, master):

            init_dir = os.path.expanduser("~").replace('\\', '/') + '/Desktop/Dataset'
            project_to_upload = filedialog.askdirectory(parent=master.root, initialdir=init_dir, 
                                                        title="XNAT-PIC Project Uploader: Select project directory in DICOM format to upload")
            # Check for empty selected folder
            if os.path.isdir(project_to_upload) == False:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder does not exist!')
            elif os.listdir(project_to_upload) == []:
                messagebox.showerror('XNAT-PIC Uploader', 'Error! The selected folder is empty!')
            else:
                # Start progress bar
                progressbar = ProgressBar(bar_title='XNAT-PIC Uploader')
                progressbar.start_determinate_bar()

                list_dirs = os.listdir(project_to_upload)

                start_time = time.time()

                def upload_thread():

                    for i, sub in enumerate(list_dirs):
                        sub = os.path.join(project_to_upload, sub)

                        progressbar.show_step(i + 1, len(list_dirs))
                        progressbar.update_progressbar(i, len(list_dirs))

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
                                self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Experiment'], 
                                                        subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()
                                for var in subject_data.keys():
                                    if var not in ['Project', 'Subject', 'Experiment', 'Acquisition_date', 'C_V']:
                                        params[var] = subject_data[var]
                            except:
                                # Define the subject_id and the experiment_id if the custom variables file is not available
                                self.sub.set(exp.split('/')[-3].replace('.','_'))
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([exp.split('/')[-3].replace('_dcm', ''), exp.split('/')[-2].replace('.', '_')]).replace(' ', '_'))
                                params['experiment_id'] = self.exp.get()

                            progressbar.set_caption('Uploading ' + str(self.exp.get()) + ' ...')
                            
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
                    progressbar.update_bar(0.00000001)
                
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
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Experiment'],
                                                    subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                        for var in subject_data.keys():
                            if var not in ['Project', 'Subject', 'Experiment' 'Acquisition_date', 'C_V']:
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
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Experiment'],
                                                    subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                        params['experiment_id'] = self.exp.get()
                        for var in subject_data.keys():
                            if var not in ['Project', 'Subject', 'Experiment', 'Acquisition_date', 'C_V']:
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

    check_credentials()

    # root = tk.Tk()
    app = xnat_pic_gui()
    # s = SplashScreen(root, timeout=5000)
    # root.mainloop()

           