import ttkbootstrap as ttk
import tkinter as tk

class Treeview():

    def __init__(self, root, columns, width):

        self.root = root
        
        self.tree = ttk.Treeview(root, selectmode='browse')
        self.scrollbar = ttk.Scrollbar(root, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=self.scrollbar.set)
        self.tree["columns"] = [x[0] for x in columns if x[0] != "#0"]
        for idx, col in columns:
            self.tree.heading(idx, text=col, anchor=tk.NW)
            self.tree.column(idx, stretch=tk.YES, width=width)

    def set(self, dict_items):

        self.items = dict_items

        for key in dict_items.keys():
            if key == '0':
                main = self.tree.insert(dict_items[key]['parent'], "end", iid=int(key), text=dict_items[key]['text'], 
                                                            values=dict_items[key]['values'], open=True)
            else:
                if dict_items[key]['parent'] == '0':
                    level_1 = self.tree.insert(main, "end", iid=int(key), text=dict_items[key]['text'], values=dict_items[key]['values'], open=False)
                else:
                    level_2 = self.tree.insert(level_1, "end", iid=int(key), text=dict_items[key]['text'], values=dict_items[key]['values'])

    def find_items(self, item):
        data = []
        for parent in self.tree.get_children():
            if item.lower() in self.tree.item(parent)['text'].lower():
                data.append(parent)
            for child in self.tree.get_children(parent):
                if item.lower() in self.tree.item(child)['text'].lower():
                    data.append(child)
                for subchild in self.tree.get_children(child):
                    if item.lower() in self.tree.item(subchild)['text'].lower():
                        data.append(subchild)
        if data != []:
            self.tree.selection_set(data[0])
            self.tree.focus(data[0])
            self.tree.see(data[0])

    def remove_selection(self):
        for i in self.tree.selection():
            self.tree.selection_remove(i)
