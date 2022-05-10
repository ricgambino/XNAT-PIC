# -*- coding: utf-8 -*-
"""
Created on Mon Mar 21 2022

@author: Riccardo Gambino
"""

"""
Progress bar class.
"""
import tkinter as tk
#import tkinter.ttk as ttk
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tkinter import HORIZONTAL
# from threading import Thread
# import time

class ProgressBar():
    def __init__(self, bar_title):

        self.title = bar_title
        self.popup = ttk.Toplevel()
        self.popup.geometry("%dx%d+%d+%d" % (500, 100, 700, 500))
        self.popup.title(bar_title)
        self.progress_var = tk.DoubleVar()
        self.bar_length = 400
        self.bar_maximum = 100
        self.label = tk.Label(self.popup, text='Loading ...', font=("Calibri", 14, "bold"))
        self.label.grid(row=1, column=1)
        # self.style = ttk.Style()
        # self.style.theme_use('alt')
        # self.style.configure('blue.Horizontal.TProgressbar', troughcolor='#4d4d4d', troughrelief='flat', background='#2f92ff')
        self.caption = tk.Label(self.popup, text='', font=("Calibri", 10))
        self.caption.grid(row=3, column=1)

    def show_step(self, index, total):
        self.step = tk.Label(self.popup, text=str(index) + ' / ' + str(total), font=("Calibri", 14, "bold"))
        self.step.grid(row=2, column=2, sticky=tk.W)
        self.popup.update()

    def set_caption(self, text):
        self.caption.config(text='')
        self.caption.config(text=text)
        self.popup.update()
        
    def start_determinate_bar(self):

        print('Starting progress bar...')

        self.progressbar = ttk.Progressbar(self.popup, variable=self.progress_var,
                                             orient=HORIZONTAL, 
                                            length=self.bar_length, mode='determinate', maximum=self.bar_maximum)
        self.progressbar.grid(row=2, column=1, padx=10)

    def start_indeterminate_bar(self):

        print('Starting progress bar...')

        self.progressbar = ttk.Progressbar(self.popup, 
                                            orient=HORIZONTAL, 
                                            length=self.bar_length, mode='indeterminate')
        self.progressbar.grid(row=2, column=1, padx=10)
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
        
