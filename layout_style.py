from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk

PATH_IMAGE = "images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
BACKGROUND_COLOR = "#ffffff"
THEME_COLOR = "#E5EAF0"
THEME_COLOR_2 = '#0070C0'
TEXT_BTN_COLOR = "black"
TEXT_BTN_COLOR_2 = "white"
TEXT_LBL_COLOR = "black"
BG_BTN_COLOR = "#E5EAF0"
BG_BTN_COLOR_2 = '#0070C0'
BG_LBL_COLOR = "black"
DISABLE_LBL_COLOR = '#D3D3D3'
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
SMALL_FONT_2 = ("Calibri", 10)
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"
BORDERWIDTH = 3

class MyStyle():

    def __init__(self):
    
        self.style = ttk.Style()

        self.style.theme_use("alt")

        self.style.configure("TLabel", background="#ffffff", foreground="black")
        self.style.configure("Popup.TLabel", background="#ffffff", foreground="black", font=SMALL_FONT_2)
        self.style.configure("Attach.TLabel", background="#ffffff", foreground="blue", font=("Calibri", 8, "underline"))

        self.style.configure("TButton", background="#0080FF", foreground="white", borderwidth=0, font=("Calibri", 20, "bold"),
                                anchor=tk.CENTER, relief=tk.FLAT, padding=10, cursor=CURSOR_HAND)
        self.style.map("TButton", background=[('active', '#0066cc'), ('disabled', '#d5dde7')], foreground=[('active', 'white'), ('disabled', "#E5EAF0")])

        self.style.configure("MainPopup.TButton", background="#0080FF", foreground="white", borderwidth=0, font=("Calibri", 16, "bold"),
                                anchor=tk.CENTER, relief=tk.FLAT, padding=5)

        self.style.configure("Popup.TButton", background="#d5dde7", foreground="black", borderwidth=0, font=("Calibri", 8),
                                anchor=tk.CENTER, relief=tk.FLAT, padding=2)
        self.style.map("Popup.TButton", background=[('disabled', '#b4c3d4'), ('active', '#d5dde7')], foreground=[('disabled', 'white'), ('active', "black")])

        self.style.configure("TCheckbutton", background="#ffffff", borderwidth=0, font=("Calibri", 12),
                                anchor=tk.CENTER, relief=tk.FLAT)
        self.style.map("TCheckbutton", background=[('active', "#ffffff")])

        self.style.configure("Popup.TCheckbutton", background="#ffffff", borderwidth=0, font=("Calibri", 8),
                                anchor=tk.CENTER, relief=tk.FLAT)

        self.style.configure("TRadiobutton", background="#ffffff", borderwidth=0, anchor=tk.CENTER)
        self.style.map("TRadiobutton", background=[('active', "#ffffff")])

        self.style.configure("TEntry", background="white", foreground="black", borderwidth=0, relief=tk.FLAT)
        self.style.map("TEntry", background=[('disabled', "white")], foreground=[('disabled', 'white')])
        
        self.style.map("Metadata.TEntry",fieldbackground=[("active", "white"), ("disabled", THEME_COLOR)],
                                        foreground=[("active", "white"), ("disabled", 'black')])

        self.style.configure("TMenubutton", background="white", foreground="black", borderwidth=0, relief=tk.FLAT)

        self.style.configure("TCombobox", background="#ffffff", foreground="black", borderwidth=0, relief=tk.FLAT)
        self.style.map("TCombobox", fieldbackground=[("active", "white"), ("disabled", THEME_COLOR)])

        self.style.configure("TLabelframe", background="#ffffff", borderwidth=2,
                                anchor=tk.CENTER, highlightcolor="#0080FF")
        self.style.configure("TLabelframe.Label", font=("Calibri", 12), background="#ffffff")

        self.style.configure("Popup.TLabelframe", background="#ffffff", borderwidth=2,
                                anchor=tk.CENTER, highlightcolor="#0080FF")
        self.style.configure("Popup.TLabelframe.Label", font=("Calibri", 12), background="#ffffff")
        
        self.style.configure("Metadata.TLabelframe", background="#ffffff", anchor=tk.CENTER, highlightbackground = "#0080FF", highlightcolor="#ffffff", borderwidth=3, relief='solid')
        self.style.configure("Metadata.TLabelframe.Label", font=("Calibri", 12, 'bold'), background="#ffffff")

        self.style.configure("TNotebook", tabmargins = [2, 5, 2, 0], background = 'white')
        self.style.configure("TNotebook.Tab", padding = [1, 1], background=THEME_COLOR, font=("Calibri", 12))
        self.style.map("TNotebook.Tab", background = [("selected", BG_BTN_COLOR_2)], foreground = [("selected", "white")], expand = [("selected", [1, 1, 1, 0])])

        self.style.configure("Treeview", background="white", foreground="black", relief=tk.FLAT, anchor=tk.CENTER, font=SMALL_FONT_2,
                                        highlightthickness=0, borderwidth=3)
        self.style.configure("Treeview.Heading", background="white", foreground="black", relief=tk.FLAT, anchor=tk.CENTER, font=SMALL_FONT_2,
                                        highlightthickness=0, borderwidth=3)

    def get_style(self):
        return self.style
