import socket
import threading
import can
import json
import logging
import time
import pickle

from can import Bus


class Udp2Can(threading.Thread):
    def __init__(self, port, device, name="Unnamed"):
        threading.Thread.__init__(self)
        self.port = port
        self.device = device
        self.name = name
        self.setDaemon(True)
        self._stop_event = threading.Event()
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.bus = None

    def run(self):
        self.bus = Bus(self.device)
        self.socket.bind('0.0.0.0', self.port)
        while not self._stop_event.is_set():
            (client_data, client_address) = self.socket.recvfrom(1024)
            logging.info("%s UDP msg from %s" % (self.name, client_address))
            msg = pickle.loads(client_data)
            self.bus.send(msg, 0.1)

    def stop(self):
        self._stop_event.set()


class Can2Udp(threading.Thread):
    def __init__(self, host, port, device, name="Unnamed"):
        threading.Thread.__init__(self)
        self.host = host
        self.port = port
        self.device = device
        self.name = name
        self.setDaemon(True)
        self._stop_event = threading.Event()
        self.bus = None
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def run(self):
        self.bus = Bus(self.device)
        while not self._stop_event.is_set():
            msg = self.bus.recv(0.1)
            if msg is not None:
                logging.info("%s recv cam msg" % self.name)
                msgpickle = pickle.dumps(msg)
                self.socket.sendto(msgpickle, (self.host, self.port))

    def stop(self):
        self._stop_event.set()


class Config(object):
    def __init__(self, j):
        self.__dict__ = json.loads(j)


logging.getLogger().setLevel(logging.INFO)
logging.info("Reading config")
config = Config(open("config.json", "r").read())
logging.info("Config readed %s %s" % (config.udp2can, config.can2udp))

udp2canworkers = []
can2udpworkers = []

for u2c in config.udp2can:
    t = Udp2Can(u2c['port'], u2c['device'], u2c['name'])
    udp2canworkers.append(t)
    t.start()

for c2u in config.can2udp:
    t = Can2Udp(c2u['host'], c2u['port'], c2u['device'], c2u['name'])
    can2udpworkers.append(t)
    t.start()

try:
    while True:
        time.sleep(0.5)
except Exception as Ex:
    for t in udp2canworkers:
        t.stop()
    for t in can2udpworkers:
        t.stop()
