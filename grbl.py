import serial
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
parser.add_argument('-t', '--test', help='do not output serial', action='store_true')
args = parser.parse_args()

class GRBL:
    def __init__(self, port, timeout, num, pos_max, pos_min):
        self.port = port
        self.timeout = timeout
        self.num = num
        self.pos_max = pos_max
        self.pos_min = pos_min
        self.port = serial.Serial(port, 115200, timeout=timeout)
        self.port.write(b"\r\n\r\n")
        time.sleep(1)
        self.port.reset_output_buffer()  # Flush startup text in serial input
        self.port.reset_input_buffer()  # Flush startup text in serial input
        if args.verbose:
            print('GRBL #' + str(num) + ' added: ' + self.port.name)
    def get_settings(self):
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Reading settings from ' + str(self.port.name))
        self.port.write(b"$$\n")
        if args.verbose:
            print(self.port.read(2000).decode('utf-8'), end='')
    def set_settings(self, data):
        if args.verbose:
            print('GRBL #'+str(self.num)+' Setting settings to '+str(self.port.name))
        for item in data.keys():
            if args.verbose:
                print('Item '+item+'\tset to '+str(data[item][1])+'\tin adress '+data[item][0]+', echo: ', end='')
            msg = data[item][0]+'='+str(data[item][1])+'\n'
            self.port.write(msg.encode())
            if args.verbose:
                print(self.port.readline().decode('utf-8'), end='')
    def home(self, rapid):
        if args.verbose:
            print('GRBL #'+str(self.num)+' Homing :'+str(self.port.name))
        self.port.write(b"$H\n")
        if not rapid:
            while self.port.in_waiting <= 0:
                if args.verbose:
                    print('GRBL #'+str(self.num)+' waiting for homing: '+str(self.port.name))
                    time.sleep(1)
            if args.verbose:
                print('echo: '+self.port.readline().decode('utf-8'), end='')
    def rx(self):
        return self.port.readline().decode('utf-8')
    def tx(self, msg):
        self.port.write(msg.encode())
    def move(self, pos_x, pos_y, pos_z, feedrate, mode):
        # position -430 to 0
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Moving ' + str(self.port.name))
            print(f"Data position X: {pos_x} Y: {pos_y} Z: {pos_z}")

        pos_x = map_int(pos_x, (-50, 50), (self.pos_min, self.pos_max))
        pos_y = map_int(pos_y, (-50, 50), (self.pos_min, self.pos_max))
        pos_z = map_int(pos_z, (-50, 50), (self.pos_min, self.pos_max))

        if args.verbose:
            print(f"Mapped position X: {pos_x} Y: {pos_y} Z: {pos_z}")

        msg = 'G90 ' + mode + ' X' + str(pos_x) + ' Y' + str(pos_y) + ' Z' + str(pos_z) + ' F' + str(feedrate) + '\n'

        if args.verbose:
            print('Output GCode: ' + msg + ', echo: ', end='')
        if not args.test:
            self.port.write(msg.encode())
            if args.verbose:
                print(self.port.readline().decode('utf-8'), end='')

def map_int(val, src, dst):
    return int(((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0])
