import serial
import time
import argparse
import websockets
import asyncio

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
parser.add_argument('-t', '--test', help='do not output serial', action='store_true')
args = parser.parse_args()

emotion_list = ["Angry", "Disgusted", "Fearful",
                "Happy", "Neutral", "Sad", "Surprised"]

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
                'homing_seek':['$25', 6000],
                'homing_debounce':['$26', 25],
                'x_step':['$100', 80],
                'y_step':['$101', 80],
                'z_step':['$102', 80],
                'x_max_rate':['$110', 10000],
                'y_max_rate':['$111', 10000],
                'z_max_rate':['$112', 10000],
                'x_accel':['$120', 1000],
                'y_accel':['$121', 1000],
                'z_accel':['$122', 1000],
                'x_travel':['$130', 1000],
                'y_travel':['$131', 1000],
                'z_travel':['$132', 1000],
                }



position_data_dict = {  "Angry":    [   [19, 50.65, 9.29], [24.85, 8.52, 1.81], [-5.55, 17.87, 1.28], [-9.51, 18.79, -18.11], [30.73, 29.96, 1.46], [9.42, -2.63, 26.25], [33.88, -2.51, -0.55], [-8.27, -20.74, -30.97], [17.03, 26.93, -14.53], [-41.05, -27.66, -3.65], [-48.46, -43.57, -31.81], [-43.75, -23.84, -41.16]
                        ],
                        "Disgusted":[   [-41.2, -13.46, 7.43], [4.1, -12.98, -17.56], [2.96, 33.1, 45.52], [30.42, 5.86, -2.09], [12.2, 28.1, 21.67], [-7.51, -35.22, -38.34], [-19.45, -3.46, -9.97], [-31.68, -42.36, -25.77], [6.2, 25.89, 19.48], [1.32, -2.41, 17.11], [41.23, 43.98, 20.42], [-7.81, -15.71, -1.75]

                        ],
                        "Fearful":[     [17.15, 19.92, 32.44], [42.73, 35.83, 7.82], [-27.86, -48.92, -41.18], [-9.91, 24.4, 42.16], [38.74, 25.3, 16.97], [20, 28.72, 33.45], [30.31, 23.84, 21.11], [24.32, 29.35, 30.79], [27.59, 23.61, 23.1], [26.22, 29.34, 29.17], [26.19, 23.79, 24.47], [27.26, 29.04, 27.97]
                        ],
                        "Happy":[       [-21.3, -18.21, -15.64], [-15.88, -19.15, -23.03], [-24.2, -21.11, -15.67], [-12.22, -14.42, -21.92], [-29.61, -30.32, -19.61], [0.63, 22.25, 35.09], [32.77, 16.44, -5.84], [-23.92, -31.19, -27.78], [-19.42, -13.12, -12.75], [-17.26, -22.41, -24.29], [-22.05, -17.99, -15.46], [-16.17, -19.18, -21.9]
                        ],
                        "Neutral":  [   [50, 49.89, 49.55], [48.96, 48.1, 46.95], [45.47, 43.64, 41.43], [38.81, 35.75, 32.23], [28.24, 23.77, 18.85], [13.54, 7.93, 2.13], [-3.72, -9.46, -14.97], [-20.13, -24.89, -29.18], [-33.01, -36.38, -39.3], [-41.8, -43.91, -45.66], [-47.08, -48.18, -49.01], [-49.57, -49.9, -50]
                        ],
                        "Sad":[         [50, 38.9, 28.45], [18.65, 9.51, 1.02], [-6.82, -14, -20.53], [-26.41, -31.63, -36.2], [-40.12, -43.39, -46], [-47.96, -49.27, -49.92], [-49.92, -49.27, -47.96], [-46, -43.39, -40.12], [-36.2, -31.63, -26.41], [-20.53, -14, -6.82], [1.02, 9.51, 18.65], [28.45, 38.9, 50]
                        ],
                        "Surprised":[   [-50, -49.97, -49.88], [-49.72, -49.51, -49.22], [-48.87, -48.44, -47.94], [-47.37, -46.72, -45.98], [-45.16, -44.25, -43.25], [-42.14, -40.93, -39.61], [-38.17, -36.6, -34.89], [-33.04, -31.01, -28.81], [-26.41, -23.79, -20.9], [-17.73, -14.2, -10.26], [-5.8, -0.66, 5.42], [12.95, 23.24, 50]
                        ],
                        "null":[        [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]
                        ]
                      }
position_status = [
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1]
]
position_status_default = [
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1],
    [1, 1, 1]
]
num_of_grbl = 12
grbl = []




def showSettings(port_i):

    if not args.test:
        if args.verbose:
            print('GRBL #' + str(port_i) + ' Reading settings from ' + str(grbl[port_i].name))
        grbl[port_i].write(b"$$\n")
        if args.verbose:
            print(grbl[port_i].read(2000).decode('utf-8'), end='')

def setSettings(port_i):
    if not args.test:
        if args.verbose:
            print('GRBL #'+str(port_i)+' Setting settings to '+str(grbl[port_i].name))
        for item in setting_dict.keys():
            if args.verbose:
                print('Item '+item+'\tset to '+str(setting_dict[item][1])+'\tin adress '+setting_dict[item][0])
            msg = setting_dict[item][0]+'='+str(setting_dict[item][1])+'\n'
            grbl[port_i].write(msg.encode())
            if args.verbose:
                print(grbl[port_i].readline().decode('utf-8'), end='')

