from machine import Pin, ADC
import network
import time
import urequests

# Configuración del WiFi
ssid = 'Tu_SSID'
password = 'Tu_contraseña'

# Conexión a WiFi
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect(ssid, password)

# Esperar hasta que la conexión sea exitosa
while not wlan.isconnected():
    time.sleep(1)

# Configuración del sensor AD8232
adc = ADC(Pin(34))  # Asumiendo que el sensor está conectado al pin 34
adc.atten(ADC.ATTN_11DB)  # Configuración para un rango de lectura completo

def leer_sensor():
    valor = adc.read()
    return valor

def enviar_datos(valor):
    url = 'http://tu_servidor/datos'  # URL del servidor al que enviar los datos
    headers = {'content-type': 'application/json'}
    data = {'valor_ecg': valor}

    try:
        response = urequests.post(url, json=data, headers=headers)
        print(response.text)
    except Exception as e:
        print('Error al enviar los datos:', e)

# Ciclo principal
while True:
    valor_ecg = leer_sensor()
    enviar_datos(valor_ecg)
    time.sleep(1)  # Esperar 1 segundo antes de la próxima lectura
