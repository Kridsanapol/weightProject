from tkinter import *
from tkinter import font as tkfont
from PIL import Image, ImageTk
import scanfruit
import sqlite3
import os
import socket
from picamera import PiCamera
from time import sleep
from datetime import datetime

#import self as self


class SampleApp(Tk):

    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)

        self.title_font = tkfont.Font(family='Helvetica', size=18, weight="bold", slant="italic")

        self.container = Frame(self)
        self.container.pack(side="top", fill="both", expand=True)
        self.container.grid_rowconfigure(0, weight=1)
        self.container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        frame = ScanPage(parent=self.container, controller=self, price = None, fname = None, weight=None, picName=None)
        self.frames["ScanPage"] = frame
        frame.grid(row=0, column=0, sticky="nsew")

        frame.tkraise()

    def show_frame(self, page_name, priceArg,fnameArg,weightArg,picNameArg):
        frame = globals()[page_name](parent=self.container, controller=self, price=priceArg, fname=fnameArg,weight=weightArg,picName=picNameArg)
        self.frames[page_name] = frame
        frame.grid(row=0, column=0, sticky="nsew")
        frame.tkraise()


class ScanPage(Frame):
    def __init__(self, parent, controller, price,fname,weight,picName):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="Scan page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        button1 = Button(self, text="Scan fruit", command=lambda: controller.show_frame("SelectPage",None,None,None,None))
        button1.pack(fill="x")



class SelectPage(Frame):
    
    def __init__(self, parent, controller, price,fname,weight,picName):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="Please select item", font=controller.title_font)
        label.pack(side = "top", fill = "x", pady = 10)
        midframe4 = Frame(self, relief=RAISED, borderwidth=0)
        midframe4.pack()
        
        camera.start_preview()
        sleep(5)
        camera.capture('/home/pi/models/tutorials/image/imagenet/image.jpg')
        camera.stop_preview()
        s=scanfruit.scan_fruit("image.jpg") #scan
        #s=scanfruit.scan_fruit("strawberries.jpg") #scan
        print("fruits " , s)
        conn = sqlite3.connect('demo1.sqlite')
        c = conn.cursor()
        
        weight1=2

        for x in s:
            print(x[0])
            name=x[0]
            c.execute("SELECT * fROM  material WHERE fname=?", (name,))
            item = c.fetchall()
            price=0
            cname=NONE
            print(item)
            for rows in item:
                cname = rows[1]
                price = rows[2]
                picName=rows[3]
                
                print("Price from Database ", price)
                print("picName from Database ", picName)
            if cname==name:
                button = Button(self, text=name+" ราคา "+str(price)+" บาท/กก.",command=lambda prices=price, fname=name, w=weight1 ,picN=picName: controller.show_frame("CalPage", prices,fname,w,picN))
                button.pack(fill="x")
            
        button1 = Button(self, text="Scan again", command=lambda: controller.show_frame("SelectPage",None,None,None,None))
        button1.pack(side="bottom",fill="x")
                
        s.clear()    
        conn.commit()
        conn.close()    
        
      


class CalPage(Frame):
    def __init__(self, parent, controller, price,fname,weight,picName):
        Frame.__init__(self, parent)
        self.controller = controller
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        s.connect("/tmp/loadcell")
        s.send(b'Hello, world')
        data = s.recv(1024).decode()
        s.close()
        
        weight=int(data)
        

        label = Label(self, text="Price calculation page", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)

        midframe = Frame(self, relief=RAISED, borderwidth=1)
        midframe.pack(padx=10)
        midframe1 = Frame(self, relief=RAISED, borderwidth=0)
        midframe1.pack(padx=10)
        
        pName="img/"+picName
        #print("picName: ",pName)
        load = Image.open(pName)
        render = ImageTk.PhotoImage(load)
        img = Label(midframe, image=render)
        img.image = render
        img.pack()
        
       
        label = Label(midframe1, text="ราคา/หน่วย "+str(price)+" บาท/กก.")
        label.pack()
        label = Label(midframe1, text="น้ำหนัก " + str(weight/1000) + " กิโลกรัม")
        label.pack()
        label = Label(midframe1, text="ราคารวม " + str(price*(weight/1000)) + " บาท")
        label.pack()

        button1 = Button(self, text="Confirm payment", command=lambda: controller.show_frame("SalesPage",price,fname,weight,None))
        button1.pack(side="top", pady=30, padx=5)

class SalesPage(Frame):
    def __init__(self, parent, controller, price,fname,weight,picName):
        Frame.__init__(self, parent)
        self.controller = controller
        label = Label(self, text="Seved!!", font=controller.title_font)
        label.pack(side="top", fill="x", pady=10)
        idmat=0
        total=price*(weight/1000)
        conn = sqlite3.connect('demo1.sqlite')
        c = conn.cursor()
        c.execute("SELECT * fROM  material WHERE fname=?", (fname,))
        item = c.fetchall()
        for rows in item:
            idmat = rows[0]
        print(idmat)
        time = datetime.now().strftime("%B %d,%Y %I:%M%p")
        print(time)
        c.execute("INSERT INTO Selling(idMat,date,weight,total)VALUES(?,?,?,?)",(idmat,time,weight/1000,total))
        conn.commit()
        conn.close() 

        button1 = Button(self, text="Back to scanpage ", command=lambda: controller.show_frame("ScanPage",None,None,None,None))
        button1.pack(fill="x")



if __name__ == "__main__":
    app = SampleApp()
    camera = PiCamera()
    app.mainloop()