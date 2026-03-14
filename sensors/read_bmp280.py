import time
import json
import sys
import board
import busio
import adafruit_bmp280

# ----------------------------------------------------------------------------
# Script: read_bmp280.py
# Description: Lecture des données de température, de pression et d'altitude via un capteur
# BMP280 connecté au Raspberry Pi 3 B par bus I2C.
# Sortie: JSON sur la sortie standard (stdout) pour interface Node-RED.
# ----------------------------------------------------------------------------

# Initialisation du bus I2C: board.SCL (GPIO 3), board.SDA (GPIO 2)
# Assurez-vous d'avoir activé l'I2C via `sudo raspi-config` ou `raspi-config nonint do_i2c 0`
i2c = busio.I2C(board.SCL, board.SDA)

# Initialisation du capteur BMP280. 
# Selon le module, l'adresse logicielle par défaut peut être 0x77 (souvent modules Adafruit) 
# ou 0x76 (souvent modules BME/BMP génériques d'AliExpress/Amazon).
try:
    # Essai adresse courante
    bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)
except ValueError:
    try:
        # Essai adresse alternative
        bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x77)
    except Exception as error:
        print(json.dumps({"error": "Failed to init BMP280 on both 0x76 and 0x77. " + str(error)}))
        sys.exit(1)

# Optionnel: Modification de la pression au niveau de la mer locale en hPa 
# pour une mesure précise de l'altitude.
# bmp280.sea_level_pressure = 1013.25

def read_sensor():
    try:
        # Les lectures du BMP280 sont généralement fiables car elles ne reposent
        # pas sur des temporisations aussi critiques que les DHT, mais sur l'I2C
        data = {
            "sensor": "BMP280",
            "temperature": round(bmp280.temperature, 1),
            "pressure": round(bmp280.pressure, 1), # Pression en hPa
            "altitude": round(bmp280.altitude, 1)  # Altitude en mètres
        }
        print(json.dumps(data))
        sys.exit(0)
    except Exception as error:
        print(json.dumps({"error": str(error)}))
        sys.exit(1)

if __name__ == '__main__':
    read_sensor()
