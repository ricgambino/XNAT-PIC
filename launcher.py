from ast import Str
from dataclasses import field
from doctest import master
from logging import exception, raiseExceptions
from msilib import type_binary
from pickle import TRUE
import shutil, stat
import tkinter as tk
from tkinter import CENTER, MULTIPLE, NW, SINGLE, filedialog,messagebox
from tkinter import font
from tkinter.tix import COLUMN, Balloon
from turtle import width
from unittest import result
from PIL import Image, ImageTk, ImageDraw
from tkinter import Button, Tk, HORIZONTAL
from tkinter import ttk
import json
import time
import os, re
from functools import partial
import subprocess
import platform 
from importlib_metadata import metadata
from numpy import empty
from progress_bar import ProgressBar
from dicom_converter import Bruker2DicomConverter
import xnat
from xnat_upload import xnat_uploader, xnat_uploader_dir
import pyAesCrypt
from tabulate import tabulate
import datetime
import threading
from dotenv import load_dotenv


PATH_IMAGE = "images\\"
PERCENATGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
BACKGROUND_COLOR = "#31C498"
THEME_COLOR = "black"
TEXT_BTN_COLOR = "black"
TEXT_LBL_COLOR = "white"
BG_BTN_COLOR = "#80FFE6"
BG_LBL_COLOR = "black"
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"


load_dotenv()
password = os.environ.get('secretKey')
bufferSize = int(os.environ.get('bufferSize1')) * int(os.environ.get('bufferSize2'))
      
