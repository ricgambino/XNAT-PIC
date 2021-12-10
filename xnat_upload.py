# -*- coding: utf-8 -*-
"""
Created on Dec 7, 2021

@author: Riccardo Gambino

"""
import shutil, os
import xnat
from glob import glob
from tkinter import messagebox
import re
import datetime
import pydicom
import sys
import traceback
import tkinter as tk
from tkinter import filedialog
from tqdm import tqdm


def xnat_uploader(folder_to_upload, project_id, num_cust_vars, address, user, psw):

    subject_id = '_'.join(os.path.basename(folder_to_upload).split('_')[:-1])

    # Check if 'MR' folder is already into the folder_to_upload path
    if 'MR' != os.path.basename(folder_to_upload):
        folder_to_upload = os.path.join(folder_to_upload, 'MR').replace('\\', '/')
    else:
        folder_to_upload = folder_to_upload.replace('\\', '/')
    
    # Check for directories into folder_to_upload path
    list_dirs = os.listdir(folder_to_upload)
    # Loop over directories
    for dir in tqdm(range(len(list_dirs))):
        # Manage custom variables
        folder_to_upload_elem = folder_to_upload.split('/')
        folder_to_upload_elem.pop() # The last element is dropped
        custom_vars = []
        custom_values = []
        for n in range(1, num_cust_vars + 1):
            custom_values.append(folder_to_upload_elem[-n])
            custom_vars.append(folder_to_upload_elem[-n])
        custom_vars = custom_vars[::-1]
        custom_values = custom_values[::-1] 

        # Get the complete local path of the folder
        local_path = os.path.join(folder_to_upload, list_dirs[dir]).replace('\\', '/')
        # Check for files into local path
        file_list = sorted(glob(local_path + '/*', recursive=True))
        for file in file_list:
            # progress_bar(file, len(file_list))
            # file_path = os.path.join(local_path, file).replace('\\', '/')
            file_path = file.replace('\\', '/')
            # Check for Date and Time of the study
            ds = pydicom.dcmread(file_path)
            if ds.StudyTime != '':
                # Case 1: Date and Time are explicited                         
                ds.StudyTime = ds.StudyTime.split('.',1)[0]
                ds.StudyTime = "_".join(ds.StudyTime.split('.'))
                ds.StudyDate = "_".join(ds.StudyDate.split('.'))
                if ds.StudyDate != "" and ds.StudyTime != "":
                    experiment_id = (
                        subject_id + "_" + ds.StudyDate + "_" + ds.StudyTime)
            else:
                # Case 2: Date and Time are not explicited, so those fields are filled with the current date and time
                experiment_id = (
                    subject_id
                    + "_"
                    + datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
                )
            # Add custom variables to experiment_id
            for var in custom_values:
                experiment_id += "_" + var
            
        try:
            ####################################################################################################
            # XNAT connection
            with xnat.connect(server=address, user=user, password=psw) as session:
                zip_dst = shutil.make_archive(subject_id, "zip", local_path) # .zip file of the current subfolder

                project = session.classes.ProjectData(name=project_id, parent=session)
                subject = session.classes.SubjectData(parent=project, label=subject_id)
                # Import data to XNAT
                session.services.import_(zip_dst,
                                        overwrite="delete", # Overwrite parameter is important!
                                        project=project_id,
                                        subject=subject_id,
                                        experiment=experiment_id,
                                        content_type='application/zip')
                subject = project.subjects[subject_id]
                exp = project.subjects[subject_id].experiments[experiment_id]

                # Fill custom variables fields
                for i, element in enumerate(custom_vars):
                    subject.fields[element] = custom_values[i]
                    exp.fields[element] = custom_values[i]
                    # print("custom values ",custom_values[i])
                os.remove(zip_dst) # Remove temporary .zip file
            # XNAT connection is closed automatically
            ####################################################################################################

        except Exception as e:
            messagebox.showerror("XNAT-PIC - Uploader", e)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_tb(exc_traceback)
            sys.exit(1)

    ########
    messagebox.showinfo("XNAT-PIC - Uploader", "DICOM images have been successfully imported to XNAT!")

    return