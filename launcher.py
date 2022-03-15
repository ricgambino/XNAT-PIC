from ast import Str
from dataclasses import field
from doctest import master
from logging import exception, raiseExceptions
import tkinter as tk
from tkinter import CENTER, MULTIPLE, NW, SINGLE, filedialog,messagebox
from tkinter import font
from tkinter.tix import COLUMN, Balloon
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
import sys
import threading
from ProgressBar import App
from progressbar import progressbar
from bruker2dicom_converter import bruker2dicom
import xnat
from xnat_upload import xnat_uploader, xnat_uploader_dir
import pyAesCrypt
from tabulate import tabulate
import datetime


PATH_IMAGE = "images\\"
PERCENATGE_SCREEN = 0.9  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
BACKGROUND_COLOR = "#31C498"
THEME_COLOR = "black"
TEXT_BTN_COLOR = "black"
BG_BTN_COLOR = "#80FFE6"
BIG_FONT = ("Calibri", 22, "bold")
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"

# Password to access to saved credentials now is stored in a local folder
with open(os.path.join(os.path.expanduser("~"), "Documents", "XNAT_login_credentials.json")) as auth_file:
    data = json.load(auth_file)
    password = data['password']
    bufferSize = int(data['bufferSize_1']) * int(data['bufferSize_2'])

       
