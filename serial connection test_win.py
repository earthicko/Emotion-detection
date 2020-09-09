import serial
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
args = parser.parse_args()

# list port = python -m serial.tools.list_ports
port_dict = {0:'COM5',
             1:'COM15',
             2:'COM4',
             3:'COM14',
             4:'COM13',
             5:'COM12',
             6:'COM11',
             7:'COM9',
             8:'COM6',
             9:'COM10',
             10:'COM8',
             11:'COM16'}

setting_dict = {'homing_cycle':['$22', 1],
                'homing_feed':['$24', 2000],
                'homing_seek':['$25', 1000],
                'homing_debounce':['$26', 250],
                'x_step':['$100', 80],
                'y_step':['$101', 80],
                'z_step':['$102', 80],
                'x_max_rate':['$110', 10000],
                'y_max_rate':['$111', 10000],
                'z_max_rate':['$112', 10000],
                'x_accel':['$120', 2000],
                'y_accel':['$121', 2000],
                'z_accel':['$122', 2000],
                'x_travel':['$130', 1000],
                'y_travel':['$131', 1000],
                'z_travel':['$132', 1000],
                }

position_data_neutral = [[0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0],
                         [0, 0, 0]]

position_data_angry =   [[10, 0, 10],
                         [0, 10, 0],
                         [10, 0, 10],
                         [0, 10, 0],
                         [10, 0, 10],
                         [0, 10, 0],
                         [10, 0, 10],
                         [0, 10, 0],
                         [10, 0, 10],
                         [0, 10, 0],
                         [10, 0, 10],
                         [0, 10, 0]]

num_of_grbl = 1

grbl = []


for i in range(num_of_grbl):
    grbl.append(serial.Serial(port_dict[i], 115200, timeout=5))
    if args.verbose:
        print('GRBL #'+str(i)+' added: '+grbl[i].name)
    grbl[i].write(b"\r\n\r\n")
    time.sleep(2)   # Wait for grbl to initialize
    grbl[i].reset_input_buffer()  # Flush startup text in serial input

def showSettings(port_i):
    if args.verbose:
        print('Reading settings from '+str(grbl[port_i].name))
    port.write(b"$$\n")
    if args.verbose:
        print(grbl[port_i].read(2000).decode('utf-8'))

def setSettings(port_i):
    if args.verbose:
        print('Setting settings to '+str(grbl[port_i].name))
    for item in setting_dict.keys():
        if args.verbose:
            print('Item '+item+'\tset to '+str(setting_dict[item][1])+'\tin adress '+setting_dict[item][0])
        msg = setting_dict[item][0]+'='+str(setting_dict[item][1])+'\n'
        grbl[port_i].write(msg.encode())
        if args.verbose:
            print(grbl[port_i].readline().decode('utf-8'))

def home(port_i):
    if args.verbose:
        print('Homing '+str(grbl[port_i].name))
    grbl[port_i].write(b"$H\n")
    if args.verbose:
        print(grbl[port_i].readline().decode('utf-8'))

def move(port_i, position_data):
    if args.verbose:
        print('Moving '+str(grbl[port_i].name))
    x_pos = position_data[port_i][0]
    y_pos = position_data[port_i][1]
    z_pos = position_data[port_i][2]
    msg = str(x_pos)+str(y_pos)+str(z_pos)
    print(msg)
    if args.verbose:
        print(grbl[port_i].readline().decode('utf-8'))






for i in range(num_of_grbl):
    #showSettings(grbl[i])
    #setSettings(grbl[i])
    home(i)

while True:
    for i in range(num_of_grbl):
        move(i, position_data_angry)

for i in range(num_of_grbl):
    grbl[i].close()
