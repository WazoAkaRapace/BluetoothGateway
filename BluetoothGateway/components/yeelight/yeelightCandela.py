import threading
import struct
import codecs
from bluepy import btle
from .structures import getrequest


def cmd(cmd):
    def _wrap(self, *args, **kwargs):
        req = cmd(self, *args, **kwargs)

        params = None
        wait = self._wait_after_call
        if isinstance(req, tuple):
            params = req[1]
            req = req[0]

        query = {"type": req}
        if params:
            if "wait" in params:
                wait = params["wait"]
                del params["wait"]
            query.update(params)

        print(">> %s (wait: %s)", query, wait)

        _ex = None
        try_count = 3
        while try_count > 0:
            try:
                res = self.control_char.write(getrequest(req).build(query),
                                              withResponse=True)
                #self._conn.wait(wait)

                return res
            except Exception as ex:
                print("got exception on %s, tries left %s: %s",
                              query, try_count, ex)
                _ex = ex
                try_count -= 1
                self.connect()
                continue
        raise _ex

    return _wrap

class yeelight_candela:
    REGISTER_NOTIFY_HANDLE = 0x16
    MAIN_UUID = "8e2f0cbd-1a66-4b53-ace6-b494e25f87bd"
    NOTIFY_UUID = "8f65073d-9f57-4aaa-afea-397d19d5bbeb"
    CONTROL_UUID = "aa7d3f34-2d4f-41e0-807f-52fbf8cf7443"

    def __init__(self, mac, conn, status_cb=None, paired_cb=None,
                 keep_connection=False, wait_after_call=0):
        self._mac = mac
        self.connexion = conn
        self._is_on = False
        self._brightness = None
        self._temperature = None
        self._rgb = None
        self._mode = None
        self._paired_cb = paired_cb
        self._status_cb = status_cb
        self._keep_connection = keep_connection
        self._wait_after_call = wait_after_call
        self._conn = None
        self.connect()

    @property
    def mac(self):
        return self._mac

    @property
    def available(self):
        return self._mode is not None

    @property
    def mode(self):
        return self._mode

    def connect(self):
        try:
            if self._conn:
                self._conn.disconnect()

            try:
                self._conn = btle.Peripheral(self._mac, addrType=btle.ADDR_TYPE_PUBLIC)
            except btle.BTLEException as ex:
                print("Faild first connexion on " + self._mac)
                btle.Scanner().scan(10)
                self._conn = btle.Peripheral(self._mac, addrType=btle.ADDR_TYPE_PUBLIC)

            handles = self._conn.getCharacteristics()
            for handle in handles:
                if handle.uuid == yeelight_candela.NOTIFY_UUID:
                    notify_char = handle
                if handle.uuid == yeelight_candela.CONTROL_UUID:
                    control_chars = handle

            self.notify_handle = notify_char.getHandle()
            self.control_char = control_chars
            self.control_handle = self.control_char.getHandle()

            # We need to register to receive notifications
            self._conn.writeCharacteristic(self.REGISTER_NOTIFY_HANDLE,
                                    struct.pack("<BB", 0x01, 0x00))
        except btle.BTLEException as generic:
            print("Faild to connect to " + self.mac)


    def disconnect(self):
        self._conn.disconnect()

    def subscribe(self):
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
        elif message.topic == "light/" + self.mac + "/state/set":
            self.set_state(str(message.payload.decode("utf-8")))

    def refresh(self):
        return -1

    @cmd
    def turn_on(self):
        self.connexion.publish("light/" + self.mac + "/state", "ON", retain=True)
        return "SetOnOff", {"state": True}

    @cmd
    def turn_off(self):
        self.connexion.publish("light/" + self.mac + "/state", "OFF", retain=True)

        return "SetOnOff", {"state": False}

    @cmd
    def set_brightness(self, brightness):
        if int(brightness) <= 100:
            self.connexion.publish("light/" + self.mac + "/brightness", str(brightness), retain=True)
            return "SetBrightness", {"brightness": int(brightness)}

    def set_state(self, status):
        if status == "ON":
            self.turn_on()
        elif status == "OFF":
            self.turn_off()

    def handleNotification(self, handle, data):
        print("<< %s", data)


