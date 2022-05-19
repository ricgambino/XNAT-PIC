from tkinter import messagebox
import ttkbootstrap as ttk
import tkinter as tk
from accessory_functions import disable_buttons, enable_buttons, open_image
from datetime import date

PATH_IMAGE = "images\\"
CURSOR_HAND = "hand2"

class ProjectManager():

    def __init__(self, session):

        self.session = session
        # Load icons
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 8, 8)
        self.warning_icon = open_image(PATH_IMAGE + "warning_icon.png", 15, 15)

        self.master = tk.Toplevel(background="white")
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        self.master.resizable(False, False)

        ###########################################################################
        # Project Widgets
        ###########################################################################
        # LabelFrame for Project Info
        self.project_labelframe = ttk.LabelFrame(self.master, text="Add New Project")
        self.project_labelframe.pack(fill='x', padx=10, pady=10)
        # TITLE
        self.project_title = tk.StringVar()
        self.project_title_label = ttk.Label(self.project_labelframe, text="Project Title *")
        self.project_title_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_title_entry = ttk.Entry(self.project_labelframe, width=50, textvariable=self.project_title)
        self.project_title_entry.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        # ID
        self.project_id = tk.StringVar()
        self.project_id_label = ttk.Label(self.project_labelframe, text="Project ID *")
        self.project_id_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.project_id_labelframe = ttk.Labelframe(self.project_labelframe, style="Hidden.TLabelframe")
        self.project_id_labelframe.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NW)
        self.project_id_entry = ttk.Entry(self.project_id_labelframe, width=50, textvariable=self.project_id,
                                            state='disabled')
        self.project_id_entry.pack(fill='x', anchor=tk.W)
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

        def enable_submit(*args):
            if self.project_id.get() != '':
                if self.project_id.get() in list(self.session.projects):
                    self.error_label = ttk.Label(self.project_id_labelframe, image=self.warning_icon,
                                                text="A Project with the same project_id already exists.\n"
                                                    "Please select an other ID.", style="Error.TLabel",
                                                compound='left')
                    self.error_label.pack(fill='x', anchor=tk.NW)
                    self.submit_btn.config(state='disabled')
                else:
                    try:
                        self.error_label.destroy()
                    except:
                        pass
                    self.submit_btn.config(state='normal')

            else:
                self.submit_btn.config(state='disabled')
        self.project_id.trace('w', enable_submit)

        #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        self.exit_btn = ttk.Button(self.master, text="Quit", command=lambda: self.master.destroy())
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit", state='disabled', command=self.create_new_project)
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

        # Mainloop
        self.master.mainloop()

    def create_new_project(self):

        result = messagebox.askyesno("XNAT-PIC Uploader", "A new project will be created. Are you sure?")
        if result is False:
            self.master.deiconify()
            return
        # try:
        #     project = self.session.classes.ProjectData(
        #                     name=self.project_id.get(), parent=self.session)
        # except exception as e:
        #     messagebox.showerror("Error!", str(e))
        
        # self.session.clearcache()
        messagebox.showinfo('XNAT-PIC Uploader', 'A new project is created.')
        self.master.destroy()
        self.master.quit()

