from doctest import master
from logging import exception
import shutil
import tkinter as tk
from tkinter import DISABLED, END, MULTIPLE, SINGLE, W, filedialog, messagebox
from tkinter.font import Font
from tkinter.tix import COLUMN
from turtle import bgcolor, width
from unicodedata import name
from unittest import result
from PIL import Image, ImageTk
from tkinter import ttk
import time
import os, re
import os.path
from functools import partial
import subprocess
import platform
from progress_bar import ProgressBar
from dicom_converter import Bruker2DicomConverter
import xnat
from read_visupars import read_visupars_parameters
import pyAesCrypt
from tabulate import tabulate
import datetime
import threading
from dotenv import load_dotenv
from xnat_uploader import Dicom2XnatUploader, FileUploader, read_table
import datefinder
import pydicom
from tkcalendar import DateEntry
from accessory_functions import *
from idlelib.tooltip import Hovertip
import csv
import pandas

PATH_IMAGE = "images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
BACKGROUND_COLOR = "#31C498"
THEME_COLOR = "black"
TEXT_BTN_COLOR = "black"
TEXT_LBL_COLOR = "white"
BG_BTN_COLOR = "#80FFE6"
BG_LBL_COLOR = "black"
DISABLE_LBL_COLOR = '#D3D3D3'
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"
BORDERWIDTH = 3

load_dotenv()
bufferSize = int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2'))

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

