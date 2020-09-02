import serial
from serial.tools import list_ports

class BTAdapter:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def getAvailablePorts(self):
        availableComports = list_ports.comports()
        return[x for x in availableComports]