class SubjectManager():

    def __init__(self, session):

        self.session = session
        # Load icons
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 8, 8)
        self.warning_icon = open_image(PATH_IMAGE + "warning_icon.png", 15, 15)

        self.master = tk.Toplevel(background="white")
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        self.master.resizable(False, False)

        ###########################################################################
        # Subject Widgets
        ###########################################################################
        # LabelFrame for Subject Info
        self.subject_labelframe = ttk.LabelFrame(self.master, text="Subject Info")
        self.subject_labelframe.pack(fill='x', padx=10, pady=10)

        # Parent Project
        self.parent_project = tk.StringVar()
        self.list_of_projects = list(self.session.projects)
        self.parent_project_label = ttk.Label(self.subject_labelframe, text="Parent Project *")
        self.parent_project_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_project_menu = ttk.OptionMenu(self.subject_labelframe, self.parent_project, 0, *self.list_of_projects)
        self.parent_project_menu.config(width=45)
        self.parent_project_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Subject ID
        self.subject_id = tk.StringVar()
        self.subject_id_label = ttk.Label(self.subject_labelframe, text="Subject ID *")
        self.subject_id_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_id_labelframe = ttk.Labelframe(self.subject_labelframe, style="Hidden.TLabelframe")
        self.subject_id_labelframe.grid(row=1, column=1, padx=5, pady=5, sticky=tk.NW)
        self.subject_id_entry = ttk.Entry(self.subject_id_labelframe, width=50, 
                                        textvariable=self.subject_id, state='disabled')
        self.subject_id_entry.pack(fill='x', anchor=tk.NW)

        def enable_subject_id(*args):
            if self.parent_project.get() != '':
                enable_buttons([self.subject_id_entry])
            else:
                disable_buttons([self.subject_id_entry])
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
                self.subject_age.set("")
            else:
                pass
        self.subject_age.trace('w', check_date)

        # Subject Weight
        self.subject_weight = tk.StringVar()
        self.subject_weight.unit = tk.StringVar()
        self.subject_weight_label = ttk.Label(self.subject_labelframe, text="Weight")
        self.subject_weight_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.W)
        self.subject_weight_entry = ttk.Entry(self.subject_labelframe, width=50, textvariable=self.subject_weight)
        self.subject_weight_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        units = ["Kg", "hg", "g", "mg"]
        self.subject_weight_menu = ttk.OptionMenu(self.subject_labelframe, self.subject_weight.unit, units[2], *units)
        self.subject_weight_menu.grid(row=4, column=3, padx=5, pady=5, sticky=tk.W)

        # Subject Notes
        self.subject_description = tk.StringVar()
        self.subject_description_label = ttk.Label(self.subject_labelframe, text="Notes")
        self.subject_description_label.grid(row=5, column=0, padx=5, pady=5, sticky=tk.NW)
        self.subject_description_entry = ttk.Text(self.subject_labelframe, width=50, height=8)
        self.subject_description_entry.grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)
        self.subject_description_scrollbar = ttk.Scrollbar(self.subject_labelframe, orient='vertical', 
                                                        command=self.subject_description_entry.yview)
        self.subject_description_scrollbar.grid(row=5, column=2, padx=0, pady=5, sticky=tk.NS)
        self.subject_description_entry.configure(yscrollcommand=self.subject_description_scrollbar.set)

        self.error = tk.StringVar()

        def enable_submit(*args):
            if self.parent_project.get() != '' and self.subject_id.get() != '':
                if self.subject_id.get() in list(self.session.projects[self.parent_project.get()].subjects.key_map.keys()):
                    if self.error.get() == '':
                        self.error.set('Error')
                        self.error.label = ttk.Label(self.subject_id_labelframe, image=self.warning_icon,
                                                    text="A Subject with the same subject_id within "+ str(self.parent_project.get()) + 
                                                    " project\nalready exists. "
                                                    "Please select an other ID.", style="Error.TLabel",
                                                    compound='left')
                        self.error.label.pack(fill='x', anchor=tk.NW)
                        self.submit_btn.config(state='disabled')
                else:
                    try:
                        self.error.set("")
                        self.error.label.destroy()
                    except:
                        pass
                    self.submit_btn.config(state='normal')
            else:
                self.submit_btn.config(state='disabled')
        self.subject_id.trace('w', enable_submit)

        #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        self.exit_btn = ttk.Button(self.master, text="Quit", command=lambda: self.master.destroy())
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit", state='disabled', command=self.create_new_subject)
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

        # Mainloop
        self.master.mainloop()

    def create_new_subject(self):

        result = messagebox.askyesno("XNAT-PIC Uploader", "A new subject will be created. Are you sure?")
        if result is False:
            self.master.deiconify()
            return
        # try:
        #     project = self.session.projects[self.project_id.get()]
        # except:
        #     project = self.session.classes.ProjectData(
        #                     name=self.project_id.get(), parent=self.session)
        #     self.session.clearcache()

        # subject = self.session.classes.SubjectData(
        #                     parent=project, label=self.subject_id.get())
        # self.session.clearcache()
        messagebox.showinfo('XNAT-PIC Uploader', 'A new subject is created.') 
        self.master.destroy()
        self.master.quit()

