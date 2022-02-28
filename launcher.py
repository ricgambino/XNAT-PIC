from ast import Str
from doctest import master
from logging import raiseExceptions
import tkinter as tk
from tkinter import CENTER, filedialog,messagebox
from tkinter import font
from tkinter.tix import COLUMN, Balloon
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
from progressbar import progressbar
try:
    from bruker2dicom_converter import bruker2dicom
except:
    from bruker2dicom import bruker2dicom
import xnat    
import pyAesCrypt

DELTA_SCREEN = 200
PATH_IMAGE = "C:\\Users\\Sara Zullino.HARI\\Desktop\\FG\\Image\\"

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
        self.root.configure(background='black')
        # If you want the logo 
        #self.root.iconbitmap(r"logo3.ico")

        # Define Canvas and logo in background
        mywidth = self.root.screenwidth-DELTA_SCREEN
        logo = Image.open(PATH_IMAGE + "NW_Header2.png")
        wpercent = (mywidth/float(logo.size[0]))
        hsize = int((float(logo.size[1])*float(wpercent)))
        my_canvas = tk.Canvas(self.root, width=mywidth, height=hsize, bg="#31C498", highlightthickness=3, highlightbackground="black")
        my_canvas.pack(padx=40, pady=40)
      
        logo = logo.resize((mywidth,hsize), Image.ANTIALIAS)  
        self.logo = ImageTk.PhotoImage(logo)
        my_canvas.create_image(-0.5, 0, anchor=tk.NW, image=self.logo)
        
        # Button to enter
        enter_text = tk.StringVar()
        enter_btn = tk.Button(self.root, textvariable=enter_text, font=("Calibri", 22, "bold"), bg="#80FFE6", fg="black", height=1, width=18, borderwidth=0, command=lambda: (my_canvas.pack_forget(), enter_btn.pack_forget(), xnat_pic_gui.choose_you_action(self, "")), cursor="hand2")
        enter_text.set("ENTER")
        my_canvas.create_window(680, 750, anchor = "nw", window = enter_btn)
        
        self.frame_main = tk.Frame(self.root)
        
        # Choose to upload files, fill in the info, convert files, process images
    def choose_you_action(self, where):
        # Canvas
        # If condition: to know if you get to this frame from the enter button or from the back button
         if where == "":
             ind = self.root
         else:
             ind = where
         
         # Define Canvas and update logo in background
         mywidth = ind.screenwidth-DELTA_SCREEN
         logo2 = Image.open(PATH_IMAGE + "logo41.png")
         wpercent = (mywidth/float(logo2.size[0]))
         hsize = int((float(logo2.size[1])*float(wpercent)))
         self.my_canvas = tk.Canvas(ind, width=mywidth, height=hsize, bg="#31C498", highlightthickness=1, highlightbackground="black")
         self.my_canvas.pack(padx=40, pady=40)

         logo2 = logo2.resize((mywidth,hsize), Image.ANTIALIAS)
         self.logo2 = ImageTk.PhotoImage(logo2)
         self.my_canvas.create_image(1, 1, anchor=tk.NW, image=self.logo2)
            
         # Positions for button
         x_btn = 100
         y_btn = 400
         xdelta_btn = 400
        
         # Convert files Bruker2DICOM
         convert_text = tk.StringVar()
         self.convert_btn = tk.Button(ind, textvariable=convert_text, font=("Calibri", 22, "bold"), bg="#80FFE6", fg="black", height=1, width=20, borderwidth=0, command=partial(self.bruker2dicom_conversion, self), cursor="hand2")
         convert_text.set("Bruker2DICOM")
         self.my_canvas.create_window(x_btn, y_btn, anchor = "nw", window = self.convert_btn)
         
         # Fill in the info
         info_text = tk.StringVar()
         self.info_btn = tk.Button(ind, textvariable=info_text, font=("Calibri", 22, "bold"), bg="#80FFE6", fg="black", height=1, width=20, borderwidth=0, cursor="hand2")
         info_text.set("Fill in the info")
         self.my_canvas.create_window(x_btn + xdelta_btn, y_btn, anchor = "nw", window = self.info_btn)

         # Upload files
         upload_text = tk.StringVar()
         self.upload_btn = tk.Button(ind, textvariable=upload_text, font=("Calibri", 22, "bold"), bg="#80FFE6", fg="black", height=1, width=20, borderwidth=0, command=partial(self.xnat_dcm_uploader, self), cursor="hand2")
         upload_text.set("Uploader")
         self.my_canvas.create_window(x_btn + 2*xdelta_btn, y_btn, anchor = "nw", window = self.upload_btn)        
        
         # Processing your files
         process_text = tk.StringVar()
         self.process_btn = tk.Button(ind, textvariable=process_text, font=("Calibri", 22, "bold"), bg="#80FFE6", fg="black", height=1, width=20, borderwidth=0, cursor="hand2")
         process_text.set("Processing")
         self.my_canvas.create_window(x_btn + 3*xdelta_btn, y_btn, anchor = "nw", window = self.process_btn)
        

         # Info 
         # Info msg
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
                 
         # Button for info 
         # Positions for button
         x_btn = 245
         y_btn = 470
         xdelta_btn = 400

         logo_info = Image.open(PATH_IMAGE + "info.png")
         self.logo_info = ImageTk.PhotoImage(logo_info)
         
         self.info_convert_btn = tk.Button(ind, image = self.logo_info, bg="#80FFE6", borderwidth=0, command = lambda: helpmsg("button1"), cursor="question_arrow")
         self.my_canvas.create_window(x_btn, y_btn, anchor="nw", window=self.info_convert_btn)

         self.info_info_btn = tk.Button(ind, image = self.logo_info, bg="#80FFE6", borderwidth=0, command = lambda: helpmsg("button2"), cursor="question_arrow")
         self.my_canvas.create_window(x_btn + xdelta_btn, y_btn, anchor="nw", window=self.info_info_btn)

         self.info_upload_btn = tk.Button(ind, image = self.logo_info, bg="#80FFE6", borderwidth=0, command = lambda: helpmsg("button3"), cursor="question_arrow")
         self.my_canvas.create_window(x_btn + 2*xdelta_btn, y_btn, anchor="nw", window=self.info_upload_btn)

         self.info_process_btn = tk.Button(ind, image = self.logo_info, bg="#80FFE6", borderwidth=0, command = lambda: helpmsg("button4"), cursor="question_arrow")
         self.my_canvas.create_window(x_btn + 3*xdelta_btn, y_btn, anchor="nw", window=self.info_process_btn) 

         # Logo on top
         logo3 = Image.open(PATH_IMAGE + "path163.png")
         self.logo3 = ImageTk.PhotoImage(logo3)
         label1 = tk.Label(ind, image=self.logo3,  bg="#31C498", width=1716)
         self.my_canvas.create_window(0.5, 20, anchor=tk.NW, window=label1)
         

    def get_page(self):
        return self.root   

    class bruker2dicom_conversion():
        def __init__(self, master):
        
             def start_conversion():               
                messagebox.showinfo("Bruker2DICOM","Select project directory in Bruker ParaVision format")
                
                # Choose your directory
                folder_to_convert = filedialog.askdirectory(parent=master.root, initialdir=os.path.expanduser("~"), title="XNAT-PIC: Select project directory in Bruker ParaVision format")
                
                if not folder_to_convert:
                    sys.exit(0)
                     
                master.root.deiconify()
                master.root.update()
                master.root.title("Bruker2DICOM")
                head, tail = os.path.split(folder_to_convert)
                project_foldername = tail.split('.',1)[0] + "_dcm"
                dst = os.path.join(head, project_foldername).replace('\\', '/')

                try:
                    # If the destination folder already exists, throw exception
                    if os.path.isdir(dst):
                        raise Exception("Destination folder %s already exists" % dst)
                    else:
                      os.mkdir(dst)
                    # Convert from bruker to DICOM and disable the buttons
                    master.convert_btn['state'] = tk.DISABLED
                    master.info_btn['state'] = tk.DISABLED
                    master.upload_btn['state'] = tk.DISABLED
                    master.process_btn['state'] = tk.DISABLED
                    master.root.config(cursor="watch")               
                    bruker2dicom(folder_to_convert, dst, master)
                    master.root.config(cursor="arrow")
                    my_exeption = False
                    
                except Exception as e:
                    master.root.config(cursor="arrow") 
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
                    sys.exit(0)

             threading.Thread(target=start_conversion).start()

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
            my_elements = master.my_canvas.find_all()
            master.my_canvas.delete(my_elements[1])
            master.my_canvas.delete(my_elements[2])
            master.my_canvas.delete(my_elements[3])
            master.my_canvas.delete(my_elements[4])
            master.my_canvas.delete(my_elements[5])
            master.my_canvas.delete(my_elements[6])
            master.my_canvas.delete(my_elements[7])
            master.my_canvas.delete(my_elements[8])

            xlabel_txtbox = 500
            ylabel_txtbox = 400
            ydelta_txt2btn = 70
            xlabel_btn = 650
            
            # Upload DICOM files
            label1 = tk.Label(frame_two, text='Upload new DICOM images to XNAT project', bg="#80FFE6", fg="black")
            label1.config(font=("Calibri", 26, "bold"))
            master.my_canvas.create_window(xlabel_txtbox, ylabel_txtbox, anchor=tk.NW, window=label1)
            dicom_text = tk.StringVar()
            self.dicom_btn = tk.Button(frame_two, textvariable=dicom_text, font=("Calibri", 22, "bold"), bg="black", fg="white", height=1, width=20, borderwidth=0, command=partial(self.xnat_dcm_uploader_select_project, session, master), cursor="hand2")
            dicom_text.set("DICOM2XNAT")
            master.my_canvas.create_window(xlabel_btn, ylabel_txtbox+ydelta_txt2btn, anchor = "nw", window = self.dicom_btn)
            
            # Upload files
            label1 = tk.Label(frame_two, text='Upload other files to XNAT project', bg="#80FFE6", fg="black")
            label1.config(font=("Calibri", 26, "bold"))
            master.my_canvas.create_window(530, ylabel_txtbox+3*ydelta_txt2btn, anchor=tk.NW, window=label1)
            file_text = tk.StringVar()
            file_btn = tk.Button(frame_two, textvariable=file_text, font=("Calibri", 22, "bold"), bg="black", fg="white", height=1, width=20, borderwidth=0, command=partial(self.xnat_files_uploader, session, master), cursor="hand2")
            file_text.set("FILES2XNAT")
            master.my_canvas.create_window(xlabel_btn, ylabel_txtbox+4*ydelta_txt2btn, anchor = "nw", window = file_btn)
            
            # Button to go to the previous page
            back_text = tk.StringVar()   
            self.back_btn = tk.Button(frame_two, textvariable=back_text, font=("Calibri", 22, "bold"), bg="white", fg="black", height=1, width=10, borderwidth=0, command=lambda: (master.my_canvas.pack_forget(), xnat_pic_gui.choose_you_action(master, frame_two)), cursor="hand2")
            back_text.set("Back")
            master.my_canvas.create_window(20, 850, anchor = "nw", window = self.back_btn)
        
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

        def check_project_name(self,master):
            if self.entry_prjname.var.get().lower in self.OPTIONS:
                messagebox.showerror(
                    "Error!",
                    "Project ID %s already exists! Please, enter a different project ID"
                    % self.entry_prjname.var.get(),
                )
            else:
                self.xnat_dcm_uploader_select_custom_vars(master)
        
        def xnat_dcm_uploader_select_project(self,session,master):

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
            popup2.value.set("  Project ID  ")
            popup2.entry_prjname.grid(row=0, column=2)
            popup2.entry_prjname.var = tk.StringVar()
            popup2.entry_prjname.var.set("  Project ID  ")
            popup2.entry_prjname["textvariable"] = popup2.entry_prjname.var
           
            # PROJECTS LIST
            self.OPTIONS = session.projects
            popup2.prj = tk.StringVar()
            popup2.project_list = tk.OptionMenu(popup2, popup2.prj, *self.OPTIONS)
            popup2.project_list.grid(row=2, column=2)
            self.newprj_var = tk.IntVar()
            popup2.btn_newprj = tk.Checkbutton(popup2, variable=self.newprj_var, onvalue=1, offvalue=0, command=isChecked)
            popup2.btn_newprj.grid(row=0, column=1)           
            
            session.disconnect()

        def xnat_files_uploader(self, session, master):

            session.disconnect()





if __name__ == "__main__":
    root = tk.Tk()
    app = xnat_pic_gui(root)
    root.mainloop()