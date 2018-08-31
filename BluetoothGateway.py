import paho.mqtt.client as mqtt
from bluepy import btle
import json
import BluetoothGateway.components.awox as awox
import BluetoothGateway.components.xiaomiht as xiaomi
import BluetoothGateway.components.yeelight.yeelightCandela as yee_Candela
import time
import ssl

class MainManager:

    def __init__(self):
        self.connexion = None
        self.connected = False
        self.booting = True
        self.deviceList = []
        self.lastRefresh = {}
        self.config = {}
        print("Reading config file...")
        self.initialize_config()
        print("Initializing mqtt connexion...")
        self.initialize_mqtt()
        print("Loading devices...")
        self.initialize_devices()
        print("Subscribing to mqtt channels...")
        self.proceed_subscribes()
        print("Takeoff ")
        self.booting = False


    def on_connect(self, client, userdata, flags, rc):
        print("MQTT client connected !")
        self.connected = True
        if not self.booting:
            self.proceed_subscribes()
            print("Channels have been re-subscribed")

    def on_message(self, client, userdata, message):
        print("New message : " + message.topic + " [" + str(message.payload.decode("utf-8")) + "]")
        for device in self.deviceList:
            device.on_message(message)

    def on_disconnect(self, client, userdata, rc):
        print("MQTT client disconnected...")
        self.connected = False

    ##############################################
    ########        Initial setup         ########
    ##############################################
    def initialize_config(self):
        with open('config.json', 'r') as f:
            self.config = json.load(f)

        # Config check
        if 'user' not in self.config:
            print("User setting is missing")
            exit(1)
        if 'password' not in self.config:
            print("Password setting is missing")
            exit(1)
        if 'host' not in self.config:
            print("Host setting is missing")
            exit(1)
        if 'port' not in self.config:
            print("Using default port : 1883")
            self.config['port'] = 1883


    ##############################################
    ########          MQTT setup          ########
    ##############################################
    def initialize_mqtt(self):
        print("Connecting to " + self.config['host'])
        self.connexion = mqtt.Client("BluePy")
        self.connexion.username_pw_set(self.config['user'], self.config['password'])
        if 'ca_cert' in self.config:
            self.connexion.tls_set(ca_certs=self.config['ca_cert'])
            print("MQTT Encryption is enabled ! Good boy :3")
        self.connexion.reconnect_delay_set()
        self.connexion.on_connect = self.on_connect
        self.connexion.on_message = self.on_message
        self.connexion.on_disconnect = self.on_disconnect
        self.connexion.connect(self.config['host'], port=self.config['port'])
        self.connexion.loop_start()
        while not self.connected:
            time.sleep(0.03)

    ##############################################
    ########        Devices setup         ########
    ##############################################
    def initialize_devices(self):
        if 'devices' in self.config:
            for device in self.config['devices']:
                print(device['type'])
                if device['type'] == "xiaomiht":
                    self.deviceList.append(xiaomi.XiaomiHT(device['mac'], self.connexion, device['refresh']))
                elif device['type'] == "awoxaroma":
                    self.deviceList.append(awox.MqttAroma(device['mac'], self.connexion))
                elif device['type'] == "yeelightcandela":
                    self.deviceList.append(yee_Candela.yeelight_candela(device['mac'], self.connexion))
        else:
            print("No devices, no Gateway.")
            exit(0)

    def proceed_subscribes(self):
        for device in self.deviceList:
            device.subscribe()


# Starting the main program !
manager = MainManager()

while True:
    time.sleep(0.03)
    for device in manager.deviceList:
        if device.refresh() > 0:
            if device in manager.lastRefresh:
                if time.time() > manager.lastRefresh[device] + device.refresh():
                    device.update()
                    manager.lastRefresh[device] = time.time()
            else:
                device.update()
                manager.lastRefresh[device] = time.time()
