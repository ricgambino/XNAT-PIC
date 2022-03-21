# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 2022

@author: Riccardo Gambino
"""

"""
Progress bar class.
"""
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import HORIZONTAL
# from threading import Thread
# import time

class ProgressBar():
    def __init__(self, bar_title):

        self.title = bar_title
        self.popup = tk.Toplevel()
        self.popup.geometry("%dx%d+%d+%d" % (500, 80, 700, 500))
        self.popup.title(bar_title)
        self.progress_var = tk.DoubleVar()
        self.bar_length = 400
        self.bar_maximum = 100
        self.label = tk.Label(self.popup, text='Loading ...', font=("Calibri", 14, "bold")).place(relx=0.5, rely=0.5, anchor = 's')
        self.style = ttk.Style()
        self.style.theme_use('alt')
        self.style.configure('blue.Horizontal.TProgressbar', troughcolor  = '#4d4d4d', troughrelief = 'flat', background   = '#2f92ff')

    def set_caption(self, index, total):
        self.label = tk.Label(self.popup, text='Converting ... ' + str(index) + ' / ' + str(total), font=("Calibri", 14, "bold")).place(relx=0.5, rely=0.5, anchor = 's')
        self.popup.update()
        
    def start_determinate_bar(self):

        self.progressbar = ttk.Progressbar(self.popup, variable=self.progress_var,
                                            style="blue.Horizontal.TProgressbar", orient=HORIZONTAL, 
                                            length=self.bar_length, mode='determinate', maximum=self.bar_maximum)
        self.progressbar.pack(expand=False, fill="x", side="top")
        self.progressbar.place(relx=0.5, rely=0.5, anchor = 'n')

    def start_indeterminate_bar(self):

        print('Starting progress bar...')

        self.progressbar = ttk.Progressbar(self.popup,
                                            style="blue.Horizontal.TProgressbar", 
                                            orient=HORIZONTAL, 
                                            length=self.bar_length, mode='indeterminate')
        self.progressbar.pack(expand=False, fill="x", side="top")
        self.progressbar.place(relx=0.5, rely=0.5, anchor = 'n')
        self.progressbar.start()

    def update_bar(self, step=0.001):
        self.progressbar.step(step)
        self.progressbar.update()
             
    def update_progressbar(self, current_step, max_step):
        progress = int(current_step * self.bar_maximum / max_step)
        self.progress_var.set(progress)
        self.popup.update()
    
    def stop_progress_bar(self):
        self.progressbar.stop()
        self.popup.destroy()
        
