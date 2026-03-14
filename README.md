# 🌡️ Projet Station Météo - Raspberry Pi 3 B & Node-RED

Ce projet est une solution complète, robuste et industrielle pour la collecte, le traitement, la visualisation et le stockage de données météorologiques. Il est conçu pour être déployé sur un **Raspberry Pi 3 Model B**, agissant comme une passerelle IoT (Edge Gateway) avec **Node-RED** comme orchestrateur.

---

## 1️⃣ Partie Théorique (Compréhension globale)

### 🏗️ Architecture du système
Le système repose sur une architecture IoT *Edge Computing* : la collecte, le traitement et l'affichage sont hébergés localement sur le Raspberry Pi, garantissant une autonomie totale (pas de dépendance au Cloud). Le stockage local s'effectue via SQLite.

### 🔄 Schéma fonctionnel détaillé
```mermaid
graph TD;
    A[Capteur DHT22\nTempérature/Humidité] -->|GPIO 4 (Signal Numérique)| C(Raspberry Pi 3B\nScripts Python)
    B[Capteur BMP280\nTempérature/Pression/Alt.] -->|I2C (SDA/SCL)| C
    C -->|JSON| D{Node-RED\n(Orchestrateur & Traitement)}
    D -->|Requêtes SQL| E[(Base de données\nSQLite locale)]
    D -->|WebSockets| F[Dashboard Web UI\nGauges & Graphiques]
    D -->|HTTP GET| G[Client externe\nExport CSV]
```

### 🧠 Rôles des composants
- **Raspberry Pi 3 B** : Cerveau du système. Ses capacités matérielles (CPU Quad-Core ARM Cortex-A53, 1Go LPDDR2) sont largement suffisantes pour supporter un OS complet (Raspberry Pi OS), l'environnement Node.js, une base de données et l'exécution de scripts Python sans saccade.
- **Node-RED** : Environnement de programmation visuelle (*Flow-based programming*), développé par IBM. Il simplifie drastiquement le raccordement (wiring) entre le matériel (capteurs), les API (Dashboard) et la persistance (SQLite).
- **Réseau de capteurs IoT** : Les capteurs agissent comme les terminaux "Leaf" (feuilles). Dans une configuration plus large, ces capteurs pourraient communiquer via LoRaWAN ou Zigbee. Ici, pour minimiser la latence et la complexité, ils sont fixés en connexion filaire directe (GPIO & I2C).

### 🔌 Protocoles utilisés
- **1-Wire (GPIO)** : Protocole temporel asynchrone pour le DHT22.
- **I2C (Inter-Integrated Circuit)** : Bus série synchrone multi-maître/multi-esclave utilisé pour le BMP280.
- **WebSocket** : Par Node-RED Dashboard pour rafraîchir en temps réel l'interface web sans recharger la page.
- **HTTP / HTTPS** : Pour l'interface d'administration de Node-RED, des requêtes REST (Export CSV) et le Dashboard (TCP Port 1880).

### ⚙️ Justification technique et contraintes
- **Absence d'ADC sur le RPi** : Le Raspberry Pi ne dispose pas de convertisseur analogique-numérique. C'est pourquoi nous avons sélectionné des capteurs envoyant **directement un signal numérique** (I2C et série propriétaire 1-Wire).
- **Contrainte RTOS (Real Time OS)** : Linux n'est pas un système d'exploitation temps réel. Le protocole 1-Wire du DHT22 nécessite un timing très précis parfois interrompu par l'OS, ce qui peut causer des erreurs de lecture intermittentes. Nos scripts Python (`RuntimeError`) et Node-RED sont conçus pour les ignorer et re-tenter (Tolérance aux pannes).
- **Contraintes énergétiques** : Le Raspberry Pi 3 B consomme, en charge modérée (Ici WiFi ON + Node-RED), environ 2W à 3W. Une alimentation officielle de **5V / 2.5A** (12.5W max) est indispensable pour éviter les "Under-voltage" et préserver l'intégrité de la carte SD.

---

## 2️⃣ Partie Matérielle

