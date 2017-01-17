# -*- coding:UTF-8 -*-
import snowboydecoder
import sys
import signal
import urllib
import urllib2
import ssl
import json
import PyBaiduYuyinLib as pby
#from websocket import create_connection
import websocket
import threading
import jieba
from time import sleep

interrupted = False

input_device_index = None

tts = pby.TTS(app_key='sGhDdT1kVt3ziy8kGwhNuPrG', secret_key='3f10r9nMR8w2GdnmVNtXIIyh0NqS5dzm')
r = pby.Recognizer(app_key='sGhDdT1kVt3ziy8kGwhNuPrG', secret_key='3f10r9nMR8w2GdnmVNtXIIyh0NqS5dzm')
m = pby.Microphone(device_index=input_device_index)

def signal_handler(signal, frame):
    global interrupted
    interrupted = True

def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.4)
print('Listening... Press Ctrl+C to exit')

def on_message(ws, message):
    #~ data = json.loads(message)
    #~ if data["type"] == 'result':
        #~ sct = threading.Thread(target=send_cmd, args=(data["data"],))
        #~ sct.start()
        #~ send_cmd(data["data"])

def on_close(ws):
    print '####close####'

ws = websocket.WebSocketApp("wss://ws.test.com/s/134", on_message = on_message, on_close = on_close)
wst = threading.Thread(target=ws.run_forever, kwargs=dict(sslopt={"cert_reqs": ssl.CERT_NONE}))
wst.daemon = True
wst.start()
conn_timeout = 5
while not ws.sock.connected and conn_timeout:
    sleep(1)
    conn_timeout -= 1

def google_cb():
    msg = '{"type": "recognition"}'
    ws.send(msg)
####################################################
def baidu_cb():
    with m as source:
        audio = r.listen(source, timeout=3)
    print("Got it! Now to recognize it...")
    try:
        text = r.recognize(audio)
        print 'baidu said:' + text
        send_cmd(text)
    except LookupError:
        print("Oops! Didn't catch that")
###################################################
def thread_cb():
    google_cb()
    #baidu_ct = threading.Thread(target=baidu_cb)
    #google_ct = threading.Thread(target=google_cb)
    #baidu_ct.start()
    #google_ct.start()
# main loop
detector.start(detected_callback=thread_cb,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()
