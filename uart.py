from serial.tools import list_ports
import serial
import logging


class Device:
    def __init__(self):
        self.ser = None
        self.name = None
        self.type = None
        self.firmware = None

    def __str__(self):
        s = 'Device(' + str(self.ser.port) + \
                ', Name: ' + str(self.name) + \
                ', Type: ' + str(self.type) + \
                ', Firmware: ' + str(self.firmware) + ')'
        return s

    def get_type(self):
        self.ser.write(b'I\r')
        string = str(self.ser.read_until(expected=b'\r'))
        string2 = ''
        count = 0
        while "OK" not in string and count < 3:
            string2 = string
            string = str(self.ser.read_until(expected=b'\r'))
            count = count + 1
        if "OK" in string and string2 != '':
            try:
                x = string2.split(',')
                self.type = x[1]
                self.firmware = x[2].split('\\')[0]
                return True
            except IndexError:
                return False
        else:
            return False

    def get_name(self):
        self.ser.write(b'Name,?\r')
        string = str(self.ser.read_until(expected=b'\r'))
        string2 = ''
        count = 0
        while "OK" not in string and count < 3:
            string2 = string
            string = str(self.ser.read_until(expected=b'\r'))
            count = count + 1
        if "OK" in string:
            x = string2.split(',')
            self.name = x[1].split('\\')[0]
            return True
        else:
            return False

    def set_name(self, name):
        send = 'Name,' + name + '\r'
        self.ser.write(bytes(send, 'utf-8'))
        string = str(self.ser.read_until(expected=b'\r'))
        count = 0
        while "OK" not in string and count < 3:
            string = str(self.ser.read_until(expected=b'\r'))
            count = count + 1
        if "OK" in string:
            return self.get_name()
        else:
            return False

    def send_command(self, command):
        self.ser.write(bytes(command, 'utf-8'))
        string = str(self.ser.read_until(expected=b'\r'))
        count = 0
        while "OK" not in string and count < 3:
            string = str(self.ser.read_until(expected=b'\r'))
            count = count + 1
        if "OK" in string:
            return True
        else:
            return False

    def get_reading(self):
        string = str(self.ser.read_until(expected=b'\r'))
        str_value = string.split("'")[1]
        str_value = str_value.split('\\')[0]
        if self.type == 'HUM':
            try:
                str_values = str_value.split(',')
                hum = float(str_values[0])
                temp = float(str_values[1])
                value = [hum, temp]
            except (IndexError, ValueError) as error:
                logging.error(str(error))
                return None
        else:
            try:
                value = float(str_value)
            except ValueError as error:
                logging.error(str(error))
                return None
        return value

    def get_devices():
        ports = list(list_ports.comports())
        device_list = []
        for p in ports:
            if p.device != '/dev/ttyAMA0':
                d = Device()
                d.ser = serial.Serial(p.device)
                while d.get_type() is False:
                    logging.info('Failed to get type')
                while d.get_name() is False:
                    logging.info('Failed to get type')
                logging.info(str(d))
                device_list.append(d)
        return device_list


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("uart.log"),
            logging.StreamHandler()
        ]
    )
    devices = Device.get_devices()

    for d in devices:
        if d.type == 'HUM':
            d.send_command('O,T,1')
    while True:
        for d in devices:
            logging.info(d.type)
            logging.info(d.get_reading())
