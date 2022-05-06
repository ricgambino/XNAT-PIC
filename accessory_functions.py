import os
import pandas as pd
from tabulate import tabulate

# Accessory functions
def disable_buttons(list_of_buttons):
    for btn in list_of_buttons:
        try:
            btn.configure(state="disabled")
        except:
            pass

def enable_buttons(list_of_buttons):
    for btn in list_of_buttons:
        try:
            btn.configure(state="normal")
        except:
            pass

def destroy_widgets(widgets):
    for widget in widgets:
        try:
            widget.destroy()
        except:
            pass

def delete_widgets(canva, widgets_id):
    for id in widgets_id:
        try:
            canva.delete(id)
        except:
            pass

def get_dir_size(path):

    total_weight = 0
    if os.path.isdir(path):
        for l, level1 in enumerate(os.listdir(path)):
            if os.path.isfile(os.path.join(path, level1)):
                total_weight += os.path.getsize(os.path.join(path, level1))
            elif os.path.isdir(os.path.join(path, level1)):
                for m, level2 in enumerate(os.listdir(os.path.join(path, level1))):
                    if os.path.isfile(os.path.join(path, level1, level2)):
                        total_weight += os.path.getsize(os.path.join(path, level1, level2))
                    elif os.path.isdir(os.path.join(path, level1, level2)):
                        for n, level3 in enumerate(os.listdir(os.path.join(path, level1, level2))):
                            if os.path.isfile(os.path.join(path, level1, level2, level3)):
                                total_weight += os.path.getsize(os.path.join(path, level1, level2, level3))
                            elif os.path.isdir(os.path.join(path, level1, level2, level3)):
                                for p, level4 in enumerate(os.listdir(os.path.join(path, level1, level2, level3))):
                                    if os.path.isfile(os.path.join(path, level1, level2, level3, level4)):
                                        total_weight += os.path.getsize(os.path.join(path, level1, level2, level3, level4))
                            #         elif os.path.isdir(os.path.join(path, level1, level2, level3,level4)):
                            #             for q, level5 in enumerate(os.listdir(os.path.join(path, level1, level2, level3, level4))):
                            #                 if os.path.isfile(os.path.join(path, level1, level2, level3, level4, level5)):
                            #                     total_weight += os.path.getsize(os.path.join(path, level1, level2, level3, level4, level5))
                            #                 elif os.path.isdir(os.path.join(path, level1, level2, level3,level4, level5)):
                            #                     for q, level6 in enumerate(os.listdir(os.path.join(path, level1, level2, level3, level4, level5))):
                            #                         if os.path.isfile(os.path.join(path, level1, level2, level3, level4, level5, level6)):
                            #                             total_weight += os.path.getsize(os.path.join(path, level1, level2, level3, level4, level5, level6))


        return round(total_weight, 2)
    else:
        return 0

def read_table(path_to_read):

    data_dict = {}
    data = pd.read_table(path_to_read, delimiter='\s\s+', header=[0], skiprows=1,
        dtype={'Variable': str}, engine='python').values.tolist()
    for elem in data:
        data_dict[elem[0]] = elem[1]
    return data_dict

def write_table(path_to_write, edit, info=[]):

    try:
        # If there is already a file, edit it
        data = read_table(path_to_write)
        for j in edit.keys():
            for k in data.keys():
                if j == k:
                    data[k] = edit[j]
        with open(path_to_write.replace('\\', '/'), 'w+') as out_file:
            out_file.write(tabulate(data.items(), headers=['Variable', 'Value']))
    except:
        # If the file does not exist yet
        with open(path_to_write.replace('\\', '/'), 'w+') as out_file:
            out_file.write(tabulate(info.items(), headers=['Variable', 'Value']))
            out_file.write(tabulate(edit.items()))
