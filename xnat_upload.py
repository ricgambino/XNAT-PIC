# -*- coding: utf-8 -*-
"""
Created on Dec 7, 2021

@author: Riccardo Gambino

"""
from base64 import encode
from pydoc import cli
import shutil, os
from threading import local
from urllib import request
import xnat
from xnat import core
from glob import glob
from tkinter import messagebox
import sys
import traceback
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm
import pandas as pd

def read_table(path_to_custom_var_file):

    data_dict = {}
    data = pd.read_table(path_to_custom_var_file, delimiter='\s\s+', header=[0], skiprows=1,
        dtype={'Variable': str}, engine='python').values.tolist()
    for elem in data:
        data_dict[elem[0]] = elem[1]
    return data_dict


def xnat_uploader(folder_to_upload, project_id, num_cust_vars, address, user, psw, master):

    # READ FROM .TXT FILE INTO THE SUBJECT FOLDER
    subject_data = read_table('/'.join([folder_to_upload, 'Custom_Variables.txt']))

    subject_id = subject_data['Subject']
    experiment_id = '_'.join([subject_data['Project'], subject_data['Subject'], subject_data['Group'], subject_data['Timepoint']]).replace(' ', '_')
    
    # Check if 'MR' folder is already into the folder_to_upload path
    if 'MR' != os.path.basename(folder_to_upload):
        folder_to_upload = os.path.join(folder_to_upload, 'MR').replace('\\', '/')
    else:
        folder_to_upload = folder_to_upload.replace('\\', '/')

    try:
        flag = 0
        with xnat.connect(server=address, user=user, password=psw, default_timeout=30) as session:

            project = session.classes.ProjectData(
                                                name=project_id, parent=session)
            subject = session.classes.SubjectData(
                                                parent=project, label=subject_id)
            if experiment_id in subject.experiments.key_map.keys():
                # ALERT! That patient already exists!
                answer = messagebox.askyesno("XNAT-PIC Uploader", "A patient with the same experiment_id already exists. Do you want to upload it anyway?")
                if answer is False:
                    flag = 1
        if flag == 1:
            return

    except Exception as e:
                messagebox.showerror("XNAT-PIC - Uploader", e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)
                sys.exit(1)

    # Check for directories into folder_to_upload path
    list_dirs = os.listdir(folder_to_upload)

    try:
        with xnat.connect(server=address, user=user, password=psw) as session:

            project = session.classes.ProjectData(
                                                name=project_id, parent=session)
            subject = session.classes.SubjectData(
                                            parent=project, label=subject_id)
            subject.fields.clear()

            # Loop over directories
            for dir in tqdm(range(len(list_dirs))):

                # Get the complete local path of the folder
                local_path = os.path.join(folder_to_upload, list_dirs[dir]).replace('\\', '/')
                # if 'resources' in local_path:
                #     subpaths = os.listdir(local_path)
                #     local_path = os.path.join(local_path, subpaths[0]).replace('\\', '/')
        
                zip_dst = shutil.make_archive(local_path.split('/')[-1], "zip", local_path) # .zip file of the current subfolder

                session.services.import_(zip_dst,
                                        overwrite="delete", # Overwrite parameter is important!
                                        project=project_id,
                                        subject=subject_id,
                                        experiment=experiment_id,
                                        content_type='application/zip')

                experiment = subject.experiments[experiment_id]
                experiment.fields.clear()
                
                for var in subject_data.keys():
                    if var == 'AcquisitionDate' or var == 'Timepoint':
                        experiment.fields[var] = subject_data[var]
                    else:
                        experiment.fields[var] = subject_data[var]
                        subject.fields[var] = subject_data[var]
                    # print(var)
                os.remove(zip_dst)

    except Exception as e:
                messagebox.showerror("XNAT-PIC - Uploader", e)
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_tb(exc_traceback)
                sys.exit(1)

            # try:
            #     ####################################################################################################
            #     # XNAT connection
            #     with xnat.connect(server=address, user=user, password=psw) as session:

            #         zip_dst = shutil.make_archive(subject_id, "zip", local_path) # .zip file of the current subfolder
            #         project = session.classes.ProjectData(name=project_id, parent=session)
            #         subject = session.classes.SubjectData(parent=project, label=subject_id)
            #         # Import data to XNAT
            #         session.services.import_(zip_dst,
            #                                 overwrite="delete", # Overwrite parameter is important!
            #                                 project=project_id,
            #                                 subject=subject_id,
            #                                 experiment=experiment_id,
            #                                 content_type='application/zip')
            #         subject = project.subjects[subject_id]
            #         exp = project.subjects[subject_id].experiments[experiment_id]

            #         # Fill custom variables fields
            #         for i, element in enumerate(custom_vars):
            #             subject.fields[element] = custom_values[i]
            #             exp.fields[element] = custom_values[i]
            #             # print("custom values ",custom_values[i])
            #         os.remove(zip_dst) # Remove temporary .zip file
                    
            #     # XNAT connection is closed automatically
            #     ####################################################################################################

            # except Exception as e:
            #     messagebox.showerror("XNAT-PIC - Uploader", e)
            #     exc_type, exc_value, exc_traceback = sys.exc_info()
            #     traceback.print_tb(exc_traceback)
            #     sys.exit(1)


    ########
    messagebox.showinfo("XNAT-PIC - Uploader", "DICOM images have been successfully imported to XNAT!")

    # master.progress.stop()

    return

def upload_files_xnat(folder_to_upload, project_id, num_cust_vars, address, user, psw, master):

    with xnat.connect(address, user, psw) as session:
        test_project = session.projects[project_id]
        test_subjects = test_project.subjects['da_PyMT_5']
        test_exp = test_subjects.experiments['da_PyMT_5_20190327_134300']
        test_resources = test_exp.resources


    files = os.scandir(folder_to_upload)

    for file in enumerate(files, 1):
        if file.is_file():

            with xnat.connect(address, user=user, password=psw) as session:

                local_path = 'E:\\Desktop\\Riccardo\\Project\\Data\\InVivo\\da_PyMT_5_dcm\\MR\\resources\\Results_8_9_0.99\\8_9_deltaST_map_4.2_ppm.jpg'.replace('\\', '/')
                with open(local_path, 'rb') as f:
                    img = f.read()
                image = {"1": img}
                answer = session.put(path=test_resources.uri + '/Results/files/Im1.jpg', files=image)
                print('Done')
    return