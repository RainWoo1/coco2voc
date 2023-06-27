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

from coco_to_voc_aux import annotations_to_seg

def add_file():
    files = filedialog.askopenfilenames(title='입력 파일을 선택하세요', \
        initialdir=r"C:\Users\waycen\Downloads", \
        filetypes=(('json files','*.json'),('all files','*.*')))
    for file in files:
        list_file.insert(END, file) # list_file.insert('', 'end', text=file, values=file, iid=str(file) + "번")

# 선택 삭제
def del_file():
    for index in reversed(list_file.curselection()):
        list_file.delete(index)

# 저장 경로 (폴더)
def browse_dest_path():
    folder_selected = filedialog.askdirectory()
    if folder_selected == "": # 사용자가 취소를 누를 때
        print("폴더 선택 취소")
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
    coco_instance = COCO(annVal) # COCO 파일 불러오기
    coco_imgs = coco_instance.imgs # coco image 전체 불러오기 {이미지 id: "images" 하위에 있는 정보 읽어오기}

    if n == None: n = len(coco_imgs)
    else:
        assert type(n) == int, "n must be an integer"
        n = min(n, len(coco_imgs))

    # 파일 다운로드 시 파일명으로 상위폴더 만들기
    filename = os.path.basename(annotations_file)
    if CheckVar1.get() == 1: # 상위폴더 만들기
        class_target_path = folder + '/' + filename[:-4] + '/' # JSON 파일을 import한다고 가정
        try:
            if not os.path.exists(class_target_path):
                os.makedirs(class_target_path)
        except OSError:
            print("Error: Failed to create the directory")
    elif CheckVar1.get() == 0:
        class_target_path = folder + '/'

    for i, img in enumerate(coco_imgs):
        img_id = coco_instance.getImgIds(img) # [14]

        # lesion
        category_id = coco_instance.getCatIds(catNms=['lesion']) # 81 # print(coco_anns[9]['image_id'])
       
        annotation_ids = coco_instance.getAnnIds(catIds=category_id, imgIds=img_id) # [1]
        if not annotation_ids:
            continue
        annotations = coco_instance.loadAnns(annotation_ids)
        class_seg, instance_seg, id_seg, class_mask = annotations_to_seg(annotations, coco_instance, apply_border, color) # segment에 annotation하는 함수
        Image.fromarray(class_mask).convert("P").save(class_target_path + coco_imgs[img_id[0]]['file_name'][:-4] + '_EGC.png') # NumPy 배열을 PIL 이미지로 변환
        
        # tool
        category_id = coco_instance.getCatIds(catNms=['tools']) # [82]
        annotation_id1 = coco_instance.getAnnIds(catIds=category_id, imgIds=img_id)
        if not annotation_id1:
            continue
        else:
            annotations1 = coco_instance.loadAnns(annotation_id1)
            class_seg, instance_seg, id_seg, class_mask = annotations_to_seg(annotations1, coco_instance, apply_border, color) # segment에 annotation하는 함수
            Image.fromarray(class_mask).convert("P").save(class_target_path + coco_imgs[img_id[0]]['file_name'][:-4] +  '_EGC_' + str(category_id[0]) +'.png')
    
    print("=== Log: ", filename, " finished ===")
    completedThreadNumber += 1
    progress = (completedThreadNumber)/totalThreadNumber * 100  # 실제 percent 정보를 계산
    p_var.set(progress)
    progress_bar.update()


def s(event):
    if list_file.size() == 0:
        msgbox.showwarning("경고", "이미지 파일을 추가하세요")
        return

    if len(txt_dest_path.get()) == 0:
        msgbox.showwarning("경고", "저장 경로를 선택하세요")
        return

    start()


