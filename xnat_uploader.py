# -*- coding: utf-8 -*-
"""
Created on Dec 7, 2021

@author: Riccardo Gambino

"""
import pandas as pd
import os
from tkinter import messagebox
import xnat, shutil, time

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

    def upload(self, folder_to_upload, project_id):

        # Check if 'MR' folder is already into the folder_to_upload path
        if 'MR' != os.path.basename(folder_to_upload):
            folder_to_upload = os.path.join(folder_to_upload, 'MR').replace('\\', '/')
        else:
            folder_to_upload = folder_to_upload.replace('\\', '/')

        # Check for existing file!!!
        subject_data = read_table('/'.join([folder_to_upload, 'Custom_Variables.txt']))

        subject_id = subject_data['Subject']
        experiment_id = '_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_')

        project = self.session.classes.ProjectData(
                                        name=project_id, parent=self.session)
        subject = self.session.classes.SubjectData(
                                        parent=project, label=subject_id)

        if experiment_id in subject.experiments.key_map.keys():
        # ALERT! That patient already exists!
            answer = messagebox.askyesno("XNAT-PIC Uploader", "A patient with the same experiment_id already exists. Do you want to upload it anyway?")
            
            if answer is False:
                return

        start_time = time.time()

        zip_dst = shutil.make_archive(folder_to_upload.split('/')[-2], "zip", folder_to_upload) # .zip file of the current subfolder

        with xnat.connect(server=self.session._original_uri, jsession=self.session._jsession, cli=True, logger=self.session.logger) as connection:
            connection.services.import_(zip_dst,
                                    overwrite="delete", # Overwrite parameter is important!
                                    project=project_id,
                                    subject=subject_id,
                                    experiment=experiment_id,
                                    content_type='application/zip')

            experiment = project.subjects[subject_id].experiments[experiment_id]
            
            for var in subject_data.keys():
                # Check for empty custom variables!!!
                if var == 'Project' or var == 'Subject':
                    subject.fields[var] = subject_data[var]
                    experiment.fields[var] = subject_data[var]
                else:
                    experiment.fields[var] = subject_data[var]

        os.remove(zip_dst)

        end_time = time.time()
        print('Elapsed time: ' + str(end_time - start_time) + ' seconds')
