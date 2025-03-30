from machine import Pin, I2C
from ssd1306 import SSD1306_I2C
import network
import time
import math

# Configuración de I2C en Raspberry Pi Pico W (usando I2C1)
SCL_PIN = 15  # GP15 como SCL
SDA_PIN = 14  # GP14 como SDA
WIDTH = 128   # Ancho de la pantalla OLED
HEIGHT = 64   # Alto de la pantalla OLED

i2c = I2C(1, scl=Pin(SCL_PIN), sda=Pin(SDA_PIN))

# Inicializar la pantalla OLED
oled = SSD1306_I2C(WIDTH, HEIGHT, i2c)

# Configuración del botón (con pull-up interno)
boton = Pin(18, Pin.IN, Pin.PULL_UP)

# Configuración WiFi
SSID = "Familia Ortiz"
PASSWORD = "GH030205"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)  # Activar WiFi
wifi.connect(SSID, PASSWORD)  # Conectar a la red

# Configuración de LEDs
led_midiendo = Pin(17, Pin.OUT)  # LED "Midiendo"
led_wifi = Pin(19, Pin.OUT)  # LED "WiFi"
led_avanzar = Pin(16, Pin.OUT)  # LED "Avanzar"

# Estado inicial de LEDs
led_midiendo.value(0)  # Apagado (no está midiendo)
led_wifi.value(0)  # Apagado
led_avanzar.value(1)  # Encendido (indica que puede moverse)

oled.fill(0)
oled.text("Conectando a ", 10, 10)
oled.text("WiFi...", 10, 20)
oled.show()

# Esperar conexión
for i in range(10):
    if wifi.isconnected():
        oled.fill(0)
        oled.text("¡Conectado!", 10, 10)
        oled.text("IP:", 10, 30)
        oled.text(str(wifi.ifconfig()[0]), 10, 40)  # Mostrar la IP
        oled.show()
        time.sleep(5)
        led_wifi.value(1)
        break
else:
    oled.fill(0)
    oled.text("No se pudo", 10, 20)
    oled.text("conectar a WiFi", 10, 30)
    oled.show()
    led_wifi.value(0)
    time.sleep(5)

oled.fill(0)
oled.text("Presiona para", 10, 20)
oled.text("medir..", 10, 30)
oled.show()

def draw_signal(oled, rssi, Distancia):
    oled.fill(0)
    oled.text(f"Distancia: {Distancia}m", 5, 10)
    oled.text("Senal WiFi", 5, 50)
    oled.text(f"RSSI: {rssi} dBm", 5, 20)
    
    # Dibujar barras de señal WiFi
    if rssi >= -30:
        level = 5  # Excelente
    elif -50 <= rssi < -30:
        level = 4  # Buena
    elif -70 <= rssi < -50:
        level = 3  # Aceptable
    elif -80 <= rssi < -70:
        level = 2  # Débil
    else:
        level = 1  # Muy débil o inestable
    
    bar_width = 5
    x_start = 90
    y_base = 60
    height_levels = [4, 8, 12, 16, 20]  # Alturas de las barras
    
    for i in range(5):
        if i < level:
            oled.fill_rect(x_start + i * (bar_width + 3), y_base - height_levels[i], bar_width, height_levels[i], 1)
        else:
            oled.rect(x_start + i * (bar_width + 3), y_base - height_levels[i], bar_width, height_levels[i], 1)
    
    oled.show()

distancia = 0  # Inicializa la distancia en 0 metros

while True:
    if boton.value() == 0:
        led_avanzar.value(0)  # Apagar LED (NO moverse)
        led_midiendo.value(1)  # Encender LED midiendo...
        
        oled.fill(0)
        oled.text(f"Midiendo RSSI", 10, 20)
        oled.text(f"Distancia: {distancia}m", 10, 30)
        oled.show()
        
        rssi_values = []  # Lista para almacenar los valores de RSSI
        
        for i in range(200):  # 200 muestras en 20 segundos
            if not wifi.isconnected():
                led_wifi.value(not led_wifi.value())  # Parpadea LED WiFi
                oled.fill(0)
                oled.text("No conectado", 10, 20)
                oled.show()
            else:
                led_wifi.value(1)  # Mantener encendido si hay conexión
                rssi = wifi.status('rssi')  # Obtener RSSI
                draw_signal(oled, rssi, distancia)
                rssi_values.append(rssi)
            time.sleep(0.1)  # Medir cada 100ms
        
        # Calcular promedio y desviación estándar
        if rssi_values:
            avg_rssi = sum(rssi_values) / len(rssi_values)
            std_dev_rssi = math.sqrt(sum([(x - avg_rssi) ** 2 for x in rssi_values]) / len(rssi_values))
        else:
            avg_rssi = 0
            std_dev_rssi = 0
        
        # Guardar en el archivo
        with open("RSSI_Medicion.txt", "a") as log:
            log.write(f"\n# Distancia: {distancia}m\n")
            log.write(f"Promedio RSSI: {avg_rssi:.2f} dBm\n")
            log.write(f"Desviación estándar: {std_dev_rssi:.2f} dBm\n")
        # Fin de medición
        led_midiendo.value(0)  # Apagar LED Midiendo
        led_avanzar.value(1)  # Encender LED Avanzar

        oled.fill(0)
        oled.text("Medicion", 10, 10)
        oled.text("Guardada", 10, 20)
        oled.text("Mover +1m y", 10, 40)
        oled.text("Presionar..", 10, 50)
        oled.show()
        time.sleep(1)
        
        distancia += 1  # Incrementa la distancia solo cuando se presiona el botón
