from tkinter import ttk
import tkinter as tk
from PIL import Image, ImageTk

PATH_IMAGE = "images\\"
PERCENTAGE_SCREEN = 1  # Defines the size of the canvas. If equal to 1 (100%) ,it takes the whole screen
WHITE = "#ffffff"
LIGHT_GREY = "#F1FFFE"
LIGHT_GREY_DISABLED = "#91A3B1"
AZURE = "#008ad7"
AZURE_DISABLED = "#99D0EF"
DARKER_AZURE = "#006EAC"
TEXT_BTN_COLOR = "black"
TEXT_BTN_COLOR_2 = "white"
TEXT_LBL_COLOR = "black"
BG_BTN_COLOR = "#E5EAF0"
BG_LBL_COLOR = "black"
DISABLE_LBL_COLOR = '#D3D3D3'
LARGE_FONT = ("Calibri", 22, "bold")
SMALL_FONT = ("Calibri", 16, "bold")
SMALL_FONT_2 = ("Calibri", 10)
SMALL_FONT_3 = ("Calibri", 12)
CURSOR_HAND = "hand2"
QUESTION_HAND = "question_arrow"
BORDERWIDTH = 3

class MyStyle():

    def __init__(self):
    
        self.style = ttk.Style()

        self.style.theme_use("alt")

        self.style.configure("TLabel", background=LIGHT_GREY, foreground="black")
        self.style.configure("Popup.TLabel", background=WHITE, foreground="black", font=SMALL_FONT_2)
        self.style.configure("Attach.TLabel", background=WHITE, foreground="blue", font=("Calibri", 8, "underline"))

        self.style.configure("TButton", background=AZURE, foreground=WHITE, borderwidth=0, font=("Calibri", 20, "bold"),
                                anchor=tk.CENTER, relief=tk.FLAT, padding=10, cursor=CURSOR_HAND)
        self.style.map("TButton", background=[('active', DARKER_AZURE), ('disabled', AZURE_DISABLED)], foreground=[('active', WHITE), ('disabled', "#E5EAF0")])

        self.style.configure("MainPopup.TButton", background=AZURE, foreground=WHITE, borderwidth=0, font=("Calibri", 16, "bold"),
                                anchor=tk.CENTER, relief=tk.FLAT, padding=5)

        self.style.configure("Popup.TButton", background=AZURE, foreground=WHITE, borderwidth=0, font=("Calibri", 8),
                                anchor=tk.CENTER, relief=tk.FLAT, padding=2)
        self.style.map("Popup.TButton", background=[('disabled', AZURE_DISABLED), ('active', AZURE)], foreground=[('disabled', LIGHT_GREY_DISABLED), ('active', WHITE)])

        self.style.configure("TCheckbutton", background=LIGHT_GREY, borderwidth=0, font=("Calibri", 12),
                                anchor=tk.CENTER, relief=tk.FLAT)
        self.style.map("TCheckbutton", background=[('active', LIGHT_GREY), ('disabled', LIGHT_GREY_DISABLED)])

        self.style.configure("Popup.TCheckbutton", background=WHITE, borderwidth=0, font=("Calibri", 8),
                                anchor=tk.CENTER, relief=tk.FLAT)
        self.style.map("Popup.TCheckbutton", background=[('active', WHITE), ('disabled', WHITE)])

        self.style.configure("TRadiobutton", background=LIGHT_GREY, borderwidth=0, anchor=tk.CENTER)
        self.style.map("TRadiobutton", background=[('active', LIGHT_GREY)])

        self.style.configure("Popup.TRadiobutton", background=WHITE, borderwidth=0, anchor=tk.CENTER)
        self.style.map("Popup.TRadiobutton", background=[('active', WHITE)])

        self.style.configure("TEntry", background=LIGHT_GREY, foreground="black", borderwidth=0, relief=tk.FLAT)
        self.style.map("TEntry", background=[('disabled', LIGHT_GREY_DISABLED)], foreground=[('disabled', 'white')])
        
        self.style.map("Metadata.TEntry",fieldbackground=[("active", WHITE), ("disabled", LIGHT_GREY)],
                                        foreground=[("active", WHITE), ("disabled", 'black')])

        self.style.configure("TMenubutton", background=LIGHT_GREY, foreground="black", borderwidth=0, relief=tk.FLAT)

        self.style.configure("TCombobox", background=LIGHT_GREY, foreground="black", borderwidth=0, relief=tk.FLAT)
        self.style.map("TCombobox", fieldbackground=[("active", LIGHT_GREY), ("disabled", LIGHT_GREY_DISABLED)])

        self.style.configure("Popup.TCombobox", background=WHITE, foreground="black", borderwidth=0, relief=tk.FLAT)
        self.style.map("Popup.TCombobox", fieldbackground=[("active", WHITE), ("disabled", WHITE)])

        self.style.configure("TLabelframe", background=LIGHT_GREY, borderwidth=2, anchor=tk.CENTER, highlightcolor=AZURE)
        self.style.configure("TLabelframe.Label", font=("Calibri", 12), background=LIGHT_GREY)

        self.style.configure("Popup.TLabelframe", background=WHITE, borderwidth=2,
                                anchor=tk.CENTER, highlightcolor=AZURE)
        self.style.configure("Popup.TLabelframe.Label", font=("Calibri", 12), background=WHITE)
        
        self.style.configure("Metadata.TLabelframe", background=LIGHT_GREY, anchor=tk.CENTER, highlightbackground = AZURE, highlightcolor=LIGHT_GREY, borderwidth=3, relief='solid')
        self.style.configure("Metadata.TLabelframe.Label", font=("Calibri", 12, 'bold'), background=LIGHT_GREY)

        self.style.configure("TNotebook", tabmargins = [2, 5, 2, 0], background = LIGHT_GREY)
        self.style.configure("TNotebook.Tab", padding = [1, 1], background=LIGHT_GREY, font=("Calibri", 12))
        self.style.map("TNotebook.Tab", background = [("selected", AZURE)], foreground = [("selected", "white")], expand = [("selected", [1, 1, 1, 0])])

        self.style.configure("Treeview", background=LIGHT_GREY, foreground="black", relief=tk.FLAT, anchor=tk.CENTER, font=SMALL_FONT_2,
                                        highlightthickness=0, borderwidth=3)
        self.style.configure("Treeview.Heading", background=LIGHT_GREY, foreground="black", relief=tk.FLAT, anchor=tk.CENTER, font=SMALL_FONT_2,
                                        highlightthickness=0, borderwidth=3)

        self.style.configure("Vertical.TScrollbar", background=LIGHT_GREY, foreground="black", relief=tk.FLAT, anchor=tk.CENTER,
                                        highlightthickness=0, borderwidth=3)

    def get_style(self):
        return self.style
