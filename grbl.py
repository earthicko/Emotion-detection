import serial
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
parser.add_argument('-t', '--test', help='do not output serial', action='store_true')
args = parser.parse_args()
print('GRBL      :grbl arguments')
print('GRBL      :--verbose: '+str(args.verbose))
print('GRBL      :--test: '+str(args.test))

class GRBL:
    position_data = []
    position_output = []
    iteration = []
    iteration_default = []

    def __init__(self, port, timeout, num, pos_max, pos_min, iteration):
        self.timeout = timeout
        self.num = num
        self.pos_max = pos_max  # G Code Value
        self.pos_min = pos_min  # G Code Value
        self.position_data = []
        self.position_output = []
        self.iteration = []
        self.iteration_default = []
        for i in range(3):
            self.position_data.append(50)
            self.position_output.append(pos_max)
            self.iteration.append(iteration)
            self.iteration_default.append(iteration)
        self.feedrate = 6000
        self.mode = 'G0'

        if not args.test:
            self.device = serial.Serial(port, 115200, timeout=timeout)
            self.device.write(b"\r\n\r\n")
            time.sleep(1)
            self.device.reset_output_buffer()  # Flush startup text in serial input
            self.device.reset_input_buffer()  # Flush startup text in serial input

        if args.verbose:
            if args.test:
                print('GRBL      :Dummy #' + str(num) + ' added: ')
            else:
                print('GRBL      :GRBL #' + str(num) + ' added: ' + self.device.name)

    def get_settings(self):
        if args.test:
            print('GRBL      :No settings on test mode')
        else:
            if args.verbose:
                print('GRBL      :GRBL #' + str(self.num) + ' Reading settings from ' + str(self.device.name))
            self.device.write(b"$$\n")
            if args.verbose:
                print('GRBL      :'+self.device.read(2000).decode('utf-8'), end='')

    def set_settings(self, data):
        if args.test:
            print('GRBL      :No settings on test mode')
        else:
            if args.verbose:
                print('GRBL      :GRBL #' + str(self.num) + ' Setting settings to ' + str(self.device.name))
            for item in data.keys():
                if args.verbose:
                    print('GRBL      :Item ' + item + '\tset to ' + str(data[item][1]) + '\tin address ' + data[item][
                        0] + ', echo: ',
                          end='')
                msg = data[item][0] + '=' + str(data[item][1]) + '\n'
                self.device.write(msg.encode())
                if args.verbose:
                    print('GRBL      :'+self.device.readline().decode('utf-8'), end='')

    def reset(self):
        for i in range(3):
            self.position_data[i] = 50
            self.iteration[i] = self.iteration_default[i]
        self.feedrate = 6000
        self.mode = 'G0'
        print('GRBL      :GRBL #' + str(self.num) + ' Reset: Iter: '+str(self.iteration)+' Iter_default: '+str(self.iteration_default)+' pos_data: '+str(self.position_data))

    def iterate(self):
        if args.verbose:
            print('GRBL      :GRBL #' + str(self.num) + ' Iteration')
            print(f'GRBL      :Before Position: {self.position_data[0]}, {self.position_data[1]}, {self.position_data[2]} / ', end='')
            print(f'Before Iteration: {self.iteration[0]}, {self.iteration[1]}, {self.iteration[2]}')
        for i in range(3):
            self.position_data[i] += self.iteration[i]
            if self.position_data[i] > 50:
                self.position_data[i] = 100 - self.position_data[i]  # 100 - 53 = 47
                self.iteration[i] = - self.iteration[i]
            elif self.position_data[i] < -50:
                self.position_data[i] = - 100 - self.position_data[i]  # - 100 + 53 = - 47
                self.iteration[i] = - self.iteration[i]
        if args.verbose:
            print(f'GRBL      :After Position: {self.position_data[0]}, {self.position_data[1]}, {self.position_data[2]} / ', end='')
            print(f'After Iteration: {self.iteration[0]}, {self.iteration[1]}, {self.iteration[2]}')

    def home(self, wait):
        if args.test:
            print('GRBL      :No homing at test mode')
        else:
            if args.verbose:
                print('GRBL      :GRBL #' + str(self.num) + ' Homing :' + str(self.device.name))
            self.device.write(b"$H\n")
            if wait:
                while self.device.in_waiting <= 0:
                    if args.verbose:
                        print('GRBL      :GRBL #' + str(self.num) + ' waiting for homing: ' + str(self.device.name))
                        time.sleep(1)
                if args.verbose:
                    print('GRBL      :echo: ' + self.device.readline().decode('utf-8'), end='')

    def rx(self):
        if args.test:
            print('GRBL      :No RX at test mode')
            return 'No RX at test mode'
        else:
            return self.device.readline().decode('utf-8')

    def tx(self, msg):
        if args.test:
            print('GRBL      :No TX at test mode')
        else:
            self.device.write(msg.encode())

    def set_position(self, position, feedrate, mode):
        for i in range(3):
            if position[i] > 50:
                print("\033[31m"+"GRBL      :ERROR at: GRBL#" + str(self.num) + ": raw position[" + str(i) + "] overflow: " + str(
                    position[i])+'\033[0m')
                self.position_data[i] = 50
            elif position[i] < -50:
                print("\033[31m"+"GRBL      :ERROR at: GRBL#" + str(self.num) + ": raw position[" + str(i) + "] underflow: " + str(
                    position[i])+'\033[0m')
                self.position_data[i] = -50
            else:
                self.position_data[i] = position[i]
        self.feedrate = feedrate
        self.mode = mode
        if args.verbose:
            if args.test:
                print('GRBL      :Dummy #' + str(self.num) + ' Position Set :', end='')
            else:
                print('GRBL      :GRBL #' + str(self.num) + ' Position Set :', end='')
            print(f" X: {self.position_data[0]} Y: {self.position_data[1]} Z: {self.position_data[2]}")
    def get_position(self):
        return self.position_data

    def move(self):
        if args.verbose:
            if args.test:
                print('GRBL      :Dummy #' + str(self.num) + ' Moving ')
            else:
                print('GRBL      :GRBL #' + str(self.num) + ' Moving ' + str(self.device.name))
        for i in range(3):
            self.position_output[i] = map_int(self.position_data[i], (-50, 50), (self.pos_min, self.pos_max))
            if self.position_output[i] > self.pos_max:
                print("\033[31m"+"GRBL      :ERROR at: GRBL#" + str(self.num) + ": mapped position[" + str(i) + "] overflow: " + str(
                    self.position_data[i])+'\033[0m')
                self.position_output[i] = self.pos_max
            elif self.position_output[i] < self.pos_min:
                print("\033[31m"+"GRBL      :ERROR at: GRBL#" + str(self.num) + ": mapped position[" + str(i) + "] underflow: " + str(
                    self.position_data[i])+'\033[0m')
                self.position_output[i] = self.pos_min
        msg = 'G90 ' + self.mode + ' X' + str(self.position_output[0]) + ' Y' + str(self.position_output[1]) + ' Z' + str(
            self.position_output[2]) + ' F' + str(self.feedrate) + '\n'
        if not args.test:
            self.device.write(msg.encode())
            if args.verbose:
                print("\033[36m"+'GRBL      :Output GCode: ' + msg + ', echo: '+'\033[0m', end='')
                print('GRBL      :'+self.device.readline().decode('utf-8'), end='')
        else:
            if args.verbose:
                print("\033[36m"+'GRBL      :Output GCode: ' + msg+'\033[0m', end='')

    def in_waiting(self):
        if args.test:
            print('GRBL      :No buffer at test mode')
            return 1
        else:
            return self.device.in_waiting

    def close(self):
        if args.test:
            print('GRBL      :No serial port at test mode')
        else:
            self.device.close()

    def open(self):
        if args.test:
            print('GRBL      :No serial port at test mode')
        else:
            self.device.open()


def map_int(val, src, dst):
    return int(((val - src[0]) / (src[1] - src[0])) * (dst[1] - dst[0]) + dst[0])
