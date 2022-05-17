from ast import keyword
from time import strftime
from dotenv import set_key
from numpy import expand_dims
from pip import main
import ttkbootstrap as ttk
import tkinter as tk
from layout_style import MyStyle
from accessory_functions import enable_buttons, open_image
from datetime import date

PATH_IMAGE = "images\\"
CURSOR_HAND = "hand2"

class ObjectCreator():

    def __init__(self, session):

        self.session = session
        # self.root = root
        # Load Delete icon
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 8, 8)

    def add_project_popup(self):
        self.master = tk.Toplevel(background="white")
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        # self.master.resizable(False, False)

        # self.style_label = tk.StringVar()
        # self.style_label.set('cerculean')
        # self.style = MyStyle(self.style_label.get()).get_style()

        ###########################################################################
        # Project Widgets
        ###########################################################################
        # LabelFrame for Project Info
        self.project_labelframe = ttk.LabelFrame(self.master, text="Add New Project")
        self.project_labelframe.pack(fill='x', padx=10, pady=10)
        # TITLE
        self.project_title = tk.StringVar()
        self.project_title_label = ttk.Label(self.project_labelframe, text="Project Title")
        self.project_title_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_title_entry = ttk.Entry(self.project_labelframe, width=50, textvariable=self.project_title)
        self.project_title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        # ID
        self.project_id = tk.StringVar()
        self.project_id_label = ttk.Label(self.project_labelframe, text="Project ID")
        self.project_id_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_id_entry = ttk.Entry(self.project_labelframe, width=50, textvariable=self.project_id,
                                            state='disabled')
        self.project_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)
        self.project_id_modify = tk.IntVar()
        self.project_id_checkbutton = ttk.Checkbutton(self.project_labelframe, text="Modify", onvalue=1, 
                                        offvalue=0, variable=self.project_id_modify)
        self.project_id_checkbutton.grid(row=1, column=3, padx=5, pady=5, sticky=tk.W)
        def enable_entry(*args):
            if self.project_id_modify.get() == 1:
                self.project_id_entry.configure(state='normal')
            else:
                self.project_id_entry.configure(state='disabled')
        self.project_id_modify.trace('w', enable_entry)
        # DESCRIPTION
        self.project_description_label = ttk.Label(self.project_labelframe, text="Project Description")
        self.project_description_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.NW)
        self.project_description = tk.StringVar()
        self.project_description_entry = ttk.Text(self.project_labelframe, width=50, height=8)
        self.project_description_entry.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)
        self.project_description_scrollbar = ttk.Scrollbar(self.project_labelframe, orient='vertical', 
                                                        command=self.project_description_entry.yview)
        self.project_description_scrollbar.grid(row=2, column=2, padx=0, pady=5, sticky=tk.NS)
        self.project_description_entry.configure(yscrollcommand=self.project_description_scrollbar.set)
        # KEYWORDS
        self.project_keywords_list = []
        current_keyword = tk.StringVar()
        keyword_to_remove = tk.StringVar()
        self.project_keywords_label = ttk.Label(self.project_labelframe, text="Keywords")
        self.project_keywords_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_keyword_labelframe = ttk.Labelframe(self.project_labelframe, style="Hidden.TLabelframe")
        self.project_keyword_labelframe.grid(row=3, column=1, padx=5, pady=0, sticky=tk.NW, columnspan=3)
        self.project_keywords_entry = ttk.Entry(self.project_keyword_labelframe, width=50, textvariable=current_keyword)
        self.project_keywords_entry.pack(side='top', fill='x', anchor=tk.NW)

        def clear_keywords(*args):
            for btn in self.project_keyword_labelframe.winfo_children():
                if btn != self.project_keywords_entry:
                    btn.destroy()

        def remove_keyword(*args):
            if keyword_to_remove.get() != "":
                for key in self.project_keywords_list:
                    if key == keyword_to_remove.get():
                        self.project_keywords_list.remove(keyword_to_remove.get())
                keyword_to_remove.set("")

        def show_keywords(*args):
            keywords = []
            buttons = []
            for i in range(len(self.project_keywords_list)):
                keywords.append(str(self.project_keywords_list[i]))
            for j in range(len(keywords)):
                buttons.append(ttk.Button(self.project_keyword_labelframe, text=keywords[j], 
                                    image=self.logo_delete, compound='right', cursor=CURSOR_HAND,
                                    command=lambda c=j: (keyword_to_remove.set(buttons[c]["text"]), buttons[c].destroy()), style="Keyword.TButton"))
                buttons[j].pack(side='left', padx=0, pady=2, anchor=tk.NW)

        def set_keyword(event):
            if event.char == '\r' and current_keyword.get() != "":
                self.project_keywords_list.append(current_keyword.get())
                clear_keywords()
                show_keywords()
                current_keyword.set("")
        self.project_keywords_entry.bind("<Key>", set_keyword)
        keyword_to_remove.trace('w', remove_keyword)
        # INVESTIGATORS
        self.project_investigators_label = ttk.Label(self.project_labelframe, text="Investigators")
        self.project_investigators_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_investigators_entry = ttk.Entry(self.project_labelframe, width=50)
        self.project_investigators_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

        # Callbacks
        def title_callback(*args):
            if self.project_title.get() != '':
                self.project_id.set(self.project_title.get())
        self.project_title.trace('w', title_callback)

        #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        self.exit_btn = ttk.Button(self.master, text="Quit", command=lambda: self.master.destroy())
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit")
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

        # Mainloop
        self.master.mainloop()
        
    def add_subject_popup(self):
        self.master = tk.Toplevel(background="white")
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        # self.master.resizable(False, False)

        # self.style_label = tk.StringVar()
        # self.style_label.set('cerculean')
        # self.style = MyStyle(self.style_label.get()).get_style()
        ###########################################################################
        # Subject Widgets
        ###########################################################################
        # LabelFrame for Subject Info
        self.subject_labelframe = ttk.LabelFrame(self.master, text="Subject Info")
        self.subject_labelframe.pack(fill='x', padx=10, pady=10)

        # Parent Project
        self.parent_project = tk.StringVar()
        # self.list_of_projects = []
        self.list_of_projects = list(self.session.projects)
        self.parent_project_label = ttk.Label(self.subject_labelframe, text="Parent Project")
        self.parent_project_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_project_menu = ttk.OptionMenu(self.subject_labelframe, self.parent_project, 0, *self.list_of_projects)
        self.parent_project_menu.config(width=50)
        self.parent_project_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Subject ID
        self.subject_id = tk.StringVar()
        self.subject_id_label = ttk.Label(self.subject_labelframe, text="Subject ID")
        self.subject_id_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_id_entry = ttk.Entry(self.subject_labelframe, width=50, 
                                        textvariable=self.subject_id, state='disabled')
        self.subject_id_entry.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        def enable_subject_id(*args):
            if self.parent_project.get() != '':
                enable_buttons([self.subject_id_entry])
        self.parent_project.trace('w', enable_subject_id)

        # Subject Gender
        self.subject_gender = tk.StringVar()
        self.gender_values = ["Male", "Female"]
        self.subject_gender_label = ttk.Label(self.subject_labelframe, text="Gender")
        self.subject_gender_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_gender_menu = ttk.OptionMenu(self.subject_labelframe, self.subject_gender, 0, *self.gender_values)
        self.subject_gender_menu.grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

        # Subject Age
        today = date.today()
        today = today.strftime("%d/%m/%Y")
        self.subject_age = tk.StringVar()
        self.subject_age.set(today)
        self.subject_age_label = ttk.Label(self.subject_labelframe, text="Age")
        self.subject_age_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_age_entry = ttk.DateEntry(self.subject_labelframe)
        self.subject_age_entry.entry.config(textvariable=self.subject_age)
        self.subject_age_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)
        def check_date(*args):
            if self.subject_age.get() > today:
                self.subject_age.set(today)
            else:
                pass
        self.subject_age.trace('w', check_date)


        # Subject Weight
        self.subject_weight = tk.StringVar()
        self.subject_weight_label = ttk.Label(self.subject_labelframe, text="Weight")
        self.subject_weight_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_weight_entry = ttk.Entry(self.subject_labelframe, width=50, textvariable=self.subject_weight)
        self.subject_weight_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)


        #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        self.exit_btn = ttk.Button(self.master, text="Quit", command=lambda: self.master.destroy())
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit")
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

        # Mainloop
        self.master.mainloop()

    def add_experiment_popup(self):
        # LabelFrame for Experiment Info
        self.experiment_labelframe = ttk.LabelFrame(self.master, text="Experiment Info")
        self.experiment_labelframe.pack(fill='x', padx=10, pady=10)

        # Experiment Widgets
        self.experiment_label = ttk.Label(self.experiment_labelframe, text="Experiment ID")
        self.experiment_label.pack(side='left', padx=5, pady=5)

        

        

    def create_new_project(self):
        pass

    def create_new_subject(self):
        pass

    def create_new_experiment(self):
        pass

# if __name__ == "__main__":

#     root = tk.Tk()
#     # object_creator = ObjectCreator(root).add_project_popup()
#     object_creator = ObjectCreator(root).add_subject_popup()