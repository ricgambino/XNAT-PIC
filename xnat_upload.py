# -*- coding: utf-8 -*-
"""
Created on Dec 7, 2021

@author: Riccardo Gambino

"""
import shutil, os
from threading import local
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


def xnat_uploader(folder_to_upload, project_id, num_cust_vars, address, user, psw, master):

    subject_id = '_'.join(os.path.basename(folder_to_upload).split('_')[:-1])

    # Check if 'MR' folder is already into the folder_to_upload path
    if 'MR' != os.path.basename(folder_to_upload):
        folder_to_upload = os.path.join(folder_to_upload, 'MR').replace('\\', '/')
    else:
        folder_to_upload = folder_to_upload.replace('\\', '/')
    
    # Check for directories into folder_to_upload path
    list_dirs = os.listdir(folder_to_upload)

    # # Check for resources folder
    # flag = 0
    # if 'resources' in list_dirs and os.path.isdir(os.path.join(folder_to_upload, 'resources').replace('\\', '/')):
    #     results_path = os.listdir(os.path.join(folder_to_upload, 'resources').replace('\\', '/'))
    #     if results_path!= []:
    #         results_ans = messagebox.askyesno(
    #         "Results",
    #         "Results folder found. Would you like to upload processed images to XNAT?"
    #     )
    #     if results_ans == True:
    #         flag = 1
    #     else:
    #         flag = 0

    master._inprogress("Upload in progress")

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
        if 'resources' in local_path:
            subpaths = os.listdir(local_path)
            local_path = os.path.join(local_path, subpaths[0]).replace('\\', '/')
        else:
            # Check for files into local path
            file_list = sorted(glob(local_path + '/*', recursive=True))
            for file in file_list:
                if file.endswith('.dcm'):
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

    master.progress.stop()

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