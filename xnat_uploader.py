# -*- coding: utf-8 -*-
"""
Created on Dec 7, 2021

@author: Riccardo Gambino

"""
from numpy import empty
import pandas as pd
import os
from tkinter import messagebox
import xnat, shutil, time
from multiprocessing import Pool, cpu_count

def read_table(path_to_read):

    data_dict = {}
    data = pd.read_table(path_to_read, delimiter='\s\s+', header=[0], skiprows=1,
        dtype={'Variable': str}, engine='python').values.tolist()
    for elem in data:
        data_dict[elem[0]] = elem[1]
    return data_dict


class Dicom2XnatUploader():

    def __init__(self, session):

        self.session = session
        self.n_processes = int(cpu_count() - 1)

    def multi_core_upload(self, folder_to_upload, project_id):

        list_dirs = os.listdir(folder_to_upload)
        list_of_subjects = [(os.path.join(folder_to_upload, sub).replace('\\', '/'), project_id) for sub in list_dirs]

        start_time = time.time()

        with Pool(processes = self.n_processes) as pool:
            pool.map(self.uploader, list_of_subjects)

        end_time = time.time()
        print('Elapsed time for conversion: ' + str(end_time - start_time) + ' s')

    def single_core_upload(self, folder_to_upload, project_id, master):

        list_dirs = os.listdir(folder_to_upload)
        list_of_subjects = [(os.path.join(folder_to_upload, sub).replace('\\', '/'), project_id) for sub in list_dirs]

        start_time = time.time()

        for sub in list_of_subjects:
            self.uploader(sub)

        end_time = time.time()
        print('Elapsed time for conversion: ' + str(end_time - start_time) + ' s')

    def uploader(self, args, master):

        folder_to_upload = args[0]
        project_id = args[1]

        print('Uploading ' + str(folder_to_upload.split('/')[-1]) + ' to ' + str(project_id))

        # Check if 'MR' folder is already into the folder_to_upload path
        if 'MR' != os.path.basename(folder_to_upload):
            folder_to_upload = os.path.join(folder_to_upload, 'MR').replace('\\', '/')
        else:
            folder_to_upload = folder_to_upload.replace('\\', '/')
        flag = 0
        # Check for existing custom variables file
        try:
            subject_data = read_table('/'.join([folder_to_upload, 'Custom_Variables.txt']))
            # Define the subject_id and the experiment_id
            subject_id = subject_data['Subject']
            experiment_id = '_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_')
            flag = 1
        except Exception as error:
            # messagebox.showinfo("DICOM Uploader", "Custom Variables are not available in this folder " + str(folder_to_upload))
            # Define the subject_id and the experiment_id   
            subject_id = folder_to_upload.split('/')[-2].replace('_dcm', '')
            experiment_id = '_'.join([folder_to_upload.split('/')[-3].replace('_dcm', ''), folder_to_upload.split('/')[-2].replace('_dcm', '')]).replace(' ', '_')
            flag = 0 

        project = self.session.classes.ProjectData(
                                        name=project_id, parent=self.session)
        subject = self.session.classes.SubjectData(
                                        parent=project, label=subject_id)

        if experiment_id in subject.experiments.key_map.keys():
            # ALERT! That patient already exists!
            answer = messagebox.askyesno("XNAT-PIC - Uploader", "A patient with the same experiment_id already exists. Do you want to upload it anyway?")
            
            if answer is False:
                return

        start_time = time.time()

        try:
            zip_dst = shutil.make_archive(folder_to_upload.split('/')[-2], "zip", folder_to_upload) # .zip file of the current subfolder
            with xnat.connect(server=self.session._original_uri, jsession=self.session._jsession, cli=True, logger=self.session.logger) as connection:
                connection.services.import_(zip_dst,
                                        overwrite="delete", # Overwrite parameter is important!
                                        project=project_id,
                                        subject=subject_id,
                                        experiment=experiment_id,
                                        content_type='application/zip')

                experiment = project.subjects[subject_id].experiments[experiment_id]
                
                if flag == 1:
                    for var in subject_data.keys():
                        if subject_data[var] == '':
                            continue
                        if var == 'Project' or var == 'Subject':
                            subject.fields[var] = subject_data[var]
                            experiment.fields[var] = subject_data[var]
                        else:
                            experiment.fields[var] = subject_data[var]

            os.remove(zip_dst)
            if master.add_file_flag == 1:
                for sub_dir in os.listdir(folder_to_upload):
                    if 'Results' in sub_dir:
                        params = {}
                        params['project_id'] = project_id
                        params['subject_id'] = subject_id
                        params['experiment_id'] = experiment_id
                        self.multi_file_uploader(os.path.join(folder_to_upload, sub_dir), params)

        except Exception as e: 
            messagebox.showerror("XNAT-PIC - Uploader", e)
            try:
                connection.disconnect()
                os.remove(zip_dst)
            except:
                os.remove(zip_dst)
  
        end_time = time.time()
        print('Elapsed time: ' + str(end_time - start_time) + ' seconds')

    def multi_file_uploader(self, folder_to_upload, params):

        print('Loading additional files for subject: ' + str(params['subject_id']))

        files = os.scandir(folder_to_upload)

        for i, file in enumerate(files, 1):
            if file.is_file():
                if file.name.endswith(('.png', '.jpg', '.jpeg', '.tiff', '.mat', '.fig', '.pdf', '.xlsx')):
                    current_path_file = os.path.join(folder_to_upload, file).replace('\\', '/')
                    self.file_uploader(current_path_file, params)

    def file_uploader(self, file_to_upload, params):

        test_project = self.session.projects[params['project_id']]
        test_subjects = test_project.subjects[params['subject_id']]
        test_exp = test_subjects.experiments[params['experiment_id']]
        test_resources = test_exp.resources

        file_to_upload = file_to_upload.replace('\\', '/')
        with open(file_to_upload, 'rb') as f:
            img = f.read()
        image = {"1": img}
        try:
            with xnat.connect(server=self.session._original_uri, jsession=self.session._jsession, cli=True, logger=self.session.logger) as connection:
                connection.put(path=test_resources.uri + '/Additional_Files/files/' + str(file_to_upload.split('/')[-1]), files=image)
        except Exception as e:
            messagebox.showerror("XNAT-PIC - Uploader", e)


    
