#!/usr/bin/env python

import collections
import pyaudio
import wave

import sys
import ssl
import json
import websocket
from time import sleep

DETECT_DING = "/data/code/snowboy/resources/ding.wav"
DETECT_DONG = "/data/code/snowboy/resources/dong.wav"

ding_wav = wave.open(DETECT_DING, 'rb')
ding_data = ding_wav.readframes(ding_wav.getnframes())
audio = pyaudio.PyAudio()
stream_out = audio.open(
	format=audio.get_format_from_width(ding_wav.getsampwidth()),
	channels=ding_wav.getnchannels(),
	rate=ding_wav.getframerate(), input=False, output=True)
stream_out.start_stream()

def play_audio_file():
	global stream_out
	global ding_data
	stream_out.write(ding_data)

def on_message(ws, message):
    data = json.loads(message)
    if data["type"] == 'recognition':
        play_audio_file()

def on_close(ws):
    print '####close####'

ws = websocket.WebSocketApp("wss://ws.test.com/s/134", on_message = on_message, on_close = on_close)
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})

