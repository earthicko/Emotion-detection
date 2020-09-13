import argparse
import time
from time import ctime

import os
import sys
import subprocess
import asyncio
import websockets

# if sys.platform == 'linux':
#     from gpiozero import CPUTemperature

# input arg parsing
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', help='Print every debug messages on the console', action='store_true')
args = parser.parse_args()

# dictionary which assigns each label an emotion (alphabetical order)
emotion_dict = {0: "Angry", 1: "Disgusted", 2: "Fearful",
                3: "Happy", 4: "Neutral", 5: "Sad", 6: "Surprised", 7: "null"}


uri = 'ws://localhost:8765'



async def process():
    while True:
        input_data: str = input('next emotion: ')
        protagonistEmotion = emotion_dict[int(input_data)]

        if args.verbose:
            print("T:"+str(ctime(time.time()))+" protagonistEmotion: "+str(protagonistEmotion))

        async with websockets.connect(uri) as websocket:
            await websocket.send(protagonistEmotion)


asyncio.get_event_loop().run_until_complete(process())
