#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append('/data/code/speech_app')
from wxbot import *
import io, os, subprocess
import jieba
import json
import urllib
import urllib2
import PyBaiduYuyinLib as pby

#avconv -i  voice_8139999124168371158.mp3 -ar 8000 -acodec libopencore_amrnb -f amr 1.amr
class WxVoiceControl():
    master_name = {u'风中摆酷':'', u'在云端':''}
    avconv = '/usr/bin/avconv'
    r = ''
    def __init__(self):
        self.r = pby.Recognizer(app_key='sGhDdT1kVt3ziy8kGwhNuPrG', secret_key='3f10r9nMR8w2GdnmVNtXIIyh0NqS5dzm')
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
                if msg['user']['name'] == u'在云端':
                    if self.master_name.has_key(msg['user']['name']):
                        text = msg['content']['data']
                        if text == u'reload':
                            bol_reload = True
                        ret_data = self.send_cmd(text)
                        data = json.loads(ret_data)
                        ret_str = ''
                        if data['code'] == 0:
                            ret_str = u'成功'
                        else:
                            ret_str = data['msg']
                        wx_handle.send_msg_by_uid('"' + text + '":' + ret_str, msg['user']['id'])
                    else:
                        wx_handle.send_msg_by_uid(u'hi', msg['user']['id'])
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
