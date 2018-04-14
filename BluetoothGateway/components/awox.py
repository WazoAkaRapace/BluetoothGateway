import awoxpy
from bluepy import btle
import paho.mqtt.client as mqtt


class MqttAroma:
    def __init__(self, mac, conn):
        self.mac = mac
        self.connexion = conn
        self.light = awoxpy.awoxAroma(mac)

        if self.light.connect():
            print("Connected to " + self.mac)
        else:
            print("Not connected to " + self.mac)

    def subscribe(self):
        self.connexion.subscribe("light/" + self.mac + "/white/set")
        self.connexion.subscribe("light/" + self.mac + "/rgb/set")
        self.connexion.subscribe("light/" + self.mac + "/brightness/set")
        self.connexion.subscribe("light/" + self.mac + "/state/set")

    def on_message(self, message):
        # print("----------------------------------------------------")
        # print("message received ", str(message.payload.decode("utf-8")))
        # print("message topic=", message.topic)
        # print("message qos=", message.qos)
        # print("message retain flag=", message.retain)
        if message.topic == "light/" + self.mac + "/brightness/set":
            self.set_brightness(str(message.payload.decode("utf-8")))
        elif message.topic == "light/" + self.mac + "/white/set":
            self.set_white(str(message.payload.decode("utf-8")))
        elif message.topic == "light/" + self.mac + "/rgb/set":
            self.set_rgb(str(message.payload.decode("utf-8")))
        elif message.topic == "light/" + self.mac + "/state/set":
            self.set_state(str(message.payload.decode("utf-8")))

    def refresh(self):
        return -1

    def set_brightness(self, brightness):
        if self.light.color_mode:
            self.light.set_brightness(int(brightness) * 100 / 127)
        else:
            self.light.set_brightness(int(brightness))
        self.update_brightness()

    def update_brightness(self):
        self.light.get_state()
        if self.light.color_mode:
            brightness = self.light.get_brightness() * 127 / 100
        else:
            brightness = self.light.get_brightness()
        self.connexion.publish("light/" + self.mac + "/brightness", str(brightness), retain=True)

    def set_white(self, white):
        if white == "OFF":
            return
        white = int(white)
        if white > 500:
            white = 500
        elif white < 154:
            white = 154
        white = int((white - 154.) * 127. / 346.)
        self.light.set_white(white)
        self.update_white()

    def update_white(self):
        self.light.get_state()
        white = self.light.get_white()
        self.connexion.publish("light/" + self.mac + "/white", int((float(white)) / 127. * 346. + 154), retain=True)
        self.connexion.publish("light/" + self.mac + "/rgb/set", "OFF", retain=True)
        self.connexion.publish("light/" + self.mac + "/state/set", "ON", retain=True)

        if white > 64:
            self.connexion.publish("light/" + self.mac + "/rgb", "255,178,67", retain=True)
        else:
            self.connexion.publish("light/" + self.mac + "/rgb", "245,254,255", retain=True)

    def set_rgb(self, rgb):
        if rgb == "OFF":
            return
        colors = rgb.split(",")
        red = int(colors[0])
        green = int(colors[1])
        blue = int(colors[2])
        self.light.set_rgb(red, green, blue)
        self.update_rgb()

    def update_rgb(self):
        self.light.get_state()
        self.connexion.publish("light/" + self.mac + "/rgb",
                               str(self.light.red) + "," + str(self.light.green) + "," + str(self.light.blue),
                               retain=True)
        self.connexion.publish("light/" + self.mac + "/white/set", "OFF", retain=True)
        self.connexion.publish("light/" + self.mac + "/state/set", "ON", retain=True)

    def set_state(self, state):
        if state == "ON":
            self.light.on()
        else:
            self.light.off()
        self.update_state()

    def update_state(self):
        self.light.get_state()
        power = self.light.power
        if power:
            self.connexion.publish("light/" + self.mac + "/state", "ON", retain=True)
        else:
            self.connexion.publish("light/" + self.mac + "/state", "OFF", retain=True)
            self.connexion.publish("light/" + self.mac + "/white/set", "OFF", retain=True)
            self.connexion.publish("light/" + self.mac + "/rgb/set", "OFF", retain=True)