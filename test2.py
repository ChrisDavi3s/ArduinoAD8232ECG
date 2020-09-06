import tkinter as tk
from tkinter import ttk 

import matplotlib.animation as animation
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from tkinter import messagebox
import scipy.signal
import serial
from serial import SerialException
import peakutils
import xlwt
import threading
import time

recording = False
serialDataRecorded = []
serialOpen = False
global ser

OptionList = [
"--Select a COM port--", "0",
"1",
"2",
"3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18"
] 

connected = False
serialData = [0] * 70


def read_from_port(ser):
    global serialOpen
    global serialData
    global serialDataRecorded
    print('loop started')
    while serialOpen == True:
        reading = float(ser.readline().strip())
        serialData.append(reading)
        #print(serialData)

        if recording == True:
            serialDataRecorded.append(reading)
           # print(serialDataRecorded)
        
    





def startSerial():
    try:
        s =  var.get()
        global ser
        ser = serial.Serial('COM' + s , 9600, timeout=20)
        ser.close()
        ser.open()
        global serialOpen
        serialOpen = True
        #print("Port " + 'COM' + s + " is open!")
        global thread
        thread = threading.Thread(target=read_from_port, args=(ser,))
        thread.start()
        print('thread started')
        connectText.set("Connected to COM" + s)
        labelConnect.config(fg="green")


        return serialOpen
        
    except SerialException:
        connectText.set("Error: wrong port?")
        labelConnect.config(fg="red")
    
def kill_Serial():
     try:
       global ser
       global serialOpen
       serialOpen = False
       time.sleep(1)
       ser.close()
       connectText.set("Not connected")
       labelConnect.config(fg="red")

       print('serial closed')
     except:
       connectText.set("Failed to end serial ")


def animate(i):
    global serialData
    if len(serialData) > 70:
            serialData=serialData[-70:]
    data = serialData.copy()
    data = data[-70:]
    global ax
    #length = len(data)
    #x = np.linspace(0,length-1, dtype ='int', num = length)  
    x = np.linspace(0,69, dtype ='int', num = 70)  


    #if len(x) > 31:
    #    x = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29]
    #    data = data[-30:]
    
    
    #print(i)
    ax.clear()
    ax.plot(x,data)

def startRecording():
    global recording
    if serialOpen:
        recording = True
        recordText.set("Recording . . . ")
        labelRecord.config(fg="red")
    else:
       messagebox.showinfo("Error", "Please start the serial monitor")


    
    

def stopRecording():
    global recording
    global serialDataRecorded
    
    if recording == True:
        recording = False
        recordText.set("Not Recording  ")
        labelRecord.config(fg="black")
        processRecording(serialDataRecorded)
        serialDataRecorded = [] # this might be risky here
    else:
        messagebox.showinfo("Error", "You weren't recording!")




def processRecording(data):
    
    z = scipy.signal.savgol_filter(data, 11, 3)
    data2 = np.asarray(z,dtype=np.float32)
    a = len(data)
    base = peakutils.baseline(data2, 2)
    
    
    
    #x = np.linspace(0,a-1, dtype ='int', num = a)  
    
    y = data2 - base
    #y=data
   
    directory = tk.filedialog.asksaveasfilename(defaultextension=".xls", filetypes=(("Excel Sheet", "*.xls"),("All Files", "*.*") ))
    if directory is None: # asksaveasfile return `None` if dialog closed with "cancel".
        return

    
    
    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet("Sheet 1")
    for i in range(a):
       
        sheet1.write(i,0,i)
        sheet1.write(i,1,y[i])
    
    
    
    book.save(directory)

    

    




window = tk.Tk()
window.title("Heart Rate Monitor v0.1")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)


 # set the default option


fig = Figure(figsize=(6, 5), dpi=50)


ax=fig.add_subplot(1,1,1)
ax.set_xlim([0, 10])
ax.set_ylim([0, 150])


canvas = FigureCanvasTkAgg(fig, master=window)  # A tk.DrawingArea.
canvas.draw()















lbl_live = tk.Label( text="Live Data:", font=('Helvetica', 12), fg='red')
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)


# Select com port label
connectText = tk.StringVar(window)
connectText.set("Not connected")
labelConnect = tk.Label(fr_buttons, textvariable=connectText, font=('Helvetica', 12), fg='red')
labelConnect.grid(row=0, column=0, sticky="ew",padx=10)

# Drop down for com port selection
var = tk.StringVar(window)
var.set(OptionList[0])
#combobox = ttk.Combobox(window, values = var)
opt_com = tk.OptionMenu(fr_buttons, var, *OptionList)
opt_com.config(width=20)
#combobox.grid(row=1, column=0, sticky="ew", padx=10)
opt_com.grid(row=1, column=0, sticky="ew", padx=10)

#The button to start Serial
btn_st_serial = tk.Button(fr_buttons, text="Open Serial", command=startSerial)
btn_st_serial.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

#The button to stop Serial
btn_stop_serial = tk.Button(fr_buttons, text="Close Serial", command=kill_Serial)
btn_stop_serial.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

# Recording label
recordText = tk.StringVar(window)
recordText.set("Not Recording")
labelRecord = tk.Label(fr_buttons, textvariable=recordText, font=('Helvetica', 12), fg='black')
labelRecord.grid(row=4, column=0, sticky="ew",padx=10)

#Button to start recording
btn_st_rec = tk.Button(fr_buttons, text="Start Recording", command=startRecording)
btn_st_rec.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

#button to stop recording
btn_stop_rec = tk.Button(fr_buttons, text="Stop Recording", command=stopRecording)
btn_stop_rec.grid(row=6, column=0, sticky="ew", padx=10, pady=5)








fr_buttons.grid(row=0, column=0, sticky="ns")
lbl_live.grid(row=1, column=1, sticky="nsew")
canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")




#This closes the serial and destroys the window
def ask_quit():
    if tk.messagebox.askokcancel("Quit", "This will end the serial connection :)"):
        kill_Serial()
        window.destroy()


window.protocol("WM_DELETE_WINDOW", ask_quit)
ani = animation.FuncAnimation(fig, animate, interval=50)
window.mainloop()