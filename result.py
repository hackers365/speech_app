# -*- coding:UTF-8 -*-
import sys
import urllib
import urllib2
import ssl
import json
#from websocket import create_connection
import websocket
import threading
import jieba
from time import sleep


print('result... Press Ctrl+C to exit')

def send_cmd(result):
    print('google said:' + result)
    seg_list = jieba.lcut(result, cut_all=False)
    keyword = ','.join(seg_list).encode('utf-8')
    params = {
        'keyword': keyword
    }
    url = "http://192.168.100.50:9110/auto/controlbyword?" + urllib.urlencode(params)
    f=urllib.urlopen(url)
    s=f.read()
    print(s)

def on_message(ws, message):
    data = json.loads(message)
    if data["type"] == 'result':
        sct = threading.Thread(target=send_cmd, args=(data["data"],))
        sct.start()
        #send_cmd(data["data"])

def on_close(ws):
    print '####close####'

ws = websocket.WebSocketApp("wss://ws.test.com/s/134", on_message = on_message, on_close = on_close)
ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
