# -*- mode: python ; coding: utf-8 -*-

import os
# import time
from tkinter import *
import tkinter.ttk as ttk
from tkinter import filedialog
import tkinter.messagebox as msgbox
import threading

import numpy as np
from PIL import Image
from pycocotools.coco import COCO

from util.coco_to_voc_aux import annotations_to_seg

def add_file():
    files = filedialog.askopenfilenames(title='Select input file', \
        # initialdir=r"C:\Users\waycen\Downloads", \
        filetypes=(('json files','*.json'),('all files','*.*')))
    for file in files:
        list_file.insert(END, file)

# Delete Selected files
def del_file():
    for index in reversed(list_file.curselection()):
        list_file.delete(index)

# Save Path (Folder)
def browse_dest_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # When the user clicks Cancel
        print("Deselect Folder")
        return
    txt_dest_path.delete(0, END)
    txt_dest_path.insert(0, folder_selected)

def start():
    global completedThreadNumber
    global totalThreadNumber
    completedThreadNumber = 0
    p_var.set(0)
    progress_bar.update()

    upload_file_path = list_file.get(0, END)
    download_file_path = txt_dest_path.get()
    img_style = cmb_style.get()
    color = cmb_color.get()

    if img_style == "Shade":
        img_style = False
    else:
        img_style = True

    totalThreadNumber = len(upload_file_path)

    for i in range(len(upload_file_path)):
        print("=== Start Thread ===")
        threading.Thread(target=coco2voc, args=(upload_file_path[i], download_file_path, color, 1, img_style)).start()

    print("Test finished")

completedThreadNumber = 0
totalThreadNumber = 0

def coco2voc(annotations_file: str, folder: str, color: str, n: int = None, apply_border: bool = False):
    global completedThreadNumber
    global totalThreadNumber
    annVal = os.path.join(annotations_file) #, 'annotations', os.path.basename(annotations_file)
    coco_instance = COCO(annVal) # Load COCO file
    coco_imgs = coco_instance.imgs # Load entire coco image {Image id: Read information under "images"}

    if n == None: n = len(coco_imgs)
    else:
        assert type(n) == int, "n must be an integer"
        n = min(n, len(coco_imgs))

    # Create parent folder with filename when downloading file
    filename = os.path.basename(annotations_file)
    if CheckVar1.get() == 1: # Create parent folder
        class_target_path = folder + '/' + filename[:-4] + '/' # Suppose importing a JSON file
        try:
            if not os.path.exists(class_target_path):
                os.makedirs(class_target_path)
        except OSError:
            print("Error: Failed to create the directory")
    elif CheckVar1.get() == 0:
        class_target_path = folder + '/'
    
    supercategory_on = False
    if CheckVar2.get() == 1: # Enable supercategory
        supercategory_on = True

    cat_ids = coco_instance.getCatIds()

    if (supercategory_on):
        for i, img in enumerate(coco_imgs):
            img_id = coco_instance.getImgIds(img)
            supercategories = []

            # no supercategories
            for ids in cat_ids:
                categories = coco_instance.loadCats(ids)
                supercategory = categories[0]["supercategory"]
                if supercategory == '':
                    cat_name = categories[0]["name"]
                    annotation_ids = coco_instance.getAnnIds(catIds=ids, imgIds=img_id)
                    if not annotation_ids:
                        continue
                    annotations = coco_instance.loadAnns(annotation_ids)
                    class_seg, instance_seg, id_seg, class_mask = annotations_to_seg(annotations, coco_instance, apply_border, color) # segment에 annotation하는 함수
                    Image.fromarray(class_mask).convert("P").save(class_target_path + coco_imgs[img_id[0]]['file_name'][:-4] + '_' + cat_name + '.png') # Convert NumPy array to PIL image
                else:
                    if supercategory not in supercategories or supercategories == []:
                        supercategories.append(supercategory)
            
            # with supercategories
            if supercategories == []:
                continue
            else:
                for supercategory in supercategories:
                    cats = coco_instance.cats
                    catids = [] # Category IDs in the supercategory
                    
                    for j in cat_ids:
                        if supercategory == cats[j]["supercategory"]:
                            catids.append(j) # Creating a category list with only Category IDs
                    
                    annotation_ids = []
                    for k in catids:
                        a = coco_instance.getAnnIds(catIds=k, imgIds=img_id)
                        for h in range(len(a)):
                            annotation_ids.append(a[h]) # Import annotation id in the Category ID list
                    if not annotation_ids:
                        continue

                    annotations = coco_instance.loadAnns(annotation_ids[0])
                    class_seg, instance_seg, id_seg, class_mask = annotations_to_seg(annotations, coco_instance, apply_border, color)
                    for ann in annotation_ids:
                        annotations = coco_instance.loadAnns(ann)
                        class_seg, instance_seg, id_seg, class_mask1 = annotations_to_seg(annotations, coco_instance, apply_border, color)
                        class_mask = class_mask + class_mask1
                    Image.fromarray(class_mask).convert("P").save(class_target_path + coco_imgs[img_id[0]]['file_name'][:-4] + '_' + supercategory + '.png')

            completedThreadNumber += 1
            progress = (completedThreadNumber)/totalThreadNumber * 100
            p_var.set(progress)
            progress_bar.update()

    else: # supercategory_off = false
        for i, img in enumerate(coco_imgs):
            img_id = coco_instance.getImgIds(img)

            for ids in cat_ids:
                categories = coco_instance.loadCats(ids)
                cat_name = categories[0]["name"]
                annotation_ids = coco_instance.getAnnIds(catIds=ids, imgIds=img_id)
                if not annotation_ids:
                    continue
                annotations = coco_instance.loadAnns(annotation_ids)
                class_seg, instance_seg, id_seg, class_mask = annotations_to_seg(annotations, coco_instance, apply_border, color)
                Image.fromarray(class_mask).convert("P").save(class_target_path + coco_imgs[img_id[0]]['file_name'][:-4] + '_' + cat_name + '.png')

        completedThreadNumber += 1
        progress = (completedThreadNumber)/totalThreadNumber * 100
        p_var.set(progress)
        progress_bar.update()

    print("=== Log: ", filename, " finished ===")

