import serial
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
parser.add_argument('-t', '--test', help='do not output serial', action='store_true')
args = parser.parse_args()


class GRBL:
    position_data = [50, 50, 50]
    position_output = [0, 0, 0]

    def __init__(self, port, timeout, num, pos_max, pos_min, iteration):
        self.port = port
        self.timeout = timeout
        self.num = num
        self.pos_max = pos_max  # G Code Value
        self.pos_min = pos_min  # G Code Value
        for i in range(3):
            self.position_data[i] = 50
            self.position_output[i] = pos_max
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
        if args.test:
            print('No settings on test mode')
        else:
            if args.verbose:
                print('GRBL #' + str(self.num) + ' Reading settings from ' + str(self.port.name))
            self.port.write(b"$$\n")
            if args.verbose:
                print(self.port.read(2000).decode('utf-8'), end='')

    def set_settings(self, data):
        if args.test:
            print('No settings on test mode')
        else:
            if args.verbose:
                print('GRBL #' + str(self.num) + ' Setting settings to ' + str(self.port.name))
            for item in data.keys():
                if args.verbose:
                    print('Item ' + item + '\tset to ' + str(data[item][1]) + '\tin address ' + data[item][
                        0] + ', echo: ',
                          end='')
                msg = data[item][0] + '=' + str(data[item][1]) + '\n'
                self.port.write(msg.encode())
                if args.verbose:
                    print(self.port.readline().decode('utf-8'), end='')

    def reset(self):
        self.iteration = self.iteration_default
        for i in range(3):
            self.position_data[i] = 50
        self.feedrate = 6000
        self.mode = 'G0'

    def iterate(self):
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Iteration')
            print(f'Before Position: {self.position_data[0]}, {self.position_data[1]}, {self.position_data[2]} / ', end='')
            print(f'Before Iteration: {self.iteration[0]}, {self.iteration[1]}, {self.iteration[2]}')
        for i in range(3):
            self.position_data[i] += self.iteration[i]
            if self.position_data[i] > 50:
                self.position_data[i] = 100 - self.position_data[i]  # 100 - 53 = 47
                self.iteration[i] = - self.iteration[i]
            elif self.position_data[i] < 50:
                self.position_data[i] = - 100 + self.position_data[i]  # - 100 + 53 = - 47
                self.iteration[i] = - self.iteration[i]
        if args.verbose:
            print(f'After Position: {self.position_data[0]}, {self.position_data[1]}, {self.position_data[2]} / ', end='')
            print(f'After Iteration: {self.iteration[0]}, {self.iteration[1]}, {self.iteration[2]}')

    def home(self, wait):
        if args.test:
            print('No homing at test mode')
        else:
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
        if args.test:
            print('No RX at test mode')
            return 'No RX at test mode'
        else:
            return self.port.readline().decode('utf-8')

    def tx(self, msg):
        if args.test:
            print('No TX at test mode')
            return 'No TX at test mode'
        else:
            self.port.write(msg.encode())

    def set_position(self, position, feedrate, mode):
        for i in range(3):
            if position[i] > 50:
                print("ERROR at: GRBL#" + str(self.num) + ": raw position[" + str(i) + "] overflow: " + str(
                    position[i]))
                self.position_data[i] = 50
            elif position[i] < -50:
                print("ERROR at: GRBL#" + str(self.num) + ": raw position[" + str(i) + "] underflow: " + str(
                    position[i]))
                self.position_data[i] = -50
            else:
                self.position_data[i] = position[i]
        self.feedrate = feedrate
        self.mode = mode
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Position Set ' + str(self.port.name))
            print(f"Data position X: {self.position_data[0]} Y: {self.position_data[1]} Z: {self.position_data[2]}")

    def move(self):
        if args.verbose:
            print('GRBL #' + str(self.num) + ' Moving ' + str(self.port.name))
        for i in range(3):
            self.position_output[i] = map_int(self.position_data[i], (-50, 50), (self.pos_min, self.pos_max))
            if self.position_output[i] > self.pos_max:
                print("ERROR at: GRBL#" + str(self.num) + ": mapped position[" + str(i) + "] overflow: " + str(
                    self.position_data[i]))
                self.position_output[i] = self.pos_max
            elif self.position_output[i] < self.pos_min:
                print("ERROR at: GRBL#" + str(self.num) + ": mapped position[" + str(i) + "] underflow: " + str(
                    self.position_data[i]))
                self.position_output[i] = self.pos_min
        msg = 'G90 ' + self.mode + ' X' + str(self.position_output[0]) + ' Y' + str(self.position_output[1]) + ' Z' + str(
            self.position_output[2]) + ' F' + str(self.feedrate) + '\n'
        if not args.test:
            self.port.write(msg.encode())
            if args.verbose:
                print('Output GCode: ' + msg + ', echo: ', end='')
                print(self.port.readline().decode('utf-8'), end='')
        else:
            if args.verbose:
                print('Output GCode: ' + msg)

    def in_waiting(self):
        if args.test:
            print('No buffer at test mode')
            return 'No buffer at test mode'
        else:
            return self.port.in_waiting

    def close(self):
        if args.test:
            print('No serial port at test mode')
            return 'No serial port at test mode'
        else:
            self.port.close()

    def open(self):
        if args.test:
            print('No serial port at test mode')
            return 'No serial port at test mode'
        else:
            self.port.open()


def map_int(val, src, dst):
    return int(((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0])
