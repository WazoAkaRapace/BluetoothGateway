from bluepy import btle
import time
import thread


class Notification:
    def __init__(self, conn, classname):
        self.name = 'notification'
        self.conn = conn
        self.classname = classname

    def subscribe(self, timer=0):
        try:
            delegate = NotificationDelegate(self.conn, self.classname)
            self.conn.setDelegate(delegate)
            thread.start_new_thread(self.waiter(), (timer,))
        except:
            self.conn.disconnect()

    def waiter(self, timer=0):
        try:
            if timer != 0:
                timeout = time.time() + timer
                print(timeout)
                while time.time() < timeout:
                    self.conn.waitForNotifications(0.5)
                    time.sleep(0.03)
                self.conn.disconnect()
            else:
                while True:
                    self.conn.waitForNotifications(0.5)
                    time.sleep(0.03)
        except:
            self.conn.disconnect()


class NotificationDelegate(btle.DefaultDelegate):
    def __init__(self, conn, classname):
        btle.DefaultDelegate.__init__(self)
        self.conn = conn
        self.classname = classname

    def handleNotification(self, cHandle, data):
        self.classname.handlenotification(self.conn, cHandle, data)
