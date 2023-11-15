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
import pandas as pd
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
from serial.tools import list_ports
from tkinter import filedialog
import matplotlib.pyplot as plt
import tensorflow as tf
# Variables Globales
recording = False
serialDataRecorded = []
serialOpen = False
global ser
""" windows 
# Lista de puertos COM disponibles
OptionList = [
    "--Select a COM port--", "0",
    "1",
    "2",
    "3","4","5","6","7","8","9","10","11","12","13","14","15","16","17","18"
] 
"""
# windows
# Función para obtener la lista de puertos serie disponibles
def get_serial_ports():
    ports = list_ports.comports()
    return [port.device for port in ports]


#Actualizar la lista de opciones con los puertos disponibles
OptionList = get_serial_ports()
OptionList.insert(0, "--Select a COM port--")

sampling_rate = 360   # 360 samples per second
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
    global recording

    print('bucle iniciado')
    while serialOpen == True:
        try:
            # Intenta leer y convertir la línea a float
            reading = ser.readline().strip().decode('utf-8')
            reading_float = float(reading)
            
            # Si la conversión es exitosa, agregar el dato
            serialData.append(reading_float)

            if recording == True:
                serialDataRecorded.append(reading_float)

        except ValueError:
            # Aquí puedes manejar los datos mal formados o simplemente pasar
            print(f"Dato no válido recibido: {reading}")
            pass

        
# Actualizar la función startSerial para Windows
def startSerial():
    """
    Abre el puerto COM seleccionado y comienza a leer datos del mismo.
    """
    try:
        s = var.get()
        global ser
        ser = serial.Serial(s, 9600, timeout=20)  # Utiliza el nombre del puerto tal cual
        ser.close()
        ser.open()
        global serialOpen
        serialOpen = True
        global thread
        thread = threading.Thread(target=read_from_port, args=(ser,))
        thread.start()
        print('hilo iniciado')
        connectText.set("Conectado a " + s)
        labelConnect.config(fg="green")

        return serialOpen
        
    except SerialException:
        connectText.set("Error: no puerto serial")
        labelConnect.config(fg="red")
def startSerial():
    """
    Abre el puerto COM seleccionado y comienza a leer datos del mismo.
    """
    try:
        s = var.get()
        global ser
        ser = serial.Serial(s, 9600, timeout=20)  # Cambiado para usar el nombre del puerto en Linux
        ser.close()
        ser.open()
        global serialOpen
        serialOpen = True
        global thread
        thread = threading.Thread(target=read_from_port, args=(ser,))
        thread.start()
        print('hilo iniciado')
        connectText.set("Conectado a " + s)
        labelConnect.config(fg="green")

        return serialOpen
        
    except SerialException:
        connectText.set("Error: no puerto serial")
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



def calculate_heart_rate(data):
    # Detección de picos
    peaks, _ = scipy.signal.find_peaks(data, height=0)  # Ajusta el parámetro 'height' según sea necesario

    # Calcular los intervalos entre latidos (en número de muestras)
    ibi = np.diff(peaks)

    # Convertir a tiempo si se conoce la frecuencia de muestreo (fs)
    fs = 360  # Por ejemplo, 250 Hz
    ibi_time = ibi / fs

    # Calcular la frecuencia cardíaca en LPM
    heart_rate = 60 / ibi_time

    # Devuelve la frecuencia cardíaca promedio o como una serie, dependiendo de tus necesidades
    return np.mean(heart_rate)

def processRecording(data):
    """
    Procesa los datos registrados aplicando un filtro Savitzky-Golay y una corrección de línea de base,
    calcula la frecuencia cardíaca y guarda todo en un archivo CSV.

    Args:
        data (list): Los datos registrados.
    """
    # Aplicar filtro Savitzky-Golay
    z = scipy.signal.savgol_filter(data, 11, 3)
    data2 = np.asarray(z, dtype=np.float32)
    a = len(data)

    # Corrección de línea de base
    base = peakutils.baseline(data2, 2)
    y = data2 - base

    # Calcular la frecuencia cardíaca
    heart_rate_data = calculate_heart_rate(y)

    # Pedir al usuario que elija el nombre y ubicación del archivo
    directory = tk.filedialog.asksaveasfilename(defaultextension=".csv", filetypes=(("CSV file", "*.csv"), ("All Files", "*.*")))
    if directory is None:
        return

    # Crear DataFrame con los datos originales, procesados y la frecuencia cardíaca
    df = pd.DataFrame({'Time': range(a), 'Original_Data': data, 'ECG_Signal': y, 'Heart_Rate': heart_rate_data})

    # Guardar DataFrame como CSV
    df.to_csv(directory, index=False)



    
def load_studio(file_path):
    """
    Carga un estudio guardado anteriormente en varios formatos de archivo.
    """
    global serialData

    if file_path.endswith('.xls') or file_path.endswith('.xlsx'):
        data = pd.read_excel(file_path, engine='openpyxl')
    elif file_path.endswith('.csv'):
        data = pd.read_csv(file_path)
    elif file_path.endswith('.txt'):
        # Suponiendo que el archivo TXT tiene una columna 'heart_rate', separada por comas
        data = pd.read_csv(file_path, sep=",", header=None, names=["Heart_Rate"])
    elif file_path.endswith('.dat'):
        # Aquí deberás añadir la lógica para leer archivos .dat
        pass
    else:
        raise ValueError("Formato de archivo no soportado")

    serialData = data['Heart_Rate'].tolist()
    studio_text.set("Estudio cargado")
    return data 

