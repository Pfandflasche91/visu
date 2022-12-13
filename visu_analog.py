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

LARGE_FONT=("Verdana",12)
style.use("ggplot")

fig = Figure(figsize=(5,5),dpi =100)
ax1 = fig.add_subplot(1,1,1)
print("setup fig")

def animate(i):
    x_ = []
    for x in range(queue.len()):
        x_.append(x)
    
    if ser.inWaiting() > 0:
            data = ser.read(5)
           # print("recieved: "+ str(data)[2:7])
            queue.enqueue(float(str(data)[2:7]))
    ax1.clear()  
    ax1.plot(x_,queue.get())          
            
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
        for F in(StartPage,PageOne):
            frame = F(container, self)
            self.frames[F]= frame
            frame.grid(row=0, column =0, sticky = "nsew")
        self.show_frame(StartPage)
    
    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class StartPage(tk.Frame):
    def __init__(self, parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text="StartPage", font = LARGE_FONT)
        label.pack(pady=10,padx=10)
        
        button1 =ttk.Button(self, text="visualization",
                           command = lambda: controller.show_frame(PageOne))
        button1.pack()
        
class PageOne(tk.Frame):
    def __init__(self,parent, controller):
        tk.Frame.__init__(self,parent)
        label = tk.Label(self,text="Visualization: Analog Signals", font = LARGE_FONT)
        label.pack(pady=10,padx=10)
        button1 =ttk.Button(self, text="backtohome",
                           command = lambda: controller.show_frame(StartPage))
        button1.pack()

        canvas = FigureCanvasTkAgg(fig,self)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP,fill=tk.BOTH, expand=True)
            
            
class MyCircularQueue():

    def __init__(self, k):
        self.k = k
        self.queue = [1] * k
        self.head = self.tail = -1

    # Insert an element into the circular queue
    def enqueue(self, data):

        if ((self.tail + 1) % self.k == self.head):
            for i in range(self.k -1):
                self.queue[i] = self.queue[i+1]
            self.queue[self.k -1] = data    
            #print("The circular queue is full\n")

        elif (self.head == -1):
            self.head = 0
            self.tail = 0
            self.queue[self.tail] = data
        else:
            self.tail = (self.tail + 1) % self.k
            self.queue[self.tail] = data
    
    def get(self):
        return self.queue[:]
    def len(self):
        return len(self.queue)    
    
    def printCQueue(self):
        if(self.head == -1):
            print("No element in the circular queue")

        elif (self.tail >= self.head):
            for i in range(self.head, self.tail + 1):
                print(self.queue[i], end=" ")
            print()
        else:
            for i in range(self.head, self.k):
                print(self.queue[i], end=" ")
            for i in range(0, self.tail + 1):
                print(self.queue[i], end=" ")
            print()
            
global queue

if __name__ == "__main__":
    #run()
    queue = MyCircularQueue(250)
    ser = serial.Serial('COM5',56000)
    print("serial com established")
    app = visu()
    ani = animation.FuncAnimation(fig, animate, interval = 10)
    app.mainloop()