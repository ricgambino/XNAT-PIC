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

        self.style.configure("TButton", background="#0080FF", foreground="white", borderwidth=0, font=("Calibri", 20, "bold"),
                                anchor=tk.CENTER, relief=tk.FLAT, padding=10)
        self.style.map("TButton", background=[('active', '#0066cc')], foreground=[('active', '!disabled', 'white')])
        self.style.configure("TCheckbutton", background="#ffffff", borderwidth=0, font=("Calibri", 12),
                                anchor=tk.CENTER, relief=tk.FLAT)
        self.style.map("TCheckbutton", background=[('active', "#ffffff")], highlightcolor=[('focus', "#ffffff")])
        self.style.configure("TLabelframe", background="#ffffff", borderwidth=1,
                                anchor=tk.CENTER, highlightcolor="#0080FF")
        self.style.configure("TLabelframe.Label", font=("Calibri", 12, 'bold'), background="#ffffff")

        self.style.configure("Metadata.TLabelframe", background="#ffffff", anchor=tk.CENTER, highlightbackground = "#0080FF", highlightcolor="#ffffff", borderwidth=3, relief='solid')
        self.style.configure("Metadata.TLabelframe.Label", font=("Calibri", 12, 'bold'), background="#ffffff")

        self.style.configure("TNotebook", tabmargins = [2, 5, 2, 0], background = 'white')
        self.style.configure("TNotebook.Tab", padding = [1, 1], background = THEME_COLOR, font = ("Calibri", 12))
        self.style.map("TNotebook.Tab", background = [("selected", BG_BTN_COLOR_2)], foreground = [("selected", "white")], expand = [("selected", [1, 1, 1, 0])])


    def get_style(self):
        return self.style
