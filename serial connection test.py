import serial
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
args = parser.parse_args()

# list port = python -m serial.tools.list_ports
port_dict = {0:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75830333938351103152-if00',
             1:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_85734323331351204021-if00',
             2:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_85632333136351C050B0-if00',
             3:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_55838343633351410212-if00',
             4:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5583834363335161C161-if00',
             5:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_55838343833351905281-if00',
             6:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_75833353734351D08290-if00',
             7:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_55838343633351318152-if00',
             8:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_558383436333516132C0-if00',
             9:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_558383436333513181D0-if00',
             10:'/dev/serial/by-id/usb-Arduino__www.arduino.cc__0043_5583834363335161C140-if00',
             11:'/dev/serial/by-id/usb-NicoHood_HoodLoader2_Uno-if00'}

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

num_of_grbl = 10

def showSettings(port):
    if args.verbose:
        print('Reading settings from '+str(port.name))
    port.write(b"$$\n")
    i = 0
    if args.verbose:
        print(port.read(2000))

def setSettings(port):
    if args.verbose:
        print('Setting settings to '+str(port.name))
    for item in setting_dict.keys():
        if args.verbose:
            print('Item '+item+'\tset to '+str(setting_dict[item][1])+'\tin adress '+setting_dict[item][0])
        msg = setting_dict[item][0]+'='+str(setting_dict[item][1])+'\n'
        port.write(msg.encode())
        if args.verbose:
            print(port.readline())
            

grbl = []
for i in range(num_of_grbl):
    grbl.append(serial.Serial(port_dict[i], 115200, timeout=10))
    if args.verbose:
        print('GRBL #'+str(i)+' added: '+grbl[i].name)
    grbl[i].write(b"\r\n\r\n")
    time.sleep(1)   # Wait for grbl to initialize
    grbl[i].reset_input_buffer()  # Flush startup text in serial input

print('\n')

for i in range(num_of_grbl):
    showSettings(grbl[i])
    setSettings(grbl[i])


for i in range(num_of_grbl):
    grbl[i].close()