class xnat_pic_gui(tk.Frame):

    def __init__(self, master):

        self.root = master
        root.attributes('-fullscreen', True)
        root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
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
        self.root.geometry(str(w) + "x" + str(h))
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
        self.enter_btn = tk.Button(self.my_canvas, textvariable=enter_text, font=BIG_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=lambda: (self.enter_btn.destroy(), xnat_pic_gui.choose_you_action(self)), cursor=CURSOR_HAND)
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
         self.convert_btn = tk.Button(self.my_canvas, textvariable=convert_text, font=BIG_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.bruker2dicom_conversion, self), cursor=CURSOR_HAND)
         convert_text.set("Bruker2DICOM")
         self.my_canvas.create_window(x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.convert_btn)
         
         # Fill in the info
         info_text = tk.StringVar()
         self.info_btn = tk.Button(self.my_canvas, textvariable=info_text, font=BIG_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.metadata, self), cursor=CURSOR_HAND)
         info_text.set("Fill in the info")
         self.my_canvas.create_window(2*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.info_btn)

         # Upload files
         upload_text = tk.StringVar()
         self.upload_btn = tk.Button(self.my_canvas, textvariable=upload_text, font=BIG_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.xnat_dcm_uploader, self), cursor=CURSOR_HAND)
         upload_text.set("Uploader")
         self.my_canvas.create_window(3*x_btn, y_btn, width = width_btn, anchor = tk.CENTER, window = self.upload_btn)        
        
         # Processing your files
         process_text = tk.StringVar()
         self.process_btn = tk.Button(self.my_canvas, textvariable=process_text, font=BIG_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, cursor=CURSOR_HAND)
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

            def isChecked():
                master.results_flag = self.results_flag.get()

            self.conv_popup = tk.Toplevel()
            self.conv_popup.geometry("%dx%d+%d+%d" % (500, 120, 700, 500))
            self.conv_popup.title('DICOM Converter')
            self.btn_prj = tk.Button(self.conv_popup, text='Convert Project', font=("Calibri", 18, "bold"), 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (self.prj_conversion(master), self.conv_popup.destroy()))
            self.btn_prj.grid(row=2, column=0, padx=10, pady=5)
            self.btn_sbj = tk.Button(self.conv_popup, text='Convert Subject', font=("Calibri", 18, "bold"), 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (self.sbj_conversion(master), self.conv_popup.destroy()))
            self.btn_sbj.grid(row=3, column=0, padx=10, pady=5)
            self.results_flag = tk.IntVar()
            master.results_flag = self.results_flag.get()
            self.btn_results = tk.Checkbutton(self.conv_popup, text='Upload results', variable=self.results_flag,
                                onvalue=1, offvalue=0, command=isChecked)
            self.btn_results.grid(row=2, column=1, padx=100, pady=10)

        def prj_conversion(self, master):

            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                    sys.exit(0)
            master.root.deiconify()
            master.root.update()
            self.dst = self.folder_to_convert + '_dcm'

            try:
                # Convert from bruker to DICOM and disable the buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                master.process_btn['state'] = tk.DISABLED

                list_dirs = os.listdir(self.folder_to_convert)
                progressbar = App(txt_title='DICOM Converter')
                progressbar.start_progressbar()
                for j, dir in enumerate(list_dirs, 1):
                    progressbar.update_progressbar(j, len(list_dirs))
                    current_folder = os.path.join(self.folder_to_convert, dir).replace('\\', '/')
                    if os.path.isdir(current_folder):
                        current_dst = os.path.join(self.dst, dir).replace('\\', '/')
                        # If the destination folder already exists throw exception, otherwise create the new folder
                        if os.path.isdir(current_dst):
                            raise Exception("Destination folder %s already exists" % current_dst)
                        else:
                            os.makedirs(current_dst)

                        conv = [(i,l) for i, l in bruker2dicom(current_folder, current_dst, master)]

                progressbar.stop_progress_bar()
                my_exeption = False           

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL

            if my_exeption is False:
                messagebox.showinfo("Bruker2DICOM","Done! Now you can upload your files to XNAT.")
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL
                # sys.exit(0)

        def sbj_conversion(self, master):

            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                    sys.exit(0)
            master.root.deiconify()
            master.root.update()
            head, tail = os.path.split(self.folder_to_convert)
            head = head + '_dcm'
            project_foldername = tail.split('.',1)[0] + "_dcm"
            self.dst = os.path.join(head, project_foldername).replace('\\', '/')

            # If the destination folder already exists throw exception, otherwise create the new folder
            if os.path.isdir(self.dst):
                raise Exception("Destination folder %s already exists" % self.dst)
            else:
                os.makedirs(self.dst)

            try:
                # Convert from bruker to DICOM and disable the buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                master.process_btn['state'] = tk.DISABLED

                progressbar = App(txt_title='DICOM Converter')
                progressbar.start_progressbar()
                for i, length in bruker2dicom(self.folder_to_convert, self.dst, master):
                    progressbar.update_progressbar(i, length)
                progressbar.stop_progress_bar()
                my_exeption = False           

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Bruker2Dicom", e)
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL

            if my_exeption is False:
                messagebox.showinfo("Bruker2DICOM","Done! Now you can upload your files to XNAT.")
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL
                # sys.exit(0)

                      
    # Fill in information
    class metadata():
        def __init__(self, master):
                messagebox.showinfo("Metadata","Select project directory!")
                #master.convert_btn['state'] = tk.DISABLED
                #master.info_btn['state'] = tk.DISABLED
                #master.upload_btn['state'] = tk.DISABLED
                #master.process_btn['state'] = tk.DISABLED
               
                # Choose your directory
                self.information_folder = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory!")
                project_name = (self.information_folder.rsplit("/",1)[1])
                
                all_sub = []
                # Create the empty layout files in all the subjects
                # if the file for the entire project does not exist, create it, otherwise open it
                if os.path.exists(str(self.information_folder) + "\\" + str(project_name) + "_" + "Custom_Variables.txt") is False:

                    for item in os.listdir(self.information_folder):
                        path = str(self.information_folder) + "\\" + str(item)
                        #name = str(item) + "_" + "Custom_Variables.txt"
                        
                        # Check if the content of the project is a folder and therefore a patient or a file not to be considered (no comment)
                        if os.path.isdir(path):
                        #with open(path + "\\" + name, 'w+') as meta_file:
                                    # Create the empty layout files in all the subjects
                                    #meta_file.write(tabulate([['Project', str(project_name)], ['Subject', str(item)], ['Acquisition_date', ""], 
                                    #['Group', ""], ['Dose', ""], ['Timepoint', ""]], headers=['Variable', 'Value']))

                                    all_sub = all_sub + ["--"] + [['Project', str(project_name)], ['Subject', str(item)], ['Acquisition_date', ""], 
                                    ['Group', ""], ['Dose', ""], ['Timepoint', ""]]
                                        
                        with open(str(self.information_folder) + "\\" + project_name + '_' + 'Custom_Variables.txt', 'w+') as meta_file:
                            meta_file.write(tabulate(all_sub, headers=['Variable', 'Value']))
                        
                # Get all the values ​​of the variables of all subjects
                fields = ["Project", "Subject", "Acquisition_date", "Group", "Dose", "Timepoint"]
                data = []   
                with open(str(self.information_folder) + "\\" + project_name + '_' + 'Custom_Variables.txt', 'r') as meta_file:
                            data = (meta_file.read().split('\n'))
                            results = [i for i in data if any(i for j in fields if str(j) in i)]
                            for word in fields:
                                results = [x.replace(word, '', 1).strip() for x in results]
                            
                #################### Update the frame ####################
                master.convert_btn.destroy()
                master.info_btn.destroy()
                master.upload_btn.destroy()
                master.process_btn.destroy()
                master.info_convert_btn.destroy()
                master.info_info_btn.destroy()
                master.info_upload_btn.destroy()
                master.info_process_btn.destroy()
                frame = master.get_page()
                # Subject list 
                label = tk.Label(frame, text='List of folders contained in the project: ' + project_name, bg="white", fg="black")
                label.config(font=("Calibri", 12, "bold"))
                master.my_canvas.create_window(150, 270, anchor=tk.NW, window=label)

                my_listbox = tk.Listbox(frame, selectmode=SINGLE, bg="#80FFE6", fg="black", width=45, height=27)
                my_listbox.config(font=("Calibri", 12, "bold"))
                master.my_canvas.create_window(150, 300, anchor = "nw", window = my_listbox)
                # List of subject in the project in the listbox
                results_prj = list(map(lambda i: results[i], range(1, len(results), len(fields))))
                my_listbox.insert(tk.END, *results_prj)
                # Attach listbox to scrollbar
                my_yscrollbar = tk.Scrollbar(frame, orient="vertical")
                my_listbox.config(yscrollcommand = my_yscrollbar.set)
                my_yscrollbar.config(command = my_listbox.yview)
                master.my_canvas.create_window(120, 790, anchor = "nw", window = my_yscrollbar)

                my_xscrollbar = tk.Scrollbar(frame, orient="horizontal")
                my_listbox.config(xscrollcommand = my_xscrollbar.set)
                my_xscrollbar.config(command = my_listbox.xview)
                
                master.my_canvas.create_window(150, 860, anchor = "nw", window = my_xscrollbar)
                
                #################### Subject form ####################
                # Project label
                x_label = 650
                y_label = 300
                delta_label = 80

                prj_label = tk.Label(frame, text='Project: ', bg="#80FFE6", fg="black", width=10, height=1)
                prj_label.config(font=("Calibri", 16, "bold"))
                master.my_canvas.create_window(x_label, y_label, anchor = "nw", window = prj_label)
                
                sub_label = tk.Label(frame, text='Subject: ', bg="#80FFE6", fg="black", width=10, height=1)
                sub_label.config(font=("Calibri", 16, "bold"))
                master.my_canvas.create_window(x_label, y_label+delta_label, anchor = "nw", window = sub_label)

                date_label = tk.Label(frame, text='Acq. date: ', bg="#80FFE6", fg="black", width=10, height=1)
                date_label.config(font=("Calibri", 16, "bold"))
                master.my_canvas.create_window(x_label, y_label+2*delta_label, anchor = "nw", window = date_label)

                group_label = tk.Label(frame, text='Group: ', bg="#80FFE6", fg="black", width=10, height=1)
                group_label.config(font=("Calibri", 16, "bold"))
                master.my_canvas.create_window(x_label, y_label+3*delta_label, anchor = "nw", window = group_label)

                dose_label = tk.Label(frame, text='Dose: ', bg="#80FFE6", fg="black", width=10, height=1)
                dose_label.config(font=("Calibri", 16, "bold"))
                master.my_canvas.create_window(x_label, y_label+4*delta_label, anchor = "nw", window = dose_label)

                timepoint_label = tk.Label(frame, text='Timepoint: ', bg="#80FFE6", fg="black", width=10, height=1)
                timepoint_label.config(font=("Calibri", 16, "bold"))
                master.my_canvas.create_window(x_label, y_label+5*delta_label, anchor = "nw", window = timepoint_label)

                # Project entry
                x_label = 800
                y_label = 300
                delta_label = 80
                large_font = ("Calibri", 16, "bold")
                small_font = ("Calibri", 12)

                prj_entry = tk.Entry(frame, state='disabled', font = large_font, width=35)
                master.my_canvas.create_window(x_label, y_label, anchor = "nw", window = prj_entry)
                
                sub_entry = tk.Entry(frame, state='disabled', font = large_font, width=35)
                master.my_canvas.create_window(x_label, y_label+delta_label, anchor = "nw", window = sub_entry)

                date_entry = tk.Entry(frame, state='disabled', font = large_font, width=35)
                master.my_canvas.create_window(x_label, y_label+2*delta_label, anchor = "nw", window = date_entry)

                group_entry = tk.Entry(frame, state='disabled', font = large_font, width=35)
                master.my_canvas.create_window(x_label, y_label+3*delta_label, anchor = "nw", window = group_entry)

                dose_entry = tk.Entry(frame, state='disabled', font = large_font, width=35)
                master.my_canvas.create_window(x_label, y_label+4*delta_label, anchor = "nw", window = dose_entry)

                timepoint_entry = tk.Entry(frame, state='disabled', font = large_font, width=25)
                master.my_canvas.create_window(x_label, y_label+5*delta_label, anchor = "nw", window = timepoint_entry)

                # Menu
                # Dose
                OPTIONS = ["untreated", "treated"]
                selected_group = tk.StringVar()
                group_menu = ttk.Combobox(frame, textvariable=selected_group, font = small_font)
                group_menu['values'] = OPTIONS
                group_menu['state'] = 'disabled'
                master.my_canvas.create_window(1200, y_label+3*delta_label, anchor = "nw", window = group_menu)
                
                # Timepoint
                time_entry = tk.Entry(frame, state='disabled', font = small_font, width=10)
                master.my_canvas.create_window(1110, y_label+5*delta_label, anchor = "nw", window = time_entry)

                OPTIONS = ["seconds", "minutes", "hours", "days", "month", "years"]
                selected_timepoint = tk.StringVar()
                timepoint_menu = ttk.Combobox(frame, textvariable=selected_timepoint, font = small_font, width=3)
                timepoint_menu['values'] = OPTIONS
                timepoint_menu['state'] = 'disabled'
                master.my_canvas.create_window(1200, y_label+5*delta_label, anchor = "nw", window = timepoint_menu)
               
                
                # Load the info about the selected subject
                def items_selected(event):
                    # Normal entry
                    selected_timepoint.set('')
                    selected_group.set('')
                    time_entry.delete(0, tk.END)
                    prj_entry.config(state=tk.NORMAL)
                    sub_entry.config(state=tk.NORMAL)
                    date_entry.config(state=tk.NORMAL)
                    group_entry.config(state=tk.NORMAL)
                    dose_entry.config(state=tk.NORMAL)
                    timepoint_entry.config(state=tk.NORMAL)

                    """ handle item selected event
                    """
                    # get selected indices
                    global selected_index 
                    selected_index = my_listbox.curselection()[0]
                    prj_entry.delete(0, tk.END)
                    prj_entry.insert(0, project_name)
                    prj_entry.config(state=tk.DISABLED)


                    sub_entry.delete(0, tk.END)
                    sub_entry.insert(0, str(results[selected_index*len(fields)+1]))
                    sub_entry.config(state=tk.DISABLED)

                    date_entry.delete(0, tk.END)
                    date_entry.insert(0, str(results[selected_index*len(fields)+2]))
                    date_entry.config(state=tk.DISABLED)

                    group_entry.delete(0, tk.END)
                    group_entry.insert(0, str(results[selected_index*len(fields)+3]))
                    group_entry.config(state=tk.DISABLED)

                    dose_entry.delete(0, tk.END)
                    dose_entry.insert(0, str(results[selected_index*len(fields)+4]))
                    dose_entry.config(state=tk.DISABLED)
                    
                    timepoint_entry.delete(0, tk.END)
                    timepoint_entry.insert(0, str(results[selected_index*len(fields)+5]))
                    timepoint_entry.config(state=tk.DISABLED)
                    

                my_listbox.bind("<Double-Button-1>", items_selected)
                
                #################### Modify the metadata ####################
                modify_text = tk.StringVar() 
                modify_btn = tk.Button(frame, textvariable=modify_text, font=("Calibri", 18, "bold"), bg="black", fg="white", height=1, width=15, borderwidth=0, command = lambda: modify_metadata(), cursor="hand2")
                modify_text.set("Modify")
                master.my_canvas.create_window(650, 790, anchor = "nw", window = modify_btn)
                
                # Normal entry 
                def modify_metadata():
                    prj_entry.config(state=tk.NORMAL)
                    sub_entry.config(state=tk.NORMAL)
                    group_entry.config(state=tk.NORMAL)
                    date_entry.config(state=tk.NORMAL)
                    dose_entry.config(state=tk.NORMAL)
                
                    # Option menu for the dose
                    group_menu['state'] = 'readonly'

                    def group_changed(event):
                        """ handle the group changed event """
                        group_entry.config(state=tk.NORMAL)
                        group_entry.delete(0, tk.END)
                        group_entry.insert(0, str(selected_group.get()))                    

                    group_menu.bind("<<ComboboxSelected>>", group_changed)
                    
                    # Option menu for the timepoint
                    time_entry['state'] = 'normal'
                    timepoint_menu['state'] = 'readonly'

                    def timepoint_changed(event):
                        """ handle the timepoint changed event """
                        timepoint_entry.config(state=tk.NORMAL)
                        timepoint_str = str(time_entry.get()) + "-" + str(selected_timepoint.get())
                        try:
                          float(time_entry.get())
                        except Exception as e: 
                          messagebox.showerror("XNAT-PIC", "Insert a number")

                        timepoint_entry.delete(0, tk.END)
                        timepoint_entry.insert(0, timepoint_str)
                        timepoint_entry.config(state=tk.DISABLED)

                    timepoint_menu.bind("<<ComboboxSelected>>", timepoint_changed)
                    time_entry.bind("<Return>", timepoint_changed)

                #################### Confirm the metadata ####################
                confirm_text = tk.StringVar() 
                confirm_btn = tk.Button(frame, textvariable=confirm_text, font=("Calibri", 18, "bold"), bg="black", fg="white", height=1, width=15, borderwidth=0, command = lambda: confirm_metadata(), cursor="hand2")
                confirm_text.set("Confirm")
                master.my_canvas.create_window(920, 790, anchor = "nw", window = confirm_btn)

                def confirm_metadata():
                    try:
                        selected_index
                        pass
                    except Exception as e:
                         messagebox.showerror("XNAT-PIC", "Select a folder from the list box on the left")

                    if not prj_entry.get():
                       messagebox.showerror("XNAT-PIC", "Insert the name of the project")
                    
                    if not sub_entry.get():
                       messagebox.showerror("XNAT-PIC", "Insert the name of the subject")

                    if dose_entry.get(): 
                        try:
                            float(dose_entry.get())
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Insert a number in dose")

                    if date_entry.get():
                        try:
                           datetime.datetime.strptime(date_entry.get(), '%Y-%m-%d')
                        except Exception as e:
                           messagebox.showerror("XNAT-PIC", "Incorrect data format in acquisition date, should be YYYY-MM-DD")

                    if timepoint_entry.get(): 
                        input_num = str(timepoint_entry.get()).split('-')[0]
                        try:
                            float(input_num)
                        except Exception as e: 
                            messagebox.showerror("XNAT-PIC", "Insert a number in timepoint value before seconds, minutes, hours..")    

                    results[selected_index*len(fields)+0] = prj_entry.get()
                    results[selected_index*len(fields)+1] = sub_entry.get()
                    results[selected_index*len(fields)+2] = date_entry.get()
                    results[selected_index*len(fields)+3] = group_entry.get()
                    results[selected_index*len(fields)+4] = dose_entry.get()
                    results[selected_index*len(fields)+5] = timepoint_entry.get()
                    
                    selected_timepoint.set('')
                    selected_group.set('')
                    time_entry.delete(0, tk.END)
                    prj_entry.config(state=tk.DISABLED)
                    sub_entry.config(state=tk.DISABLED)
                    date_entry.config(state=tk.DISABLED)
                    dose_entry.config(state=tk.DISABLED)
                    group_entry.config(state=tk.DISABLED)
                    time_entry.config(state=tk.DISABLED)
                    group_menu['state'] = tk.DISABLED
                    timepoint_menu['state'] = tk.DISABLED
                #################### Save the metadata ####################
                save_text = tk.StringVar() 
                save_btn = tk.Button(frame, textvariable=save_text, font=("Calibri", 18, "bold"), bg="black", fg="white", height=1, width=15, borderwidth=0, command = lambda: save_metadata(), cursor="hand2")
                save_text.set("Save")
                master.my_canvas.create_window(1190, 790, anchor = "nw", window = save_btn)
                
                def save_metadata():
                    err = False
                    try:
                        selected_index
                    except Exception as e:
                        err = True
                        messagebox.showerror("XNAT-PIC", "Select a folder from the list box on the left")
                        
                    if not err:
                        all_sub = []
                        
                        for i in range(0, len(results), len(fields)):
                            all_sub = all_sub + ["--"] + [['Project', str(results[i])], ['Subject', str(results[i+1])], ['Acquisition_date', str(results[i+2])], 
                                        ['Group', str(results[i+3])], ['Dose', str(results[i+4])], ['Timepoint', str(results[i+5])]]
                                        
                        with open(str(self.information_folder) + "\\" + project_name + '_' + 'Custom_Variables.txt', 'w+') as meta_file:
                           meta_file.write(tabulate(all_sub, headers=['Variable', 'Value']))
                        
                        i = 0
                        # Create file for all the folder in the project
                        for item in os.listdir(self.information_folder):
                          path = str(self.information_folder) + "\\" + str(item)
                          name = str(item) + "_" + "Custom_Variables.txt"
                        
                        # Check if the content of the project is a folder and therefore a patient or a file not to be considered (no comment)
                          if os.path.isdir(path):
                             with open(path + "\\" + name, 'w+') as meta_file:
                                    # Create the empty layout files in all the subjects
                                    meta_file.write(tabulate([['Project', str(results[i])], ['Subject', str(results[i+1])], ['Acquisition_date', str(results[i+2])], 
                                    ['Group', str(results[i+3])], ['Dose', str(results[i+4])], ['Timepoint', str(results[i+5])]], headers=['Variable', 'Value']))
                                    i += 6
                        # Destroy of the elements of the current frame and go to the previous frame
                        label.destroy()
                        my_listbox.destroy()
                        my_yscrollbar.destroy()
                        my_xscrollbar.destroy()

                        prj_label.destroy()
                        sub_label.destroy()
                        date_label.destroy()
                        group_label.destroy()
                        dose_label.destroy()
                        timepoint_label.destroy()
                        prj_entry.destroy()
                        sub_entry.destroy()
                        date_entry.destroy()
                        group_entry.destroy()
                        dose_entry.destroy()
                        timepoint_entry.destroy()
                        
                        timepoint_menu.destroy()
                        time_entry.destroy()
                        group_menu.destroy()

                        modify_btn.destroy()
                        confirm_btn.destroy()
                        save_btn.destroy()
                        exit_btn.destroy()
                        xnat_pic_gui.choose_you_action(master)
                
                #################### Exit the metadata ####################
                exit_text = tk.StringVar() 
                exit_btn = tk.Button(frame, textvariable=exit_text, font=("Calibri", 18, "bold"), bg="#80FFE6", fg="black", height=1, width=15, borderwidth=0, command = lambda: exit_metadata(), cursor="hand2")
                exit_text.set("Exit")
                master.my_canvas.create_window(1500, 850, anchor = "nw", window = exit_btn)

                def exit_metadata():
                    result = messagebox.askquestion("Exit", "You have NOT SAVED your changes. Do you want to go out anyway?", icon='warning')
                    if result == 'yes':
                        label.destroy()
                        my_listbox.destroy()
                        my_yscrollbar.destroy()
                        my_xscrollbar.destroy()

                        prj_label.destroy()
                        sub_label.destroy()
                        date_label.destroy()
                        group_label.destroy()
                        dose_label.destroy()
                        timepoint_label.destroy()
                        prj_entry.destroy()
                        sub_entry.destroy()
                        date_entry.destroy()
                        group_entry.destroy()
                        dose_entry.destroy()
                        timepoint_entry.destroy()
                        
                        timepoint_menu.destroy()
                        time_entry.destroy()
                        group_menu.destroy()

                        modify_btn.destroy()
                        confirm_btn.destroy()
                        save_btn.destroy()
                        exit_btn.destroy()
                        xnat_pic_gui.choose_you_action(master)

    # Upload files         
    class xnat_dcm_uploader():

        def __init__(self, master):    
            
            self.home = os.path.expanduser("~")
            self.stack_frames = []
            self.stack_frames.append(master.get_page())
            
            # Log into XNAT
            popup1 = tk.Toplevel()
            popup1.title("XNAT-PIC  ~  Login")
            master.root.width = 400
            master.root.height = 130
            master.x = (int(master.root.screenwidth) - master.root.width) / 2
            master.y = (int(master.root.screenheight)- master.root.height) / 3
            popup1.geometry("%dx%d+%d+%d" % (master.root.width, master.root.height, master.x, master.y))           
            
            # XNAT ADDRESS      
            popup1.label_address = tk.Label(popup1, text="  XNAT web address  ", font=("Calibri", 10, "bold"))   
            popup1.label_address.grid(row=0, column=0, padx=1, ipadx=1)
            popup1.entry_address = tk.Entry(popup1)
            popup1.entry_address.var = tk.StringVar()
            popup1.entry_address["textvariable"] = popup1.entry_address.var
            popup1.entry_address.grid(row=0, column=1, padx=1, ipadx=1)
           
            # XNAT USER 
            popup1.label_user = tk.Label(popup1, text="Username", font=("Calibri", 10, "bold"))
            popup1.label_user.grid(row=1, column=0, padx=1, ipadx=1)
            popup1.entry_user = tk.Entry(popup1)
            popup1.entry_user.var = tk.StringVar()
            popup1.entry_user["textvariable"] = popup1.entry_user.var
            popup1.entry_user.grid(row=1, column=1, padx=1, ipadx=1)

            # XNAT PASSWORD 
            popup1.label_psw = tk.Label(popup1, text="Password", font=("Calibri", 10, "bold"))
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
                text="Login", font=("Calibri", 10, "bold"), 
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
            
            # New Button
            xlabel_txtbox = 500
            ylabel_txtbox = 400
            ydelta_txt2btn = 70
            xlabel_btn = 650
            
            # Upload DICOM files
            label1 = tk.Label(frame_two, text='Upload new DICOM images to XNAT project', bg="#80FFE6", fg="black")
            label1.config(font=("Calibri", 26, "bold"))
            master.my_canvas.create_window(xlabel_txtbox, ylabel_txtbox, anchor=tk.NW, window=label1)
            dicom_text = tk.StringVar()
            dicom_btn = tk.Button(frame_two, textvariable=dicom_text, font=("Calibri", 22, "bold"), bg="black", fg="white", height=1, width=20, borderwidth=0, command=partial(self.xnat_dcm_uploader_select_project, session, master), cursor="hand2")
            dicom_text.set("DICOM2XNAT")
            master.my_canvas.create_window(xlabel_btn, ylabel_txtbox+ydelta_txt2btn, anchor = "nw", window = dicom_btn)
            
            # Upload files
            label2 = tk.Label(frame_two, text='Upload other files to XNAT project', bg="#80FFE6", fg="black")
            label2.config(font=("Calibri", 26, "bold"))
            master.my_canvas.create_window(530, ylabel_txtbox+3*ydelta_txt2btn, anchor=tk.NW, window=label2)
            file_text = tk.StringVar()
            file_btn = tk.Button(frame_two, textvariable=file_text, font=("Calibri", 22, "bold"), bg="black", fg="white", height=1, width=20, borderwidth=0, command=partial(self.xnat_files_uploader, session, master), cursor="hand2")
            file_text.set("FILES2XNAT")
            master.my_canvas.create_window(xlabel_btn, ylabel_txtbox+4*ydelta_txt2btn, anchor = "nw", window = file_btn)
            
            # Button to go to the previous page
            back_text = tk.StringVar()   
            back_btn = tk.Button(frame_two, textvariable=back_text, font=("Calibri", 22, "bold"), bg="white", fg="black", height=1, width=10, borderwidth=0, command=lambda: (back_btn.destroy(), dicom_btn.destroy(), file_btn.destroy(), label1.destroy(), label2.destroy(), session.disconnect(), xnat_pic_gui.choose_you_action(master)), cursor="hand2")
            back_text.set("Back")
            master.my_canvas.create_window(20, 850, anchor = "nw", window = back_btn)
        
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