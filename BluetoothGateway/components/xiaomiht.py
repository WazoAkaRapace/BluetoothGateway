import time, sched
from bluepy import btle
import paho.mqtt.client as mqtt
from ..notification import Notification
import json


class XiaomiHT:
    def __init__(self, mac, conn, refresh):
        self.mac = mac
        self.connexion = conn
        self.device = None
        self.battery = 0
        self.refresh_val = refresh


    def subscribe(self):
        pass

    def on_message(self, message):
        pass

    def refresh(self):
        return self.refresh_val

    def update(self):
        try:
            try:
                self.device = btle.Peripheral(self.mac, addrType=btle.ADDR_TYPE_PUBLIC)
            except btle.BTLEException as inst:
                print(inst.message + " - retrying...")
                self.device = btle.Peripheral(self.mac, addrType=btle.ADDR_TYPE_PUBLIC)
            batt = bytearray(self.device.readCharacteristic(0x18))
            self.battery = batt[0]
            notification = Notification(self.device, self)
            self.device.writeCharacteristic(0x10, bytes(bytearray([0x01, 0x00])), withResponse=True)
            notification.subscribe(2)
        except btle.BTLEException as inst:
            print(inst.message + " - Abort.")
            return

    def handlenotification(self, conn, handle, data):
        result = {}
        if hex(handle) == '0xe':
            received = bytearray(data)
            temp, hum = "".join(map(chr, received)).replace("T=", "").replace("H=", "").rstrip(' \t\r\n\0').split(" ")
            print("Temperature : " + temp + "C" + " - Humidite : " + hum + "%")
            result['temp'] = temp
            result['humid'] = hum
            result['batterie'] = self.battery
            conn.disconnect()
            self.connexion.publish("sensor/" + self.mac, json.dumps(result), retain=True)






