"""
Este código es una aplicación GUI para un monitor de frecuencia cardíaca. Utiliza tkinter para la GUI,
matplotlib para trazar y serial para comunicación con una placa Arduino.
La aplicación permite al usuario seleccionar un puerto COM, iniciar y detener la comunicación serie,
y registrar los datos. Los datos registrados se procesan utilizando scipy y peakutils,
y luego se guarda como un archivo de Excel. La GUI se compone de una gráfica en vivo de los datos.
y varios botones para controlar la aplicación.
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

# Variables Globales
recording = False
serialDataRecorded = []
serialOpen = False
global ser

# Lista de puertos COM disponibles
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
    Lee datos del puerto serie y los agrega a serialData.
     Si la grabación está habilitada, también agrega los datos a serialDataRecorded.

    Args:
         ser (serial.Serial): el objeto del puerto serie.
    """
    global serialOpen
    global serialData
    global serialDataRecorded
    print('bucle iniciado')
    while serialOpen == True:
        reading = float(ser.readline().strip())
        serialData.append(reading)

        if recording == True:
            serialDataRecorded.append(reading)
        
def startSerial():
    """
    Abre el puerto COM seleccionado y comienza a leer datos del mismo.
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
        print('hilo iniciado')
        connectText.set("Conectado a COM" + s)
        labelConnect.config(fg="green")

        return serialOpen
        
    except SerialException:
        connectText.set("Error: Py?")
        labelConnect.config(fg="red")
    
def kill_Serial():
    """
    Cierra el puerto serie.
    """
    try:
        global ser
        global serialOpen
        serialOpen = False
        time.sleep(1)
        ser.close()
        connectText.set("No conectado")
        labelConnect.config(fg="red")

        print('serial cerrado')
    except:
        connectText.set("No se pudo finalizar el serial ")


def animate(i):
    """
    Actualiza el gráfico en vivo con los datos más recientes de los datos en serie. 
        Args: i (int): 
    el número de fotograma actual.
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
    Permite grabar datos desde el puerto serie.t.
    """
    global recording
    if serialOpen:
        recording = True
        recordText.set("Grabando . . . ")
        labelRecord.config(fg="red")
    else:
        messagebox.showinfo("Error", "Por favor inicie el monitor serial")

def stopRecording():
    """
    Desactiva la grabación de datos desde el puerto serie y procesa los datos grabados.
    """
    global recording
    global serialDataRecorded
    
    if recording == True:
        recording = False
        recordText.set("No grabar")
        labelRecord.config(fg="black")
        processRecording(serialDataRecorded)
        serialDataRecorded = []
    else:
        messagebox.showinfo("Eror", "no estabas grabando!")

def processRecording(data):
    """
    Processes los datos registrados aplicando un filtro Savitzky-Golay y una corrección de línea de base,
     y guarda los datos procesados como un archivo de Excel.

    Args:
        data (list): Los datos registrados.
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

# Crear la ventana GUI
window = tk.Tk()
window.title("Monitor de frecuencia cardíaca v0.1")
window.rowconfigure(0, minsize=800, weight=1)
window.columnconfigure(1, minsize=800, weight=1)

# Crear el grafico en vivo
fig = Figure(figsize=(6, 5), dpi=50)
ax=fig.add_subplot(1,1,1)
ax.set_xlim([0, 10])
ax.set_ylim([0, 150])
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.draw()

# Crear los elementos GUI
lbl_live = tk.Label( text="Live Data:", font=('Helvetica', 12), fg='red')
fr_buttons = tk.Frame(window, relief=tk.RAISED, bd=2)

connectText = tk.StringVar(window)
connectText.set("No conectado")
labelConnect = tk.Label(fr_buttons, textvariable=connectText, font=('Helvetica', 12), fg='red')
labelConnect.grid(row=0, column=0, sticky="ew",padx=10)

var = tk.StringVar(window)
var.set(OptionList[0])
opt_com = tk.OptionMenu(fr_buttons, var, *OptionList)
opt_com.config(width=20)
opt_com.grid(row=1, column=0, sticky="ew", padx=10)

btn_st_serial = tk.Button(fr_buttons, text="Abrir Serial", command=startSerial)
btn_st_serial.grid(row=2, column=0, sticky="ew", padx=10, pady=5)

btn_stop_serial = tk.Button(fr_buttons, text="Cerrar Serial", command=kill_Serial)
btn_stop_serial.grid(row=3, column=0, sticky="ew", padx=10, pady=5)

recordText = tk.StringVar(window)
recordText.set("No Grabando")
labelRecord = tk.Label(fr_buttons, textvariable=recordText, font=('Helvetica', 12), fg='black')
labelRecord.grid(row=4, column=0, sticky="ew",padx=10)

btn_st_rec = tk.Button(fr_buttons, text="Iniciar Grabacion", command=startRecording)
btn_st_rec.grid(row=5, column=0, sticky="ew", padx=10, pady=5)

btn_stop_rec = tk.Button(fr_buttons, text="Terminar Grabacion", command=stopRecording)
btn_stop_rec.grid(row=6, column=0, sticky="ew", padx=10, pady=5)

fr_buttons.grid(row=0, column=0, sticky="ns")
lbl_live.grid(row=1, column=1, sticky="nsew")
canvas.get_tk_widget().grid(row=0, column=1, sticky="nsew")

# Close the serial port and destroy the window when quitting
def ask_quit():
    if tk.messagebox.askokcancel("Terminar", "Esto finalizará la conexión en serial y cerrará la aplicación."):
        kill_Serial()
        window.destroy()

window.protocol("WM_DELETE_WINDOW", ask_quit)
ani = animation.FuncAnimation(fig, animate, interval=50)
window.mainloop()