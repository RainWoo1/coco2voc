from tkinter import *
import tkinter.ttk as ttk
from tkinter import filedialog, messagebox
from coco_to_voc import coco2voc

# Create a Window
window=Tk()

# Window Settings
window.title("COCO to VOC")
window.geometry("640x400+100+100")
window.resizable(False, False)

def openFile():
    # global file, my_str
    file = filedialog.askopenfilename(initialdir='C:/Users/waycen/Downloads', title='Open file', filetypes=(('json files','*.json'),('all files','*.*')))
    label.configure(text="파일: " + file)
    # print(file)
    return file

def saveFile():
    # global file1
    file1 = filedialog.askopenfilename(initialdir='C:/Users/waycen/Downloads', title='Choose Dir', filetypes=(('png files','*.png'),('jpg files','*.jpg'),('all files','*.*')))
    label.configure(text="파일: " + file1)
    return file1

# def convert():
#     if choose == "Shade":
#     coco2voc(file, file1, 1, False) #원래파일경로, 새로운경로, 1, True: border false: shade
#     elif choose == "Line":
#         coco2voc(file, file1, 1, True) #원래파일경로, 새로운경로, 1, True: border false: shade
#     else:
#         messagebox.showinfo("error", "Please select either Shade or Line.")

label1 = Label(window, text="COCO format을 선택해 주세요.")
label1.pack()

# Upload button
button = Button(window, overrelief="solid", width=15, command=openFile, repeatdelay=1000, repeatinterval=100, text="업로드 파일선택")
button.pack()

label = Label(window)
label.pack()


# Combobox
list=["Shade", "Line"] # 콤보 박스에 나타낼 항목 리스트
combobox = ttk.Combobox(window)
combobox.config(height=5)
combobox.config(values=list) # 나타낼 항목 리스트
combobox.config(state="readonly")
combobox.set("Line") # 맨 처음 나타낼 값 정하기
combobox.pack()

# Save button
button1 = Button(window, overrelief="solid", width=15, command=saveFile, repeatdelay=1000, repeatinterval=100, text="파일 저장경로 선택")
button1.pack()

# Convert
button2 = Button(window, overrelief="solid", width=15, command=saveFile, repeatdelay=1000, repeatinterval=100, text="변환")
button2.pack()

print(button2.cget)
print(type(button2))

choose = "Shade"
if combobox.get == "Line": choose = "Line"
elif combobox.get == "Shade": choose = "Shade"


window.mainloop()