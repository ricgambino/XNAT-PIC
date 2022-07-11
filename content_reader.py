import os
from glob import glob
import tkinter as tk
from tkinter.messagebox import NO
import ttkbootstrap as ttk
from tkinter.filedialog import askdirectory
from read_visupars import read_visupars_parameters
from read_method import read_method_parameters
import pandas as pd
from dateutil.parser import parse

def read_folder_details(main_dir):

    # Initialize data dictionary
    data = {}
    # Get the list of subfolders into main_dir
    list_of_dirs = os.listdir(main_dir)
    # Filter subfolder according by the presence of 2dseq file
    list_of_dirs = [x for x in list_of_dirs if glob(os.path.join(main_dir, x).replace("\\", "/") + '/**/2dseq', recursive=True) != []]
    # Sort subfolders according to folder name
    list_of_dirs.sort(key=float)

    for i, dir in enumerate(list_of_dirs):
        # Initialize dictionary key
        data[str(dir)] = {}
        data[str(dir)]["FolderName"] = str(dir)
        acqp_file = os.path.join(main_dir, dir, "acqp")
        with open(acqp_file, 'r'):
            acqp_content = read_visupars_parameters(acqp_file)

        data[str(dir)]["ProtocolName"] = acqp_content["ACQ_protocol_name"]
        data[str(dir)]["Method"] = acqp_content["ACQ_method"]
        data[str(dir)]["NSlices"] = acqp_content["NSLICES"]
        data[str(dir)]["SliceThickness[mm]"] = acqp_content["ACQ_slice_thick"]

        visu_file = os.path.join(main_dir, dir, "visu_pars")
        if not os.path.exists(visu_file):
            visu_file = glob(os.path.join(main_dir, dir).replace("\\", "/") + '/**/visu_pars', recursive=True)[0]
        with open(visu_file, 'r'):
            visu_content = read_visupars_parameters(visu_file)

        if "VisuAcqSize" in visu_content.keys():
            if isinstance(visu_content["VisuAcqSize"], (int, float)) == False:
                data[str(dir)]["MatrixSize"] = str(int(visu_content["VisuAcqSize"][0])) + "x" + str(int(visu_content["VisuAcqSize"][1]))
            else:
                data[str(dir)]["MatrixSize"] = int(visu_content["VisuAcqSize"])
        else:
            data[str(dir)]["MatrixSize"] = None

        if "VisuInstanceModality" in visu_content.keys():
            data[str(dir)]["InstanceModality"] = visu_content["VisuInstanceModality"]
        else:
            data[str(dir)]["InstanceModality"] = ""

        if "VisuAcqDate" in visu_content.keys():
            if isinstance(visu_content["VisuAcqDate"], str):
                dt = parse(visu_content["VisuAcqDate"].replace("<", "").replace(">", ""))
                data[str(dir)]["AcquisitionDate"] = "/".join([str(dt.date()), str(dt.time())])
            else:
                dt = visu_content["VisuAcqDate"]
                data[str(dir)]["AcquisitionDate"] = "/".join([str(dt.date()), str(dt.time())])

        method_file = os.path.join(main_dir, dir, "method")
        with open(method_file, 'r'):
            method_content = read_method_parameters(method_file)

        if "PVM_SatTransPulse" in method_content.keys():
            data[str(dir)]["PulseLength[ms]"] = round(float(method_content.get("PVM_SatTransPulse")[0]), 2)
        else:
            data[str(dir)]["PulseLength[ms]"] = ""
        if "PVM_SatTransPulseAmpl_uT" in method_content.keys():
            data[str(dir)]["PulseAmplitude[uT]"] = round(float(method_content.get("PVM_SatTransPulseAmpl_uT")), 2)
        else:
            data[str(dir)]["PulseAmplitude[uT]"] = ""
        if "PVM_SatTransPulseLength2" in method_content.keys():
            data[str(dir)]["PulseLength2[ms]"] = round(float(method_content.get("PVM_SatTransPulseLength2"))/1000, 2)
        else:
            data[str(dir)]["PulseLength2[ms]"] = ""
        if "PVM_NSatFreq" in method_content.keys():
            data[str(dir)]["NSaturationFrequencies"] = int(method_content.get("PVM_NSatFreq"))
        else:
            data[str(dir)]["NSaturationFrequencies"] = ""

    # Transform dictionary into Dataframe
    pd_data = pd.DataFrame.from_dict(data, orient="index")
    # Sort dataframe according to folder name
    pd_data.sort_values("FolderName")
    
    return pd_data, main_dir

def save_folder_details(data, dir):

    # Save details into the main folder
    with open(dir + "/Content.txt", "w+") as out_file:
        string_pd_data = data.to_string(header=True, index=False, justify='center')
        out_file.write(string_pd_data)

def show_folder_details(root, data):

    popup = tk.Toplevel(root)
    widths = [100, 200, 100, 100, 120, 100, 120, 180, 120, 120, 120, 100]
    tree = ttk.Treeview(popup)
    columns = [x for x in data.columns]
    tree['columns'] = [x for x in data.columns]
    tree.column("#0", width=0, stretch=NO)
    tree.heading("#0", text="", anchor=tk.CENTER)
    for k, col in enumerate(columns):
        tree.column(col, anchor=tk.CENTER, width=widths[k])
        tree.heading(col, text=col, anchor=tk.CENTER)

    for i in range(data.shape[0]):
        tree.insert(parent='', index='end', iid=i, text='', 
                    values=list(data.values[i]))
    tree.pack()
    close_btn = ttk.Button(popup, text='Close', command=popup.destroy)
    close_btn.pack(pady=10)


if __name__ == "__main__":

    root = tk.Tk()
    # Define the main directory
    main_dir = askdirectory(parent=root, title="Select experiment directory")
    data, dir = read_folder_details(main_dir)
    save_folder_details(data, dir)
    show_folder_details(root, data)
    root.mainloop()