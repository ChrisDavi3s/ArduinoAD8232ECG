"""
This code is a GUI application for a heart rate monitor. It uses tkinter for the GUI, 
matplotlib for plotting, and serial for communication with an Arduino board. 
The application allows the user to select a COM port, start and stop the serial communication, 
and record the data. The recorded data is processed using scipy and peakutils, 
and then saved as an Excel file. The GUI is composed of a live plot of the data 
and several buttons for controlling the application. 
"""
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

# Global variables
recording = False
serialDataRecorded = []
serialOpen = False
global ser

# List of available COM ports
OptionList = [
    "--Select a COM port--", "0",
    "1",
    "2",
    "3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18"
] 

connected = False
serialData = [0] * 70

def read_from_port(ser):
    """
    Reads data from the serial port and appends it to serialData.
    If recording is enabled, also appends the data to serialDataRecorded.

    Args:
        ser (serial.Serial): The serial port object.
    """
    global serialOpen
    global serialData
    global serialDataRecorded
    print('loop started')
    while serialOpen == True:
        reading = float(ser.readline().strip())
        serialData.append(reading)

        if recording == True:
            serialDataRecorded.append(reading)
        
def startSerial():
    """
    Opens the selected COM port and starts reading data from it.
    """
    try:
        s =  var.get()
        global ser
        ser = serial.Serial('COM' + s , 9600, timeout=20)
        ser.close()
        ser.open()
        global serialOpen
        serialOpen = True
        global thread
        thread = threading.Thread(target=read_from_port, args=(ser,))
        thread.start()
        print('thread started')
        connectText.set("Connected to COM" + s)
        labelConnect.config(fg="green")

        return serialOpen
        
    except SerialException:
        connectText.set("Error: Py?")
        labelConnect.config(fg="red")
    
def kill_Serial():
    """
    Closes the serial port.
    """
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
    """
    Updates the live plot with the latest data from serialData.

    Args:
        i (int): The current frame number.
    """
    global serialData
    if len(serialData) > 70:
        serialData=serialData[-70:]
    data = serialData.copy()
    data = data[-70:]
    global ax
    x = np.linspace(0,69, dtype ='int', num = 70)  

    ax.clear()
    ax.plot(x,data)

def startRecording():
    """
    Enables recording of data from the serial port.
    """
    global recording
    if serialOpen:
        recording = True
        recordText.set("Gravando . . . ")
        labelRecord.config(fg="red")
    else:
        messagebox.showinfo("Error", "Por favor inicie el monitor serial")

def stopRecording():
    """
    Disables recording of data from the serial port and processes the recorded data.
    """
    global recording
    global serialDataRecorded
    
    if recording == True:
        recording = False
        recordText.set("No grabar ")
        labelRecord.config(fg="black")
        processRecording(serialDataRecorded)
        serialDataRecorded = []
    else:
        messagebox.showinfo("Eror", "no estabas grabando!")

def processRecording(data):
    """
    Processes the recorded data by applying a Savitzky-Golay filter and baseline correction,
    and saves the processed data as an Excel file.

    Args:
        data (list): The recorded data.
    """
    z = scipy.signal.savgol_filter(data, 11, 3)
    data2 = np.asarray(z,dtype=np.float32)
    a = len(data)
    base = peakutils.baseline(data2, 2)
    
    y = data2 - base
   
    directory = tk.filedialog.asksaveasfilename(defaultextension=".xls", filetypes=(("Excel Sheet", "*.xls"),("All Files", "*.*") ))
    if directory is None:
        return
    
    book = xlwt.Workbook(encoding="utf-8")
    sheet1 = book.add_sheet("Sheet 1")
    for i in range(a):
        sheet1.write(i,0,i)
        sheet1.write(i,1,y[i])
    
    book.save(directory)

# Create the GUI window
window = tk.Tk()
window.title("Heart Rate Monitor v0.1")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

# Create the live plot
fig = Figure(figsize=(6, 5), dpi=50)
ax=fig.add_subplot(1,1,1)
ax.set_xlim([0, 10])
ax.set_ylim([0, 150])
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()

# Create the GUI elements
lbl_live = tk.Label( text="Live Data:", font=('Helvetica', 12), fg='red')
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)

connectText = tk.StringVar(window)
connectText.set("Not connected")
labelConnect = tk.Label(fr_buttons, textvariable=connectText, font=('Helvetica', 12), fg='red')
labelConnect.grid(row=0, column=0, sticky="ew",padx=10)

var = tk.StringVar(window)
var.set(OptionList[0])
opt_com = tk.OptionMenu(fr_buttons, var, *OptionList)
opt_com.config(width=20)
opt_com.grid(row=1, column=0, sticky="ew", padx=10)

btn_st_serial = tk.Button(fr_buttons, text="Open Serial", command=startSerial)
btn_st_serial.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

btn_stop_serial = tk.Button(fr_buttons, text="Close Serial", command=kill_Serial)
btn_stop_serial.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

recordText = tk.StringVar(window)
recordText.set("Not Recording")
labelRecord = tk.Label(fr_buttons, textvariable=recordText, font=('Helvetica', 12), fg='black')
labelRecord.grid(row=4, column=0, sticky="ew",padx=10)

btn_st_rec = tk.Button(fr_buttons, text="Start Recording", command=startRecording)
btn_st_rec.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

btn_stop_rec = tk.Button(fr_buttons, text="Stop Recording", command=stopRecording)
btn_stop_rec.grid(row=6, column=0, sticky="ew", padx=10, pady=5)

fr_buttons.grid(row=0, column=0, sticky="ns")
lbl_live.grid(row=1, column=1, sticky="nsew")
canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")

# Close the serial port and destroy the window when quitting
def ask_quit():
    if tk.messagebox.askokcancel("Quit", "This will end the serial connection and close the application."):
        kill_Serial()
        window.destroy()

window.protocol("WM_DELETE_WINDOW", ask_quit)
ani = animation.FuncAnimation(fig, animate, interval=50)
window.mainloop()