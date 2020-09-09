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
