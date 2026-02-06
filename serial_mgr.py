# serial_mgr.py
import serial
from serial.tools import list_ports

class SerialMgr:

    def __init__(self):
        self.ser = None

    def scan_ch340(self):
        return [p.device for p in list_ports.comports()
                if "CH340" in p.description]

    def open(self, port):
        if self.ser and self.ser.is_open:
            return
        self.ser = serial.Serial(port, 115200, timeout=0.5)

    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()

    def write(self, data):
        if self.ser and self.ser.is_open:
            self.ser.write(data)