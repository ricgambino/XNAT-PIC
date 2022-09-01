# -*- coding: utf-8 -*-
"""
Created on 29-08-2022

@author: Gambino R.
"""

from datetime import datetime
import os
from glob import glob
import tkinter as tk
from tkinter.messagebox import NO
import ttkbootstrap as ttk
# from tkinter.filedialog import askdirectory
from read_visupars import read_visupars_parameters
from read_method import read_method_parameters
import pandas as pd
from dateutil.parser import parse
import pydicom
from cest_dict import codify_cest_dict
from pydicom import datadict


class FolderDetails():
    def __init__(self, main_dir):

        self.main_dir = main_dir

        # Initialize data dictionary
        self.data = {}

    def read_folder_details_raw_images(self):

        # Get the list of subfolders into main_dir
        self.list_of_dirs = os.listdir(self.main_dir)
        # Filter subfolder according by the presence of 2dseq file
        self.list_of_dirs = [x for x in self.list_of_dirs if glob(os.path.join(self.main_dir, x).replace("\\", "/") + '/**/2dseq', recursive=True) != []]
        # Sort subfolders according to folder name
        self.list_of_dirs.sort(key=float)

        for i, dir in enumerate(self.list_of_dirs):
            # Initialize dictionary key
            self.data[str(dir)] = {}
            self.data[str(dir)]["FolderName"] = str(dir)
            acqp_file = os.path.join(self.main_dir, dir, "acqp")
            with open(acqp_file, 'r'):
                acqp_content = read_visupars_parameters(acqp_file)

            self.data[str(dir)]["ProtocolName"] = acqp_content["ACQ_protocol_name"]
            self.data[str(dir)]["Method"] = acqp_content["ACQ_method"]
            self.data[str(dir)]["NSlices"] = acqp_content["NSLICES"]
            self.data[str(dir)]["SliceThickness[mm]"] = acqp_content["ACQ_slice_thick"]

            visu_file = os.path.join(self.main_dir, dir, "visu_pars")
            if not os.path.exists(visu_file):
                visu_file = glob(os.path.join(self.main_dir, dir).replace("\\", "/") + '/**/visu_pars', recursive=True)[0]
            with open(visu_file, 'r'):
                visu_content = read_visupars_parameters(visu_file)

            if "VisuAcqSize" in visu_content.keys():
                if isinstance(visu_content["VisuAcqSize"], (int, float)) == False:
                    self.data[str(dir)]["MatrixSize"] = str(int(visu_content["VisuAcqSize"][0])) + "x" + str(int(visu_content["VisuAcqSize"][1]))
                else:
                    self.data[str(dir)]["MatrixSize"] = int(visu_content["VisuAcqSize"])
            else:
                self.data[str(dir)]["MatrixSize"] = None

            if "VisuInstanceModality" in visu_content.keys():
                self.data[str(dir)]["InstanceModality"] = visu_content["VisuInstanceModality"]
            else:
                self.data[str(dir)]["InstanceModality"] = ""

            if "VisuAcqDate" in visu_content.keys():
                if isinstance(visu_content["VisuAcqDate"], str):
                    dt = parse(visu_content["VisuAcqDate"].replace("<", "").replace(">", ""))
                    self.data[str(dir)]["AcquisitionDate"] = "/".join([str(dt.date()), str(dt.time())])
                else:
                    dt = visu_content["VisuAcqDate"]
                    self.data[str(dir)]["AcquisitionDate"] = "/".join([str(dt.date()), str(dt.time())])

            method_file = os.path.join(self.main_dir, dir, "method")
            with open(method_file, 'r'):
                method_content = read_method_parameters(method_file)

            if "PVM_SatTransPulse" in method_content.keys():
                self.data[str(dir)]["PulseLength[ms]"] = round(float(method_content.get("PVM_SatTransPulse")[0]), 2)
            else:
                self.data[str(dir)]["PulseLength[ms]"] = ""
            if "PVM_SatTransPulseAmpl_uT" in method_content.keys():
                self.data[str(dir)]["PulseAmplitude[uT]"] = round(float(method_content.get("PVM_SatTransPulseAmpl_uT")), 2)
            else:
                self.data[str(dir)]["PulseAmplitude[uT]"] = ""
            if "PVM_SatTransPulseLength2" in method_content.keys():
                self.data[str(dir)]["PulseLength2[ms]"] = round(float(method_content.get("PVM_SatTransPulseLength2"))/1000, 2)
            else:
                self.data[str(dir)]["PulseLength2[ms]"] = ""
            if "PVM_NSatFreq" in method_content.keys():
                self.data[str(dir)]["NSaturationFrequencies"] = int(method_content.get("PVM_NSatFreq"))
            else:
                self.data[str(dir)]["NSaturationFrequencies"] = ""

        # Transform dictionary into Dataframe
        self.pd_data = pd.DataFrame.from_dict(self.data, orient="index")
        # Sort dataframe according to folder name
        self.pd_data.sort_values("FolderName")

    def read_folder_details_dcm_images(self):

        # Get the list of subfolders into main_dir
        self.list_of_dirs = os.listdir(os.path.join(self.main_dir, "MR").replace("\\", "/"))
        # Filter subfolder according by the presence of 2dseq file
        self.list_of_dirs = [x for x in self.list_of_dirs if glob(os.path.join(self.main_dir, "MR", x).replace("\\", "/") + '/*.dcm', recursive=False) != []]
        # Sort subfolders according to folder name
        self.list_of_dirs.sort(key=float)

        for i, dir in enumerate(self.list_of_dirs):
            # Initialize dictionary key
            self.data[str(dir)] = {}
            self.data[str(dir)]["FolderName"] = str(dir)

            current_dir = os.path.join(self.main_dir, "MR",  dir)
            dcm_file = glob(current_dir + "/*.dcm", recursive=False)[0]

            dataset = pydicom.dcmread(dcm_file)
            print(dataset[0x10610010].value)
            codify_cest_dict(dataset[0x10610010].value)
            for k,v in datadict.DicomDictionary.items():
                print(k,v)
            description = dataset[0x10611005].description
            print(description)
            self.data[str(dir)]["ProtocolName"] = dataset.ProtocolName
            self.data[str(dir)]["Method"] = dataset.SequenceName.replace(" ", "")
            self.data[str(dir)]["NSlices"] = dataset.NumberOfSlices
            self.data[str(dir)]["SliceThickness[mm]"] = dataset.SliceThickness
            # self.data[str(dir)]["MatrixSize"] = str(int(dataset.AcquisitionMatrix[1])) + "x" + str(int(dataset.AcquisitionMatrix[2]))
            self.data[str(dir)]["MatrixSize"] = list(dataset.AcquisitionMatrix)
            self.data[str(dir)]["InstanceModality"] = dataset.Modality
            self.data[str(dir)]["AcquisitionDate"] = datetime.strftime(datetime.strptime(dataset.AcquisitionDate, "%Y%m%d"), "%d/%m/%Y")
            if "Pulse Length (ms)" in dataset[0x10611005].description:
                self.data[str(dir)]["PulseLength[ms]"] = dataset.PulseLength
            if hasattr(dataset, "PulseAmplitude"):
                self.data[str(dir)]["PulseAmplitude[uT]"] = dataset.PulseAmplitude
            if hasattr(dataset, "PulseLength2"):
                self.data[str(dir)]["PulseLength2[ms]"] = dataset.PulseLength2
            if hasattr(dataset, "NumberOfFrequencies"):
                self.data[str(dir)]["NSaturationFrequencies"] = dataset.NumberOfFrequencies
        # Transform dictionary into Dataframe
        self.pd_data = pd.DataFrame.from_dict(self.data, orient="index")
        # Sort dataframe according to folder name
        self.pd_data.sort_values("FolderName")

    def save_folder_details(self):

        # Save details into the main folder
        with open(self.main_dir + "/Content.txt", "w+") as out_file:
            string_pd_data = self.pd_data.to_string(header=True, index=False, justify='center')
            out_file.write(string_pd_data)

    def show_folder_details(self, root):

        self.popup = tk.Toplevel(root)
        self.popup.geometry("+%d+%d" % (300, 400))
        widths = [100, 200, 100, 100, 120, 100, 120, 180, 120, 120, 120, 100]
        tree = ttk.Treeview(self.popup)
        scrollbar = ttk.Scrollbar(self.popup, orient='vertical', command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        columns = [x for x in self.pd_data.columns]
        tree['columns'] = [x for x in self.pd_data.columns]
        tree.column("#0", width=0, stretch=NO)
        tree.heading("#0", text="", anchor=tk.CENTER)
        for k, col in enumerate(columns):
            tree.column(col, anchor=tk.CENTER, width=widths[k])
            tree.heading(col, text=col, anchor=tk.CENTER)

        for i in range(self.pd_data.shape[0]):
            tree.insert(parent='', index='end', iid=i, text='', 
                        values=list(self.pd_data.values[i]))
        tree.pack(side='left')
        scrollbar.pack(side='right', fill='y')
        # close_btn = ttk.Button(self.popup, text='Close', command=self.popup.destroy)
        # close_btn.pack(pady=10)


# if __name__ == "__main__":

#     root = tk.Tk()
#     # Define the main directory
#     main_dir = askdirectory(parent=root, title="Select experiment directory")
#     data, dir = read_folder_details(main_dir)
#     save_folder_details(data, dir)
#     show_folder_details(root, data)
#     root.mainloop()