if __name__ == '__main__':

    window = Tk()
    window.title("COCO to VOC")

    # 파일 프레임 (파일 추가)
    file_frame = Frame(window) # label1 = Label(window, text="COCO format을 선택해 주세요.")
    file_frame.pack(fill="x", padx=5, pady=5) # label1.pack()

    btn_add_file = Button(file_frame, padx=5, pady=5, width=12, text="파일추가", command=add_file)
    btn_add_file.pack(side="left")

    btn_del_file = Button(file_frame, padx=5, pady=5, width=12, text="선택삭제", command=del_file)
    btn_del_file.pack(side="right")

    # 리스트 프레임
    list_frame = Frame(window)
    list_frame.pack(fill="both", padx=5, pady=5)

    scrollbar = Scrollbar(list_frame)
    scrollbar.pack(side="right", fill="y")

    # list_file = ttk.Treeview(list_frame, columns=(1, 2), height=15, show="headings", yscrollcommand=scrollbar.set)
    # list_file.pack(side='left')
    # list_file.heading(1, text="파일명")
    # list_file.heading(2, text="진행상황")
    # list_file.column(2, width=100)

    list_file = Listbox(list_frame, selectmode="extended", height=15, yscrollcommand=scrollbar.set)
    list_file.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=list_file.yview)

    # 저장 경로 프레임
    path_frame = LabelFrame(window, text="저장경로")
    path_frame.pack(fill="x", padx=5, pady=5, ipady=5)

    txt_dest_path = Entry(path_frame)
    txt_dest_path.pack(side="left", fill="x", expand=True, padx=5, pady=5, ipady=4) # 높이 변경

    btn_dest_path = Button(path_frame, text="찾아보기", width=10, command=browse_dest_path)
    btn_dest_path.pack(side="right", padx=5, pady=5)

    # 이미지 파일 만들기 혹은 안 만들기
    CheckVar1 = IntVar()
    c1 = Checkbutton(window, text="다운로드 시 파일명으로 폴더 만들기", variable=CheckVar1)
    c1.pack()

    # 옵션 프레임
    frame_option = LabelFrame(window, text="옵션")
    frame_option.pack(padx=5, pady=5, ipady=5)

    # 1. 선, 면 옵션
    # 선, 면 레이블
    lbl_style = Label(frame_option, text="스타일", width=8)
    lbl_style.pack(side="left", padx=5, pady=5)

    # 선, 면 콤보
    opt_style = ["Shade", "Line"]
    cmb_style = ttk.Combobox(frame_option, state="readonly", values=opt_style, width=10)
    cmb_style.current(0)
    cmb_style.pack(side="left", padx=5, pady=5)

    # 2. 색 옵션
    # 색 레이블
    lbl_color = Label(frame_option, text="색", width=8)
    lbl_color.pack(side="left", padx=5, pady=5)

    # 색 레이블 콤보
    opt_color = ["빨간색", "파란색", "흰색"]
    cmb_color = ttk.Combobox(frame_option, state="readonly", values=opt_color, width=10)
    cmb_color.current(0)
    cmb_color.pack(side="left", padx=5, pady=5)

    # 진행 상황 Progress Bar
    frame_progress = LabelFrame(window, text="진행상황")
    frame_progress.pack(fill="x", padx=5, pady=5, ipady=5)

    p_var = DoubleVar()
    progress_bar = ttk.Progressbar(frame_progress, maximum=100, variable=p_var)
    progress_bar.pack(fill="x", padx=5, pady=5)

    # 실행 프레임
    frame_run = Frame(window)
    frame_run.pack(fill="x", padx=5, pady=5)

    btn_close = Button(frame_run, padx=5, pady=5, text="닫기", width=12, command=window.quit) # window.quit command=windowquit()
   
    btn_close.pack(side="right", padx=5, pady=5)

    btn_start = Button(frame_run, padx=5, pady=5, text="시작", width=12)
    btn_start.bind('<Button-1>', s)
    btn_start.pack(side="right", padx=5, pady=5)

    window.resizable(True, True)
    window.mainloop()