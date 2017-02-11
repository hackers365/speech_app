#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append('/data/code/speech_app')
from wxbot import *
import io, os, subprocess
import ssl
import websocket
import threading
import jieba
import json
import urllib
import urllib2
import PyBaiduYuyinLib as pby
from time import sleep

#avconv -i  voice_8139999124168371158.mp3 -ar 8000 -acodec libopencore_amrnb -f amr 1.amr
class WxVoiceControl():
    master_name = {u'风中摆酷':'', u'在云端':''}
    receive_master = u'风中摆酷'
    image_list = ['/tmp/1.jpeg', '/tmp/2.jpeg', '/tmp/3.jpeg']
    my_image_list = ['/tmp/temp.jpeg']
    avconv = '/usr/bin/avconv'
    r = ''
    ws = ''
    wx_handle = ''
    def __init__(self, wx_handle):
        self.r = pby.Recognizer(app_key='sGhDdT1kVt3ziy8kGwhNuPrG', secret_key='3f10r9nMR8w2GdnmVNtXIIyh0NqS5dzm')
        self.wx_handle = wx_handle
        self.ws_connect()

    def ws_connect(self):
        self.ws = websocket.WebSocketApp("wss://ws.test.com/s/134", on_message = self.on_message, on_close = self.on_close, on_error=self.on_error)
        wst = threading.Thread(target=self.ws.run_forever, kwargs=dict(sslopt={"cert_reqs": ssl.CERT_NONE}))
        wst.daemon = True
        wst.start()
        conn_timeout = 5
        sleep(2)
        while not self.ws.sock.connected and conn_timeout:
            sleep(1)
            conn_timeout -= 1
    def on_close(self, ws):
        print '### close ###'
        sleep(5)
        self.ws_connect()
    def on_error(self, ws, error):
        print error
        #self.ws_connect()

    def send_img_by_name(self, name, image_list=None):
        user_id = self.wx_handle.get_user_id(name)
        if not image_list:
            image_list = self.image_list
        if user_id:
            for i in range(len(image_list)):
                if os.path.exists(image_list[i]):
                    self.wx_handle.send_img_msg_by_uid(image_list[i], user_id)
                    #os.remove(image_list[i])

    def send_my_img_list(self, living=None):
        for i in range(len(self.my_image_list)):
            if living:
                urllib.urlretrieve("http://rpi2:8080/stream/snapshot.jpeg", self.my_image_list[i])            
            else:
                urllib.urlretrieve("http://rpi2:8080/stream/snapshot.jpeg", self.my_image_list[i])            
            sleep(1)
        self.send_img_by_name(u'风中摆酷', self.my_image_list)

    def on_message(self, ws, message):
        data = json.loads(message)
        print(data)
        if data["type"] == u'door_open':
            ret = self.wx_handle.send_msg(self.receive_master, time.strftime('%Y-%m-%d %H:%M:%S') + u'门被打开了')
            self.send_img_by_name(self.receive_master)

    def send_cmd(self, result):
        seg_list = jieba.lcut(result, cut_all=False)
        print(seg_list)
        keyword = ','.join(seg_list).encode('utf-8')
        params = {
            'keyword': keyword
        }
        url = "http://192.168.100.50:9110/auto/controlbyword?" + urllib.urlencode(params)
        f=urllib.urlopen(url)
        s=f.read()
        print(s)
        return s
    def get_stt(self, msg):
        curr_path = os.getcwd()
        voice_path = curr_path + '/temp/voice_' + msg['msg_id'] + '.mp3'
        amr_path = curr_path + '/temp/voice_' + msg['msg_id'] + '.amr'
        cmd_str = '%s -v quiet -i %s -ar 8000 -acodec libopencore_amrnb -f amr -'
        process = subprocess.Popen(cmd_str %(self.avconv, voice_path), stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
        amr_data, stderr = process.communicate()
        audio_data = pby.AudioData(8000, amr_data)
        text = self.r.recognize(audio_data)
        print text
        return text

    def handle_msg_all(self, msg, wx_handle):
        bol_reload = False
        if msg['msg_type_id'] == 4:
            if msg['content']['type'] == 0:             #text
                print(msg)
                if self.master_name.has_key(msg['user']['name']):
                    text = msg['content']['data']
                    if text == u'reload':
                        bol_reload = True
                        return
                    elif text == u'image':
                        self.send_my_img_list()
                        return 
                    elif text == u'limage':
                        self.send_my_img_list(True)
                        return 
                    ret_data = self.send_cmd(text)
                    data = json.loads(ret_data)
                    ret_str = ''
                    if data['code'] == 0:
                        ret_str = u'成功'
                    else:
                        ret_str = data['msg']
                    wx_handle.send_msg_by_uid('"' + text + '":' + ret_str, msg['user']['id'])

                #self.send_img_msg_by_uid("img/1.png", msg['user']['id'])
                #self.send_file_msg_by_uid("img/1.png", msg['user']['id'])
            elif msg['content']['type'] == 4:           #voice
                if self.master_name.has_key(msg['user']['name']):
                    wx_handle.get_voice(msg['msg_id'])
                    text = self.get_stt(msg)
                    ret_data = self.send_cmd(text)
                    data = json.loads(ret_data)
                    ret_str = ''
                    if data['code'] == 0:
                        ret_str = u'成功'
                    else:
                        ret_str = data['msg']
                    wx_handle.send_msg_by_uid('"' + text + '":' + ret_str, msg['user']['id'])
        return True, bol_reload
