from tkinter import *
from tkinter import messagebox
from tkinter import filedialog as fd
from PIL import ImageTk, Image
import glob
from enum import Enum
import os.path
import threading
import time
import numpy as np
import re
from google.cloud import vision
from google.cloud.vision import types
import cv2
import pandas as pd

class CropImage:
    def __init__(self, x1, y1, x2, y2, category, images):
        self.x1, self.y1, self.x2, self.y2 = (x1, y1, x2, y2)
        self.category = category
        self.images = images
        
    def init_image(self, i):
        self.initial = Image.open(self.images[i])
        path, self.file_name = os.path.split(self.images[i])

    def crop(self):
        if self.category == Category.NAME:
            self.crop_name()
        elif self.category == Category.KILL:
            self.crop_kill()
        elif self.category == Category.DS:
            self.crop_ds()
        
    def crop_name(self):
        crop = self.initial.crop((self.x1, self.y1, self.x2, self.y2))
        img = np.array(crop) 
        img = img[:, :, ::-1].copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        structuringElement = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))

        imgTopHat = cv2.morphologyEx(gray, cv2.MORPH_TOPHAT, structuringElement)
        imgBlackHat = cv2.morphologyEx(gray, cv2.MORPH_BLACKHAT, structuringElement)

        imgGrayscalePlusTopHat = cv2.add(gray, imgTopHat)
        gray = cv2.subtract(imgGrayscalePlusTopHat, imgBlackHat)

        img_blurred = cv2.GaussianBlur(gray, ksize=(5, 5), sigmaX=0)

        ret, img_thresh = cv2.threshold(
            img_blurred, 
            190, #name : 180
            255,
            cv2.THRESH_BINARY
        )
        
        cv2.imwrite('data/croped/name/' + self.file_name, img_thresh)
        
    def crop_kill(self):
        crop = self.initial.crop((self.x1, self.y1, self.x2, self.y2))
        
        lower_blue = (0, 0, 0)
        upper_blue =(255, 255, 60)

        img = np.array(crop) 
        img = img[:, :, ::-1].copy() 

        img_hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        img_mask = cv2.inRange(img_hsv, lower_blue, upper_blue)
        img_result = cv2.bitwise_not(img, img)
        img_result1 = cv2.bitwise_and(img_result, img_result, mask=img_mask)
        cv2.imwrite('data/croped/kill/' + self.file_name, img_result1)
        
    def crop_ds(self):
        crop = self.initial.crop((self.x1, self.y1, self.x2, self.y2))
        crop.save('data/croped/ds/' + self.file_name)
        
class DetectImage:
    def __init__(self, images):
        self.name = list()
        self.power = list()
        self.kill = list()
        self.t1 = list()
        self.t2 = list()
        self.t3 = list()
        self.t4 = list()
        self.t5 = list()
        self.dead = list()
        self.support = list()

        self.images = images
        
        self.df = None
        
    def detect(self, i):
        self.detect_name(i)
        self.detect_kill(i)
        self.detect_ds(i)
    
    def detect_name(self, i):
        path, file_name = os.path.split(self.images[i])
    
        detect_name = self.detect_text('data/croped/name/' + file_name)
        detect_name = self.change_to_list(detect_name)
        self.name.append(detect_name[0])
        self.power.append(self.change_to_number(detect_name[-2]))
        self.kill.append(self.change_to_number(detect_name[-1]))
        
    def detect_kill(self, i):
        path, file_name = os.path.split(self.images[i])

        detect_kill = self.detect_text('data/croped/kill/' + file_name)
        detect_kill = self.change_to_list(detect_kill)

        self.t1.append(self.change_to_number(detect_kill[0]))
        self.t2.append(self.change_to_number(detect_kill[1]))
        self.t3.append(self.change_to_number(detect_kill[2]))
        self.t4.append(self.change_to_number(detect_kill[3]))
        self.t5.append(self.change_to_number(detect_kill[4]))
        
    def detect_ds(self, i):
        path, file_name = os.path.split(self.images[i])
        
        detect_ds = self.detect_text('data/croped/ds/' + file_name)
        detect_ds = self.change_to_list(detect_ds)
        self.dead.append(self.change_to_number(detect_ds[detect_ds.index('전사')+1]))
        self.support.append(self.change_to_number(detect_ds[detect_ds.index('원조')+1]))
        
    def detect_text(self, path):
        """Detects text in the file."""
        from google.cloud import vision
        import io
        client = vision.ImageAnnotatorClient()

        # [START vision_python_migration_text_detection]
        with io.open(path, 'rb') as image_file:
            content = image_file.read()

        image = vision.types.Image(content=content)

        response = client.text_detection(image=image)
        texts = response.text_annotations

        return texts[0].description

    def change_to_number(self, s_power):
        list_of_numbers = re.findall(r'\d+', s_power)
        return int(''.join(list_of_numbers))
    
    def change_to_list(self, chars):
        tmp_texts = list()
        s = ""
        for c in chars:
            if c != '\n':
                s += c
            else:
                tmp_texts.append(s)
                s = ""

        return tmp_texts
    
    def export_to_excel(self, filename):        
        self.df = pd.DataFrame({'name': self.name,
                                'power':self.power,
                                'all_kill':self.kill,
                                'T1_kill':self.t1,
                                'T2_kill':self.t2,
                                'T3_kill':self.t3,
                                'T4_kill':self.t4,
                                'T5_kill':self.t5,
                                'dead':self.dead,
                                'support':self.support})
        
        self.df.to_excel(filename)
        
