from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk

PATH_IMAGE = "images\\"

class AzureStyle():

    def __init__(self):
    
        self.style = ttk.Style()

        # logo = Image.open(PATH_IMAGE + "switch-off.png").convert("RGBA")
        # logo = logo.resize((10, 10), Image.ANTIALIAS)
        # logo = ImageTk.PhotoImage(logo)
        
        self.style.theme_create("Azure")
        self.style.theme_settings("Azure", {
            "Main.TButton": {
                "configure": {
                    "padding": 10,
                    "background": "#0080FF",
                    "foreground": "white",
                    "borderwidth": 1,
                    "font": ("Calibri", 20, "bold"),
                    "anchor": tk.CENTER,
                    "relief": tk.FLAT,
                },
                "map": {
                    "foreground": [('active', '!disabled', 'white')],
                    "background": [('active', '#0066cc')]
                }
            },
            "Mini.TButton": {
                "configure": {
                    "padding": 10,
                    "background": "#0080FF",
                    "foreground": "white",
                    "borderwidth": 1,
                    "font": ("Calibri", 16, "bold"),
                    "anchor": tk.CENTER,
                    "relief": tk.FLAT,
                },
                "map": {
                    "foreground": [('active', '!disabled', 'white')],
                    "background": [('active', '#0066cc')]
                }
            },
            "Switch": {
                "configure": {
                    "foreground": "white",
                    "background": "#0080FF",
                    # "image": ImageTk.PhotoImage(logo)
                }
            }
        })

    def apply_theme(self):
        self.style.theme_use("Azure")
