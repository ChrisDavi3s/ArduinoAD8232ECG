#!/bin/bash

# Definir el nombre del entorno virtual
ENV_NAME="ecg_env"

# Crear el entorno virtual
python3 -m venv $ENV_NAME

# Activar el entorno virtual
source $ENV_NAME/bin/activate

# Actualizar pip
pip install --upgrade pip

# Instalar paquetes específicos
pip install numpy scipy matplotlib tk peakutils xlwt

# Instalar TensorFlow (esto instalará la última versión, puedes especificar una versión si lo necesitas)
pip install tensorflow

# Agregar cualquier otro paquete que requieras
# pip install <paquete>

echo "Entorno virtual y paquetes instalados."
# activar el entorno virtual  si este aun no esta activado


source $ENV_NAME/bin/activate