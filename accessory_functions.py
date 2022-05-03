import os
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
