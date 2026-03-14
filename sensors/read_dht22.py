import time
import json
import sys
import board
import adafruit_dht

# ----------------------------------------------------------------------------
# Script: read_dht22.py
# Description: Lecture des données de température et d'humidité via un capteur
# DHT22 connecté au Raspberry Pi 3 B.
# Sortie: JSON sur la sortie standard (stdout) pour interface Node-RED.
# ----------------------------------------------------------------------------

# Initialisation du capteur DHT22 sur la broche GPIO 4 (Pin 7)
# Note: board.D4 correspond au GPIO 4 du processeur BCM.
dhtDevice = adafruit_dht.DHT22(board.D4)

def read_sensor():
    try:
        # Lecture de la température et de l'humidité
        temperature_c = dhtDevice.temperature
        humidity = dhtDevice.humidity
        
        # Vérification de la validité des données
        if temperature_c is not None and humidity is not None:
            data = {
                "sensor": "DHT22",
                "temperature": round(temperature_c, 1),
                "humidity": round(humidity, 1)
            }
            # Envoi des données en format JSON
            print(json.dumps(data))
            sys.exit(0)
        else:
            print(json.dumps({"error": "Failed to retrieve data"}))
            sys.exit(1)
            
    except RuntimeError as error:
        # Les erreurs (RuntimeError) sont extrêment courantes avec les 
        # capteurs DHT en raison du timing critique de leur protocole 1-wire.
        # Node-RED pourra relancer le script si nécessaire.
        print(json.dumps({"error": "RuntimeError: " + error.args[0]}))
        sys.exit(1)
    except Exception as error:
        # Libération des ressources et fermeture propore en cas d'erreur grave
        dhtDevice.exit()
        print(json.dumps({"error": str(error)}))
        sys.exit(1)

if __name__ == '__main__':
    # Nous pourrions boucler avec time.sleep(), mais dans notre architecture
    # c'est Node-RED qui orchestre le scheduling, donc on lit une fois et on quitte.
    read_sensor()