class Category(Enum):
    NAME = 0
    KILL = 1
    DS = 2

class Dialog():
    def __init__(self, parent, category, images):
        self.parent = parent
        self.frame = Frame(self.parent)
        self.category = category
        self.images = images
        self.old_x, self.old_y, self.new_x, self.new_y = (0, 0, 0, 0)
        
        self.drag_area = None

        self.img = Image.open(self.images[0])
        w, h = self.img.size
        self.img = self.img.resize((int(w/2), int(h/2)))
        self.image = ImageTk.PhotoImage(self.img)

        w, h = self.img.size
        self.canvas = Canvas(parent, width=w, height=h)
        self.canvas.grid(column=0, row=0)
        self.canvas.create_image(0, 0, anchor=NW, image=self.image)
        self.canvas.image = self.image

        self.parent.bind("<Button-1>", self.motion1)
        self.parent.bind("<ButtonRelease-1>", self.motion2)
        self.parent.bind("<B1-Motion>", self.motion3)

    def motion1(self, event):
        self.canvas.delete(self.drag_area)
        self.drag_area = None
        self.old_x, self.old_y = event.x, event.y

    def motion2(self, event):
        self.new_x, self.new_y = event.x, event.y
        
        msg = messagebox.askokcancel("확인", "제대로 영역지정을 하셨나요?")

        if msg:
            self.parent.destroy()

            if self.category == Category.NAME:
                img = Image.open(self.images[0]).crop((self.old_x*2, self.old_y*2, self.new_x*2, self.new_y*2))

                w, h = img.size
                application.canvas_name = Canvas(application.parent, width=w/2, height=h/2)
                application.canvas_name.grid(column=1, row=2, padx=1, pady=5, columnspan=3)

                img = img.resize((int(w/2), int(h/2)))
                image = ImageTk.PhotoImage(img)
                application.canvas_name.create_image(0, 0, anchor=NW, image=image)
                application.canvas_name.image = image
                
                application.crop_name = CropImage(self.old_x * 2, self.old_y * 2, self.new_x * 2, self.new_y * 2, Category.NAME, self.images)
                
            elif self.category == Category.KILL:
                img = Image.open(self.images[0]).crop((self.old_x * 2, self.old_y * 2, self.new_x * 2, self.new_y * 2))

                w, h = img.size
                application.canvas_kill = Canvas(application.parent, width=w / 2, height=h / 2)
                application.canvas_kill.grid(column=1, row=3, padx=1, pady=5, columnspan=3)

                img = img.resize((int(w / 2), int(h / 2)))
                image = ImageTk.PhotoImage(img)
                application.canvas_kill.create_image(0, 0, anchor=NW, image=image)
                application.canvas_kill.image = image
                
                application.crop_kill = CropImage(self.old_x * 2, self.old_y * 2, self.new_x * 2, self.new_y * 2, Category.KILL, self.images)
                
            elif self.category == Category.DS:
                img = Image.open(self.images[0]).crop((self.old_x * 2, self.old_y * 2, self.new_x * 2, self.new_y * 2))

                w, h = img.size
                application.canvas_ds = Canvas(application.parent, width=w / 2, height=h / 2)
                application.canvas_ds.grid(column=1, row=4, padx=1, pady=5, columnspan=3)

                img = img.resize((int(w / 2), int(h / 2)))
                image = ImageTk.PhotoImage(img)
                application.canvas_ds.create_image(0, 0, anchor=NW, image=image)
                application.canvas_ds.image = image
                
                application.crop_ds = CropImage(self.old_x * 2, self.old_y * 2, self.new_x * 2, self.new_y * 2, Category.DS, self.images)

    def motion3(self, event):
        if self.drag_area != None:
            self.canvas.delete(self.drag_area)

        w = 2
        self.drag_area = self.canvas.create_rectangle(self.old_x, self.old_y, event.x, event.y, width=w)
    
