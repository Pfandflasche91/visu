import serial
from serial import Serial

import csv
import os

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk
from datetime import datetime

from functools import partial
from ringbuffer import MyCircularQueue 
LARGE_FONT=("Verdana",12)
style.use("ggplot")

sig_val = 0

class dataStorage:
    
    def __init__(self,):
        self.signalName = ""
        self.signalUnit = ""
        self.signalCount = 0
        self.signalValues = [None]
    
    def setsignalCount(self,con):
        self.signalCount = con
        self.signalValues = [None] * self.signalCount    
    
    def setsignalName(self,con):
        self.signalName = con
    
    def setsignalUnit(self, con):
        self.signalUnit = con
    
    def writeData(self,msg):
        start = -5
        end = 0 
        for i in range(int(self.signalCount)):
            start = start + 5
            end = end +5#
            self.signalValues[i] = msg[start:end]   
                 
def readSerial(application,page):
    data = dataStorage()
    global sig_val
    if application.getserialCommunication(page).inWaiting() > 0:
        #TODO: get rid of direct call of variabls 
                message = application.getserialCommunication(page).read_until()
                data.setsignalName(str(message)[2:7])
                data.setsignalUnit(str(message)[8:9])
                data.setsignalCount(int(str(message)[10:12]))
                end = data.signalCount*5+13
                data.writeData(str(message)[13:end])
                for i in range(data.signalCount):
                    application.enqueue(page,float(data.signalValues[i]),sig_val)  
                if sig_val == 0 :
                    sig_val = 1
                else:
                    sig_val = 0 
    


def animate(frame, application, page):
    x_ = []
    for x in range(application.getqueue(page,0).len()):
        x_.append(x)
    try: 
        if application.getisConnected(page):
            readSerial(application,page)       
    except:
        print("expection")
        pass
    
    ax1 = application.getplot(page)
    ax2 = application.getplotax2(page)
    ax1.clear() 
    ax2.clear() 
    ax1.plot(x_,application.getqueuevalue(page,0))          
    ax2.plot(x_,application.getqueuevalue(page,1))         
    