def animateStatic(i, ax):
    """
    Actualiza el gráfico en vivo con los datos más recientes.
    Args:
        i (int): el número de fotograma actual.
        ax (matplotlib.axes.Axes): Ejes en los que dibujar el gráfico.
    """
    global data
    window_size = 2 * sampling_rate  # 10 segundos de datos
    start_index = max(0, i - window_size)
    end_index = i
    ax.clear()
    ax.plot(data['ECG_Signal'][start_index:end_index])
    ax.set_xlim(start_index, end_index)
    ax.set_title("Señal ECG en simulacion")
    ax.set_xlabel("Muestras")
    ax.set_ylabel("Señal ECG (mV)")

def iniciar_animacion():
    global data
    fig, ax = plt.subplots()  # Crear una nueva figura y ejes
    ani = animation.FuncAnimation(fig, animateStatic, fargs=(ax,), frames=len(data), interval=(1000/sampling_rate)/4, blit=False)
    #ani = FuncAnimation(fig, animate, frames=range(len(data)), interval=(1000/sampling_rate)/2, blit=False)
    plt.show()

def select_file():
    global data
    root = tk.Tk()
    root.withdraw()  # Oculta la ventana principal de Tk
    file_path = filedialog.askopenfilename()
    if file_path:
        data = load_studio(file_path)  # Actualiza la variable global data
        iniciar_animacion()  # Ahora data ya está actualizada para usar en iniciar_animacion
    

def predict(progress_bar, btn_gen_report):
    """
    Toma el estudio cargado y lo pasa por el modelo de deep learning para predecir arritmias.
    Devuelve las predicciones y actualiza la barra de progreso y el estado del botón de reporte.
    """
    global global_predictions # Variable global para almacenar las predicciones
    model = tf.keras.models.load_model('ECGguideDL/model.h5')
    ecg_signal = data['ECG_Signal'].tolist()

    desired_length = 720
    num_segments = len(ecg_signal) // desired_length
    if len(ecg_signal) % desired_length != 0:
        padding_length = (num_segments + 1) * desired_length - len(ecg_signal)
        ecg_signal = np.pad(ecg_signal, (0, padding_length), 'constant')
        num_segments += 1

    global_predictions = []
    for i in range(num_segments):
        segment = ecg_signal[i * desired_length:(i + 1) * desired_length]
        segment = segment.reshape(1, -1, 1)  # Redimensionar
        prediction = model.predict(segment)
        global_predictions.extend(prediction)
        # Actualizar la barra de progreso
        progress = (i + 1) / num_segments * 100
        progress_bar['value'] = progress
        progress_bar.update_idletasks()

    # Activa el botón de generar reporte después de completar la predicción
    btn_gen_report['state'] = 'normal'

    return global_predictions


def generate_report():
    """
    Genera un archivo que contiene las anotaciones creadas por el modelo.
    Agrega una etiqueta para cada ventana de 720 datos en función de la probabilidad de arritmia.
    """
    global global_predictions

    if global_predictions is None:
        print("No hay predicciones disponibles.")
        return

    # Generar etiquetas para cada ventana de 720 datos
    expanded_labels = []
    for pred in global_predictions:
        label = 1 if pred > 0.5 else 0
        expanded_labels.extend([label] * 720)  # Replicar la etiqueta para cada dato en la ventana

    # Asegurarse de que la longitud de las etiquetas coincida con la de los datos
    if len(expanded_labels) > len(data):
        expanded_labels = expanded_labels[:len(data)]
    elif len(expanded_labels) < len(data):
        expanded_labels.extend([0] * (len(data) - len(expanded_labels)))  # Rellenar con 0 si es necesario

    data['Etiquetas'] = expanded_labels

    save_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Seleccione dónde guardar el archivo CSV"
    )

    if save_path:
        data.to_csv(save_path, index=False)
        print(f"Archivo guardado en: {save_path}")
    else:
        print("Guardado cancelado.")



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

model_text = tk.StringVar(window)
model_text.set("Modelo de deep learning")
label_model = tk.Label(fr_buttons, textvariable=model_text, font=('Helvetica', 15), fg='green')
label_model.grid(row=7, column=0, sticky="ew",padx=10)

btn_load_studio = tk.Button(fr_buttons, text="Cargar Estudio", command=select_file)
btn_load_studio.grid(row=8, column=0, sticky="ew", padx=10, pady=5)

studio_text = tk.StringVar(window) 
studio_text.set("No hay estudio cargado")
label_studio = tk.Label(fr_buttons, textvariable=studio_text, font=('Helvetica', 12), fg='black')
label_studio.grid(row=9, column=0, sticky="ew",padx=10)

btn_prediction = tk.Button(fr_buttons, text="Predecir", command=lambda: threading.Thread(target=predict, args=(progress_bar, btn_gen_report)).start())
btn_prediction.grid(row=10, column=0, sticky="ew", padx=10, pady=5)

# Barra de progreso
progress_bar = ttk.Progressbar(fr_buttons, orient='horizontal', mode='determinate', length=100)
progress_bar.grid(row=11, column=0, pady=10)

btn_gen_report = tk.Button(fr_buttons, text="Generar Reporte", command=generate_report,state='disabled')
btn_gen_report.grid(row=12, column=0, sticky="ew", padx=10, pady=5)




## crear un timer para mostrar el tiempo de grabacion 
timer_text = tk.StringVar(window)

                    


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