### 📦 Liste complète des composants
1. **Raspberry Pi 3 Model B** avec connectivité WiFi activée.
2. **Carte MicroSD (16 Go ou 32 Go)** - Class 10 (ex: SanDisk Ultra) pour supporter les I/O fréquents de la DB SQLite.
3. **Alimentation Officielle 5V/2.5A** Micro-USB.
4. **Capteur DHT22 (AM2302)** : Plus précis que le DHT11 (-40 à 80°C ±0.5°C, Humidité 0-100% ±2%).
5. **Capteur BMP280** : Haute précision (Pression ±1 hPa, Température ±1.0°C).
6. **Breadboard (Platine d'essai)** et fils de prototypage (Jumper Wires M/F).
7. **Résistance 10kΩ** : Obligatoire pour le DHT22 *(Pull-Up resistor)* seulement si votre DHT22 n'est pas soudé sur un PCB incluant cette résistance.

### ⚡ Schéma de câblage complet
| Composant | Pin Capteur | Pin Raspberry Pi 3 (Physical Pin) | Rôle / Nom (BCM) |
| :--- | :--- | :--- | :--- |
| **DHT22** | Pin 1 (VCC) | Pin 1 | 3.3V Power |
| **DHT22** | Pin 2 (DATA) | Pin 7 | **GPIO 4** |
| **DHT22** | Pin 4 (GND) | Pin 9 | Ground (GND) |
| **BMP280** | VIN | Pin 17 | 3.3V Power |
| **BMP280**| GND | Pin 20 | Ground (GND) |
| **BMP280**| SCL | Pin 5 | **GPIO 3 (SCL)** |
| **BMP280**| SDA | Pin 3 | **GPIO 2 (SDA)** |

*Note sur la Pull-Up (DHT22) :* Si vous utilisez le capteur nu (4 pins au lieu de 3 sur module), vous **devez** placer une résistance de **10 kΩ** entre les pins VCC (3.3V) et DATA du capteur pour maintenir un état logique "Haut" stable au repos.

---

## 3️⃣ Partie Installation Système (Ligne de commande)

**Objectif** : Transformer un OS vierge en passerelle IoT opérationnelle et sécurisée.

### Etape 1 : Mise à jour du système critique
```bash
sudo apt update && sudo apt upgrade -y
```
*(Justification : Corrige les vulnérabilités de sécurité, met à jour les blobs materiels et prépare l'installation.*

### Etape 2 : Activation des Bus I2C pour le BMP280
```bash
sudo raspi-config nonint do_i2c 0
```
*(Justification : Le bus I2C matériel du RPi est désactivé par défaut au niveau kernel. Cette commande l'active sans interface manuelle).*
Vérification matérielle : `sudo apt install i2c-tools -y && i2cdetect -y 1`. Vous devriez voir `76` ou `77`.

### Etape 3 : Installation environnement Node.js et Node-RED
On utilise le script d'installation officiel qui gère automatiquement les versions compatibles ARM (RPi3) :
```bash
bash <(curl -sL https://raw.githubusercontent.com/node-red/linux-installers/master/deb/update-nodejs-and-nodered)
```
Taper `y` aux différentes confirmations (NPM et Nodes Pi).
*(Justification : Node-RED nécessite une version spécifique de Node.js avec les wrappers systemd pour se lancer au boot).*

### Etape 4 : Activation de Node-RED au démarrage (Daemon Systemd)
```bash
sudo systemctl enable nodered.service
sudo systemctl start nodered.service
```

### Etape 5 : Environnement virtuel Python et bibliothèques
Debian (RaspberryOS) bride l'installation globale PIP (PEP 668). On utilise un VirtualEnv (`venv`).
```bash
sudo apt install python3-venv python3-pip libgpiod2 -y
python3 -m venv ~/meteo_env
source ~/meteo_env/bin/activate
pip install adafruit-circuitpython-dht adafruit-circuitpython-bmp280
```
*(Justification : Librairies Adafruit standard industrielles pour interagir avec le GPIO `libgpiod2` sans privilèges root massifs).*

### Etape 6 : Installation des nodes Node-RED nécessaires
```bash
cd ~/.node-red
npm install node-red-dashboard node-red-node-sqlite node-red-node-email node-red-contrib-ui-builder
sudo systemctl restart nodered.service
```

---

## 4️⃣ Partie Structure du Projet

```text
meteo_station/
│
├── flows.json         # Définition du flow Node-RED (exportable/importable)
├── settings.js        # Configuration et sécurisation du serveur Node-RED
│
├── sensors/
│   ├── read_dht22.py  # Script Python pour DHT22 (sort JSON)
│   └── read_bmp280.py # Script Python pour BMP280 (sort JSON)
│
├── database/
│   └── meteo.db       # Base de données SQLite locale, générée par Node-RED
│
└── README.md          # Ce fichier de documentation intégrale
```

### Instructions de déploiement
1. Créez les dossiers `sensors` et `database` si ce n'est pas encore fait : `mkdir -p /home/pi/meteo_station/sensors /home/pi/meteo_station/database`.
2. Placer et modifier les permissions des scripts : `chmod +x /home/pi/meteo_station/sensors/*.py`.
3. Les bases de données s'auto-créent grâce au noeud SQLite de Node-RED en utilisant le chemin absolu.
4. **Pour importer le projet (Flow)** : Ouvrez `http://<IP_DU_RPI>:1880`, Menu `(≡) > Import`, copiez-collez le contenu de `flows.json`, déployez.
5. Remplacez le fichier standard `/home/pi/.node-red/settings.js` par notre `settings.js` personnalisé. Relancez le service Node-RED.

### Procédures de Debug et Tests de Validation
- **Tester un capteur (Python) depuis un terminal** :
  ```bash
  /home/pi/meteo_env/bin/python /home/pi/meteo_station/sensors/read_dht22.py
  ```
  *Résultat attendu : `{"sensor": "DHT22", "temperature": 23.4, "humidity": 55.1}`*
- **Analyser les logs de Node-RED (si le Dashboard ne compile pas)** :
  ```bash
  journalctl -u nodered -f
  ```
- **Problème de permissions de port (Si vous accédez Node-RED depuis Windows)** : Vérifiez que l'IP du Raspberry Pi est correcte.

---

## 5️⃣ Partie Développement (Fonctionnement Applicatif)

### Logique du Flow Node-RED (Explication de `flows.json`)
Le Flow importé accomplit cela, de manière entièrement visuelle, mais hautement asynchrone :
1. **Trigger (Timer)** : Un nœud "*Inject*" se lance toutes les 60 secondes.
2. **Collecte (Nodes *Exec*)** : Il lance simultanément les deux exécutables Python grâce au `venv`.
3. **Traduction (Nodes *JSON*)** : Le texte JSON sortant de Python (`stdout`) est sérialisé en Objet JavaScript natif au sein de Node-RED.
4. **Validation (Nodes *Switch*)** : Vérifie la présence d'une clé `"error"`. Si le script Python n'a pas pu lire le senseur (Ex: `RuntimeError` du DHT), la structure est ignorée.
5. **Préparation (Node *Function*)** : Extrait la Température/Humidité/Pression fraîche, et génère la commande SQL : `INSERT INTO meteo (timestamp, temp_dht, hum_dht, temp_bmp, pressure, altitude) VALUES ...`.
6. **Stockage (Node *SQLite*)** : Éxecute la requête. Les données historiques sont dorénavant persistantes.
7. **Affichage (Nodes *Dashboard*)** : En parallèle à la DB, les payloads mettent à jour des jauges animées situées sur `http://<IP_DU_RPI>:1880/ui`.
8. **Endpoint CSV (API HTTP)** : Fournit l'historique exportable via GET `/export` (Noeuds `http in`, `csv`, `http out`).

---

## 6️⃣ Partie Sécurité & Déploiement Industriel

Tel que conçu (voir fichier `settings.js`), le projet intègre la sécurité requise en ingénierie informatique :
1. **Authentification de l'Éditeur (`adminAuth`)** :
   Node-RED n'est plus en accès libre. Seul l'utilisateur (Par défault `admin` / mdp `password` chiffré par algorithme `bcrypt` avec 8 tours de sel). Un pirate sur le même réseau WiFi ne peut ni modifier ni altérer votre programme.
2. **Authentification du Dashboard (`httpNodeAuth`)** :
   La consultation des jauges demande un accès basique (Ex : `visiteur` / mdp `visiteur`).
3. **Restriction des commandes systèmes (`execAllowList`)** :
   Le noeud Exec est un vecteur potentiel de failles RCE (Remote Code Execution). Dans `settings.js`, il convient en production de ne lui autoriser que `['/home/pi/meteo_env/bin/python']`
4. **Firewall Système Linux (`UFW`)** :
   ```bash
   sudo apt install ufw
   sudo ufw allow 22/tcp       # SSH admin
   sudo ufw allow 1880/tcp     # Front/Back-End Node-RED
   sudo ufw default deny incoming
   sudo ufw enable
   ```

---

## 7️⃣ Partie Améliorations Possibles (Scalabilité & Autonomie)

Si vous désirez amener ce prototype fonctionnel au statut de *Produit* ou d'architecture *Cloud*, voici les *upgrades* envisageables :

1. **Intégration d'un Broker MQTT (Mosquitto) :**
   Remplacer les noeuds Exec par des scripts Python tournant en arrière-plan (Daemon systemd) publiant continuellement en MQTT (ex Payload `{t: 25, h: 50}` sur `meteo/salon`). Node-RED ne ferait plus que s'abonner (Subscriber). Cela permettrait de greffer plusieurs Raspberry Pi ou des ESP32, tout en découplant la logique d'état.
2. **Stockage Time-Series (InfluxDB + Grafana) :**
   Dans Node-RED, nous utilisons actuellement SQLite (SGBDR relationnel). Pour des mesures temporelles scalables (millions d'entrées), l'idéal est de brancher le nœud *Node-RED InfluxDB* pour envoyer l'entité `{measurement: meteo, fields: {temp: x}}`. Grafana (installable nativement sur le Raspberry Pi 3) offre une Dashboard de monitoring beaucoup plus puissant que les Ui_Gauges basiques incluses.
3. **Autonomie Énergétique (Solaire) :**
   - **PiJuice HAT** : Interface UPS qui rajoute à la batterie du Pi une connexion RTOS de niveau batterie restante.
   - **Matériel Solaire** : Un panneau de 20W à 30W couplé à un régulateur de charge Solaire (MPPT) et une batterie au Plomb (ou Li-FePO4). Le 12V généré pourra être abaissé via un module `Step-Down Buck Converter (LM2596)` réglé précisément sur `5.1V`.
4. **Envoi Télémétrie au Cloud via AWS IoT / Azure IoT Hub :**
   En utilisant les certificats (X.509) générés par le cloud public et le protocole MQTTS (Port 8883), le Raspberry Pi synchronise local->cloud pour accès mondial et Machine Learning (Prédiction temps). Node-Red propose des nœuds Amazon IoT natifs.
