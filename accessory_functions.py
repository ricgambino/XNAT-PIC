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
        for n, level1 in enumerate(os.listdir(path)):
            if os.path.isfile(os.path.join(path, level1)):
                total_weight += os.path.getsize(os.path.join(path, level1))
            elif os.path.isdir(os.path.join(path, level1)):
                for m, level2 in enumerate(os.listdir(os.path.join(path, level1))):
                    if os.path.isfile(os.path.join(path, level1, level2)):
                        total_weight += os.path.getsize(os.path.join(path, level1, level2))
                    elif os.path.isdir(os.path.join(path, level1, level2)):
                        for m, level3 in enumerate(os.listdir(os.path.join(path, level1, level2))):
                            if os.path.isfile(os.path.join(path, level1, level2, level3)):
                                total_weight += os.path.getsize(os.path.join(path, level1, level2, level3))

        return int(total_weight)
    else:
        return 0