def home(port_i):
    if not args.test:
        if args.verbose:
            print('GRBL #'+str(port_i)+' Homing :'+str(grbl[port_i].name))
        grbl[port_i].write(b"$H\n")
        while grbl[port_i].in_waiting <= 0:
            if args.verbose:
                print('GRBL #'+str(port_i)+' waiting for homing: '+str(grbl[port_i].name))
                time.sleep(1)
        if args.verbose:
            print(grbl[port_i].readline().decode('utf-8'), end='')

def map_int(val, src, dst):
    return int(((val - src[0]) / (src[1]-src[0])) * (dst[1]-dst[0]) + dst[0])

def position_iterate(position_data, position_iteration):
    counter = 0
    global position_status
    for controller_i in range (0, 12):
        for motor_i in range (0, 3):
            #print(f"con: {controller_i} mot: {motor_i}")
            if position_status[controller_i][motor_i] == 1:
                position_data[controller_i][motor_i] += position_iteration
                if position_data[controller_i][motor_i] > 50:
                    position_data[controller_i][motor_i] = 100 - position_data[controller_i][motor_i]
                    position_status[controller_i][motor_i] = 0
            elif position_status[controller_i][motor_i] == 0:
                position_data[controller_i][motor_i] -= position_iteration
                if position_data[controller_i][motor_i] < -50:
                    position_data[controller_i][motor_i] = - position_data[controller_i][motor_i]
                    position_status[controller_i][motor_i] = 1
    return position_data

def move(port_i, position_data, feedrate, mode):
    #position -430 to 0
    if not args.test:
        if args.verbose:
            print('GRBL #'+str(port_i)+' Moving '+str(grbl[port_i].name))
    x_pos = position_data[port_i][0]
    y_pos = position_data[port_i][1]
    z_pos = position_data[port_i][2]

    if args.verbose:
        print(f"Data position X: {x_pos} Y: {y_pos} Z: {z_pos}")

    x_pos = map_int(x_pos, (-50, 50), (-430, 0))
    y_pos = map_int(y_pos, (-50, 50), (-430, 0))
    z_pos = map_int(z_pos, (-50, 50), (-430, 0))

    if args.verbose:
        print(f"Mapped position X: {x_pos} Y: {y_pos} Z: {z_pos}")

    msg = 'G90 '+mode+' X'+str(x_pos)+' Y'+str(y_pos)+' Z'+str(z_pos)+' F'+str(feedrate)+'\n'

    if args.verbose:
        print('Output GCode: ' + msg)
    if not args.test:
        grbl[port_i].write(msg.encode())
        if args.verbose:
            print(grbl[port_i].readline().decode('utf-8'), end='')


serial_wait_timer_mode_change = 3
serial_wait_timer_mode_same = 1
serial_wait_timer_for_next_move = serial_wait_timer_mode_change
serial_last_triggered = 0
name_last = ''
mode = 'null'
mode_last = 'null'
consistent_name_counter = 0
mode_change_criteria = 30
position_next_move = position_data_dict["null"]
position_plus = 5

async def receiveData(websocket, path):
    global serial_last_triggered
    global serial_wait_timer_mode_change
    global serial_wait_timer_mode_same
    global serial_wait_timer_for_next_move
    global name_last
    global mode
    global mode_last
    global consistent_name_counter
    global mode_change_criteria
    global position_next_move
    global position_status
    global position_status_default

    name = await websocket.recv()
    #print(f"Received data: {name}")
    #print(f"Last Data:     {name_last}")
    if name == name_last:
        consistent_name_counter += 1
    else:
        consistent_name_counter = 0
    #print('Consistent name counter:'+str(consistent_name_counter))
    if time.time() - serial_last_triggered > serial_wait_timer_for_next_move:
        print(str(serial_wait_timer_for_next_move)+'seconds passed')
        for port_i in range(0, num_of_grbl):
            move(port_i, position_next_move, 6000, 'G0')
        serial_last_triggered = time.time()
        position_next_move = position_iterate(position_next_move, position_plus)


    if consistent_name_counter >= mode_change_criteria:
        if mode_last != name:
            # change mode
            mode = name
            print(f"Mode change to {mode}")
            serial_wait_timer_for_next_move = serial_wait_timer_mode_change
            position_next_move = position_data_dict[mode]
            position_status = position_status_default
        else:
            #print(f"Mode is same to {mode}")
            serial_wait_timer_for_next_move = serial_wait_timer_mode_same

    else:
        #do not change mode
        serial_wait_timer_for_next_move = serial_wait_timer_mode_same
        #print(f"Mode is same to {mode}")


    name_last = name
    mode_last = mode


for i in range(num_of_grbl):
    if not args.test:
        grbl.append(serial.Serial(port_dict[i], 115200, timeout=5))
        if args.verbose:
            print('GRBL #' + str(i) + ' added: ' + grbl[i].name)

        grbl[i].write(b"\r\n\r\n")
        time.sleep(1)  # Wait for grbl to initialize
        grbl[i].reset_input_buffer()  # Flush startup text in serial input
        grbl[i].reset_output_buffer()  # Flush startup text in serial input

for i in range(num_of_grbl):
    setSettings(i)
    home(i)
    move(i, position_data_dict['null'], 6000, 'G0')


start_server = websockets.serve(receiveData, "localhost", 8765)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()

for i in range(num_of_grbl):
    grbl[i].close()
