import serial
from serial import Serial

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib import style
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure

import tkinter as tk
from tkinter import ttk

from functools import partial
from ringbuffer import MyCircularQueue 
LARGE_FONT=("Verdana",12)
style.use("ggplot")


def animate(frame, application, page):
    
    x_ = []
    for x in range(application.getqueue(page).len()):
        x_.append(x)
    
    try: 
        if application.getisConnected(page):
            if application.getserialCommunication(page).inWaiting() > 0:
                    data = application.getserialCommunication(page).read(5)
                    application.enqueue(page,float(str(data)[2:7]))
    except:
        pass
    
    ax1 = application.getplot(page)
    ax1.clear()  
    ax1.plot(x_,application.getqueuevalue(page))          
            
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
    
    def getqueue(self,con):
        return self.frames[con].getqueue()
    
    def enqueue(self,con,value):
        self.frames[con].enqueue(value)
    
    def getqueuevalue(self,con):
        return self.frames[con].getqueuevalue()
        
class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        self.serialCommunication = None
        self.isConnected = False
        self.fig = Figure(figsize=(5,5),dpi =100)
        self.ax1 = self.fig.add_subplot(1,1,1)
        self.queue = MyCircularQueue(200)
        
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text="StartPage", font = LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        buttonconnect =ttk.Button(self, text="connect",
                         command = self.connect)
        buttonconnect.pack()

        button_disconnect = button1 =ttk.Button(self, text="disconnect",
                         command = self.disconnect)
        button_disconnect.pack()
        
        canvas = FigureCanvasTkAgg(self.fig,self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH, expand=True)
    
    def connect(self):
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
            self.isConnected = True
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
                     
    def getqueue(self):
        return self.queue
    
    def enqueue(self,con):
        self.queue.enqueue(con)

    def getqueuevalue(self):
        return self.queue.get()
                

if __name__ == "__main__":

    app = visu()
    ani = animation.FuncAnimation(app.getfig(StartPage), partial(animate, application = app, page = StartPage), interval = 10)
    app.mainloop()