def s(event):
    if list_file.size() == 0:
        msgbox.showwarning("Warning", "Add an image file") # Add an image file
        return
    if len(txt_dest_path.get()) == 0:
        msgbox.showwarning("Warning", "Select a storage path") # Select a storage path
        return
    start()

if __name__ == '__main__':

    window = Tk()
    window.title("COCO to VOC")

    # File Frame (Add File)
    file_frame = Frame(window)
    file_frame.pack(fill="x", padx=5, pady=5) # label1.pack()

    btn_add_file = Button(file_frame, padx=5, pady=5, width=12, text="Add File", command=add_file)
    btn_add_file.pack(side="left")

    btn_del_file = Button(file_frame, padx=5, pady=5, width=12, text="Delete Selection", command=del_file)
    btn_del_file.pack(side="right")

    # List frame
    list_frame = Frame(window)
    list_frame.pack(fill="both", padx=5, pady=5)

    scrollbar = Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    list_file = Listbox(list_frame, selectmode="extended", height=15, yscrollcommand=scrollbar.set)
    list_file.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=list_file.yview)

    # Storage Path Frame
    path_frame = LabelFrame(window, text="Save Path")
    path_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    txt_dest_path = Entry(path_frame)
    txt_dest_path.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4) # Change height

    btn_dest_path = Button(path_frame, text="Browse", width=10, command=browse_dest_path)
    btn_dest_path.pack(side="right", padx=5, pady=5)

    # Create an image file
    CheckVar1 = IntVar()
    # Create a folder with file names when download
    c1 = Checkbutton(window, text="Create a folder with file names", variable=CheckVar1)
    c1.pack()

    # Supercategory
    CheckVar2 = IntVar()
    # Create Supercategory file as one file
    c2 = Checkbutton(window, text="Create Supercategory file as one file", variable=CheckVar2)
    c2.pack()

    # Option frame
    frame_option = LabelFrame(window, text="Option")
    frame_option.pack(padx=5, pady=5, ipady=5)

    # 1. Line, Area Options
    # Line, Area Labels
    lbl_style = Label(frame_option, text="Style", width=8)
    lbl_style.pack(side="left", padx=5, pady=5)

    # Line, Area Combo
    opt_style = ["Shade", "Line"]
    cmb_style = ttk.Combobox(frame_option, state="readonly", values=opt_style, width=10)
    cmb_style.current(0)
    cmb_style.pack(side="left", padx=5, pady=5)

    # 2. Color Options
    # Color Label
    lbl_color = Label(frame_option, text="Color", width=8)
    lbl_color.pack(side="left", padx=5, pady=5)

    # Color Label Combo
    opt_color = ["Red", "Blue", "White"]
    cmb_color = ttk.Combobox(frame_option, state="readonly", values=opt_color, width=10)
    cmb_color.current(0)
    cmb_color.pack(side="left", padx=5, pady=5)

    # Progress Bar
    frame_progress = LabelFrame(window, text="Progress Bar")
    frame_progress.pack(fill="x", padx=5, pady=5, ipady=5)

    p_var = DoubleVar()
    progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
    progress_bar.pack(fill="x", padx=5, pady=5)

    # Run Frame
    frame_run = Frame(window)
    frame_run.pack(fill="x", padx=5, pady=5)

    btn_close = Button(frame_run, padx=5, pady=5, text="Close", width=12, command=window.quit)
   
    btn_close.pack(side="right", padx=5, pady=5)

    btn_start = Button(frame_run, padx=5, pady=5, text="Start", width=12)
    btn_start.bind('<Button-1>', s)
    btn_start.pack(side="right", padx=5, pady=5)

    window.resizable(True, True)
    window.mainloop()