class visu(tk.Tk):
    
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        #TODO
        # tk.Tk.iconbitmap(self, default="bild.ico")
        tk.Tk.wm_title(self,"Visualization")
        
        container = tk.Frame(self)
        container.pack(side="top",fill="both", expand = True)
        container.grid_rowconfigure(0,weight =1)
        container.grid_columnconfigure(0, weight =1)
        
        self.frames = {}
        frame = StartPage(container, self)
        self.frames[StartPage]= frame
        frame.grid(row=0, column =0, sticky = "nsew")
        frame.tkraise()
        
    def getserialCommunication(self,con) :
        return self.frames[con].getserialCommunication()
    
    def getisConnected(self,con):
        return self.frames[con].getisConnected()
    
    def getfig(self,con):
        return self.frames[con].getfig()
    
    def getplot(self,con):
        return self.frames[con].getplot()
    
    def getplotax2(self,con):
        return self.frames[con].getplotax2()
    
    def getqueue(self,con,hub):
        return self.frames[con].getqueue(hub)
    
    def enqueue(self,con,value,hub):
        self.frames[con].enqueue(value,hub)
    
    def getqueuevalue(self,con,hub):
        return self.frames[con].getqueuevalue(hub)
        
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        self.serialCommunication = None
        self.isConnected = False
        self.fig = Figure(figsize=(5,5),dpi =100)
        self.ax1 = self.fig.add_subplot(2,1,1)
        self.ax2 = self.fig.add_subplot(2,1,2)
        self.queue = [None] * 2
        self.queue[0] = MyCircularQueue(50)
        self.queue[1] = MyCircularQueue(50)
        
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text="Project Visu V0.0", font = LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        #style
        style = ttk.Style()
        style.configure("Button.TFrame")
        style.configure("SerialCommunication.TFrame", background= "green")
        style.configure("UI.TFrame")
        
        frame_serialCommunication=ttk.Frame(self,style="Button.TFrame")
        frame_serialCommunication.pack(anchor=tk.NW)
        label_connection= tk.Label(frame_serialCommunication,text= "Serial Connection:", font= LARGE_FONT)
        label_connection.pack( anchor=tk.NW)
        frame_button= ttk.Frame(frame_serialCommunication,style = "SerialCommunication.TFrame")
        frame_button.pack(anchor=tk.NW)
        frame_ui=ttk.Frame(self,style="UI.TFrame")
        frame_ui.pack()
        
        buttonconnect =ttk.Button(frame_button, text="connect",
                         command = self.connect)
        buttonconnect.grid(ipadx=10, ipady=8,row=0,column = 0)
        

        button_disconnect =ttk.Button(frame_button, text="disconnect",
                         command = self.disconnect)
        button_disconnect.grid(ipadx=10, ipady=8,row=0,column = 1)
        
        canvas = FigureCanvasTkAgg(self.fig,frame_ui)
        canvas.draw()
        canvas.get_tk_widget().grid(row=0,column = 0, sticky="nw")
        frame_control=ttk.Frame(frame_ui)
        frame_control.grid(ipadx=50, ipady=225,row=0,column = 1)
        label_control= tk.Label(frame_control,text= "Control:", font= LARGE_FONT)
        label_control.grid(row=0,column = 0,sticky="nw")
        label_control= tk.Label(frame_control,text= "Enter Angle between 0° and 180°:")
        label_control.grid(row=1,column = 0,sticky="nw")
        entry_angle= ttk.Entry(frame_control)
        entry_angle.grid(row=2,column = 0 ,sticky="nw")
        
        button_send = ttk.Button(frame_control, text="send",
                         command = partial(self.send,entry=entry_angle,signalname="motor",unit="degree",count=1))
        button_send.grid(row=2,column = 1,sticky="nw")
        
        button_savetocsv= ttk.Button(frame_control, text="save to csv",
                         command = partial(self.savetocsv, data=self.queue))
        button_savetocsv.grid(row=3,column = 0,sticky="nw")
    
    def savetocsv(self,data):
        print(os.getcwd())
        with open (os.getcwd()+"/test.csv","w") as f:
            writer = csv.writer(f)
            writer.writerow(data[0].get())  
     
    def fetchentries(self,entry):
        return entry.get()
        
    def send(self,entry,signalname,unit,count):
        if self.isConnected :
            value=self.fetchentries(entry)
            #TODO fix this
            if int(value)<0:
                value = "000"    
            elif int(value)<10 and int(value) >=0:
                value="00"+ value
            elif int(value)>=10 and int(value)<100:
                value ="0" + value
            elif int(value)>=180:
                value = "180"
                
            self.serialCommunication.write((signalname + "_" + unit +"_"+ str(count) +"_"+ value +"\n").encode())
            #TODO: send over serial com
            print((signalname + "_" + unit +"_"+ str(count) +"_"+ value +"\n"))
        
    def connect(self):
        print("connect")
        try:
            self.serialCommunication = serial.Serial('COM5',56000)
            print("serial com established")
            print(self.serialCommunication)
            self.isConnected = True
        except:
            print("Connection not possible !!!")
    
    def disconnect(self):
        try:
            self.serialCommunication.close()
            print("disconnected!!")
            self.isConnected = False
        except:
            print("Cant disconnect")    
    def getisConnected(self):
        return self.isConnected
            
    def getserialCommunication(self):
        return self.serialCommunication  
    
    def getfig(self):
        return self.fig  
    
    def getplot(self):
        return self.ax1
    
    def getplotax2(self):
        return self.ax2
                     
    def getqueue(self,con):
        return self.queue[con]
    
    def enqueue(self,con,hub):
        self.queue[hub].enqueue(con)

    def getqueuevalue(self,con):
        return self.queue[con].get()
                

if __name__ == "__main__":

    app = visu()
    ani = animation.FuncAnimation(app.getfig(StartPage), partial(animate, application = app, page = StartPage), interval = 100)
    app.mainloop()