class xnat_pic_gui(tk.Frame):

    def __init__(self, master):

        self.root = master
        self.root.state("zoomed")
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
        self.root.configure(background=THEME_COLOR)
        # If you want the logo 
        #self.root.iconbitmap(r"logo3.ico")

        # Define Canvas and logo in background
        global my_width
        my_width = int(w*PERCENATGE_SCREEN)
        logo = Image.open(PATH_IMAGE + "logo41.png")
        wpercent = (my_width/float(logo.size[0]))
        global my_height
        my_height = int((float(logo.size[1])*float(wpercent))*PERCENATGE_SCREEN)
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
        self.enter_btn = tk.Button(self.my_canvas, textvariable=enter_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=lambda: (self.enter_btn.destroy(), xnat_pic_gui.choose_you_action(self)), cursor=CURSOR_HAND)
        enter_text.set("ENTER")
        self.my_canvas.create_window(int(my_width/2), int(my_height*0.7), width = int(my_width/5), anchor = tk.CENTER, window = self.enter_btn)
        
        
    # Choose to upload files, fill in the info, convert files, process images
    def choose_you_action(self):
         ##########################################
         # Action buttons           
         # Positions for action button parametric with respect to the size of the canvas
         x_btn = int(my_width/5) # 
         y_btn = int(my_height*60/100)
         width_btn = int(my_width/7)

         # Convert files Bruker2DICOM
         convert_text = tk.StringVar()
         self.convert_btn = tk.Button(self.my_canvas, textvariable=convert_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.bruker2dicom_conversion, self), cursor=CURSOR_HAND)
         convert_text.set("Bruker2DICOM")
         self.my_canvas.create_window(x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.convert_btn)
         
         # Fill in the info
         info_text = tk.StringVar()
         self.info_btn = tk.Button(self.my_canvas, textvariable=info_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.metadata, self), cursor=CURSOR_HAND)
         info_text.set("Fill in the info")
         self.my_canvas.create_window(2*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.info_btn)

         # Upload files
         upload_text = tk.StringVar()
         self.upload_btn = tk.Button(self.my_canvas, textvariable=upload_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.xnat_dcm_uploader, self), cursor=CURSOR_HAND)
         upload_text.set("Uploader")
         self.my_canvas.create_window(3*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.upload_btn)        
        
         # Processing your files
         process_text = tk.StringVar()
         self.process_btn = tk.Button(self.my_canvas, textvariable=process_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, cursor=CURSOR_HAND)
         process_text.set("Processing")
         self.my_canvas.create_window(4*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.process_btn)
        
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
         
         self.info_convert_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=0, command = lambda: helpmsg("button1"), cursor=QUESTION_HAND)
         self.my_canvas.create_window(x_btn, y_btn1, anchor=tk.CENTER, window=self.info_convert_btn)

         self.info_info_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=0, command = lambda: helpmsg("button2"), cursor=QUESTION_HAND)
         self.my_canvas.create_window(2*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_info_btn)

         self.info_upload_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=0, command = lambda: helpmsg("button3"), cursor=QUESTION_HAND)
         self.my_canvas.create_window(3*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_upload_btn)

         self.info_process_btn = tk.Button(self.my_canvas, image = self.logo_info, bg=BG_BTN_COLOR, borderwidth=0, command = lambda: helpmsg("button4"), cursor=QUESTION_HAND)
         self.my_canvas.create_window(4*x_btn, y_btn1, anchor=tk.CENTER, window=self.info_process_btn)        

    def get_page(self):
        return self.root   

    class bruker2dicom_conversion():
        
        def __init__(self, master):

            self.params = {}

            def isChecked():
                self.params['results_flag'] = self.results_flag.get()
            
            def checkOverwrite():
                master.overwrite_flag = self.overwrite_flag.get()

            self.conv_popup = tk.Toplevel()
            self.conv_popup.geometry("%dx%d+%d+%d" % (500, 150, 700, 500))
            self.conv_popup.title('DICOM Converter')
            self.btn_prj = tk.Button(self.conv_popup, text='Convert Project', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (self.conv_popup.destroy(), self.prj_conversion(master)))
            self.btn_prj.grid(row=2, column=0, padx=10, pady=5)
            self.btn_sbj = tk.Button(self.conv_popup, text='Convert Subject', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (self.conv_popup.destroy(), self.sbj_conversion(master)))
            self.btn_sbj.grid(row=3, column=0, padx=10, pady=5)
            self.results_flag = tk.IntVar()
            # master.results_flag = self.results_flag.get()
            self.btn_results = tk.Checkbutton(self.conv_popup, text='Copy results', variable=self.results_flag,
                                onvalue=1, offvalue=0, command=isChecked)
            self.btn_results.grid(row=2, column=1, sticky='W')
            self.overwrite_flag = tk.IntVar()
            master.overwrite_flag = self.overwrite_flag.get()
            self.btn_overwrite = tk.Checkbutton(self.conv_popup, text="Overwrite existing folders", variable=self.overwrite_flag,
                                onvalue=1, offvalue=0, command=checkOverwrite)
            self.btn_overwrite.grid(row=3, column=1, sticky='W')
            # self.params = {'results_flag': master.results_flag,
            #                 'overwrite_flag': master.overwrite_flag
            #                 }

        def prj_conversion(self, master):

            ############### Whole project conversion ################
            # Ask for project directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for the chosen directory
                messagebox.showerror("Dicom Converter", "You have not chosen a directory")
                return
            master.root.deiconify()
            master.root.update()
            self.dst = self.folder_to_convert + '_dcm'
            
            try:
                # Disable the buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                master.process_btn['state'] = tk.DISABLED

                start_time = time.time()

                # Start the progress bar
                progressbar = ProgressBar(bar_title='DICOM Project Converter')
                progressbar.start_determinate_bar()
                # progressbar.start_indeterminate_bar()

                # Check for subjects within the given project
                list_dirs = os.listdir(self.folder_to_convert)
                # Initialize the list of conversion errors
                conversion_err = []
                for j, dir in enumerate(list_dirs, 0):
        
                    # Update the current step of the progress bar
                    # progressbar.update_progressbar(j, len(list_dirs))
                    progressbar.set_caption(j + 1, len(list_dirs))
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
                        converter = Bruker2DicomConverter(current_folder, current_dst, self.params)
                        # converter.start_conversion()
                        # converter.multi_processes_conversion()
                        tp = threading.Thread(target=converter.multi_core_conversion, args=())
                        tp.start()
                        while tp.is_alive() == True:
                            # progressbar.update_bar()
                            progressbar.update_bar(0.36)
                            time.sleep(0.5)
                        else:
                            progressbar.update_progressbar(j + 1, len(list_dirs))

                # Stop the progress bar and close the popup
                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Total elapsed time: ' + str(end_time - start_time) + ' s')

                messagebox.showinfo("Bruker2DICOM","The conversion is done!\n\n\n\n"
                                    "Exceptions:\n\n" +
                                    str([str(x) for x in conversion_err])[1:-1])
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL          

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL
                self.conv_popup.destroy()
                
        def sbj_conversion(self, master):

            ############### Single subject conversion ################
            # Ask for subject directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select subject directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for chosen directory
                messagebox.showerror("Dicom Converter", "You have not chosen a directory")
                return
            master.root.deiconify()
            master.root.update()
            head, tail = os.path.split(self.folder_to_convert)
            head = head + '_dcm'
            project_foldername = tail.split('.',1)[0] + "_dcm"
            self.dst = os.path.join(head, project_foldername).replace('\\', '/')

            # If the destination folder already exists throw exception, otherwise create the new folder
            if os.path.isdir(self.dst):
                # Case 1 --> The directory already exists
                if master.overwrite_flag == 1:
                    # Existent folder with overwrite flag set to 1 --> remove folder and generate new one
                    shutil.rmtree(self.dst)
                    os.makedirs(self.dst)
                else:
                    # Existent folder without overwriting flag set to 0 --> ignore folder
                    messagebox.showerror("Dicom Converter", "Destination folder %s already exists" % self.dst)
                    return
            else:
                # Case 2 --> The directory does not exist
                if self.dst.split('/')[-1].count('_dcm') > 1:
                    # Check to avoid already converted folders
                    messagebox.showerror("Dicom Converter", "Chosen folder %s already converted" % self.dst)
                    return
                else:
                    # Create the new destination folder
                    os.makedirs(self.dst)

            try:
                # Convert from bruker to DICOM and disable the buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                master.process_btn['state'] = tk.DISABLED

                start_time = time.time()

                # Start the progress bar
                progressbar = ProgressBar(bar_title='DICOM Subject Converter')
                progressbar.start_indeterminate_bar()

                # Start converter
                converter = Bruker2DicomConverter(self.folder_to_convert, self.dst, self.params)
                # Initialize conversion thread
                tp = threading.Thread(target=converter.multi_core_conversion, args=())
                tp.start()
                while tp.is_alive() == True:
                    # As long as the thread is working, update the progress bar
                    progressbar.update_bar()
                progressbar.stop_progress_bar()

                end_time = time.time()
                print('Total elapsed time: ' + str(end_time - start_time) + ' s')

                messagebox.showinfo("Bruker2DICOM","Done! Now you can upload your files to XNAT.")
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL          

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL
                 
    # Fill in information
    class metadata():
        def __init__(self, master):

                messagebox.showinfo("Metadata","Select project directory!")

                # Disable all buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                master.process_btn['state'] = tk.DISABLED
               
                # Choose your directory
                self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")
                
                # If there is no folder selected, re-enable the buttons and return
                if not self.information_folder:
                    master.convert_btn['state'] = tk.NORMAL
                    master.info_btn['state'] = tk.NORMAL
                    master.upload_btn['state'] = tk.NORMAL
                    master.process_btn['state'] = tk.NORMAL
                    return
             
                project_name = (self.information_folder.rsplit("/",1)[1])
                fields = ["Project", "Subject", "Acquisition_date", "Group", "Dose", "Timepoint"]
                results = []
                path_list = []
                item_list = []

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
                                # If the txt file do not exist, create an empty layout
                                tmp_result = [str(project_name), str(item), '','','', '']
                                with open(path + "\\" + name, 'w+') as meta_file:
                                    meta_file.write(tabulate([['Project', str(tmp_result[0])], ['Subject', str(tmp_result[1])], ['Acquisition_date', str(tmp_result[2])], 
                                    ['Group', str(tmp_result[3])], ['Dose', str(tmp_result[4])], ['Timepoint', str(tmp_result[5])]], headers=['Variable', 'Value']))
                             
                             results.extend(tmp_result)           # Save all the info of the project
                             path_list.append(path + "\\" + name) # Save all the path
                             item_list.append(str(item))

                #################### Update the frame ####################
                master.convert_btn.destroy()
                master.info_btn.destroy()
                master.upload_btn.destroy()
                master.process_btn.destroy()
                master.info_convert_btn.destroy()
                master.info_info_btn.destroy()
                master.info_upload_btn.destroy()
                master.info_process_btn.destroy()

                #################### Folder list #################### 
                x_folder_list = int(my_width*10/100)
                y_folder_list = int(my_height*18/100)
                label = tk.Label(master.my_canvas, text='List of folders contained in the project: ' + '\n'+ project_name, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, font = SMALL_FONT)
                master.my_canvas.create_window(x_folder_list, y_folder_list, width = int(my_width*25/100), height = int(my_height*5/100), anchor=tk.NW, window=label)
                
                y_folder_list1 = int(my_height*25/100)
                my_listbox = tk.Listbox(master.my_canvas, selectmode=SINGLE, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, font=SMALL_FONT)
                master.my_canvas.create_window(x_folder_list, y_folder_list1, width = int(my_width*25/100), height = int(my_height*40/100) ,anchor = tk.NW, window = my_listbox)

                # List of subject in the project in the listbox
                #results_prj = list(map(lambda i: results[i], range(1, len(results), len(fields))))
                #my_listbox.insert(tk.END, *results_prj)
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
                # Project label
                keys = ["Project", "Subject", "Acq. date", "Group", "Dose", "Timepoint"]
                count = 0
                labels=[]
                x_lbl = int(my_width*40/100)
                y_lbl_perc = 25
                y_lbl_delta = 7.5
                for key in keys:
                    y_lbl = int(my_height*y_lbl_perc/100)
                    labels.append(tk.Label(master.my_canvas, text=key, font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR))
                    master.my_canvas.create_window(x_lbl, y_lbl, width = int(my_width*8/100), anchor = tk.NW, window = labels[count])
                    y_lbl_perc += y_lbl_delta
                    count += 1

                # Project entry               
                count = 0
                entries=[]
                x_entry = int(my_width*50/100)
                y_entry_perc = 25
                y_entry_delta = 7.5
                for key in keys:
                    y_entry = int(my_height*y_entry_perc/100)
                    entries.append(tk.Entry(master.my_canvas, state='disabled', font=SMALL_FONT))
                    master.my_canvas.create_window(x_entry, y_entry, width = int(my_width*20/100), anchor = tk.NW, window = entries[count])
                    y_entry_perc += y_entry_delta
                    count += 1

                # Menu
                # Dose
                OPTIONS = ["untreated", "treated"]
                selected_group = tk.StringVar()
                group_menu = ttk.Combobox(master.my_canvas, textvariable=selected_group, font = SMALL_FONT)
                group_menu['values'] = OPTIONS
                group_menu['state'] = 'disabled'
                x_dose_menu = int(my_width*72/100)
                y_dose_perc = 25
                y_dose_delta = 7.5
                y_dose_menu = int(my_height*(y_dose_perc+3*y_dose_delta)/100)
                master.my_canvas.create_window(x_dose_menu, y_dose_menu, anchor = tk.NW, width = int(my_width*9.5/100), window = group_menu)
                
                # Timepoint
                OPTIONS = ["pre", "post"]
                selected_timepoint = tk.StringVar()
                timepoint_menu = ttk.Combobox(master.my_canvas, textvariable=selected_timepoint, font = SMALL_FONT)
                timepoint_menu['values'] = OPTIONS
                timepoint_menu['state'] = 'disabled'
                x_timepoint_menu = int(my_width*72/100)
                y_timepiont_menu = int(my_height*(y_dose_perc+5*y_dose_delta)/100)
                master.my_canvas.create_window(x_timepoint_menu, y_timepiont_menu, anchor = tk.NW, width = int(my_width*5/100), window = timepoint_menu)

                time_entry = tk.Entry(master.my_canvas, state='disabled', font = SMALL_FONT)
                x_timepoint_menu1 = int(my_width*78/100)
                master.my_canvas.create_window(x_timepoint_menu1, y_timepiont_menu, anchor = tk.NW, width = int(my_width*5/100), window = time_entry)

                OPTIONS1 = ["seconds", "minutes", "hours", "days", "month", "years"]
                selected_timepoint1 = tk.StringVar()
                timepoint_menu1 = ttk.Combobox(master.my_canvas, textvariable=selected_timepoint1, font = SMALL_FONT)
                timepoint_menu1['values'] = OPTIONS1
                timepoint_menu1['state'] = 'disabled'
                x_timepoint_menu2 = int(my_width*84/100)
                master.my_canvas.create_window(x_timepoint_menu2, y_timepiont_menu, anchor = tk.NW, width = int(my_width*8/100), window = timepoint_menu1)

                #################### Load the info about the selected subject ####################
                def items_selected(event):
                    # Clear all the combobox and the entry
                    selected_group.set('')
                    selected_timepoint.set('')
                    selected_timepoint1.set('')
                    time_entry.delete(0, tk.END)
                    """ handle item selected event
                    """
                    # Get selected indices
                    global selected_index 
                    selected_index = my_listbox.curselection()[0]
                   
                    max_lim = len(fields)
                    for i in range(0, max_lim):
                        entries[i].config(state=tk.NORMAL)
                        entries[i].delete(0, tk.END)
                        entries[i].insert(0, str(results[selected_index*max_lim+i]))
                        entries[i].config(state=tk.DISABLED)

                my_listbox.bind("<Double-Button-1>", items_selected)
                
                #################### Modify the metadata ####################
                modify_text = tk.StringVar() 
                modify_btn = tk.Button(master.my_canvas, textvariable=modify_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: modify_metadata(), cursor=CURSOR_HAND)
                modify_text.set("Modify")
                y_btn = int(my_height*69/100)
                width_btn = int(my_width*14/100)
                master.my_canvas.create_window(x_lbl, y_btn, anchor = tk.NW, width = width_btn, window = modify_btn)
                 
                def modify_metadata():
                    # Normal entry
                    for i in range(0, len(fields)-1):
                        entries[i].config(state=tk.NORMAL)

                    # Option menu for the dose
                    group_menu['state'] = 'readonly'

                    def group_changed(event):
                        """ handle the group changed event """
                        entries[fields.index("Group")].delete(0, tk.END)
                        entries[fields.index("Group")].insert(0, str(selected_group.get()))                    

                    group_menu.bind("<<ComboboxSelected>>", group_changed)
                    
                    # Option menu for the timepoint
                    timepoint_menu1['state'] = 'readonly'
                    time_entry['state'] = 'normal'
                    timepoint_menu['state'] = 'readonly'

                    def timepoint_changed(event):
                        entries[fields.index("Timepoint")].config(state=tk.NORMAL)
                        """ handle the timepoint changed event """
                        timepoint_str = str(selected_timepoint.get()) + "-" + str(time_entry.get()) + "-" + str(selected_timepoint1.get())
                        
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
                         messagebox.showerror("XNAT-PIC", "Select a folder from the list box on the left")
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

                    if entries[fields.index("Dose")].get(): 
                        try:
                            float(entries[fields.index("Dose")].get())
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Insert a number in dose")
                            raise

                    if entries[fields.index("Timepoint")].get(): 
                        if not str(entries[fields.index("Timepoint")].get()).split('-')[0] in OPTIONS:
                           messagebox.showerror("XNAT-PIC", "Select pre/post in timepoint")
                           raise
                        if not str(entries[fields.index("Timepoint")].get()).split('-')[2] in OPTIONS1:
                           messagebox.showerror("XNAT-PIC", "Select seconds, minutes, hours, days, month, years in timepoint")
                           raise

                        input_num = str(entries[fields.index("Timepoint")].get()).split('-')[1]
                        try:
                            float(input_num)
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Insert a number in timepoint between pre/post and seconds, minutes, hours..")  
                            raise

                confirm_text = tk.StringVar() 
                confirm_btn = tk.Button(master.my_canvas, textvariable=confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: confirm_metadata(), cursor=CURSOR_HAND)
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
                        selected_timepoint.set('')
                        selected_timepoint1.set('')
                        time_entry.delete(0, tk.END)
                        time_entry.config(state=tk.DISABLED)
                        group_menu['state'] = tk.DISABLED
                        timepoint_menu['state'] = tk.DISABLED
                        timepoint_menu1['state'] = tk.DISABLED
                        
                        # Saves the changes made by the user in the txt file
                        with open(path_list[selected_index], 'w+') as meta_file:
                                        meta_file.write(tabulate([['Project', str(results[selected_index*max_lim+0])], ['Subject', str(results[selected_index*max_lim+1])], ['Acquisition_date', str(results[selected_index*max_lim+2])], 
                                        ['Group', str(results[selected_index*max_lim+3])], ['Dose', str(results[selected_index*max_lim+4])], ['Timepoint', str(results[selected_index*max_lim+5])]], headers=['Variable', 'Value']))

                #################### Confirm multiple metadata ####################
                multiple_confirm_text = tk.StringVar() 
                multiple_confirm_btn = tk.Button(master.my_canvas, textvariable=multiple_confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: confirm_multiple_metadata(), cursor=CURSOR_HAND)
                multiple_confirm_text.set("Multiple Confirm")
                x_multiple_conf_btn = int(my_width*78/100)
                master.my_canvas.create_window(x_multiple_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = multiple_confirm_btn)
                
                def confirm_multiple_metadata():

                    messagebox.showinfo("Metadata","Select the folders from the box on the left for which to copy the info entered! Press ENTER to confirm or ESC to cancel!")
                    
                    confirm_metadata()

                    my_listbox.selection_set(selected_index)    
                    my_listbox['selectmode'] = MULTIPLE
                    
                    # The user presses 'enter' to confirm 
                    def items_selected2(event):
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
                       my_listbox.selection_clear(0, 'end')
                       my_listbox['selectmode'] = SINGLE
                       

                    my_listbox.bind("<Return>", items_selected2)
                    
                    # The user presses 'esc' to cancel
                    def items_cancel(event):
                         # Clear the focus and the select mode of the listbox is single
                        messagebox.showinfo("Metadata","The information was not saved for the selected folders!")
                        my_listbox.selection_clear(0, 'end')
                        my_listbox['selectmode'] = SINGLE
                    my_listbox.bind("<Escape>", items_cancel)

                #################### Save the metadata ####################
                save_text = tk.StringVar() 
                save_btn = tk.Button(master.my_canvas, textvariable=save_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: save_metadata(), cursor=CURSOR_HAND)
                save_text.set("Save")
                y_btn1 = int(my_height*77/100)
                master.my_canvas.create_window(x_multiple_conf_btn, y_btn1, anchor = tk.NW, width = width_btn, window = save_btn)
                
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
                exit_text = tk.StringVar() 
                exit_btn = tk.Button(master.my_canvas, textvariable=exit_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: exit_metadata(), cursor=CURSOR_HAND)
                exit_text.set("Exit")
                x_exit_btn = int(my_width*10/100)
                master.my_canvas.create_window(x_exit_btn, y_btn1, anchor = tk.NW,width = width_btn, window = exit_btn)

                def exit_metadata():
                    result = messagebox.askquestion("Exit", "You have NOT SAVED your changes. Do you want to go out anyway?", icon='warning')
                    if result == 'yes':
                        clear_metadata_frame()

                def clear_metadata_frame():
                    label.destroy()
                    my_listbox.destroy()
                    my_yscrollbar.destroy()
                    my_xscrollbar.destroy()

                    for i in range(0, len(fields)): 
                        labels[i].destroy()   
                        entries[i].destroy()
                    
                    timepoint_menu.destroy()
                    timepoint_menu1.destroy()
                    time_entry.destroy()
                    group_menu.destroy()

                    modify_btn.destroy()
                    confirm_btn.destroy()
                    save_btn.destroy()
                    exit_btn.destroy()
                    multiple_confirm_btn.destroy()
                    xnat_pic_gui.choose_you_action(master)
    # Upload files         
    class xnat_dcm_uploader():

        def __init__(self, master):    
            
            self.home = os.path.expanduser("~")
            self.stack_frames = []
            self.stack_frames.append(master.get_page())
            
            # Disable all buttons
            master.convert_btn['state'] = tk.DISABLED
            master.info_btn['state'] = tk.DISABLED
            master.upload_btn['state'] = tk.DISABLED
            master.process_btn['state'] = tk.DISABLED

            # Log into XNAT
            popup1 = tk.Toplevel()
            popup1.title("XNAT-PIC  ~  Login")
            master.x = my_width * 3 / 8
            master.y = my_height / 3
            popup_font = ("Calibri", 10, "bold")
            popup1.geometry("%dx%d+%d+%d" % (my_width*0.2, my_height*0.1, master.x, master.y))           
            
            def normal_btn(event):
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL
                return
                
            popup1.bind("<Destroy> ", normal_btn)
            # XNAT ADDRESS      
            popup1.label_address = tk.Label(popup1, text="  XNAT web address  ", font=popup_font)   
            popup1.label_address.grid(row=0, column=0, padx=1, ipadx=1)
            popup1.entry_address = tk.Entry(popup1)
            popup1.entry_address.var = tk.StringVar()
            popup1.entry_address["textvariable"] = popup1.entry_address.var
            popup1.entry_address.grid(row=0, column=1, padx=1, ipadx=1)
           
            # XNAT USER 
            popup1.label_user = tk.Label(popup1, text="Username", font=popup_font)
            popup1.label_user.grid(row=1, column=0, padx=1, ipadx=1)
            popup1.entry_user = tk.Entry(popup1)
            popup1.entry_user.var = tk.StringVar()
            popup1.entry_user["textvariable"] = popup1.entry_user.var
            popup1.entry_user.grid(row=1, column=1, padx=1, ipadx=1)

            # XNAT PASSWORD 
            popup1.label_psw = tk.Label(popup1, text="Password", font=popup_font)
            popup1.label_psw.grid(row=2, column=0, padx=1, ipadx=1)           
            
            # Show/Hide the password
            def toggle_password():
                if popup1.entry_psw.cget('show') == '':
                    popup1.entry_psw.config(show='*')
                    popup1.toggle_btn.config(text='Show Password')
                else:
                    popup1.entry_psw.config(show='')
                    popup1.toggle_btn.config(text='Hide Password')
            

            popup1.entry_psw = tk.Entry(popup1, show="*")
            popup1.entry_psw.var = tk.StringVar()
            popup1.entry_psw["textvariable"] = popup1.entry_psw.var
            popup1.entry_psw.grid(row=2, column=1, padx=1, ipadx=1)
            popup1.toggle_btn = tk.Button(popup1, text='Show Password',  command=toggle_password)
            popup1.toggle_btn.grid(row=2, column=2)


            # XNAT HTTP/HTTPS 
            popup1.http = tk.StringVar()

            # SAVE CREDENTIALS CHECKBOX
            popup1.remember = tk.IntVar()

            # SHOW THE PASSWORD
            popup1.show_psw = tk.BooleanVar()
            
            # BUTTONS
            popup1.button_connect = tk.Button(
                popup1,
                text="Login", font=popup_font, 
                width=15,
                command=partial(self.check_connection,master, popup1)
            )
            popup1.button_connect.grid(row=5, column=1)
            popup1.button_http = tk.Radiobutton(
                popup1,
                text=" http:// ",
                variable=popup1.http,
                value="http://",
            )
            popup1.button_http.grid(row=4, column=0)
            popup1.button_http.select()
            popup1.button_https = tk.Radiobutton(
                popup1,
                text=" https:// ",
                variable=popup1.http,
                value="https://",
            )
            popup1.button_https.grid(row=4, column=1)

            popup1.btn_remember = tk.Checkbutton(
                popup1, text="Remember me", variable=popup1.remember
            )
            popup1.btn_remember.grid(row=4, column=2, padx=1, ipadx=1)
            self.load_saved_credentials(popup1)
            
           
        def load_saved_credentials(self, popup1):
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
                popup1.entry_address.var.set(line[8:-1])
                line = login_file.readline()
                popup1.entry_user.var.set(line[9:-1])
                line = login_file.readline()
                popup1.entry_psw.var.set(line[9:-1])
                login_file.close()
                os.remove(decrypted_file)
                popup1.btn_remember.select()
            except Exception as error:
                pass

        def check_connection(self, master, popup1):
            # LOGIN
            popup1.entry_address_complete = popup1.http.get() + popup1.entry_address.var.get()
            self.entry_address_complete = popup1.entry_address_complete
            self.entry_user = popup1.entry_user.var.get()
            self.entry_psw = popup1.entry_psw.var.get()
            home = os.path.expanduser("~")
            try:
                session = xnat.connect(
                    popup1.entry_address_complete,
                    popup1.entry_user.var.get(),
                    popup1.entry_psw.var.get(),
                )
                if popup1.remember.get() == True:
                    self.save_credentials(popup1)
                else:
                    try:
                        os.remove(
                            os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                        )
                    except FileNotFoundError:
                        pass
                popup1.destroy()
                self.xnat_common_uploader(session, master)
            except xnat.exceptions.XNATLoginFailedError as err:
                messagebox.showerror("Error!", err)
            except Exception as error:
                messagebox.showerror("Error!", error)

        def save_credentials(self, popup1):

            home = os.path.expanduser("~")

            if os.path.exists(os.path.join(home, "Documents")):
                file = os.path.join(home, "Documents", ".XNAT_login_file.txt")
                login_file = open(file, "w+")
                login_file.write(
                    "Address:"
                    + popup1.entry_address.var.get()
                    + "\n"
                    + "Username:"
                    + popup1.entry_user.var.get()
                    + "\n"
                    + "Password:"
                    + popup1.entry_psw.var.get()
                    + "\n"
                    + "HTTP:"
                    + popup1.http.get()
                )
                login_file.close()
                # encrypt
                encrypted_file = os.path.join(home, "Documents", ".XNAT_login_file.txt.aes")
                pyAesCrypt.encryptFile(file, encrypted_file, password, bufferSize)
                # decrypt
                os.remove(file)   
        

        def xnat_common_uploader(self, session, master):
            # Frame
            self.stack_frames[-1].update()
            frame_two = self.stack_frames[-1]
            
            # Update canvas
            # Delete button of the previous frame
            master.convert_btn.destroy()
            master.info_btn.destroy()
            master.upload_btn.destroy()
            master.process_btn.destroy()
            master.info_convert_btn.destroy()
            master.info_info_btn.destroy()
            master.info_upload_btn.destroy()
            master.info_process_btn.destroy()            
            
            # Upload DICOM files
            x_lbl = int(my_width*20/100)
            y_lbl = int(my_height*35/100)
            x_btn = int(my_width*30/100)
            y_btn = int(my_height*39/100)
            width_lbl = int(my_width*30/100)
            width_btn = int(my_width*10/100)

            label1 = tk.Label(master.my_canvas, text='Upload new DICOM images to XNAT project', font = LARGE_FONT, bg=BG_LBL_COLOR, fg=TEXT_LBL_COLOR)
            master.my_canvas.create_window(x_lbl, y_lbl, anchor=tk.NW, width=width_lbl, window=label1)
            dicom_text = tk.StringVar()
            dicom_btn = tk.Button(master.my_canvas, textvariable=dicom_text, font = LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.xnat_dcm_uploader_select_project, session, master), cursor=CURSOR_HAND)
            dicom_text.set("DICOM2XNAT")
            master.my_canvas.create_window(x_btn, y_btn, anchor = tk.NW, width=width_btn, window = dicom_btn)
            
            # Upload files
            y_lbl1 = int(my_height*50/100)
            y_btn1 = int(my_height*54/100)
            label2 = tk.Label(master.my_canvas, text='Upload other files to XNAT project', font = LARGE_FONT, bg=BG_LBL_COLOR, fg=TEXT_LBL_COLOR)
            master.my_canvas.create_window(x_lbl, y_lbl1, anchor=tk.NW, width=width_lbl, window=label2)
            file_text = tk.StringVar()
            file_btn = tk.Button(master.my_canvas, textvariable=file_text, font = LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.xnat_files_uploader, session, master), cursor=CURSOR_HAND)
            file_text.set("FILES2XNAT")
            master.my_canvas.create_window(x_btn, y_btn1, anchor = tk.NW, width=width_btn, window = file_btn)
            
            # Button to go to the previous page
            back_text = tk.StringVar()   
            back_btn = tk.Button(master.my_canvas, textvariable=back_text, font = LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=lambda: (back_btn.destroy(), dicom_btn.destroy(), file_btn.destroy(), label1.destroy(), label2.destroy(), session.disconnect(), xnat_pic_gui.choose_you_action(master)), cursor=CURSOR_HAND)
            back_text.set("Logout")
            master.my_canvas.create_window(int(my_width*5/100), int(my_height*80/100), anchor = tk.NW, width=width_btn, window = back_btn)
        
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

        def check_project_name(self, session, master, popup):
            if popup.entry_prjname.var.get().lower in self.OPTIONS:
                messagebox.showerror(
                    "Error!",
                    "Project ID %s already exists! Please, enter a different project ID"
                    % self.entry_prjname.var.get(),
                )
            else:
                try:
                    popup.destroy()
                    self.xnat_dcm_directory_selector(session, master)
                except exception as e:
                    messagebox.showerror("Error!", str(e))
        
        def xnat_dcm_uploader_select_project(self, session, master):

            # Enable / Disable new / existing project
            def isChecked():
                 if self.newprj_var.get() == 1:
                    popup2.label_prjname['state'] = tk.NORMAL
                    popup2.label_choose_prj['state'] = tk.DISABLED
                    popup2.entry_prjname['state'] = tk.NORMAL
                    popup2.project_list['state'] = tk.DISABLED
                 elif self.newprj_var.get() == 0:
                    popup2.label_prjname['state'] = tk.DISABLED
                    popup2.label_choose_prj['state'] = tk.NORMAL
                    popup2.entry_prjname['state'] = tk.DISABLED
                    popup2.project_list['state'] = tk.NORMAL

            # POPUP 
            popup2 = tk.Toplevel()
            popup2.title("XNAT-PIC")
            master.root.width = 350
            master.root.height = 100
            master.x = (int(master.root.screenwidth) - master.root.width) / 2
            master.y = (int(master.root.screenheight)- master.root.height) / 3
            popup2.geometry("%dx%d+%d+%d" % (master.root.width, master.root.height, master.x, master.y))

            # LABEL
            popup2.label_prjname = tk.Label(popup2, text="  New project    ", anchor="w", state="disabled")
            popup2.label_choose_prj = tk.Label(popup2, text="  Select project in XNAT:  ", anchor="w")
            popup2.label_choose_prj.grid(row=2, column=0)
            popup2.label_prjname.grid(row=0, column=0)

            # ENTRY INSERT NEW PROJECT
            popup2.value = tk.StringVar()
            popup2.entry_prjname = tk.Entry(popup2, state="disabled")
            self.entry_prjname = popup2.entry_prjname
            popup2.value.set("  Project ID  ")
            popup2.entry_prjname.grid(row=0, column=2)
            popup2.entry_prjname.var = tk.StringVar()
            popup2.entry_prjname.var.set("Project ID")
            popup2.entry_prjname["textvariable"] = popup2.entry_prjname.var
            self.entry_prjname.var = popup2.entry_prjname.var
           
            # PROJECTS LIST
            self.OPTIONS = session.projects
            self.prj = tk.StringVar()
            popup2.project_list = tk.OptionMenu(popup2, self.prj, *self.OPTIONS)
            popup2.project_list.grid(row=2, column=2)
            self.newprj_var = tk.IntVar()
            popup2.btn_newprj = tk.Checkbutton(popup2, variable=self.newprj_var, onvalue=1, offvalue=0, command=isChecked)
            popup2.btn_newprj.grid(row=0, column=1)

            popup2.back_btn = tk.Button(
                popup2, text="Back", command=lambda: (popup2.destroy())
            )
            popup2.back_btn.grid(row=4, column=0)
            popup2.next_btn = tk.Button(
                popup2, text="Next", command=partial(self.check_project_name, session, master, popup2), state="disabled"
            )
            popup2.next_btn.grid(row=4, column=2)

            self.button_next = popup2.next_btn

            self.newprj_var.trace_add("write", self.enable_next)
            popup2.entry_prjname.var.trace_add("write", self.enable_next)
            self.prj.trace_add("write", self.enable_next)


        def navigate_back(self, master):
            self.stack_frames[-1].grid_remove()
            self.stack_frames.pop()
            self.stack_frames[-1].grid()


        def xnat_files_uploader(self, session, master):

            session.disconnect()

        def xnat_dcm_directory_selector(self, session, master):

            if self.newprj_var.get() == 1:
                self.project = self.entry_prjname.var.get()
            else:
                self.project = self.prj.get()

            self.folder_to_upload = filedialog.askdirectory(
                parent=master.root,
                initialdir=self.home,
                title="Please select project directory (DICOM only)",
            )
            if self.folder_to_upload==():
                os._exit(1)
            
            self.dicom2xnat(session, master)

        def dicom2xnat(self, session, master):

            # xnat_uploader(
            #     self.folder_to_upload,
            #     self.project,
            #     # num_vars,
            #     # self.entry_address_complete,
            #     # self.entry_user,
            #     # self.entry_psw
            #     session
            # )

            xnat_uploader_dir(
                self.folder_to_upload,
                self.project,
                session
            )

            os._exit(0)

if __name__ == "__main__":
    root = tk.Tk()
    app = xnat_pic_gui(root)
    root.mainloop()