class ExperimentManager():

    def __init__(self, session):

        self.session = session
        # Load icons
        self.logo_delete = open_image(PATH_IMAGE + "Reject.png", 8, 8)
        self.warning_icon = open_image(PATH_IMAGE + "warning_icon.png", 15, 15)

        self.master = tk.Toplevel(background="white")
        self.master.title("XNAT-PIC Uploader")
        self.master.geometry("+%d+%d" % (300, 250))
        self.master.resizable(False, False)

        ###########################################################################
        # Experiment Widgets
        ###########################################################################

        # LabelFrame for Experiment Info
        self.experiment_labelframe = ttk.LabelFrame(self.master, text="Experiment Info")
        self.experiment_labelframe.pack(fill='x', padx=10, pady=10)

        # Parent Project
        self.parent_project = tk.StringVar()
        self.list_of_projects = list(self.session.projects)
        self.parent_project_label = ttk.Label(self.experiment_labelframe, text="Parent Project *")
        self.parent_project_label.grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_project_menu = ttk.OptionMenu(self.experiment_labelframe, self.parent_project, '--', *self.list_of_projects)
        self.parent_project_menu.config(width=45)
        self.parent_project_menu.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)

        # Parent Subject
        self.parent_subject = tk.StringVar()
        if self.parent_project.get() != '--':
            self.list_of_subjects = list(self.session.projects[self.parent_project.get()].subjects.key_map.keys())
        else:
            self.list_of_subjects = []
        self.parent_subject_label = ttk.Label(self.experiment_labelframe, text="Parent Subject *")
        self.parent_subject_label.grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
        self.parent_subject_menu = ttk.OptionMenu(self.experiment_labelframe, self.parent_subject, '--', *self.list_of_subjects)
        self.parent_subject_menu.config(width=45)
        self.parent_subject_menu.grid(row=1, column=1, padx=5, pady=5, sticky=tk.W)

        def get_subject_list(*args):
            if self.parent_project.get() != '--' and self.parent_project.get() in self.list_of_projects:
                self.list_of_subjects = list(self.session.projects[self.parent_project.get()].subjects.key_map.keys())
            else:
                self.list_of_subjects = []
            self.parent_subject.set('--')
            self.parent_subject_menu['menu'].delete(0, 'end')
            for key in self.list_of_subjects:
                self.parent_subject_menu['menu'].add_command(label=key, command=lambda var=key:self.parent_subject.set(var))
        self.parent_project.trace('w', get_subject_list)

        # Experiment ID
        self.experiment_id = tk.StringVar()
        self.experiment_id_label = ttk.Label(self.experiment_labelframe, text="Experiment ID *")
        self.experiment_id_label.grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
        self.experiment_id_labelframe = ttk.Labelframe(self.experiment_labelframe, style="Hidden.TLabelframe")
        self.experiment_id_labelframe.grid(row=2, column=1, padx=5, pady=5, sticky=tk.NW)
        self.experiment_id_entry = ttk.Entry(self.experiment_id_labelframe, width=50, textvariable=self.experiment_id, state='disabled')
        self.experiment_id_entry.pack(fill='x', anchor=tk.NW)

        def enable_exp_id(*args):
            if self.parent_project.get() != '' and self.parent_subject.get() != '' and self.parent_subject.get() != '--':
                self.experiment_id_entry.config(state='normal')
            else:
                self.experiment_id_entry.config(state='disabled')
        self.parent_subject.trace('w', enable_exp_id)

        # Experiment Acquisition Date
        today = date.today()
        today = today.strftime("%d/%m/%Y")
        self.experiment_date = tk.StringVar()
        self.experiment_date.set(today)
        self.experiment_date_label = ttk.Label(self.experiment_labelframe, text="Age")
        self.experiment_date_label.grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
        self.experiment_date_entry = ttk.DateEntry(self.experiment_labelframe)
        self.experiment_date_entry.entry.config(textvariable=self.experiment_date)
        self.experiment_date_entry.grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

        def check_date(*args):
            if self.experiment_date.get() > today:
                self.experiment_date.set(today)
            else:
                pass
        self.experiment_date.trace('w', check_date)

        # Experiment Notes
        self.experiment_description = tk.StringVar()
        self.experiment_description_label = ttk.Label(self.experiment_labelframe, text="Notes")
        self.experiment_description_label.grid(row=4, column=0, padx=5, pady=5, sticky=tk.NW)
        self.experiment_description_entry = ttk.Text(self.experiment_labelframe, width=50, height=8)
        self.experiment_description_entry.grid(row=4, column=1, padx=5, pady=5, sticky=tk.W)
        self.experiment_description_scrollbar = ttk.Scrollbar(self.experiment_labelframe, orient='vertical', 
                                                        command=self.experiment_description_entry.yview)
        self.experiment_description_scrollbar.grid(row=4, column=2, padx=0, pady=5, sticky=tk.NS)
        self.experiment_description_entry.configure(yscrollcommand=self.experiment_description_scrollbar.set)

        self.error = tk.StringVar()

        def enable_submit(*args):
            if self.parent_project.get() != '' and self.parent_subject.get() != '' and self.experiment_id.get() != '':
                if self.experiment_id.get() in list(self.session.projects[self.parent_project.get()].subjects[self.parent_subject.get()].experiments.key_map.keys()):
                    if self.error.get() == "":
                        self.error.set("Error")
                        self.error.label = ttk.Label(self.experiment_id_labelframe, image=self.warning_icon,
                                                    text="An Experiment with the same experiment_id within "+ str(self.parent_subject.get()) + 
                                                    " subject\nalready exists. Please select an other ID.", style="Error.TLabel",
                                                    compound='left')
                        self.error.label.pack(fill='x', anchor=tk.NW)
                        self.submit_btn.config(state='disabled')
                else:
                    try:
                        self.error.set("")
                        self.error.label.destroy()
                    except:
                        pass
                    self.submit_btn.config(state='normal')
            else:
                self.submit_btn.config(state='disabled')
        self.experiment_id.trace('w', enable_submit)

        #################################################################################
        # Bottom Button
        #################################################################################
        # Exit Button
        self.exit_btn = ttk.Button(self.master, text="Quit", command=lambda: self.master.destroy())
        self.exit_btn.pack(side='left', padx=25, pady=10, anchor=tk.NW)
        # Submit Button
        self.submit_btn = ttk.Button(self.master, text="Submit", state='disabled', command=self.create_new_experiment)
        self.submit_btn.pack(side='right', padx=25, pady=10, anchor=tk.NE)

        # Mainloop
        self.master.mainloop()

    def create_new_experiment(self):

        result = messagebox.askyesno("XNAT-PIC Uploader", "A new experiment will be created. Are you sure?")
        if result is False:
            self.master.deiconify()
            return
        # try:
        #     project = self.session.projects[self.project_id.get()]
        #     subject = project.subjects[self.subject_id.get()]
        # except:
        #     project = self.session.classes.ProjectData(
        #                     name=self.project_id.get(), parent=self.session)
        #     self.session.clearcache()
        #     subject = self.session.classes.SubjectData(
        #                     parent=project, label=self.subject_id.get())

        # experiment = self.session.classes.ExperimentData(
        #                 parent=subject, label=self.experiment_id.get())
        # self.session.clearcache()
        messagebox.showinfo('XNAT-PIC Uploader', 'A new subject is created.') 
        self.master.destroy()
        self.master.quit()

# if __name__ == "__main__":

#     root = tk.Tk()
#     # object_creator = ObjectCreator(root).add_project_popup()
#     object_creator = ObjectCreator(root).add_subject_popup()