class Main(Frame):
    def __init__(self, parent):
        self.parent = parent
        self.frame = Frame(self.parent)

        self.i = 0
        
        btn_load_img = Button(parent, text='이미지 불러오기', command=self.load_image)
        btn_load_img.grid(column=0, row=0, padx=5, pady=5)
        
        btn_edit_img = Button(parent, text='이미지 편집', command=self.crop_image)
        btn_edit_img.grid(column=1, row=0, padx=5, pady=5)        
        
        btn_detect_img = Button(parent, text="이미지 인식", command=self.detect_image)
        btn_detect_img.grid(column=2, row=0, padx=5, pady=5)
        
        btn_export = Button(parent, text="엑셀파일로", command=self.export_excel)
        btn_export.grid(column=3, row=0, padx=5, pady=5)
        
        self.lbl_status = Label(parent, text='진행 상황')
        self.lbl_status.grid(column=0, row=1, padx=5, pady=5, columnspan=4)
        
        # Name
        btn_get_name = Button(parent, text='이름 & 투력 & 총 킬수', command=self.open_nameDialog)
        btn_get_name.grid(column=0, row=2, padx=5, pady=5)

        # Kill
        btn_get_kill = Button(parent, text='티어별 킬수', command=self.open_killDialog)
        btn_get_kill.grid(column=0, row=3, padx=5, pady=5)

        # Dead & Support
        btn_get_ds = Button(parent, text='전사 & 원조', command=self.open_dsDialog)
        btn_get_ds.grid(column=0, row=4, padx=5, pady=5)

    def load_image(self):
        self.files = fd.askopenfilenames()
        
        self.load()
           
    def load(self):
        total = len(self.files)
        
        s = '{}/{} 완료'.format(self.i, total)
        self.lbl_status.config(text=s)
        self.parent.update()
        
        fname = os.path.split(self.files[self.i])[1]
        im = Image.open(self.files[self.i])
        im.save('data/original/' + fname)
        
        self.i += 1
        
        s = '{}/{} 완료'.format(self.i, total)
        self.lbl_status.config(text=s)
        self.parent.update()
        
        if self.i == total:
            self.parent.after_cancel(self.job_load) 
            self.i = 0
            self.images = glob.glob('data/original/*')
            messagebox.showinfo("작업 상태", "완료!")
        else:
            self.job_load = self.parent.after(0, self.load)
            
        
    def open_nameDialog(self):
        self.nameDialog = Toplevel(self.parent)
        self.name_app = Dialog(self.nameDialog, Category.NAME, self.images)       

    def open_killDialog(self):
        self.killDialog = Toplevel(self.parent)
        self.kill_app = Dialog(self.killDialog, Category.KILL, self.images)
        
    def open_dsDialog(self):
        self.dsDialog = Toplevel(self.parent)
        self.ds_app = Dialog(self.dsDialog, Category.DS, self.images)
        
    def crop_image(self):
        total = len(self.images)
        
        s = '{}/{} 완료'.format(self.i, total)
        self.lbl_status.config(text=s)
        self.parent.update()
        
        self.crop_name.init_image(self.i)
        self.crop_name.crop()
        
        self.crop_kill.init_image(self.i)
        self.crop_kill.crop()
        
        self.crop_ds.init_image(self.i)
        self.crop_ds.crop()
        
        self.i += 1
        
        s = '{}/{} 완료'.format(self.i, total)
        self.lbl_status.config(text=s)
        self.parent.update()
        
        if self.i == total:
            self.parent.after_cancel(self.job_crop) 
            self.i = 0
            self.di = DetectImage(self.images)
            messagebox.showinfo("작업 상태", "완료!")
        else:
            self.job_crop = self.parent.after(0, self.crop_image)
 
            
    def detect_image(self):
        total = len(self.images)
        
        s = '{}/{} 완료'.format(self.i, total)
        self.lbl_status.config(text=s)
        self.parent.update()
        
        self.di.detect(self.i)
        
        self.i += 1
        
        s = '{}/{} 완료'.format(self.i, total)
        self.lbl_status.config(text=s)
        self.parent.update()
        
        if self.i == total:
            self.parent.after_cancel(self.job_detect) 
            self.i = 0
            messagebox.showinfo("작업 상태", "완료!")
        else:
            self.job_detect = self.parent.after(0, self.detect_image)
            
    def export_excel(self):
        filename = fd.asksaveasfilename(filetypes=[('excel file', ',xlsx')], title='Save file as', initialfile='memberinfo.xlsx')
        self.di.export_to_excel(filename)
        
if __name__ == "__main__":
    root = Tk()
    application = Main(root)
    root.resizable(width=False, height=False)
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="bin/ROKS-78e082836307.json"

    root.mainloop()