class xnat_pic_gui(tk.Frame):

    def __init__(self, master):
        
        self.root = master 
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
        self.root.geometry("%dx%d+0+0" % (w, h))
        self.root.title("   XNAT-PIC   ~   Molecular Imaging Center   ~   University of Torino   ")
        # If you want the logo 
        #self.root.iconbitmap(r"logo3.ico")

        # Define Canvas and logo in background
        global my_width
        my_width = int(w*PERCENTAGE_SCREEN)
        logo = Image.open(PATH_IMAGE + "logo41.png")
        wpercent = (my_width/float(logo.size[0]))
        global my_height
        my_height = int((float(logo.size[1])*float(wpercent))*PERCENTAGE_SCREEN)
        self.my_canvas = tk.Canvas(self.root, width=my_width, height=my_height, bg=BACKGROUND_COLOR, highlightthickness=3, highlightbackground=THEME_COLOR)
        self.my_canvas.place(x=int((w-my_width)/2), y=int((h-my_height)/2), anchor=tk.NW)
        
        # Adapt the size of the logo to the size of the canvas
        logo = logo.resize((my_width, my_height), Image.ANTIALIAS)  
        self.logo = ImageTk.PhotoImage(logo)
        self.my_canvas.create_image(0, 0, anchor=tk.NW, image=self.logo)
        
        # Open the image for the logo
        logo_info = Image.open(PATH_IMAGE + "info.png")
        self.logo_info = ImageTk.PhotoImage(logo_info)
        width_logo, height_logo = logo_info.size

        # Logo on top
        #logo3 = Image.open(PATH_IMAGE + "path163.png")
        #self.logo3 = ImageTk.PhotoImage(logo3)
        #label1 = tk.Label(self.root, image=self.logo3,  bg="#31C498", width=1715)
        #self.my_canvas.create_window(3, 20, anchor=tk.NW, window=label1)

        # Open the image for the accept icon
        logo_accept = Image.open(PATH_IMAGE + "accept.png")
        logo_accept = logo_accept.resize((width_logo, height_logo), Image.ANTIALIAS)
        self.logo_accept = ImageTk.PhotoImage(logo_accept)

        # Open the image for the delete icon
        logo_delete = Image.open(PATH_IMAGE + "delete.png")
        logo_delete = logo_delete.resize((width_logo, height_logo), Image.ANTIALIAS)
        self.logo_delete = ImageTk.PhotoImage(logo_delete)

        # Button to enter
        enter_text = tk.StringVar()
        self.enter_btn = tk.Button(self.my_canvas, textvariable=enter_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command=lambda: (self.enter_btn.destroy(), xnat_pic_gui.choose_you_action(self)), cursor=CURSOR_HAND)
        enter_text.set("ENTER")
        self.my_canvas.create_window(int(my_width/2), int(my_height*0.7), width = int(my_width/5), anchor = tk.CENTER, window = self.enter_btn)
        
    # Choose to upload files, fill in the info, convert files, process images
    def choose_you_action(self):
         ##########################################
         # Action buttons           
         # Positions for action button parametric with respect to the size of the canvas
         x_btn = int(my_width/4) # /5 if there is the processing button
         y_btn = int(my_height*60/100)
         width_btn = int(my_width/7)

         # Convert files Bruker2DICOM
         convert_text = tk.StringVar()
         self.convert_btn = tk.Button(self.my_canvas, textvariable=convert_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command=partial(self.bruker2dicom_conversion, self), cursor=CURSOR_HAND)
         convert_text.set("DICOM Converter")
         self.my_canvas.create_window(2*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.convert_btn)
         
         # Fill in the info
         info_text = tk.StringVar()
         self.info_btn = tk.Button(self.my_canvas, textvariable=info_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command=partial(self.metadata, self), cursor=CURSOR_HAND)
         info_text.set("Fill in the info")
         self.my_canvas.create_window(1*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.info_btn)

         # Upload files
         upload_text = tk.StringVar()
         self.upload_btn = tk.Button(self.my_canvas, textvariable=upload_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command=partial(self.XNATUploader, self), cursor=CURSOR_HAND)
         upload_text.set("Uploader")
         self.my_canvas.create_window(3*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.upload_btn)        
        
         # Processing your files
         #process_text = tk.StringVar()
         #self.process_btn = tk.Button(self.my_canvas, textvariable=process_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, cursor=CURSOR_HAND)
         #process_text.set("Processing")
         #self.my_canvas.create_window(4*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.process_btn)
    
         ##########################################
         # Info buttons
         # Messages displayed when the button is clicked
         def helpmsg(text):  
             if text == "button1":
                 msg="Convert images from Bruker ParaVision format to DICOM standard" 
             elif text == "button2":
                 msg="Fill in the information about the acquisition" 
             elif text == "button3":
                 msg="Upload DICOM images to XNAT" 
             elif text == "button4":
                 msg="Process images" 

             messagebox.showinfo("XNAT-PIC",msg)
                 
         # Positions for info button parametric with respect to the size of the canvas
         y_btn1 = int(my_height*65/100)
         
         self.info_convert_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=0, command = lambda: helpmsg("button1"), cursor=QUESTION_HAND, state = DISABLED)
         self.my_canvas.create_window(2*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_convert_btn)
         myTipConvert = Hovertip(self.info_convert_btn,'Convert images from Bruker ParaVision format to DICOM standard')

         self.info_info_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=0, command = lambda: helpmsg("button2"), cursor=QUESTION_HAND, state = DISABLED)
         self.my_canvas.create_window(1*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_info_btn)
         myTipInfo = Hovertip(self.info_info_btn,'Fill in the information about the acquisition')

         self.info_upload_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=0, command = lambda: helpmsg("button3"), cursor=QUESTION_HAND, state = DISABLED)
         self.my_canvas.create_window(3*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_upload_btn)
         myTipUpload = Hovertip(self.info_upload_btn,'Upload DICOM images to XNAT')
         #self.info_process_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: helpmsg("button4"), cursor=QUESTION_HAND)
         #self.my_canvas.create_window(4*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_process_btn)        

    def get_page(self):
        return self.root   

    class bruker2dicom_conversion():
        
        def __init__(self, master):

            self.params = {}
            
            # Disable the buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
            #master.process_btn['state'] = tk.DISABLED
            
            def normal_btn():
                self.conv_popup.destroy()
                #Enable all buttons
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                #master.process_btn['state'] = tk.NORMAL

            def isChecked():
                self.params['results_flag'] = self.results_flag.get()
            
            def checkOverwrite():
                master.overwrite_flag = self.overwrite_flag.get()

            self.conv_popup = tk.Toplevel()
            self.conv_popup.geometry("%dx%d+%d+%d" % (500, 150, my_width/3, my_height/3))
            self.conv_popup.title('XNAT-PIC Converter')
            self.conv_popup.protocol("WM_DELETE_WINDOW", normal_btn)

            self.btn_prj = tk.Button(self.conv_popup, text='Convert Project', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=BORDERWIDTH, 
                                    command=lambda: (self.conv_popup.destroy(), self.prj_conversion(master)))
            self.btn_prj.grid(row=2, column=0, padx=10, pady=5)
            self.btn_sbj = tk.Button(self.conv_popup, text='Convert Subject', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=BORDERWIDTH, 
                                    command=lambda: (self.conv_popup.destroy(), self.sbj_conversion(master)))
            self.btn_sbj.grid(row=3, column=0, padx=10, pady=5)
            self.results_flag = tk.IntVar()
            # master.results_flag = self.results_flag.get()
            self.btn_results = tk.Checkbutton(self.conv_popup, text='Copy additional files', variable=self.results_flag,
                                onvalue=1, offvalue=0, command=isChecked)
            self.btn_results.grid(row=2, column=1, sticky='W')
            self.overwrite_flag = tk.IntVar()
            master.overwrite_flag = self.overwrite_flag.get()
            self.btn_overwrite = tk.Checkbutton(self.conv_popup, text="Overwrite existing folders", variable=self.overwrite_flag,
                                onvalue=1, offvalue=0, command=checkOverwrite)
            self.btn_overwrite.grid(row=3, column=1, sticky='W')
            self.btn_results_info = tk.Button(self.conv_popup, image=master.logo_info, state = 'disabled', bg=BG_BTN_COLOR, borderwidth=0, cursor=QUESTION_HAND,
                                    command=lambda: messagebox.showinfo("XNAT-PIC","Copy additional files info"))
            self.btn_results_info.grid(row=2, column=2, sticky='W')
            myTipResults = Hovertip(self.btn_results_info,'Copy additional files')
            self.btn_overwrite_info = tk.Button(self.conv_popup, image=master.logo_info, state = 'disabled', bg=BG_BTN_COLOR, borderwidth=0, cursor=QUESTION_HAND,
                                    command=lambda: messagebox.showinfo("XNAT-PIC","If the project or the subject already exists, it will be overwritten!"))
            self.btn_overwrite_info.grid(row=3, column=2, sticky='W')
            myTipOverwrite = Hovertip(self.btn_overwrite_info,'If the project or the subject already exists, it will be overwritten!')
        def prj_conversion(self, master):

            ############### Whole project conversion ################

            # Disable the buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
            #master.process_btn['state'] = tk.DISABLED

            # Ask for project directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for the chosen directory
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                #master.process_btn['state'] = tk.NORMAL
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            master.root.deiconify()
            master.root.update()
            self.dst = self.folder_to_convert + '_dcm'

            # Initialize converter class
            converter = Bruker2DicomConverter(self.params)
            
            try:
                start_time = time.time()

                # Start the progress bar
                progressbar = ProgressBar(bar_title='XNAT-PIC Project Converter')
                progressbar.start_determinate_bar()
                # progressbar.start_indeterminate_bar()

                # Check for subjects within the given project
                list_dirs = os.listdir(self.folder_to_convert)
                # Initialize the list of conversion errors
                conversion_err = []
                for j, dir in enumerate(list_dirs, 0):
        
                    # Update the current step of the progress bar
                    # progressbar.update_progressbar(j, len(list_dirs))
                    progressbar.show_step(j + 1, len(list_dirs))
                    # Define the current subject path
                    dir_dcm = dir 
                    current_folder = os.path.join(self.folder_to_convert, dir).replace('\\', '/')
                    if os.path.isdir(current_folder):
                        current_dst = os.path.join(self.dst, dir_dcm).replace('\\', '/')
                        # Check if the current destination folder already exists
                        if os.path.isdir(current_dst):
                            # Case 1 --> The directory already exists
                            if master.overwrite_flag == 1:
                                # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                                shutil.rmtree(current_dst)
                                os.makedirs(current_dst)
                            else:
                                # Existent folder without overwriting flag set to 0 --> ignore folder
                                conversion_err.append(current_folder.split('/')[-1])
                                continue
                        else:
                            # Case 2 --> The directory does not exist
                            if current_dst.split('/')[-1].count('_dcm') > 1:
                                # Check to avoid already converted folders
                                conversion_err.append(current_folder.split('/')[-1])
                                continue
                            else:
                                # Create the new destination folder
                                os.makedirs(current_dst)

                        # Perform DICOM conversion
                        # converter.start_conversion()
                        tp = threading.Thread(target=converter.multi_core_conversion, args=(current_folder, current_dst, ))
                        tp.start()
                        while tp.is_alive() == True:
                            # progressbar.update_bar()
                            progressbar.update_bar(0.00001)
                            time.sleep(0.5)
                        else:
                            progressbar.update_progressbar(j + 1, len(list_dirs))

                # Stop the progress bar and close the popup
                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Total elapsed time: ' + str(end_time - start_time) + ' s')

                messagebox.showinfo("XNAT-PIC Converter","The conversion is done!\n\n\n\n"
                                    "Exceptions:\n\n" +
                                    str([str(x) for x in conversion_err])[1:-1])
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                #master.process_btn['state'] = tk.NORMAL          

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                #master.process_btn['state'] = tk.NORMAL
                self.conv_popup.destroy()
                
        def sbj_conversion(self, master):

            ############### Single subject conversion ################

            # Convert from bruker to DICOM and disable the buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
            #master.process_btn['state'] = tk.DISABLED

            # Ask for subject directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select subject directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for chosen directory
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                #master.process_btn['state'] = tk.NORMAL
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            master.root.deiconify()
            master.root.update()
            head, tail = os.path.split(self.folder_to_convert)
            head = head + '_dcm'
            project_foldername = tail.split('.',1)[0] 
            self.dst = os.path.join(head, project_foldername).replace('\\', '/')

            # Start converter
            converter = Bruker2DicomConverter(self.params)

            # If the destination folder already exists throw exception, otherwise create the new folder
            if os.path.isdir(self.dst):
                # Case 1 --> The directory already exists
                if master.overwrite_flag == 1:
                    # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                    shutil.rmtree(self.dst)
                    os.makedirs(self.dst)
                else:
                    # Existent folder without overwriting flag set to 0 --> ignore folder
                    messagebox.showerror("XNAT-PIC Converter", "Destination folder %s already exists" % self.dst)
                    return
            else:
                # Case 2 --> The directory does not exist
                if self.dst.split('/')[-1].count('_dcm') > 1:
                    # Check to avoid already converted folders
                    messagebox.showerror("XNAT-PIC Converter", "Chosen folder %s already converted" % self.dst)
                    return
                else:
                    # Create the new destination folder
                    os.makedirs(self.dst)

            try:
                start_time = time.time()

                # Start the progress bar
                progressbar = ProgressBar(bar_title='XNAT-PIC Subject Converter')
                progressbar.start_indeterminate_bar()

                # Initialize conversion thread
                tp = threading.Thread(target=converter.multi_core_conversion, args=(self.folder_to_convert, self.dst, ))
                tp.start()
                while tp.is_alive() == True:
                    # As long as the thread is working, update the progress bar
                    progressbar.update_bar()
                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Total elapsed time: ' + str(end_time - start_time) + ' s')

                messagebox.showinfo("XNAT-PIC Converter","Done! Now you can upload your files to XNAT.")
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                #master.process_btn['state'] = tk.NORMAL          

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Converter", e)
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                #master.process_btn['state'] = tk.NORMAL
                 
    # Fill in information
    class metadata():

        def __init__(self, master):

            # Disable all buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

            # Choose your directory
            self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")
            
            # If there is no folder selected, re-enable the buttons and return
            if not self.information_folder:
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
                return
            
            self.project_name = (self.information_folder.rsplit("/",1)[1])
            self.tmp_dict = {}
            self.results_dict = {}

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
            
            # Scan all files contained in the folder that the user has provided
            for item in os.listdir(self.information_folder):
                        path = str(self.information_folder) + "\\" + str(item)
                        name = str(item) + "_" + "Custom_Variables.txt"
                        # Check if the content of the project is a folder and therefore a patient or a file not to be considered
                        if os.path.isdir(path.replace('\\', '/')):
                            # Check if the txt file is in folder of the patient
                            # If the file exists, read le info
                            if os.path.exists((path + "\\" + name).replace('\\', '/')):
                                subject_data = read_table((path + "\\" + name).replace('\\', '/'))
                                tmp_dict = {item: subject_data}
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
                                
                                subject_data = {"Project": str(self.project_name),
                                            "Subject": str(item),
                                            "Experiment": "",
                                            "Acquisition_date": tmp_acq_date,
                                            "C_V": "",
                                            "Group": "",
                                            "Dose":"",
                                            "Timepoint":""
                                            }
                                tmp_dict = {item: subject_data}

                            self.results_dict.update(tmp_dict)

            #################### Update the frame ####################
            #master.process_btn.destroy()
            destroy_widgets([master.convert_btn.destroy(), master.info_btn.destroy(), master.upload_btn.destroy(),
                master.info_convert_btn.destroy(),master.info_info_btn.destroy(), master.info_upload_btn.destroy()])
            #################### Menu ###########################
            self.menu = tk.Menu(master.root)
            file_menu = tk.Menu(self.menu, tearoff=0)
            file_menu.add_command(label="Add ID", command = lambda: self.add_ID())
            file_menu.add_command(label="Add Custom Variables", command = lambda: self.add_custom_variable(master))
            file_menu.add_command(label="Clear Custom Variables", command = lambda: self.clear_metadata())
            file_menu.add_separator()
            file_menu.add_command(label="Save All", command = lambda: self.save_metadata())

            self.menu.add_cascade(label="File", menu=file_menu)
            self.menu.add_command(label="About", command = lambda: messagebox.showinfo("XNAT-PIC","Help"))
            self.menu.add_command(label="Exit", command = lambda: self.exit_metadata(master))
            master.root.config(menu=self.menu)

            #################### Folder list #################### 
            x_folder_list = int(my_width*10/100)
            y_folder_list = int(my_height*18/100)
            self.label = tk.Label(master.my_canvas, text='List of folders contained in the project: ' + '\n'+ self.project_name, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, font = SMALL_FONT)
            master.my_canvas.create_window(x_folder_list, y_folder_list, width = int(my_width*25/100), height = int(my_height*5/100), anchor=tk.NW, window=self.label)
            
            y_folder_list1 = int(my_height*25/100)
            self.my_listbox = tk.Listbox(master.my_canvas, selectmode=SINGLE, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, font=SMALL_FONT, takefocus = 0)
            master.my_canvas.create_window(x_folder_list, y_folder_list1, width = int(my_width*25/100), height = int(my_height*40/100) ,anchor = tk.NW, window = self.my_listbox)

            # List of subject in the project in the listbox
            self.my_listbox.insert(tk.END, *self.results_dict.keys())

            # Attach listbox to x and y scrollbar ()
            x_folder_scrollbar = int(my_width*8/100)
            self.my_yscrollbar = tk.Scrollbar(master.my_canvas, orient="vertical")
            self.my_listbox.config(yscrollcommand = self.my_yscrollbar.set)
            self.my_yscrollbar.config(command = self.my_listbox.yview)
            master.my_canvas.create_window(x_folder_scrollbar, y_folder_list1, height = int(my_height*40/100), anchor = tk.NW, window = self.my_yscrollbar)
            
            y_folder_scrollbar = int(my_height*66/100)
            self.my_xscrollbar = tk.Scrollbar(master.my_canvas, orient="horizontal")
            self.my_listbox.config(xscrollcommand = self.my_xscrollbar.set)
            self.my_xscrollbar.config(command = self.my_listbox.xview)
            master.my_canvas.create_window(x_folder_list, y_folder_scrollbar, width = int(my_width*25/100), anchor = tk.NW, window = self.my_xscrollbar)
            
            #################### Subject form ####################
            # ID
            # Label frame for ID: folder selected, project, subject and acq. date
            self.label_frame_ID = tk.LabelFrame(master.my_canvas, background = BACKGROUND_COLOR, borderwidth=5, font=SMALL_FONT, relief='solid', text="ID")

            #
            x_lbl_ID = int(my_width*40/100)
            y_lbl_ID = int(my_height*24/100)
            w_lbl_ID = int(my_width*50/100)
            h_lbl_ID = int(my_height*20/100)
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
            # Entry CV  
            self.entries_variable_ID = []  
            self.entries_value_ID = []          
            count = 0
            for key in keys_ID:
                # Variable
                self.entries_variable_ID.append(tk.Entry(self.frame_ID, disabledbackground= BACKGROUND_COLOR, disabledforeground= "white",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                self.entries_variable_ID[-1].insert(0, key)
                self.entries_variable_ID[-1]['state'] = 'disabled'
                self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                # Value
                self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, state='disabled', takefocus = 0, width=35))
                self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                count += 1

            # Calendar for acq. date
            self.cal = DateEntry(self.frame_ID, state = tk.DISABLED, width=10, font = SMALL_FONT, background=BACKGROUND_COLOR, date_pattern = 'y-mm-dd', foreground='white', borderwidth=0)
            self.cal.delete(0, tk.END)
            self.cal.grid(row=4, column=2, padx = 5, pady = 5, sticky=W)

            ####################################################################
            # Custom Variables (CV)
            # Label frame for Custom Variables: group, dose, timepoint
            self.label_frame_CV = tk.LabelFrame(master.my_canvas, background = BACKGROUND_COLOR, borderwidth=5, font=SMALL_FONT, relief='solid', text="Custom Variables")
            x_lbl_CV = x_lbl_ID
            y_lbl_CV = int(my_height*50/100)
            h_lbl_CV = int(my_height*15/100)
            w_lbl_CV = int(my_width*53/100)

            # Scroll bar in the Label frame ID
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

            keys_CV = ["Group", "Dose", "Timepoint"]
            # Entry CV  
            self.entries_variable_CV = []  
            self.entries_value_CV = []          
            count = 0
            for key in keys_CV:
                # Variable
                self.entries_variable_CV.append(tk.Entry(self.frame_CV, disabledbackground= BACKGROUND_COLOR, disabledforeground= "white",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                self.entries_variable_CV[-1].insert(0, key)
                self.entries_variable_CV[-1]['state'] = 'disabled'
                self.entries_variable_CV[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                # Value
                self.entries_value_CV.append(tk.Entry(self.frame_CV, font=SMALL_FONT, state='disabled', takefocus = 0, width=35))
                self.entries_value_CV[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                count += 1

            # Group Menu
            OPTIONS = ["untreated", "treated"]
            self.selected_group = tk.StringVar()
            self.group_menu = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_group, width=10)
            self.group_menu['values'] = OPTIONS
            self.group_menu['state'] = 'disabled'
            self.group_menu.grid(row=0, column=3, padx = 5, pady = 5, sticky=W)
            
            # UM for dose
            self.OPTIONS_UM = ["Mg", "kg", "mg", "µg", "ng"]
            self.selected_dose = tk.StringVar()
            self.dose_menu = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_dose, width=10)
            self.dose_menu['values'] = self.OPTIONS_UM
            self.dose_menu['state'] = 'disabled'
            self.dose_menu.grid(row=1, column=3, padx = 5, pady = 5, sticky=W)

            # Timepoint
            self.OPTIONS = ["pre", "post"]
            self.selected_timepoint = tk.StringVar()
            self.timepoint_menu = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_timepoint, width=10)
            self.timepoint_menu['values'] = self.OPTIONS
            self.timepoint_menu['state'] = 'disabled'
            self.timepoint_menu.grid(row=2, column=3, padx = 5, pady = 5, sticky=W)

            self.time_entry = tk.Entry(self.frame_CV, font = SMALL_FONT, state='disabled', takefocus = 0, width=5)
            self.time_entry.grid(row=2, column=4, padx = 5, pady = 5, sticky=W)

            self.OPTIONS1 = ["seconds", "minutes", "hours", "days", "weeks", "months", "years"]
            self.selected_timepoint1 = tk.StringVar()
            self.timepoint_menu1 = ttk.Combobox(self.frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=self.selected_timepoint1, width=7)
            self.timepoint_menu1['values'] = self.OPTIONS1
            self.timepoint_menu1['state'] = 'disabled'
            self.timepoint_menu1.grid(row=2, column=5, padx = 5, pady = 5, sticky=W)

            #################### Load the info about the selected subject ####################
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
                # Get selected indices
                self.selected_index = self.my_listbox.curselection()[0]
                self.selected_folder = self.my_listbox.get(self.selected_index)
                
                ID = True
                count = 1
                self.entries_variable_ID = []
                self.entries_variable_ID.append(tk.Entry(self.frame_ID, disabledbackground= BACKGROUND_COLOR, disabledforeground= "white",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                self.entries_variable_ID[-1].insert(0, "Folder")
                self.entries_variable_ID[-1]['state'] = 'disabled'
                self.entries_variable_ID[-1].grid(row=0, column=0, padx = 5, pady = 5, sticky=W)
                self.entries_variable_CV = []
                self.entries_value_ID = []
                self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, takefocus = 0, width=35))
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
                        self.entries_variable_ID.append(tk.Entry(self.frame_ID, disabledbackground= BACKGROUND_COLOR, disabledforeground= "white",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                        self.entries_variable_ID[-1].insert(0, k)
                        self.entries_variable_ID[-1]['state'] = 'disabled'
                        self.entries_variable_ID[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                        # Value
                        self.entries_value_ID.append(tk.Entry(self.frame_ID, font=SMALL_FONT, takefocus = 0, width=35))
                        self.entries_value_ID[-1].insert(0, v)
                        self.entries_value_ID[-1]['state'] = 'disabled'
                        self.entries_value_ID[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                        count += 1
                        
                    else:
                        if k != "C_V":
                            self.entries_variable_CV.append(tk.Entry(self.frame_CV, disabledbackground= BACKGROUND_COLOR, disabledforeground= "white",bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15))
                            self.entries_variable_CV[-1].insert(0, k)
                            self.entries_variable_CV[-1]['state'] = 'disabled'
                            self.entries_variable_CV[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                            # Value
                            self.entries_value_CV.append(tk.Entry(self.frame_CV, font=SMALL_FONT, takefocus = 0, width=35))
                            self.entries_value_CV[-1].insert(0, v)
                            self.entries_value_CV[-1]['state'] = 'disabled'
                            self.entries_value_CV[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                            count += 1
            
            self.my_listbox.bind('<Tab>', items_selected)
            
            #################### Modify the metadata ####################
            modify_text = tk.StringVar() 
            self.modify_btn = tk.Button(master.my_canvas, textvariable=modify_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: self.modify_metadata(), cursor=CURSOR_HAND, takefocus = 0)
            modify_text.set("Modify")
            x_lbl = x_lbl_ID
            y_btn = int(my_height*70/100)
            width_btn = int(my_width*14/100)
            master.my_canvas.create_window(x_lbl, y_btn, anchor = tk.NW, width = width_btn, window = self.modify_btn)

            #################### Confirm the metadata ####################
            confirm_text = tk.StringVar() 
            self.confirm_btn = tk.Button(master.my_canvas, textvariable=confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: self.confirm_metadata(), cursor=CURSOR_HAND, takefocus = 0)
            confirm_text.set("Confirm")
            x_conf_btn = int(my_width*59/100)
            master.my_canvas.create_window(x_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = self.confirm_btn)

            #################### Confirm multiple metadata ####################
            multiple_confirm_text = tk.StringVar() 
            self.multiple_confirm_btn = tk.Button(master.my_canvas, textvariable=multiple_confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: self.confirm_multiple_metadata(), cursor=CURSOR_HAND, takefocus = 0)
            multiple_confirm_text.set("Multiple Confirm")
            x_multiple_conf_btn = int(my_width*78/100)
            master.my_canvas.create_window(x_multiple_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = self.multiple_confirm_btn)
                
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
                self.my_listbox.selection_set(self.selected_index)

            self.cal.bind("<<DateEntrySelected>>", date_entry_selected)

            # Option menu for the group
            self.group_menu['state'] = 'readonly'

            def group_changed(event):
                """ handle the group changed event """
                self.entries_value_CV[0].delete(0, tk.END)
                self.entries_value_CV[0].insert(0, str(self.selected_group.get()))                    
                self.my_listbox.selection_set(self.selected_index)

            self.group_menu.bind("<<ComboboxSelected>>", group_changed)

            # Option menu for the dose
            self.dose_menu['state'] = 'readonly'

            def dose_changed(event):
                """ handle the dose changed event """
                dose_str = ''
                if self.entries_value_CV[1].get():
                    for word in filter(str(self.entries_value_CV[1].get()).__contains__, self.OPTIONS_UM):
                        # If a unit of measurement is already present, replace it
                        dose_str = str(self.entries_value_CV[1].get()).replace(word, str(self.selected_dose.get()))
                        self.entries_value_CV[1].delete(0, tk.END)     
                        self.entries_value_CV[1].insert(0, dose_str)                    
                        self.my_listbox.selection_set(self.selected_index)
                        return
                            # If only the number is present, add the unit of measure
                    dose_str = str(self.entries_value_CV[1].get()) + "-" + str(self.selected_dose.get())
                else:
                    # If the entry is empty, enter only the unit of measure
                    dose_str = str(self.selected_dose.get())

                self.entries_value_CV[1].delete(0, tk.END)     
                self.entries_value_CV[1].insert(0, dose_str)                    
                self.my_listbox.selection_set(self.selected_index)

            self.dose_menu.bind("<<ComboboxSelected>>", dose_changed)
            
            # Option menu for the timepoint
            self.timepoint_menu1['state'] = 'readonly'
            self.time_entry['state'] = 'normal'
            self.timepoint_menu['state'] = 'readonly'

            def timepoint_changed(event):
                self.entries_value_CV[2].config(state=tk.NORMAL)
                """ handle the timepoint changed event """
                if str(self.time_entry.get()) or str(self.selected_timepoint1.get()):
                    timepoint_str = str(self.selected_timepoint.get()) + "-" + str(self.time_entry.get()) + "-" + str(self.selected_timepoint1.get())
                else:
                    timepoint_str = str(self.selected_timepoint.get()) 

                self.my_listbox.selection_set(self.selected_index)

                if self.time_entry.get():
                    try:
                        float(self.time_entry.get())
                    except Exception as e: 
                        messagebox.showerror("XNAT-PIC", "Insert a number in the timepoint entry")

                self.entries_value_CV[2].delete(0, tk.END)
                self.entries_value_CV[2].insert(0, timepoint_str)
                self.entries_value_CV[2].config(state=tk.DISABLED)

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
                    datetime.datetime.strptime(self.entries_value_ID[3].get(), '%Y-%m-%d')
                except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Incorrect data format in acquisition date, should be YYYY-MM-DD")
                    raise

            if self.entries_value_CV[2].get() and '-' in  self.entries_value_CV[2].get(): 
                if not str(self.entries_value_CV[2].get()).split('-')[0] in self.OPTIONS:
                    messagebox.showerror("XNAT-PIC", "Select pre/post in timepoint")
                    raise
                if not str(self.entries_value_CV[2].get()).split('-')[2] in self.OPTIONS1:
                    messagebox.showerror("XNAT-PIC", "Select seconds, minutes, hours, days, weeks, months, years in timepoint")
                    raise

                input_num = str(self.entries_value_CV[2].get()).split('-')[1]
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
            tmp_path = str(self.information_folder) + "\\" + self.selected_folder + "\\" + self.selected_folder + "_" + "Custom_Variables.txt"
            with open(tmp_path.replace('\\', '/'), 'w+') as meta_file:
                meta_file.write(tabulate(self.results_dict[self.selected_folder].items(), headers=['Variable', 'Value']))
            
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
        def add_ID(self):
             # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 
            # I use len(all_entries) to get nuber of next free row
            next_row = len(self.entries_variable_ID)
            
            # Add entry variable ID
            ent_variable = tk.Entry(self.frame_ID, bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15)
            ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
            self.entries_variable_ID.append(ent_variable)                 

            # Add entry value ID in second col
            ent_value = tk.Entry(self.frame_ID, font=SMALL_FONT, takefocus = 0, width=35)
            ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
            self.entries_value_ID.append(ent_value)

        #################### Add Custom Variable #################
        def add_custom_variable(self, master):
             # Check before confirming the data
            try:
                self.selected_folder
                pass
            except Exception as e:
                    messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                    raise 
            # I use len(all_entries) to get nuber of next free row
            next_row = len(self.entries_variable_CV)
            
            # Add entry variable CV
            ent_variable = tk.Entry(self.frame_CV, bg=BACKGROUND_COLOR, borderwidth=0, highlightthickness=2, highlightbackground="black", highlightcolor="black", font=SMALL_FONT, takefocus = 0, width=15)
            ent_variable.grid(row=next_row, column=0, padx = 5, pady = 5, sticky=W)
            self.entries_variable_CV.append(ent_variable)                 

            # add entry value in second col
            ent_value = tk.Entry(self.frame_CV, font=SMALL_FONT, takefocus = 0, width=35)
            ent_value.grid(row=next_row, column=1, padx = 5, pady = 5, sticky=W)
            self.entries_value_CV.append(ent_value)
            
            # Confirm
            def confirm_CV(next_row):
                tmp_ID = {}
                tmp_ID = {self.entries_variable_CV[next_row].get() : self.entries_value_CV[next_row].get()}
                self.results_dict[self.selected_folder].update(tmp_ID)     
                self.entries_variable_CV[next_row]['state'] = tk.DISABLED
                self.entries_value_CV[next_row]['state'] = tk.DISABLED
                btn_confirm_CV.destroy()
                btn_reject_CV.destroy()
                 
            btn_confirm_CV = tk.Button(self.frame_CV, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=lambda: confirm_CV(next_row), cursor=CURSOR_HAND)
            btn_confirm_CV.grid(row=next_row, column=2, padx = 5, pady = 5, sticky=W)

            # Delete
            def reject_CV(next_row):
                print(next_row)
            btn_reject_CV = tk.Button(self.frame_CV, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=lambda: reject_CV(next_row), cursor=CURSOR_HAND)
            btn_reject_CV.grid(row=next_row, column=3, padx = 5, pady = 5, sticky=W)


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
                #df.to_excel(tmp_global_path.replace('\\', '/')) # write dataframe to file
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
                destroy_widgets([self.menu, self.label, self.my_listbox, self.my_xscrollbar, self.my_yscrollbar, self.label_frame_ID, self.label_frame_CV, self.modify_btn,
                self.confirm_btn, self.multiple_confirm_btn])
                xnat_pic_gui.choose_you_action(master)

        def clear_metadata_frame(self, master):
            destroy_widgets([self.menu, self.label, self.my_listbox, self.my_xscrollbar, self.my_yscrollbar, self.label_frame_ID, self.label_frame_CV, self.modify_btn,
            self.confirm_btn, self.multiple_confirm_btn])
            xnat_pic_gui.choose_you_action(master)

    class XNATUploader():

        def __init__(self, master):
            
            # Disable main frame buttons
            disable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

            # Start with a popup to get credentials
            login_popup = tk.Toplevel()
            login_popup.title("XNAT-PIC ~ Login")
            login_popup.geometry("%dx%d+%d+%d" % (550, 200, my_width/3, my_height/4))

            # Closing window event: if it occurs, the popup must be destroyed and the main frame buttons must be enabled
            def closed_window():
                login_popup.destroy()
                #Enable all buttons
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])
            login_popup.protocol("WM_DELETE_WINDOW", closed_window)

            # XNAT ADDRESS      
            login_popup.label_address = tk.Label(login_popup, text="  XNAT web address  ", font=SMALL_FONT)   
            login_popup.label_address.grid(row=0, column=0, padx=1, ipadx=1)
            login_popup.entry_address = tk.Entry(login_popup)
            login_popup.entry_address.var = tk.StringVar()
            login_popup.entry_address["textvariable"] = login_popup.entry_address.var # Optionmenu
            login_popup.entry_address.grid(row=0, column=1, padx=1, ipadx=1)
           
            # XNAT USER 
            login_popup.label_user = tk.Label(login_popup, text="Username", font=SMALL_FONT)
            login_popup.label_user.grid(row=1, column=0, padx=1, ipadx=1)
            login_popup.entry_user = tk.Entry(login_popup)
            login_popup.entry_user.var = tk.StringVar()
            login_popup.entry_user["textvariable"] = login_popup.entry_user.var
            login_popup.entry_user.grid(row=1, column=1, padx=1, ipadx=1)

            # XNAT PASSWORD 
            login_popup.label_psw = tk.Label(login_popup, text="Password", font=SMALL_FONT)
            login_popup.label_psw.grid(row=2, column=0, padx=1, ipadx=1)

            # Show/Hide the password
            def toggle_password():
                if login_popup.entry_psw.cget('show') == '':
                    login_popup.entry_psw.config(show='*')
                    login_popup.toggle_btn.config(text='Show Password')
                else:
                    login_popup.entry_psw.config(show='')
                    login_popup.toggle_btn.config(text='Hide Password')
            

            login_popup.entry_psw = tk.Entry(login_popup, show="*")
            login_popup.entry_psw.var = tk.StringVar()
            login_popup.entry_psw["textvariable"] = login_popup.entry_psw.var
            login_popup.entry_psw.grid(row=2, column=1, padx=1, ipadx=1)
            login_popup.toggle_btn = tk.Button(login_popup, text='Show Password',  command=toggle_password)
            login_popup.toggle_btn.grid(row=2, column=2)

            # HTTP/HTTPS 
            login_popup.http = tk.StringVar()
            login_popup.button_http = tk.Radiobutton(
                login_popup,
                text=" http:// ",
                variable=login_popup.http,
                value="http://")
            login_popup.button_http.grid(row=4, column=0)
            login_popup.button_http.select()
            login_popup.button_https = tk.Radiobutton(
                login_popup,
                text=" https:// ",
                variable=login_popup.http,
                value="https://")
            login_popup.button_https.grid(row=4, column=1)

            # SAVE CREDENTIALS CHECKBOX
            login_popup.remember = tk.IntVar()
            login_popup.btn_remember = tk.Checkbutton(
                login_popup, text="Remember me", variable=login_popup.remember
            )
            login_popup.btn_remember.grid(row=4, column=2, padx=1, ipadx=1)

            # CONNECTION
            login_popup.button_connect = tk.Button(
                login_popup,
                text="Login", font=SMALL_FONT, 
                width=15,
                command=partial(self.login, login_popup, master)
            )
            login_popup.button_connect.grid(row=5, column=0)

            # QUIT button
            def quit_event():
                login_popup.destroy()
                enable_buttons([master.convert_btn, master.info_btn, master.upload_btn])

            login_popup.button_quit = tk.Button(
                login_popup,
                text='Quit', font=SMALL_FONT,
                width=15,
                command=quit_event,
            )
            login_popup.button_quit.grid(row=5, column=2)
            self.load_saved_credentials(login_popup)

        def load_saved_credentials(self, popup):
            # REMEMBER CREDENTIALS
            try:
                home = os.path.expanduser("~")
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                decrypted_file = os.path.join(
                    home, "Documents", ".XNAT_login_file00000.txt"
                )
                pyAesCrypt.decryptFile(encrypted_file, decrypted_file, os.environ.get('secretKey'), bufferSize)
                login_file = open(decrypted_file, "r")
                line = login_file.readline()
                popup.entry_address.var.set(line[8:-1])
                line = login_file.readline()
                popup.entry_user.var.set(line[9:-1])
                line = login_file.readline()
                popup.entry_psw.var.set(line[9:-1])
                login_file.close()
                os.remove(decrypted_file)
                popup.btn_remember.select()
            except Exception as error:
                pass

        def login(self, popup, master):

            # LOGIN
            popup.entry_address_complete = popup.http.get() + popup.entry_address.var.get()
            # self.entry_address_complete = popup.entry_address_complete
            # self.entry_user = popup.entry_user.var.get()
            # self.entry_psw = popup.entry_psw.var.get()

            # Method to check if there is an existent session!!!!
            home = os.path.expanduser("~")
            try:
                self.session = xnat.connect(
                    popup.entry_address_complete,
                    popup.entry_user.var.get(),
                    popup.entry_psw.var.get(),
                )
                # print(type(self.session))
                # self.session.disconnect()
                # print(type(self.session))
                if popup.remember.get() == True:
                    self.save_credentials(popup)
                else:
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
                self.overall_uploader(master)
            except xnat.exceptions.XNATLoginFailedError as err:
                messagebox.showerror("Error!", err)
            except Exception as error:
                messagebox.showerror("Error!", error)

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
                file = os.path.join(home, "Documents", ".XNAT_login_file.txt")
                login_file = open(file, "w+")
                login_file.write(
                    "Address:"
                    + popup.entry_address.var.get()
                    + "\n"
                    + "Username:"
                    + popup.entry_user.var.get()
                    + "\n"
                    + "Password:"
                    + popup.entry_psw.var.get()
                    + "\n"
                    + "HTTP:"
                    + popup.http.get()
                )
                login_file.close()
                # encrypt
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                pyAesCrypt.encryptFile(file, encrypted_file, os.environ.get('secretKey'), bufferSize)
                # decrypt
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

        def check_experiment_name(self):

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
                                # experiment = self.session.classes.MRSessionData(parent=subject, label=self.exp.get())
                                # Clear cache to refresh the catalog
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
                destroy_widgets([master.convert_btn, master.info_btn, master.upload_btn,
                                master.info_convert_btn, master.info_info_btn, master.info_upload_btn])
            except:
                pass
            #################### Create the new frame ####################

            #############################################
            ################ Main Buttons ###############
            x_btn = int(my_width/5) # /5 if there is the processing button
            y_btn = int(my_height*20/100)
            width_btn = int(my_width/7)

            # Upload project
            prj_text = tk.StringVar()
            self.prj_btn = tk.Button(master.my_canvas, textvariable=prj_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                    command=partial(self.check_buttons, master, press_btn=0), cursor=CURSOR_HAND)
            prj_text.set("Upload Project")
            master.my_canvas.create_window(x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.prj_btn)
            
            # Upload subject
            sub_text = tk.StringVar()
            self.sub_btn = tk.Button(master.my_canvas, textvariable=sub_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                    command=partial(self.check_buttons, master, press_btn=1), cursor=CURSOR_HAND)
            sub_text.set("Upload Subject")
            master.my_canvas.create_window(2*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.sub_btn)

            # Upload experiment
            exp_text = tk.StringVar()
            self.exp_btn = tk.Button(master.my_canvas, textvariable=exp_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                    command=partial(self.check_buttons, master, press_btn=2), cursor=CURSOR_HAND)
            exp_text.set("Upload Experiment")
            master.my_canvas.create_window(3*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.exp_btn)       
            
            # Upload file
            file_text = tk.StringVar()
            self.file_btn = tk.Button(master.my_canvas, textvariable=file_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                    command=partial(self.check_buttons, master, press_btn=3), cursor=CURSOR_HAND)
            file_text.set("Upload File")
            master.my_canvas.create_window(4*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.file_btn) 

            # Upload additional files
            self.add_file_flag = tk.IntVar()
            self.add_file_btn = tk.Checkbutton(master.my_canvas, variable=self.add_file_flag, onvalue=1, offvalue=0, anchor=tk.CENTER, 
                                                background=BACKGROUND_COLOR, highlightthickness=0)
            y_ck_btn = int(my_height*30/100)
            self.check_add_files = master.my_canvas.create_text(3.6*x_btn, int(my_height*30/100), anchor = tk.CENTER, width=width_btn, 
                                                            fill='white', font=SMALL_FONT, 
                                                            text="Additional Files")
            master.my_canvas.create_window(4*x_btn, y_ck_btn, anchor=tk.CENTER, window=self.add_file_btn)

            # Custom Variables
            self.n_custom_var = tk.IntVar()
            custom_var_options = list(range(0, 5))
            self.custom_var_list = ttk.OptionMenu(master.my_canvas, self.n_custom_var, 0, *custom_var_options)
            self.check_n_custom_var = master.my_canvas.create_text(3.6*x_btn, int(my_height*33/100), anchor = tk.CENTER, width=width_btn, 
                                                            fill='white', font=SMALL_FONT, 
                                                            text="Custom Variables")
            master.my_canvas.create_window(4*x_btn, int(my_height*33/100), anchor=tk.CENTER, width=width_btn/5, window=self.custom_var_list)
            #############################################

            #############################################
            ################# Project ###################
            x_label = int(my_width/5)
            width_menu = int(my_width/5)
            # Label
            y_prj = int(my_height*40/100)
            self.select_prj = master.my_canvas.create_text(x_label, y_prj, anchor = tk.CENTER, width=width_menu, fill=DISABLE_LBL_COLOR, font=LARGE_FONT, 
                                                            text="Select Project")
            
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
            master.my_canvas.create_window(2*x_label, y_prj, anchor=tk.CENTER, width=width_menu, window=self.project_list)
            
            # Button to add a new project
            def add_project():
                enable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])
                self.entry_prjname.delete(0,tk.END)
            new_prj_text = tk.StringVar()
            self.new_prj_btn = tk.Button(master.my_canvas, textvariable=new_prj_text, state=tk.DISABLED, font=SMALL_FONT, bg=BG_BTN_COLOR, 
                                        fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_project, cursor=CURSOR_HAND)
            new_prj_text.set("Add New Project")
            master.my_canvas.create_window(3*x_btn, y_prj, width = width_btn, anchor = tk.CENTER, window = self.new_prj_btn)
            
            # Entry to write a new project
            width_btn_write = int(my_width/9)
            self.entry_prjname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn, y_prj, width = width_btn_write, anchor = tk.E, window = self.entry_prjname)

            # Button to confirm new project
            x_btn_confirm = int(my_width*84/100)
            self.confirm_new_prj = tk.Button(master.my_canvas, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=self.check_project_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_confirm, y_prj, anchor=tk.CENTER, window=self.confirm_new_prj)

            # Button to reject new project
            x_btn_reject = int(my_width*86/100)
            self.reject_new_prj = tk.Button(master.my_canvas, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=reject_project, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_reject, y_prj, anchor=tk.CENTER, window=self.reject_new_prj)
            #############################################

            #############################################
            ################# Subject ###################
            # Label
            y_sub = int(my_height*50/100)
            self.select_sub = master.my_canvas.create_text(x_label, y_sub, anchor = tk.CENTER, width = width_menu, fill = DISABLE_LBL_COLOR, font = LARGE_FONT, 
                                                            text = "Select Subject")
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

            # Menu
            if self.prj.get() != '--':
                self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
            else:
                self.OPTIONS2 = []
            self.sub = tk.StringVar()
            self.subject_list = ttk.OptionMenu(master.my_canvas, self.sub, default_value, *self.OPTIONS2)
            self.subject_list.configure(state="disabled")
            self.sub.trace('w', get_experiments)
            self.sub.trace('w', reject_subject)
            master.my_canvas.create_window(2*x_label, y_sub, anchor = tk.CENTER, width = width_menu, window = self.subject_list)
            
            # Button to add a new subject
            def add_subject():
                enable_buttons([self.entry_subname, self.confirm_new_sub, self.reject_new_sub])
                self.entry_subname.delete(0,tk.END)
            new_sub_text = tk.StringVar()
            self.new_sub_btn = tk.Button(master.my_canvas, textvariable=new_sub_text, state=tk.DISABLED, font=SMALL_FONT, bg=BG_BTN_COLOR, 
                                        fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_subject, cursor=CURSOR_HAND)
            new_sub_text.set("Add New Subject")
            master.my_canvas.create_window(3*x_btn, y_sub, width = width_btn, anchor = tk.CENTER, window = self.new_sub_btn)

            # Entry to write a new subject
            self.entry_subname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn, y_sub, width=width_btn_write, anchor=tk.E, window=self.entry_subname)

            # Button to confirm new subject
            self.confirm_new_sub = tk.Button(master.my_canvas, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=self.check_subject_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_confirm, y_sub, anchor=tk.CENTER, window=self.confirm_new_sub)

            # Button to reject new subject
            self.reject_new_sub = tk.Button(master.my_canvas, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=reject_subject, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_reject, y_sub, anchor=tk.CENTER, window=self.reject_new_sub)
            #############################################

            #############################################
            ################# Experiment ################
            def reject_experiment(*args):
                self.entry_expname.delete(0,tk.END)
                disable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])
            # Label
            y_exp = int(my_height*60/100)
            self.select_exp = master.my_canvas.create_text(x_label, y_exp, anchor=tk.CENTER, width=width_menu, fill=DISABLE_LBL_COLOR, font=LARGE_FONT, 
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
            master.my_canvas.create_window(2*x_label, y_exp, anchor=tk.CENTER, width=width_menu, window=self.experiment_list)
            
            # Button to add a new experiment
            def add_experiment():
                enable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])
                self.entry_expname.delete(0,tk.END)
            new_exp_text = tk.StringVar()
            self.new_exp_btn = tk.Button(master.my_canvas, textvariable=new_exp_text, state=tk.DISABLED, font=SMALL_FONT, bg=BG_BTN_COLOR, 
                                        fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_experiment, cursor=CURSOR_HAND)
            new_exp_text.set("Add New Experiment")
            master.my_canvas.create_window(3*x_btn, y_exp, width = width_btn, anchor = tk.CENTER, window = self.new_exp_btn)

            # Entry to write a new experiment
            self.entry_expname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn, y_exp, width=width_btn_write, anchor=tk.E, window=self.entry_expname)

            # Button to confirm new experiment
            self.confirm_new_exp = tk.Button(master.my_canvas, image = master.logo_accept, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=self.check_experiment_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_confirm, y_exp, anchor=tk.CENTER, window=self.confirm_new_exp)

            # Button to reject new experiment
            self.reject_new_exp = tk.Button(master.my_canvas, image = master.logo_delete, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                            command=reject_experiment, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_reject, y_exp, anchor=tk.CENTER, window=self.reject_new_exp)
            #############################################

            #############################################
            ################ EXIT Button ################
            def exit_upload():
                result = messagebox.askquestion("XNAT-PIC Uploader", "Do you want to exit anyway?", icon='warning')
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
                                                    self.check_n_custom_var, self.subtitle])
                    # Perform disconnection of the session if it is alive
                    try:
                        self.session.disconnect()
                        self.session = ''
                    except:
                        pass
                    # Restore the main frame
                    xnat_pic_gui.choose_you_action(master)

            self.exit_text = tk.StringVar() 
            self.exit_btn = tk.Button(master.my_canvas, textvariable=self.exit_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                    cursor=CURSOR_HAND, takefocus=0)
            self.exit_btn.configure(command=exit_upload)
            self.exit_text.set("Exit")
            y_exit_btn = int(my_height*80/100)
            width_btn = int(my_width*10/100)
            master.my_canvas.create_window(x_btn, y_exit_btn, anchor=tk.CENTER, width=width_btn, window=self.exit_btn)
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
            self.next_btn = tk.Button(master.my_canvas, textvariable=self.next_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                    command=next, cursor=CURSOR_HAND, takefocus=0, state='disabled')
            self.next_text.set("Next")
            master.my_canvas.create_window(4*x_btn, y_exit_btn, anchor=tk.CENTER, width=width_btn, window=self.next_btn)
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

            if press_btn == 0:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn])
                enable_buttons([self.project_list, self.new_prj_btn])
                # Insert subtitle
                self.subtitle = master.my_canvas.create_text(int(my_width/2), int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/7), fill='red', font=LARGE_FONT, 
                                                            text="Project Uploader")
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
                self.subtitle = master.my_canvas.create_text(int(my_width/2), int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/7), fill='red', font=LARGE_FONT, 
                                                            text="Subject Uploader")
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
                self.subtitle = master.my_canvas.create_text(int(my_width/2), int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/7), fill='red', font=LARGE_FONT, 
                                                            text="Experiment Uploader")
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
                self.subtitle = master.my_canvas.create_text(int(my_width/2), int(my_height*30/100), anchor=tk.CENTER, width=int(my_width/7), fill='red', font=LARGE_FONT, 
                                                            text="File Uploader")
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

            project_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC Project Uploader: Select project directory in DICOM format to upload")
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
                                    ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", "The subject you are trying to retrieve does not match with the custom variables."
                                                                                                "\n Would you like to continue?")
                                    if ans != True:
                                        return
                                params['subject_id'] = self.sub.get()
                                self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
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

            subject_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC Subject Uploader: Select subject directory in DICOM format to upload")
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
                            ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", "The subject you are trying to retrieve does not match with the custom variables."
                                                                                        "\n Would you like to continue?")
                            if ans != True:
                                return
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
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

            experiment_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC Experiment Uploader: Select experiment directory in DICOM format to upload")
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
                            ans = messagebox.askyesno("XNAT-PIC Experiment Uploader", "The subject you are trying to retrieve does not match with the custom variables."
                                                                                        "\n Would you like to continue?")
                            if ans != True:
                                return
                        params['subject_id'] = self.sub.get()
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
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
                            self.exp.set('_'.join([experiment_to_upload.split('/')[-3].replace('_dcm', ''), experiment_to_upload.split('/')[-2].replace('.','_')]).replace(' ', '_'))
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

            files_to_upload = filedialog.askopenfilenames(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC File Uploader: Select file to upload")
            
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
    root = tk.Tk()
    app = xnat_pic_gui(root)
    s = SplashScreen(root, timeout=5000)
    root.mainloop()

           