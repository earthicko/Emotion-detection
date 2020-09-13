import serial
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
parser.add_argument('-t', '--test', help='do not output serial', action='store_true')
args = parser.parse_args()


class GRBL:
    position = [50, 50, 50]

    def __init__(self, port, timeout, num, pos_max, pos_min, iteration):
        self.port = port
        self.timeout = timeout
        self.num = num
        self.pos_max = pos_max  # G Code Value
        self.pos_min = pos_min  # G Code Value
        for i in range(3):
            self.position[i] = 50
        self.feedrate = 6000
        self.mode = 'G0'
        self.iteration = iteration
        self.iteration_default = iteration

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
            print('GRBL #' + str(self.num) + ' Setting settings to ' + str(self.port.name))
        for item in data.keys():
            if args.verbose:
                print('Item ' + item + '\tset to ' + str(data[item][1]) + '\tin address ' + data[item][0] + ', echo: ',
                      end='')
            msg = data[item][0] + '=' + str(data[item][1]) + '\n'
            self.port.write(msg.encode())
            if args.verbose:
                print(self.port.readline().decode('utf-8'), end='')

    def reset(self):
        self.iteration = self.iteration_default
        for i in range(3):
            self.position[i] = 50
        self.feedrate = 6000
        self.mode = 'G0'

    def iterate(self):
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Iteration')
            print(f'Before Position: {self.position[0]}, {self.position[1]}, {self.position[2]} / ', end='')
            print(f'Before Iteration: {self.iteration[0]}, {self.iteration[1]}, {self.iteration[2]}')
        for i in range(3):
            self.position[i] += self.iteration[i]
            if self.position[i] > 50:
                self.position[i] = 100 - self.position[i]   # 100 - 53 = 47
                self.iteration[i] = - self.iteration[i]
            elif self.position[i] < 50:
                self.position[i] = - 100 + self.position[i]   # - 100 + 53 = - 47
                self.iteration[i] = - self.iteration[i]
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Iteration')
            print(f'After Position: {self.position[0]}, {self.position[1]}, {self.position[2]} / ', end='')
            print(f'After Iteration: {self.iteration[0]}, {self.iteration[1]}, {self.iteration[2]}')

    def home(self, wait):
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Homing :' + str(self.port.name))
        self.port.write(b"$H\n")
        if wait:
            while self.port.in_waiting <= 0:
                if args.verbose:
                    print('GRBL #' + str(self.num) + ' waiting for homing: ' + str(self.port.name))
                    time.sleep(1)
            if args.verbose:
                print('echo: ' + self.port.readline().decode('utf-8'), end='')

    def rx(self):
        return self.port.readline().decode('utf-8')

    def tx(self, msg):
        self.port.write(msg.encode())

    def set_position(self, position, feedrate, mode):
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Position Set ' + str(self.port.name))
            print(f"Data position X: {self.position[0]} Y: {self.position[1]} Z: {self.position[2]}")
        for i in range(3):
            self.position[i] = map_int(position[i], (-50, 50), (self.pos_min, self.pos_max))
        self.feedrate = feedrate
        self.mode = mode
        if args.verbose:
            print(f"Mapped position X: {self.position[0]} Y: {self.position[1]} Z: {self.position[2]}")

    def move(self):
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Moving ' + str(self.port.name))
        msg = 'G90 ' + self.mode + ' X' + str(self.position[0]) + ' Y' + str(self.position[1]) + ' Z' + str(
            self.position[2]) + ' F' + str(self.feedrate) + '\n'
        if not args.test:
            self.port.write(msg.encode())
            if args.verbose:
                print('Output GCode: ' + msg + ', echo: ', end='')
                print(self.port.readline().decode('utf-8'), end='')

    def in_waiting(self):
        return self.port.in_waiting
    def close(self):
        self.port.close()
    def open(self):
        self.port.open()



def map_int(val, src, dst):
    return int(((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0])
