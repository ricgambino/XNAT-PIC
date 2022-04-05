from doctest import master
from logging import exception
import shutil
import tkinter as tk
from tkinter import END, MULTIPLE, SINGLE, W, filedialog, mainloop, messagebox
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
from numpy import empty
from pip import main 
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
password = os.environ.get('secretKey')
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

        # Logo on top
        #logo3 = Image.open(PATH_IMAGE + "path163.png")
        #self.logo3 = ImageTk.PhotoImage(logo3)
        #label1 = tk.Label(self.root, image=self.logo3,  bg="#31C498", width=1715)
        #self.my_canvas.create_window(3, 20, anchor=tk.NW, window=label1)

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
         convert_text.set("Bruker2DICOM")
         self.my_canvas.create_window(x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.convert_btn)
         
         # Fill in the info
         info_text = tk.StringVar()
         self.info_btn = tk.Button(self.my_canvas, textvariable=info_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command=partial(self.metadata, self), cursor=CURSOR_HAND)
         info_text.set("Fill in the info")
         self.my_canvas.create_window(2*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.info_btn)

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
         
         self.info_convert_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: helpmsg("button1"), cursor=QUESTION_HAND)
         self.my_canvas.create_window(x_btn, y_btn1, anchor=tk.CENTER, window=self.info_convert_btn)

         self.info_info_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: helpmsg("button2"), cursor=QUESTION_HAND)
         self.my_canvas.create_window(2*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_info_btn)

         self.info_upload_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: helpmsg("button3"), cursor=QUESTION_HAND)
         self.my_canvas.create_window(3*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_upload_btn)

         #self.info_process_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: helpmsg("button4"), cursor=QUESTION_HAND)
         #self.my_canvas.create_window(4*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_process_btn)        

    def get_page(self):
        return self.root   

    class bruker2dicom_conversion():
        
        def __init__(self, master):

            self.params = {}
            
            # Disable the buttons
            master.convert_btn['state'] = tk.DISABLED
            master.info_btn['state'] = tk.DISABLED
            master.upload_btn['state'] = tk.DISABLED
            #master.process_btn['state'] = tk.DISABLED
            
            def normal_btn():
                self.conv_popup.destroy()
                #Enable all buttons
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
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

        def prj_conversion(self, master):

            ############### Whole project conversion ################

            # Disable the buttons
            master.convert_btn['state'] = tk.DISABLED
            master.info_btn['state'] = tk.DISABLED
            master.upload_btn['state'] = tk.DISABLED
            #master.process_btn['state'] = tk.DISABLED

            # Ask for project directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for the chosen directory
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
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
                    dir_dcm = dir + '_dcm'
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
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                #master.process_btn['state'] = tk.NORMAL          

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                #master.process_btn['state'] = tk.NORMAL
                self.conv_popup.destroy()
                
        def sbj_conversion(self, master):

            ############### Single subject conversion ################

            # Convert from bruker to DICOM and disable the buttons
            master.convert_btn['state'] = tk.DISABLED
            master.info_btn['state'] = tk.DISABLED
            master.upload_btn['state'] = tk.DISABLED
            #master.process_btn['state'] = tk.DISABLED

            # Ask for subject directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select subject directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for chosen directory
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                #master.process_btn['state'] = tk.NORMAL
                messagebox.showerror("XNAT-PIC Converter", "You have not chosen a directory")
                return
            master.root.deiconify()
            master.root.update()
            head, tail = os.path.split(self.folder_to_convert)
            head = head + '_dcm'
            project_foldername = tail.split('.',1)[0] + "_dcm"
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
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                #master.process_btn['state'] = tk.NORMAL          

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Converter", e)
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                #master.process_btn['state'] = tk.NORMAL
                 
    # Fill in information
    class metadata():
        def __init__(self, master):

                self.fill_info(master)

        def fill_info(self, master): 
                # Disable all buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                #master.process_btn['state'] = tk.DISABLED

                # Choose your directory
                self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")
                
                # If there is no folder selected, re-enable the buttons and return
                if not self.information_folder:
                    master.convert_btn['state'] = tk.NORMAL
                    master.info_btn['state'] = tk.NORMAL
                    master.upload_btn['state'] = tk.NORMAL
                    #master.process_btn['state'] = tk.NORMAL
                    return
             
                project_name = (self.information_folder.rsplit("/",1)[1])
                fields = ["Project", "Subject", "Acquisition_date", "Group", "Dose", "Timepoint"]
                results = []
                path_list = []
                item_list = []

                # Load the acq. date from visu_pars file for Bruker file or DICOM
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
                                    break
                            # Check if the DICOM is in the scans
                            for filename in [f for f in filenames if f.endswith(".dcm")]:
                                dataset = pydicom.dcmread((dirpath + "\\" + filename).replace('\\', '/'))
                                match_date = datetime.datetime.strptime(dataset.AcquisitionDate, '%Y%m%d').strftime('%Y-%m-%d')
                                break

                            if match_date:
                               break

                    return match_date

                # Scan all files contained in the folder that the user has provided
                for item in os.listdir(self.information_folder):
                         path = str(self.information_folder) + "\\" + str(item)
                         name = str(item) + "_" + "Custom_Variables.txt"
                         # Check if the content of the project is a folder and therefore a patient or a file not to be considered
                         if os.path.isdir(path):
                             # Check if the txt file is in folder of the patient
                             # If the file exists, read le info
                             if os.path.exists(path + "\\" + name):
                                with open(path + "\\" + name, 'r') as meta_file:
                                    data = (meta_file.read().split('\n'))
                                    tmp_result = [i for i in data if any(i for j in fields if str(j) in i)]
                                    for word in fields:
                                        tmp_result = [x.replace(word, '', 1).strip() for x in tmp_result]
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

                                tmp_result = [str(project_name), str(item), tmp_acq_date,'','', '']
                             #  with open(path + "\\" + name, 'w+') as meta_file:
                             #       meta_file.write(tabulate([['Project', str(tmp_result[0])], ['Subject', str(tmp_result[1])], ['Acquisition_date', str(tmp_result[2])], 
                             #       ['Group', str(tmp_result[3])], ['Dose', str(tmp_result[4])], ['Timepoint', str(tmp_result[5])]], headers=['Variable', 'Value']))
                             
                             results.extend(tmp_result)           # Save all the info of the project
                             path_list.append(path + "\\" + name) # Save all the path
                             item_list.append(str(item))

                #################### Update the frame ####################
                master.convert_btn.destroy()
                master.info_btn.destroy()
                master.upload_btn.destroy()
                #master.process_btn.destroy()
                master.info_convert_btn.destroy()
                master.info_info_btn.destroy()
                master.info_upload_btn.destroy()
                #master.info_process_btn.destroy()

                #################### Menu ###########################

                menu = tk.Menu(master.root)
                file_menu = tk.Menu(menu, tearoff=0)
                file_menu.add_command(label="Clear", command = lambda: clear_metadata())
                file_menu.add_separator()
                file_menu.add_command(label="Save All", command = lambda: save_metadata())

                menu.add_cascade(label="File", menu=file_menu)
                menu.add_command(label="About", command = lambda: messagebox.showinfo("XNAT-PIC","Help"))
                menu.add_command(label="Exit", command = lambda: exit_metadata())
                master.root.config(menu=menu)
                
                #################### Folder list #################### 
                x_folder_list = int(my_width*10/100)
                y_folder_list = int(my_height*18/100)
                label = tk.Label(master.my_canvas, text='List of folders contained in the project: ' + '\n'+ project_name, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, font = SMALL_FONT)
                master.my_canvas.create_window(x_folder_list, y_folder_list, width = int(my_width*25/100), height = int(my_height*5/100), anchor=tk.NW, window=label)
                
                y_folder_list1 = int(my_height*25/100)
                my_listbox = tk.Listbox(master.my_canvas, selectmode=SINGLE, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, font=SMALL_FONT, takefocus = 0)
                master.my_canvas.create_window(x_folder_list, y_folder_list1, width = int(my_width*25/100), height = int(my_height*40/100) ,anchor = tk.NW, window = my_listbox)

                # List of subject in the project in the listbox
                my_listbox.insert(tk.END, *item_list)

                # Attach listbox to x and y scrollbar ()
                x_folder_scrollbar = int(my_width*8/100)
                my_yscrollbar = tk.Scrollbar(master.my_canvas, orient="vertical")
                my_listbox.config(yscrollcommand = my_yscrollbar.set)
                my_yscrollbar.config(command = my_listbox.yview)
                master.my_canvas.create_window(x_folder_scrollbar, y_folder_list1, height = int(my_height*40/100), anchor = tk.NW, window = my_yscrollbar)
                
                y_folder_scrollbar = int(my_height*66/100)
                my_xscrollbar = tk.Scrollbar(master.my_canvas, orient="horizontal")
                my_listbox.config(xscrollcommand = my_xscrollbar.set)
                my_xscrollbar.config(command = my_listbox.xview)
                master.my_canvas.create_window(x_folder_list, y_folder_scrollbar, width = int(my_width*25/100), anchor = tk.NW, window = my_xscrollbar)
                
                #################### Subject form ####################
                # ID
                # Label frame for ID: folder selected, project, subject and acq. date
                label_frame_ID = tk.LabelFrame(master.my_canvas, background = BACKGROUND_COLOR, borderwidth=5, font=SMALL_FONT, relief='solid', text="ID")
                
                x_lbl_ID = int(my_width*40/100)
                y_lbl_ID = int(my_height*24/100)
                h_lbl_ID = int(my_height*20/100)
                master.my_canvas.create_window(x_lbl_ID, y_lbl_ID, anchor='nw', height = h_lbl_ID, window=label_frame_ID)

                # Label ID
                keys_ID = ["Project", "Subject", "Acq. date"]
                folder_lbl = tk.Label(label_frame_ID, background = BACKGROUND_COLOR, text="Folder", width=10, font=SMALL_FONT, fg=TEXT_BTN_COLOR)
                folder_lbl.grid(row=0, column=0, padx = 5, pady = 5, sticky=W)
                count = 1
                labels=[]
                for key in keys_ID:
                    labels.append(tk.Label(label_frame_ID, background = BACKGROUND_COLOR, text=key, width=10, font=SMALL_FONT, fg=TEXT_BTN_COLOR))
                    labels[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                    count += 1
                
                # Entry ID
                folder_entry = tk.Entry(label_frame_ID, state='disabled', width=50, font=SMALL_FONT, takefocus = 0)
                folder_entry.grid(row=0, column=1, padx = 5, pady = 5, sticky=W)              
                count = 1
                entries=[]
                for key in keys_ID:
                    entries.append(tk.Entry(label_frame_ID, state='disabled', width=50, font=SMALL_FONT, takefocus = 0))
                    entries[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                    count += 1

                # Calendar for acq. date
                cal = DateEntry(label_frame_ID, state = tk.DISABLED, width=10, font = SMALL_FONT, background=BACKGROUND_COLOR, date_pattern = 'y-mm-dd', foreground='white', borderwidth=0)
                cal.delete(0, tk.END)
                cal.grid(row=3, column=2, padx = 5, pady = 5, sticky=W)

                ####################################################################
                # Custom Variables (CV)
                # Label frame for Custom Variables: group, dose, timepoint
                label_frame_CV = tk.LabelFrame(master.my_canvas, background = BACKGROUND_COLOR, borderwidth=5, font=SMALL_FONT, relief='solid', text="Custom Variables")
                x_lbl_CV = x_lbl_ID
                y_lbl_CV = int(my_height*50/100)
                h_lbl_CV = int(my_height*15/100)
                master.my_canvas.create_window(x_lbl_CV, y_lbl_CV, height = h_lbl_CV, window=label_frame_CV, anchor='nw')

                # Label CV
                keys_CV = ["Group", "Dose", "Timepoint"]
                count = 0
                for key in keys_CV:
                    labels.append(tk.Label(label_frame_CV, background = BACKGROUND_COLOR, fg=TEXT_BTN_COLOR, font=SMALL_FONT, text=key, width=10))
                    labels[-1].grid(row=count, column=0, padx = 5, pady = 5, sticky=W)
                    count += 1

                # Entry ID              
                count = 0
                for key in keys_CV:
                    entries.append(tk.Entry(label_frame_CV, font=SMALL_FONT, state='disabled', takefocus = 0, width=35))
                    entries[-1].grid(row=count, column=1, padx = 5, pady = 5, sticky=W)
                    count += 1

                # Group Menu
                OPTIONS = ["untreated", "treated"]
                selected_group = tk.StringVar()
                group_menu = ttk.Combobox(label_frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=selected_group, width=10)
                group_menu['values'] = OPTIONS
                group_menu['state'] = 'disabled'
                group_menu.grid(row=0, column=3, padx = 5, pady = 5, sticky=W)
                
                # UM for dose
                OPTIONS_UM = ["Mg", "kg", "mg", "µg", "ng"]
                selected_dose = tk.StringVar()
                dose_menu = ttk.Combobox(label_frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=selected_dose, width=10)
                dose_menu['values'] = OPTIONS_UM
                dose_menu['state'] = 'disabled'
                dose_menu.grid(row=1, column=3, padx = 5, pady = 5, sticky=W)

                # Timepoint
                OPTIONS = ["pre", "post"]
                selected_timepoint = tk.StringVar()
                timepoint_menu = ttk.Combobox(label_frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=selected_timepoint, width=10)
                timepoint_menu['values'] = OPTIONS
                timepoint_menu['state'] = 'disabled'
                timepoint_menu.grid(row=2, column=3, padx = 5, pady = 5, sticky=W)

                time_entry = tk.Entry(label_frame_CV, font = SMALL_FONT, state='disabled', takefocus = 0, width=5)
                time_entry.grid(row=2, column=4, padx = 5, pady = 5, sticky=W)

                OPTIONS1 = ["seconds", "minutes", "hours", "days", "weeks", "months", "years"]
                selected_timepoint1 = tk.StringVar()
                timepoint_menu1 = ttk.Combobox(label_frame_CV, font = SMALL_FONT, takefocus = 0, textvariable=selected_timepoint1, width=7)
                timepoint_menu1['values'] = OPTIONS1
                timepoint_menu1['state'] = 'disabled'
                timepoint_menu1.grid(row=2, column=5, padx = 5, pady = 5, sticky=W)

                #################### Load the info about the selected subject ####################
                def items_selected(event):
                    # Clear all the combobox and the entry
                    selected_group.set('')
                    selected_timepoint.set('')
                    selected_timepoint1.set('')
                    dose_menu.set('')
                    time_entry.delete(0, tk.END)
                    cal.delete(0, tk.END)
                    dose_menu['state'] = tk.DISABLED
                    group_menu['state'] = tk.DISABLED
                    timepoint_menu['state'] = tk.DISABLED
                    time_entry.config(state=tk.DISABLED)
                    timepoint_menu1['state'] = tk.DISABLED
                    cal['state'] = tk.DISABLED

                    """ handle item selected event
                    """
                    # Get selected indices
                    global selected_index 
                    selected_index = my_listbox.curselection()[0]
                    
                    max_lim = len(fields)
                    # load the Info of the selected folder
                    folder_entry.config(state=tk.NORMAL)
                    folder_entry.delete(0, tk.END)
                    folder_entry.insert(0, str(item_list[selected_index]))
                    folder_entry.config(state=tk.DISABLED)

                    for i in range(0, max_lim):
                        entries[i].config(state=tk.NORMAL)
                        entries[i].delete(0, tk.END)
                        entries[i].insert(0, str(results[selected_index*max_lim+i]))
                        entries[i].config(state=tk.DISABLED)
                   
                my_listbox.bind('<Tab>', items_selected)
                
                #################### Clear the metadata ####################
                # clear_text = tk.StringVar() 
                # clear_btn = tk.Button(master.my_canvas, textvariable=clear_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: clear_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                # clear_text.set("Clear")
                # width_btn = int(my_width*14/100)
                # y_btn1 = int(my_height*77/100)
                # master.my_canvas.create_window(x_lbl, y_btn1, anchor = tk.NW, width = width_btn, window = clear_btn)
                
                def clear_metadata():
                    # Clear all the combobox and the entry
                    selected_dose.set('')
                    selected_group.set('')
                    selected_timepoint.set('')
                    selected_timepoint1.set('')
                    cal.delete(0, tk.END)
                    time_entry.delete(0, tk.END)

                    state = entries[0]['state']
                    # Set empty string in all the entries
                    for i in range(2, len(fields)):
                            entries[i]['state'] = tk.NORMAL
                            entries[i].delete(0, tk.END)
                            entries[i]['state'] = state

                #################### Modify the metadata ####################
                modify_text = tk.StringVar() 
                modify_btn = tk.Button(master.my_canvas, textvariable=modify_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: modify_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                modify_text.set("Modify")
                x_lbl = x_lbl_ID
                y_btn = int(my_height*70/100)
                width_btn = int(my_width*14/100)
                master.my_canvas.create_window(x_lbl, y_btn, anchor = tk.NW, width = width_btn, window = modify_btn)
                 
                def modify_metadata():
                     # Check before confirming the data
                    try:
                        selected_index
                        pass
                    except Exception as e:
                         messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                         raise 

                    # Normal entry
                    for i in range(0, 2):
                        entries[i].config(state=tk.NORMAL)

                    for i in range(3, len(fields)-1):
                        entries[i].config(state=tk.NORMAL)
                    # Acquisition date has a default format in entry but you can modify date with the calendar
                    cal['state'] = 'normal'
                    
                    def date_entry_selected(event):
                        w = event.widget
                        entries[fields.index("Acquisition_date")].config(state=tk.NORMAL)
                        entries[fields.index("Acquisition_date")].delete(0, tk.END)
                        entries[fields.index("Acquisition_date")].insert(0, str(w.get_date()))
                        entries[fields.index("Acquisition_date")].config(state=tk.DISABLED)
                        my_listbox.selection_set(selected_index)

                    cal.bind("<<DateEntrySelected>>", date_entry_selected)

                    # Option menu for the group
                    group_menu['state'] = 'readonly'

                    def group_changed(event):
                        """ handle the group changed event """
                        entries[fields.index("Group")].delete(0, tk.END)
                        entries[fields.index("Group")].insert(0, str(selected_group.get()))                    
                        my_listbox.selection_set(selected_index)

                    group_menu.bind("<<ComboboxSelected>>", group_changed)

                    # Option menu for the dose
                    dose_menu['state'] = 'readonly'

                    def dose_changed(event):
                        """ handle the dose changed event """
                        dose_str = ''
                        if entries[fields.index("Dose")].get():
                            for word in filter(str(entries[fields.index("Dose")].get()).__contains__, OPTIONS_UM):
                                # If a unit of measurement is already present, replace it
                                dose_str = str(entries[fields.index("Dose")].get()).replace(word, str(selected_dose.get()))
                                entries[fields.index("Dose")].delete(0, tk.END)     
                                entries[fields.index("Dose")].insert(0, dose_str)                    
                                my_listbox.selection_set(selected_index)
                                return
                                 # If only the number is present, add the unit of measure
                            dose_str = str(entries[fields.index("Dose")].get()) + "-" + str(selected_dose.get())
                        else:
                            # If the entry is empty, enter only the unit of measure
                            dose_str = str(selected_dose.get())

                        entries[fields.index("Dose")].delete(0, tk.END)     
                        entries[fields.index("Dose")].insert(0, dose_str)                    
                        my_listbox.selection_set(selected_index)

                    dose_menu.bind("<<ComboboxSelected>>", dose_changed)
                    
                    # Option menu for the timepoint
                    timepoint_menu1['state'] = 'readonly'
                    time_entry['state'] = 'normal'
                    timepoint_menu['state'] = 'readonly'

                    def timepoint_changed(event):
                        entries[fields.index("Timepoint")].config(state=tk.NORMAL)
                        """ handle the timepoint changed event """
                        if str(time_entry.get()) or str(selected_timepoint1.get()):
                           timepoint_str = str(selected_timepoint.get()) + "-" + str(time_entry.get()) + "-" + str(selected_timepoint1.get())
                        else:
                            timepoint_str = str(selected_timepoint.get()) 

                        my_listbox.selection_set(selected_index)

                        if time_entry.get():
                            try:
                             float(time_entry.get())
                            except Exception as e: 
                             messagebox.showerror("XNAT-PIC", "Insert a number in the timepoint entry")

                        entries[fields.index("Timepoint")].delete(0, tk.END)
                        entries[fields.index("Timepoint")].insert(0, timepoint_str)
                        entries[fields.index("Timepoint")].config(state=tk.DISABLED)

                    timepoint_menu.bind("<<ComboboxSelected>>", timepoint_changed)
                    time_entry.bind("<Return>", timepoint_changed)
                    timepoint_menu1.bind("<<ComboboxSelected>>", timepoint_changed)

                #################### Confirm the metadata ####################
                def check_entries():
                    # Check before confirming the data
                    try:
                        selected_index
                        pass
                    except Exception as e:
                         messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                         raise 

                    if not entries[fields.index("Project")].get():
                       messagebox.showerror("XNAT-PIC", "Insert the name of the project")
                       raise 

                    if not entries[fields.index("Subject")].get():
                       messagebox.showerror("XNAT-PIC", "Insert the name of the subject")
                       raise

                    if entries[fields.index("Acquisition_date")].get():
                        try:
                           datetime.datetime.strptime(entries[fields.index("Acquisition_date")].get(), '%Y-%m-%d')
                        except Exception as e:
                           messagebox.showerror("XNAT-PIC", "Incorrect data format in acquisition date, should be YYYY-MM-DD")
                           raise

                    # if entries[fields.index("Dose")].get(): 
                    #     try:
                    #         float(entries[fields.index("Dose")].get())
                    #     except Exception as e: 
                    #         messagebox.showerror("XNAT-PIC", "Insert a number in dose")
                    #         raise

                    if entries[fields.index("Timepoint")].get() and '-' in  entries[fields.index("Timepoint")].get(): 
                        if not str(entries[fields.index("Timepoint")].get()).split('-')[0] in OPTIONS:
                           messagebox.showerror("XNAT-PIC", "Select pre/post in timepoint")
                           raise
                        if not str(entries[fields.index("Timepoint")].get()).split('-')[2] in OPTIONS1:
                           messagebox.showerror("XNAT-PIC", "Select seconds, minutes, hours, days, weeks, months, years in timepoint")
                           raise

                        input_num = str(entries[fields.index("Timepoint")].get()).split('-')[1]
                        try:
                            float(input_num)
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Insert a number in timepoint between pre/post and seconds, minutes, hours..")  
                            raise

                confirm_text = tk.StringVar() 
                confirm_btn = tk.Button(master.my_canvas, textvariable=confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: confirm_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                confirm_text.set("Confirm")
                x_conf_btn = int(my_width*59/100)
                master.my_canvas.create_window(x_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = confirm_btn)

                def confirm_metadata():
                        check_entries()

                        # Update the info in the txt file
                        max_lim = len(fields)
                        for i in range(0, max_lim):
                            results[selected_index*max_lim+i] =  entries[i].get()     
                            entries[i]['state'] = tk.DISABLED            
                        
                        selected_group.set('')
                        selected_dose.set('')
                        selected_timepoint.set('')
                        selected_timepoint1.set('')
                        time_entry.delete(0, tk.END)
                        cal.delete(0, tk.END)
                        time_entry.config(state=tk.DISABLED)
                        group_menu['state'] = tk.DISABLED
                        dose_menu['state'] = tk.DISABLED
                        timepoint_menu['state'] = tk.DISABLED
                        timepoint_menu1['state'] = tk.DISABLED
                        cal['state'] = tk.DISABLED

                        # Saves the changes made by the user in the txt file
                        with open(path_list[selected_index], 'w+') as meta_file:
                                        meta_file.write(tabulate([['Project', str(results[selected_index*max_lim+0])], ['Subject', str(results[selected_index*max_lim+1])], ['Acquisition_date', str(results[selected_index*max_lim+2])], 
                                        ['Group', str(results[selected_index*max_lim+3])], ['Dose', str(results[selected_index*max_lim+4])], ['Timepoint', str(results[selected_index*max_lim+5])]], headers=['Variable', 'Value']))

                #################### Confirm multiple metadata ####################
                multiple_confirm_text = tk.StringVar() 
                multiple_confirm_btn = tk.Button(master.my_canvas, textvariable=multiple_confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, command = lambda: confirm_multiple_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                multiple_confirm_text.set("Multiple Confirm")
                x_multiple_conf_btn = int(my_width*78/100)
                master.my_canvas.create_window(x_multiple_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = multiple_confirm_btn)
                
                def normal_button():
                    #clear_btn["state"] = tk.NORMAL
                    modify_btn["state"] = tk.NORMAL
                    confirm_btn["state"] = tk.NORMAL
                    multiple_confirm_btn["state"] = tk.NORMAL
                    #save_btn["state"] = tk.NORMAL

                def confirm_multiple_metadata():
                    #clear_btn["state"] = tk.DISABLED
                    modify_btn["state"] = tk.DISABLED
                    confirm_btn["state"] = tk.DISABLED
                    multiple_confirm_btn["state"] = tk.DISABLED
                    #save_btn["state"] = tk.DISABLED
                    
                    try:
                        selected_index
                        pass
                    except Exception as e:
                         normal_button()
                         messagebox.showerror("XNAT-PIC", "Click Tab to select a folder from the list box on the left")
                         raise

                    messagebox.showinfo("Metadata","1. Select the folders from the box on the left for which to copy the info entered!\n 2. Always remaining in the box on the left, press ENTER to confirm or ESC to cancel!")
 
                    my_listbox.selection_set(selected_index)    
                    my_listbox['selectmode'] = MULTIPLE
                    
                    # The user presses 'enter' to confirm 
                    def items_selected2(event):
                       
                       seltext = [my_listbox.get(index) for index in my_listbox.curselection()]
                       result = messagebox.askquestion("Multiple Confirm", "Are you sure you want to save data for the following folders?\n" + '\n'.join(seltext), icon='warning')
                       if result == 'yes':
                        confirm_metadata()
                        # Get indexes of selected folders
                        selected_text_list = my_listbox.curselection()
                        
                        # Update the list of results
                        max_lim = len(fields)
                        for i in range(0, len(selected_text_list)):
                                for j in range(0, max_lim):
                                   results[selected_text_list[i]*max_lim+j] =  entries[j].get()

                        # Update the txt file
                        for i in range(0, len(selected_text_list)):
                                with open(path_list[selected_text_list[i]], 'w+') as meta_file:
                                                    meta_file.write(tabulate([['Project', str(results[selected_index*max_lim+0])], ['Subject', str(results[selected_index*max_lim+1])], ['Acquisition_date', str(results[selected_index*max_lim+2])], 
                        
                                                    ['Group', str(results[selected_index*max_lim+3])], ['Dose', str(results[selected_index*max_lim+4])], ['Timepoint', str(results[selected_index*max_lim+5])]], headers=['Variable', 'Value']))
                      
                        messagebox.showinfo("Metadata","The information has been saved for the selected folders!")

                       # Clear the focus and the select mode of the listbox is single
                       normal_button()
                       my_listbox.selection_clear(0, 'end')
                       my_listbox['selectmode'] = SINGLE
                       

                    my_listbox.bind("<Return>", items_selected2)
                    
                    # The user presses 'esc' to cancel
                    def items_cancel(event):
                         # Clear the focus and the select mode of the listbox is single
                        messagebox.showinfo("Metadata","The information was not saved for the selected folders!")
                        normal_button()
                        my_listbox.selection_clear(0, 'end')
                        my_listbox['selectmode'] = SINGLE
                    my_listbox.bind("<Escape>", items_cancel)

                #################### Save the metadata ####################
                # save_text = tk.StringVar() 
                # save_btn = tk.Button(master.my_canvas, textvariable=save_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: save_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                # save_text.set("Save")
                # master.my_canvas.create_window(x_multiple_conf_btn, y_btn1, anchor = tk.NW, width = width_btn, window = save_btn)
                
                def save_metadata():
                    err = False
                    try:
                        selected_index
                    except Exception as e:
                        err = True
                        messagebox.showerror("XNAT-PIC", "Select a folder from the list box on the left")

                    # Save the summary txt file of the whole project     
                    if not err:
                        all_sub = []
                        
                        for i in range(0, len(results), len(fields)):
                            all_sub = all_sub + ["--"] + [['Project', str(results[i])], ['Subject', str(results[i+1])], ['Acquisition_date', str(results[i+2])], 
                                        ['Group', str(results[i+3])], ['Dose', str(results[i+4])], ['Timepoint', str(results[i+5])]]
                                        
                        with open(str(self.information_folder) + "\\" + project_name + '_' + 'Custom_Variables.txt', 'w+') as meta_file:
                           meta_file.write(tabulate(all_sub, headers=['Variable', 'Value']))

                        # Destroy of the elements of the current frame and go to the previous frame
                        clear_metadata_frame()
                
                #################### Exit the metadata ####################
                # exit_text = tk.StringVar() 
                # exit_btn = tk.Button(master.my_canvas, textvariable=exit_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: exit_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                # exit_text.set("Exit")
                # x_exit_btn = int(my_width*10/100)
                # master.my_canvas.create_window(x_exit_btn, y_btn1, anchor = tk.NW,width = width_btn, window = exit_btn)

                def exit_metadata():
                    result = messagebox.askquestion("Exit", "Do you want to exit?", icon='warning')
                    if result == 'yes':
                        clear_metadata_frame()

                def clear_metadata_frame():
                    menu.destroy()
                    label.destroy()
                    my_listbox.destroy()
                    my_yscrollbar.destroy()
                    my_xscrollbar.destroy()

                    #for i in range(0, len(fields)): 
                    #    labels[i].destroy()   
                    #    entries[i].destroy()
                    
                    #timepoint_menu.destroy()
                    #timepoint_menu1.destroy()
                    #time_entry.destroy()
                    #group_menu.destroy()
                    #cal.destroy()
                    
                    label_frame_ID.destroy()
                    label_frame_CV.destroy()
                    #clear_btn.destroy()
                    modify_btn.destroy()
                    confirm_btn.destroy()
                    #save_btn.destroy()
                    #exit_btn.destroy()
                    multiple_confirm_btn.destroy()

                    xnat_pic_gui.choose_you_action(master)

    class XNATUploader():

        def __init__(self, master):

            def disable_buttons():
                # Disable all buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                #master.process_btn['state'] = tk.DISABLED
            
            disable_buttons()

            def enable_btn():
                login_popup.destroy()
                #Enable all buttons
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                #master.process_btn['state'] = tk.NORMAL

            login_popup = tk.Toplevel()
            login_popup.title("XNAT-PIC ~ Login")
            login_popup.geometry("%dx%d+%d+%d" % (550, 200, my_width/3, my_height/4))

            login_popup.protocol("WM_DELETE_WINDOW", enable_btn)

            # XNAT ADDRESS      
            login_popup.label_address = tk.Label(login_popup, text="  XNAT web address  ", font=SMALL_FONT)   
            login_popup.label_address.grid(row=0, column=0, padx=1, ipadx=1)
            login_popup.entry_address = tk.Entry(login_popup)
            login_popup.entry_address.var = tk.StringVar()
            login_popup.entry_address["textvariable"] = login_popup.entry_address.var
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

            login_popup.button_quit = tk.Button(
                login_popup,
                text='Quit', font=SMALL_FONT,
                width=15,
                command=lambda: (login_popup.destroy(), self.normal_btn(master, disconnect=True)),
            )
            login_popup.button_quit.grid(row=5, column=2)
            self.load_saved_credentials(login_popup)

        def normal_btn(self, master, popup=None, disconnect=False, close_popup=False):

            if disconnect == True:
                try:
                    self.session.disconnect()
                except:
                    pass
            if close_popup == True:
                try:
                    popup.destroy()
                except:
                    pass   
            #Enable all buttons
            master.convert_btn['state'] = tk.NORMAL
            master.info_btn['state'] = tk.NORMAL
            master.upload_btn['state'] = tk.NORMAL
            #master.process_btn['state'] = tk.NORMAL

        def load_saved_credentials(self, popup):
            # REMEMBER CREDENTIALS
            try:
                home = os.path.expanduser("~")
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                decrypted_file = os.path.join(
                    home, "Documents", ".XNAT_login_file00000.txt"
                )
                pyAesCrypt.decryptFile(encrypted_file, decrypted_file, password, bufferSize)
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
            self.entry_address_complete = popup.entry_address_complete
            self.entry_user = popup.entry_user.var.get()
            self.entry_psw = popup.entry_psw.var.get()

            # Method to check if there is an existent session!!!!
            home = os.path.expanduser("~")
            try:
                self.session = xnat.connect(
                    popup.entry_address_complete,
                    popup.entry_user.var.get(),
                    popup.entry_psw.var.get(),
                )
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
                self.overall_uploader(master)
                #self.project_selection(master)
            except xnat.exceptions.XNATLoginFailedError as err:
                messagebox.showerror("Error!", err)
            except Exception as error:
                messagebox.showerror("Error!", error)

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
                pyAesCrypt.encryptFile(file, encrypted_file, password, bufferSize)
                # decrypt
                os.remove(file)

        def enable_next(self, *_):
            # # EXISTING PROJECT
            if self.newprj_var.get() == 0:
                if self.prj.get() in self.OPTIONS:
                    self.button_next["state"] = "normal"
                else:
                    self.button_next["state"] = "disabled"

            # # NEW PROJECT
            else:
                if self.entry_prjname.var.get():
                    self.button_next["state"] = "normal"
                else:
                    self.button_next["state"] = "disabled"

        def check_project_name(self, *args):

            if self.entry_prjname.get() != '':
                # Method to check about project name
                if self.entry_prjname.get() in list(self.OPTIONS.key_map.keys()):
                    # Case 1 --> The project already exists
                    messagebox.showerror(
                        "XNAT-PIC Uploader!",
                        "Project ID %s already exists! Please, enter a different project ID"
                        % self.entry_prjname.get(),
                    )
                else:
                    # Case 2 --> The project does not exist yet
                    try:
                        result = messagebox.askyesno("XNAT-PIC Uploader", "A new project will be created. Are you sure?")
                        if result is False:
                            return
                        self.prj.set(self.entry_prjname.get())
                        disable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])
                        project = self.session.classes.ProjectData(
                                       name=self.prj.get(), parent=self.session)
                        self.session.clearcache()
                        messagebox.showinfo('XNAT-PIC Uploader', 'A new project is created.')                 
                    except exception as e:
                        messagebox.showerror("Error!", str(e))

        def check_subject_name(self, *args):

            if self.entry_subname.get() != '':
                # Check if the project already exists
                if self.prj.get() in list(self.OPTIONS.key_map.keys()):
                    # Method to check about project name
                    if self.entry_subname.get() in list(self.OPTIONS2.key_map.keys()):
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

                            # project = self.session.classes.ProjectData(
                            #            name=self.prj.get(), parent=self.session)
                            project = self.session.projects[self.prj.get()]
                            subject = self.session.classes.SubjectData(
                                        parent=project, label=self.sub.get())
                            self.session.clearcache()
                            messagebox.showinfo('XNAT-PIC Uploader', 'A new subject is created.')                 
                        except exception as e:
                            messagebox.showerror("Error!", str(e))
                else:
                    messagebox.showerror('XNAT-PIC Uploader', 'The current project does not exist in XNAT platform.'
                                                            'Please select an other project or create a new one.')

        def check_experiment_name(self):
            pass

        def overall_uploader(self, master):

            # def isChecked():
            #     master.add_file_flag = self.add_file_flag.get()
                           
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

            #Check Button for upload additional files
            self.add_file_flag = tk.IntVar()
            self.add_file_btn = tk.Checkbutton(master.my_canvas, text='Additional files', variable=self.add_file_flag,
                                onvalue=1, offvalue=0)
            y_ck_btn = int(my_height*30/100)
            master.my_canvas.create_window(4*x_btn, y_ck_btn, width=width_btn, anchor=tk.CENTER, window=self.add_file_btn)
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

            self.OPTIONS = list(self.session.projects)
            self.prj = tk.StringVar()
            default_value = "--"
            self.project_list = ttk.OptionMenu(master.my_canvas, self.prj, default_value, *self.OPTIONS)
            self.project_list.configure(state="disabled")
            self.prj.trace('w', get_subjects)
            master.my_canvas.create_window(2*x_label, y_prj, anchor=tk.CENTER, width=width_menu, window=self.project_list)
            
            # Button to add a new project
            def add_project():
                enable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])
                self.entry_prjname.delete(0,tk.END)
            new_prj_text = tk.StringVar()
            self.new_prj_btn = tk.Button(master.my_canvas, textvariable=new_prj_text, state=tk.DISABLED, font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_project, cursor=CURSOR_HAND)
            new_prj_text.set("Add New Project")
            master.my_canvas.create_window(3*x_btn, y_prj, width = width_btn, anchor = tk.CENTER, window = self.new_prj_btn)
            
            # Entry to write a new project
            width_btn_write = int(my_width/9)
            self.entry_prjname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn, y_prj, width = width_btn_write, anchor = tk.E, window = self.entry_prjname)

            # Button to confirm new project
            x_btn_confirm = int(my_width*84/100)
            self.confirm_new_prj = tk.Button(master.my_canvas, text = "V", bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command=self.check_project_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_confirm, y_prj, anchor=tk.CENTER, window=self.confirm_new_prj)

            # Button to reject new project
            def reject():
                self.entry_prjname.delete(0,tk.END)
                disable_buttons([self.entry_prjname, self.confirm_new_prj, self.reject_new_prj])
            x_btn_reject = int(my_width*86/100)
            self.reject_new_prj = tk.Button(master.my_canvas, text = "X", bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command=reject, cursor=CURSOR_HAND, state='disabled')
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
            # Menu
            if self.prj.get() != '--':
                self.OPTIONS2 = list(self.session.projects[self.prj.get()].subjects.key_map.keys())
            else:
                self.OPTIONS2 = []
            self.sub = tk.StringVar()
            self.subject_list = ttk.OptionMenu(master.my_canvas, self.sub, default_value, *self.OPTIONS2)
            self.subject_list.configure(state="disabled")
            self.sub.trace('w', get_experiments)
            master.my_canvas.create_window(2*x_label, y_sub, anchor = tk.CENTER, width = width_menu, window = self.subject_list)
            
            # Button to add a new subject
            def add_subject():
                enable_buttons([self.entry_subname, self.confirm_new_sub, self.reject_new_sub])
                self.entry_subname.delete(0,tk.END)
            new_sub_text = tk.StringVar()
            self.new_sub_btn = tk.Button(master.my_canvas, textvariable=new_sub_text, state=tk.DISABLED, font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_subject, cursor=CURSOR_HAND)
            new_sub_text.set("Add New Subject")
            master.my_canvas.create_window(3*x_btn, y_sub, width = width_btn, anchor = tk.CENTER, window = self.new_sub_btn)

            # Entry to write a new subject
            self.entry_subname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn, y_sub, width=width_btn_write, anchor=tk.E, window=self.entry_subname)

            # Button to confirm new subject
            self.confirm_new_sub = tk.Button(master.my_canvas, text = "V", bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command=self.check_subject_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_confirm, y_sub, anchor=tk.CENTER, window=self.confirm_new_sub)

            # Button to reject new subject
            def reject():
                self.entry_subname.delete(0,tk.END)
                disable_buttons([self.entry_subname, self.confirm_new_sub, self.reject_new_sub])

            self.reject_new_sub = tk.Button(master.my_canvas, text = "X", bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command=reject, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_reject, y_sub, anchor=tk.CENTER, window=self.reject_new_sub)
            #############################################

            #############################################
            ################# Experiment ################
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
            master.my_canvas.create_window(2*x_label, y_exp, anchor=tk.CENTER, width=width_menu, window=self.experiment_list)
            
            # Button to add a new experiment
            def add_experiment():
                enable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])
                self.entry_expname.delete(0,tk.END)
            new_exp_text = tk.StringVar()
            self.new_exp_btn = tk.Button(master.my_canvas, textvariable=new_exp_text, state=tk.DISABLED, font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=BORDERWIDTH, 
                                        command=add_experiment, cursor=CURSOR_HAND)
            new_exp_text.set("Add New Experiment")
            master.my_canvas.create_window(3*x_btn, y_exp, width = width_btn, anchor = tk.CENTER, window = self.new_exp_btn)

            # Entry to write a new experiment
            self.entry_expname = tk.Entry(master.my_canvas, font=SMALL_FONT, state="disabled")
            master.my_canvas.create_window(4*x_btn, y_exp, width=width_btn_write, anchor=tk.E, window=self.entry_expname)

            # Button to confirm new experiment
            self.confirm_new_exp = tk.Button(master.my_canvas, text = "V", bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command=self.check_experiment_name, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_confirm, y_exp, anchor=tk.CENTER, window=self.confirm_new_exp)

            # Button to reject new experiment
            def reject():
                self.entry_expname.delete(0,tk.END)
                disable_buttons([self.entry_expname, self.confirm_new_exp, self.reject_new_exp])

            self.reject_new_exp = tk.Button(master.my_canvas, text = "X", bg=BG_BTN_COLOR, borderwidth=BORDERWIDTH, command=reject, cursor=CURSOR_HAND, state='disabled')
            master.my_canvas.create_window(x_btn_reject, y_exp, anchor=tk.CENTER, window=self.reject_new_exp)
            #############################################

            #############################################
            ################ EXIT Button ################
            def exit_upload():
                result = messagebox.askquestion("XNAT-PIC Uploader", "Do you want to exit anyway?", icon='warning')
                if result == 'yes':
                    # Destroy all the existent widgets (Button, OptionMenu, ...)
                    destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
                    # Delete all widgets that cannot be destroyed
                    delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp])
                    # Perform disconnection of the session if it is alive
                    try:
                        self.session.disconnect()
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
                destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
                # Delete all widgets that cannot be destroyed
                delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.subtitle])
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
                    a = self.prj.get()
                    if a != '--':
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
                    a = self.prj.get()
                    if a != '--':
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
                    a = self.prj.get()
                    b = self.sub.get()
                    if a != '--' and b != '--':
                        enable_buttons([self.next_btn])
                self.sub.trace('w', enable_next)

            elif press_btn == 3:
                # Disable main buttons
                disable_buttons([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn])
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
                    a = self.prj.get()
                    b = self.sub.get()
                    c = self.exp.get()
                    if a != '--' and b != '--' and c != '--':
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
                try:
                    # Start progress bar
                    progressbar = ProgressBar(bar_title='XNAT-PIC Uploader')
                    progressbar.start_indeterminate_bar()

                    list_dirs = os.listdir(project_to_upload)
                    # list_of_subjects = [(os.path.join(project_to_upload, sub).replace('\\', '/'), self.prj.get()) for sub in list_dirs]

                    start_time = time.time()

                    def upload_thread():

                        self.uploader = Dicom2XnatUploader(self.session)
                        
                        for sub in list_dirs:
                            # Check if 'MR' folder is already into the folder_to_upload path
                            if 'MR' != os.path.basename(sub):
                                sub = os.path.join(sub, 'MR').replace('\\', '/')
                            else:
                                sub = sub.replace('\\', '/')
                            # Check for existing custom variables file
                            flag = 0
                            try:
                                subject_data = read_table('/'.join([sub, 'Custom_Variables.txt']))
                                # Define the subject_id and the experiment_id
                                if self.sub.get() == '--':
                                    self.sub.set(subject_data['Subject'])
                                if self.exp.get() == '--':
                                    self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                                flag = 1
                            except Exception as error:
                                # Define the subject_id and the experiment_id 
                                if self.sub.get() == '--':
                                    self.sub.set(sub.split('/')[-2].replace('_dcm', ''))
                                if self.exp.get() == '--':
                                    self.exp.set('_'.join([sub.split('/')[-3].replace('_dcm', ''), sub.split('/')[-2].replace('_dcm', '')]).replace(' ', '_'))
                                flag = 0

                            progressbar.set_caption('Uploading ' + str(self.sub.get()) + ' ...')
                            # Create parameters dictionary to pass to the uploader function
                            params = {'folder_to_upload': sub,
                                        'project_id': self.prj.get(),
                                        'subject_id': self.sub.get(),
                                        'experiment_id': self.exp.get(),
                                        'custom_var_flag': flag,
                                        'custom_var': subject_data
                                        }
                            self.uploader.upload(params)
                            # Check for Results folder
                            if self.add_file_flag.get() == 1:
                                self.session.clearcache()
                                self.uploader_file = FileUploader(self.session)
                                progressbar.set_caption('Uploading files to ' + str(self.exp.get()) + ' ...')
                                for sub_dir in os.listdir(sub):
                                    if 'Results' in sub_dir:
                                        vars = {}
                                        vars['project_id'] = self.prj.get()
                                        vars['subject_id'] = self.sub.get()
                                        vars['experiment_id'] = self.exp.get()
                                        vars['folder_name'] = sub_dir
                                        list_of_files = os.scandir(os.path.join(sub, sub_dir))
                                        file_paths = []
                                        for file in list_of_files:
                                            if file.is_file():
                                                file_paths.append(file.path)
                                        self.uploader_file.upload(file_paths, vars)

                    end_time = time.time()
                    print('Elapsed time for conversion: ' + str(end_time - start_time) + ' s')

                    t = threading.Thread(target=upload_thread, args=())
                    t.start()
                    
                    while t.is_alive() == True:
                        progressbar.update_bar()
                    
                    # Stop the progress bar and close the popup
                    progressbar.stop_progress_bar()

                except Exception as e: 
                    messagebox.showerror("XNAT-PIC - Uploader", e)

                # Restore main frame buttons
                messagebox.showinfo("XNAT-PIC Uploader","Done! Your subject is uploaded on XNAT platform.")
            # Destroy all the existent widgets (Button, OptionMenu, ...)
            destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
            # Delete all widgets that cannot be destroyed
            delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.subtitle])
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
                try:
                    self.uploader = Dicom2XnatUploader(self.session)
                    # Start progress bar
                    progressbar = ProgressBar(bar_title='XNAT-PIC Uploader')
                    progressbar.start_indeterminate_bar()

                    start_time = time.time()
                    # Check if 'MR' folder is already into the folder_to_upload path
                    if 'MR' != os.path.basename(subject_to_upload):
                        subject_to_upload = os.path.join(subject_to_upload, 'MR').replace('\\', '/')
                    else:
                        subject_to_upload = subject_to_upload.replace('\\', '/')
                    # Check for existing custom variables file
                    flag = 0
                    try:
                        subject_data = read_table('/'.join([subject_to_upload, 'Custom_Variables.txt']))
                        # Define the subject_id and the experiment_id
                        if self.sub.get() == '--':
                            self.sub.set(subject_data['Subject'])
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_'))
                        flag = 1
                    except:
                        # Define the subject_id and the experiment_id 
                        if self.sub.get() == '--':
                            self.sub.set(subject_to_upload.split('/')[-2].replace('_dcm', ''))
                        if self.exp.get() == '--':
                            self.exp.set('_'.join([subject_to_upload.split('/')[-3].replace('_dcm', ''), subject_to_upload.split('/')[-2].replace('_dcm', '')]).replace(' ', '_'))
                        flag = 0

                    progressbar.set_caption('Uploading ' + str(self.sub.get()) + ' ...')
                    # Create parameters dictionary to pass to the uploader function
                    params = {'folder_to_upload': subject_to_upload,
                                'project_id': self.prj.get(),
                                'subject_id': self.sub.get(),
                                'experiment_id': self.exp.get(),
                                'custom_var_flag': flag,
                                'custom_var': subject_data
                                }
                    t = threading.Thread(target=self.uploader.upload, args=(params, ))
                    t.start()

                    while t.is_alive() == True:
                        progressbar.update_bar()
                    else:
                        # Check for Results folder
                        if self.add_file_flag.get() == 1:
                            self.session.clearcache()
                            self.uploader_file = FileUploader(self.session)
                            for sub_dir in os.listdir(subject_to_upload):
                                if 'Results' in sub_dir:
                                    vars = {}
                                    vars['project_id'] = self.prj.get()
                                    vars['subject_id'] = self.sub.get()
                                    vars['experiment_id'] = self.exp.get()
                                    vars['folder_name'] = sub_dir
                                    list_of_files = os.scandir(os.path.join(subject_to_upload, sub_dir))
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
            destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
            # Delete all widgets that cannot be destroyed
            delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.subtitle])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)

        def experiment_uploader(self, master):
            # Call for check_project_name
            # Call for upload() method from Dicom2XnatUploader class
            pass

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
            destroy_widgets([self.prj_btn, self.sub_btn, self.exp_btn, self.file_btn, self.add_file_btn,
                                    self.exit_btn, self.project_list, self.new_prj_btn, self.entry_prjname,
                                    self.confirm_new_prj, self.reject_new_prj, self.add_file_btn,
                                    self.subject_list, self.new_sub_btn, self.experiment_list, self.new_exp_btn,
                                    self.entry_subname, self.confirm_new_sub, self.reject_new_sub,
                                    self.entry_expname, self.confirm_new_exp, self.reject_new_exp,
                                    self.next_btn, self.exit_btn])
            # Delete all widgets that cannot be destroyed
            delete_widgets(master.my_canvas, [self.select_prj, self.select_sub, self.select_exp, self.subtitle])
            # Clear and update session cache
            self.session.clearcache()
            self.overall_uploader(master)


if __name__ == "__main__":
    root = tk.Tk()
    app = xnat_pic_gui(root)
    s = SplashScreen(root, timeout=5000)
    root.mainloop()

           