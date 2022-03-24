from doctest import master
from logging import exception
import shutil
import tkinter as tk
from tkinter import MULTIPLE, SINGLE, filedialog, messagebox
from PIL import Image, ImageTk
from tkinter import ttk
import time
import os, re
from functools import partial
import subprocess
import platform
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
from multiprocessing import Pool
from xnat_uploader import Dicom2XnatUploader


PATH_IMAGE = "images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
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
         self.upload_btn = tk.Button(self.my_canvas, textvariable=upload_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command=partial(self.XNATUploader, self), cursor=CURSOR_HAND)
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
            
            # Disable the buttons
            master.convert_btn['state'] = tk.DISABLED
            master.info_btn['state'] = tk.DISABLED
            master.upload_btn['state'] = tk.DISABLED
            master.process_btn['state'] = tk.DISABLED
            
            def normal_btn():
                self.conv_popup.destroy()
                #Enable all buttons
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL

            def isChecked():
                self.params['results_flag'] = self.results_flag.get()
            
            def checkOverwrite():
                master.overwrite_flag = self.overwrite_flag.get()

            self.conv_popup = tk.Toplevel()
            self.conv_popup.geometry("%dx%d+%d+%d" % (500, 150, my_width/3, my_height/3))
            self.conv_popup.title('DICOM Converter')
            self.conv_popup.protocol("WM_DELETE_WINDOW", normal_btn)

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

        def prj_conversion(self, master):

            ############### Whole project conversion ################

            # Disable the buttons
            master.convert_btn['state'] = tk.DISABLED
            master.info_btn['state'] = tk.DISABLED
            master.upload_btn['state'] = tk.DISABLED
            master.process_btn['state'] = tk.DISABLED

            # Ask for project directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for the chosen directory
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL
                messagebox.showerror("Dicom Converter", "You have not chosen a directory")
                return
            master.root.deiconify()
            master.root.update()
            self.dst = self.folder_to_convert + '_dcm'

            # Initialize converter class
            converter = Bruker2DicomConverter(self.params)
            
            try:
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

            # Convert from bruker to DICOM and disable the buttons
            master.convert_btn['state'] = tk.DISABLED
            master.info_btn['state'] = tk.DISABLED
            master.upload_btn['state'] = tk.DISABLED
            master.process_btn['state'] = tk.DISABLED

            # Ask for subject directory
            self.folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select subject directory in Bruker ParaVision format")
            if not self.folder_to_convert:
                # Check for chosen directory
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL
                messagebox.showerror("Dicom Converter", "You have not chosen a directory")
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
                start_time = time.time()

                # Start the progress bar
                progressbar = ProgressBar(bar_title='DICOM Subject Converter')
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
                # Project label
                keys = ["Project", "Subject", "Acq. date", "Group", "Dose", "Timepoint"]
                count = 0
                labels=[]
                x_lbl = int(my_width*40/100)
                y_lbl_perc = 25
                y_lbl_delta = 7.5
                y_folder_lbl = y_folder_list
                for key in keys:
                    y_lbl = int(my_height*y_lbl_perc/100)
                    labels.append(tk.Label(master.my_canvas, text=key, font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR))
                    master.my_canvas.create_window(x_lbl, y_lbl, width = int(my_width*8/100), anchor = tk.NW, window = labels[count])
                    y_lbl_perc += y_lbl_delta
                    count += 1
                folder_lbl = tk.Label(master.my_canvas, text="Folder", font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR)
                master.my_canvas.create_window(x_lbl, y_folder_lbl, width = int(my_width*8/100), anchor = tk.NW, window = folder_lbl)

                # Project entry               
                count = 0
                entries=[]
                x_entry = int(my_width*50/100)
                y_entry_perc = 25
                y_entry_delta = 7.5
                for key in keys:
                    y_entry = int(my_height*y_entry_perc/100)
                    entries.append(tk.Entry(master.my_canvas, state='disabled', font=SMALL_FONT, takefocus = 0))
                    master.my_canvas.create_window(x_entry, y_entry, width = int(my_width*20/100), anchor = tk.NW, window = entries[count])
                    y_entry_perc += y_entry_delta
                    count += 1
                folder_entry = tk.Entry(master.my_canvas, state='disabled', font=SMALL_FONT, takefocus = 0)
                width_folder_entry = int(my_width*31.4/100)
                master.my_canvas.create_window(x_entry, y_folder_lbl, width = width_folder_entry, anchor = tk.NW, window = folder_entry)
                # Menu
                # Group
                OPTIONS = ["untreated", "treated"]
                selected_group = tk.StringVar()
                group_menu = ttk.Combobox(master.my_canvas, textvariable=selected_group, font = SMALL_FONT, takefocus = 0)
                group_menu['values'] = OPTIONS
                group_menu['state'] = 'disabled'
                x_group_menu = int(my_width*72/100)
                y_group_perc = 25
                y_group_delta = 7.5
                y_group_menu = int(my_height*(y_group_perc+3*y_group_delta)/100)
                master.my_canvas.create_window(x_group_menu, y_group_menu, anchor = tk.NW, width = int(my_width*9.5/100), window = group_menu)
                
                # Timepoint
                OPTIONS = ["pre", "post"]
                selected_timepoint = tk.StringVar()
                timepoint_menu = ttk.Combobox(master.my_canvas, textvariable=selected_timepoint, font = SMALL_FONT, takefocus = 0)
                timepoint_menu['values'] = OPTIONS
                timepoint_menu['state'] = 'disabled'
                x_timepoint_menu = int(my_width*72/100)
                y_timepiont_menu = int(my_height*(y_group_perc+5*y_group_delta)/100)
                master.my_canvas.create_window(x_timepoint_menu, y_timepiont_menu, anchor = tk.NW, width = int(my_width*5/100), window = timepoint_menu)

                time_entry = tk.Entry(master.my_canvas, state='disabled', font = SMALL_FONT, takefocus = 0)
                x_timepoint_menu1 = int(my_width*78/100)
                master.my_canvas.create_window(x_timepoint_menu1, y_timepiont_menu, anchor = tk.NW, width = int(my_width*5/100), window = time_entry)

                OPTIONS1 = ["seconds", "minutes", "hours", "days", "month", "years"]
                selected_timepoint1 = tk.StringVar()
                timepoint_menu1 = ttk.Combobox(master.my_canvas, textvariable=selected_timepoint1, font = SMALL_FONT, takefocus = 0)
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
                    # load the info of the selected folder
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
                clear_text = tk.StringVar() 
                clear_btn = tk.Button(master.my_canvas, textvariable=clear_text, font=SMALL_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: clear_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                clear_text.set("Clear")
                width_clear_btn = int(my_width*9.4/100)
                x_clear_btn = int(my_width*72/100)
                y_clear_btn = int(my_height*(y_group_perc+0*y_group_delta)/100)
                master.my_canvas.create_window(x_clear_btn, y_clear_btn, anchor = tk.NW, width = width_clear_btn, window = clear_btn)
                
                def clear_metadata():
                    # Clear all the combobox and the entry
                    selected_group.set('')
                    selected_timepoint.set('')
                    selected_timepoint1.set('')
                    time_entry.delete(0, tk.END)
                    state = entries[0]['state']
                    # Set empty string in all the entries
                    for i in range(2, len(fields)):
                            entries[i]['state'] = tk.NORMAL
                            entries[i].delete(0, tk.END)
                            entries[i]['state'] = state

                #################### Modify the metadata ####################
                modify_text = tk.StringVar() 
                modify_btn = tk.Button(master.my_canvas, textvariable=modify_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: modify_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                modify_text.set("Modify")
                y_btn = int(my_height*69/100)
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
                    for i in range(0, len(fields)-1):
                        entries[i].config(state=tk.NORMAL)

                    # Option menu for the dose
                    group_menu['state'] = 'readonly'

                    def group_changed(event):
                        """ handle the group changed event """
                        entries[fields.index("Group")].delete(0, tk.END)
                        entries[fields.index("Group")].insert(0, str(selected_group.get()))                    
                        my_listbox.selection_set(selected_index)

                    group_menu.bind("<<ComboboxSelected>>", group_changed)
                    
                    # Option menu for the timepoint
                    timepoint_menu1['state'] = 'readonly'
                    time_entry['state'] = 'normal'
                    timepoint_menu['state'] = 'readonly'

                    def timepoint_changed(event):
                        entries[fields.index("Timepoint")].config(state=tk.NORMAL)
                        """ handle the timepoint changed event """
                        timepoint_str = str(selected_timepoint.get()) + "-" + str(time_entry.get()) + "-" + str(selected_timepoint1.get())
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
                confirm_btn = tk.Button(master.my_canvas, textvariable=confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: confirm_metadata(), cursor=CURSOR_HAND, takefocus = 0)
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
                multiple_confirm_btn = tk.Button(master.my_canvas, textvariable=multiple_confirm_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: confirm_multiple_metadata(), cursor=CURSOR_HAND, takefocus = 0)
                multiple_confirm_text.set("Multiple Confirm")
                x_multiple_conf_btn = int(my_width*78/100)
                master.my_canvas.create_window(x_multiple_conf_btn, y_btn, anchor = tk.NW, width = width_btn, window = multiple_confirm_btn)
                
                def normal_button():
                    clear_btn["state"] = tk.NORMAL
                    modify_btn["state"] = tk.NORMAL
                    confirm_btn["state"] = tk.NORMAL
                    multiple_confirm_btn["state"] = tk.NORMAL
                    save_btn["state"] = tk.NORMAL

                def confirm_multiple_metadata():
                    clear_btn["state"] = tk.DISABLED
                    modify_btn["state"] = tk.DISABLED
                    confirm_btn["state"] = tk.DISABLED
                    multiple_confirm_btn["state"] = tk.DISABLED
                    save_btn["state"] = tk.DISABLED
                    
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
                save_text = tk.StringVar() 
                save_btn = tk.Button(master.my_canvas, textvariable=save_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: save_metadata(), cursor=CURSOR_HAND, takefocus = 0)
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
                exit_btn = tk.Button(master.my_canvas, textvariable=exit_text, font=LARGE_FONT, bg=BG_BTN_COLOR, fg=TEXT_BTN_COLOR, borderwidth=0, command = lambda: exit_metadata(), cursor=CURSOR_HAND, takefocus = 0)
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
                    
                    folder_lbl.destroy()
                    folder_entry.destroy()
                    timepoint_menu.destroy()
                    timepoint_menu1.destroy()
                    time_entry.destroy()
                    group_menu.destroy()
                    
                    clear_btn.destroy()
                    modify_btn.destroy()
                    confirm_btn.destroy()
                    save_btn.destroy()
                    exit_btn.destroy()
                    multiple_confirm_btn.destroy()
                    xnat_pic_gui.choose_you_action(master)

    class XNATUploader():

        def __init__(self, master):

            def disable_buttons():
                # Disable all buttons
                master.convert_btn['state'] = tk.DISABLED
                master.info_btn['state'] = tk.DISABLED
                master.upload_btn['state'] = tk.DISABLED
                master.process_btn['state'] = tk.DISABLED
            
            disable_buttons()

            def enable_btn():
                self.session.disconnect()
                login_popup.destroy()
                #Enable all buttons
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL

            login_popup = tk.Toplevel()
            login_popup.title("XNAT-PIC  ~  Login")
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
            master.process_btn['state'] = tk.NORMAL

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
            # Return to login method
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
                # self.overall_uploader(session, master)
                self.project_selection(master)
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

        def project_selection(self, master):

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

            def enable_btn():
                self.session.disconnect()
                popup2.destroy()
                #Enable all buttons
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL

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
            self.OPTIONS = self.session.projects
            self.prj = tk.StringVar()
            default_value = "Select prj"
            popup2.project_list = ttk.OptionMenu(popup2, self.prj, default_value, *self.OPTIONS)
            popup2.project_list.grid(row=2, column=2)
            self.newprj_var = tk.IntVar()
            popup2.btn_newprj = tk.Checkbutton(popup2, variable=self.newprj_var, onvalue=1, offvalue=0, command=isChecked)
            popup2.btn_newprj.grid(row=0, column=1)

            popup2.back_btn = tk.Button(
                popup2, text="Back", command=lambda: (popup2.destroy())
            )
            popup2.back_btn.grid(row=4, column=0)
            popup2.next_btn = tk.Button(
                popup2, text="Next", command=partial(self.check_project_name, popup2, master), state="disabled"
            )
            popup2.next_btn.grid(row=4, column=2)

            self.button_next = popup2.next_btn

            self.newprj_var.trace_add("write", self.enable_next)
            popup2.entry_prjname.var.trace_add("write", self.enable_next)
            self.prj.trace_add("write", self.enable_next)

            popup2.protocol("WM_DELETE_WINDOW", enable_btn)

        def check_project_name(self, popup, master):

            # Method to check about project name
            if popup.entry_prjname.var.get().lower in self.OPTIONS:
                # Case 1 --> The project already exists
                messagebox.showerror(
                    "Error!",
                    "Project ID %s already exists! Please, enter a different project ID"
                    % self.entry_prjname.var.get(),
                )
            else:
                # Case 2 --> The project does not exist yet
                try:
                    popup.destroy()
                    if self.newprj_var.get() == 1:
                        self.project = self.entry_prjname.var.get()
                    else:
                        self.project = self.prj.get()
                    self.overall_uploader(master)
                except exception as e:
                    messagebox.showerror("Error!", str(e))

        def overall_uploader(self, master):

            def enable_btn():
                self.session.disconnect()
                up_popup.destroy()
                #Enable all buttons
                master.convert_btn['state'] = tk.NORMAL
                master.info_btn['state'] = tk.NORMAL
                master.upload_btn['state'] = tk.NORMAL
                master.process_btn['state'] = tk.NORMAL

            # Initialize the uploader class with the current session
            self.uploader = Dicom2XnatUploader()

            up_popup = tk.Toplevel()
            up_popup.geometry("%dx%d+%d+%d" % (500, 300,  my_width/3, my_height/6))
            up_popup.title('XNAT Uploader')
            # Upload project
            up_popup.btn_prj = tk.Button(up_popup, text='Upload Project', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (up_popup.destroy(), self.project_uploader(master)))
            up_popup.btn_prj.grid(row=2, column=0, padx=10, pady=5)
            # Upload subject
            up_popup.btn_sbj = tk.Button(up_popup, text='Upload Subject', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (up_popup.destroy(), self.subject_uploader(master)))
            up_popup.btn_sbj.grid(row=3, column=0, padx=10, pady=5)
            # Upload experiment
            up_popup.btn_exp = tk.Button(up_popup, text='Upload Experiment', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (up_popup.destroy(), self.experiment_uploader(master)))
            up_popup.btn_exp.grid(row=4, column=0, padx=10, pady=5)
            # Upload file
            up_popup.btn_file = tk.Button(up_popup, text='Upload File', font=LARGE_FONT, 
                                    bg="grey", fg="white", height=1, width=15, borderwidth=1, 
                                    command=lambda: (up_popup.destroy(), self.file_uploader(master)))
            up_popup.btn_file.grid(row=5, column=0, padx=10, pady=5)

            up_popup.protocol("WM_DELETE_WINDOW", enable_btn)

        def project_uploader(self, master):

            project_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC Project Uploader: Select project directory in DICOM format to upload")
            # Check for empty selected folder
            if os.path.isdir(project_to_upload) == False:
                messagebox.showerror('XNAT-PIC - Uploader', 'Error! The selected folder does not exist!')
                self.normal_btn(master, disconnect=True)
                return
            elif os.listdir(project_to_upload) == []:
                messagebox.showerror('XNAT-PIC - Uploader', 'Error! The selected folder is empty!')
                self.normal_btn(master, disconnect=True)
                return

            try:
                # Start progress bar
                progressbar = ProgressBar(bar_title='XNAT Uploader')
                progressbar.start_indeterminate_bar()

                t = threading.Thread(target=self.uploader.multi_core_upload, args=(project_to_upload, self.project, self.session ))
                t.start()
                
                while t.is_alive() == True:
                    progressbar.update_bar()
                
                # Stop the progress bar and close the popup
                progressbar.stop_progress_bar()

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Uploader", e)

            # Restore main frame buttons
                messagebox.showinfo("XNAT Uploader","Done! Your subject is uploaded on XNAT platform.")
            master.convert_btn['state'] = tk.NORMAL
            master.info_btn['state'] = tk.NORMAL
            master.upload_btn['state'] = tk.NORMAL
            master.process_btn['state'] = tk.NORMAL


        def subject_uploader(self, master):

            subject_to_upload = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC Subject Uploader: Select subject directory in DICOM format to upload")
            # Check for empty selected folder
            if os.path.isdir(subject_to_upload) == False:
                messagebox.showerror('XNAT-PIC - Uploader', 'Error! The selected folder does not exist!')
                self.normal_btn(master, disconnect=True)
                return
            elif os.listdir(subject_to_upload) == []:
                messagebox.showerror('XNAT-PIC - Uploader', 'Error! The selected folder is empty!')
                self.normal_btn(master, disconnect=True)
                return

            try:
                # Start progress bar
                progressbar = ProgressBar(bar_title='XNAT Uploader')
                progressbar.start_indeterminate_bar()
                # Start thread for uploading
                upload_thread = threading.Thread(target=self.uploader.uploader, args=((subject_to_upload, self.project), self.session))
                upload_thread.start()
                while upload_thread.is_alive() == True:
                    progressbar.update_bar()
                progressbar.stop_progress_bar()

            except Exception as e: 
                messagebox.showerror("XNAT-PIC - Uploader", e)

            # Restore main frame buttons
            messagebox.showinfo("XNAT Uploader","Done! Your subject is uploaded on XNAT platform.")
            master.convert_btn['state'] = tk.NORMAL
            master.info_btn['state'] = tk.NORMAL
            master.upload_btn['state'] = tk.NORMAL
            master.process_btn['state'] = tk.NORMAL


        def experiment_uploader(self, master):
            # Call for check_project_name
            # Call for upload() method from Dicom2XnatUploader class
            pass

        def check_experiment(self, master):
            pass

        def file_uploader(self, master):

            file_to_upload = filedialog.askopenfilenames(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC File Uploader: Select file to upload")
            
            if file_to_upload == []:
                messagebox.showerror('XNAT-PIC - Uploader', 'Error! No files selected!')
                self.normal_btn(master, disconnect=True)
                return

            progressbar = ProgressBar('DICOM File Uploader')
            progressbar.start_determinate_bar()
            for i, file in enumerate(file_to_upload):
                if os.path.isfile(file):
                    tf = threading.Thread(target=self.uploader.file_uploader, args=(file, self.session,{
                                        'project_id': 'Project_X',
                                        'subject_id': 'da_PyMT_5',
                                        'experiment_id': 'Project_2_da_PyMT_5_Treated_Post_2_months',
                                    }))
                    tf.start()
                    while tf.is_alive() == True:
                        # progressbar.update_bar()
                        progressbar.update_bar(0.00001)
                        time.sleep(0.5)
                    else:
                        progressbar.update_progressbar(i + 1, len(file_to_upload))

            # Restore main frame buttons
            messagebox.showinfo("XNAT Uploader","Done! Your file is uploaded on XNAT platform.")
            master.convert_btn['state'] = tk.NORMAL
            master.info_btn['state'] = tk.NORMAL
            master.upload_btn['state'] = tk.NORMAL
            master.process_btn['state'] = tk.NORMAL



if __name__ == "__main__":
    root = tk.Tk()
    app = xnat_pic_gui(root)
    root.mainloop()