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