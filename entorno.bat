@echo off
echo Creando entorno virtual...
pip install virtualenv
virtualenv myenv

echo Activando entorno virtual...
call .\myenv\Scripts\activate

echo Instalando librerias...
pip install pandas matplotlib numpy scipy pyserial peakutils xlwt tensorflow

echo Entorno y librerias listos.
pause
