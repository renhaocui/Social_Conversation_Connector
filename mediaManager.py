import requests
import json

token = 'astute_wechat_test'
appid = 'wxc6587a03db4b22c6'
appsecret = 'fabd27f90c9a57b375723cb0f796563a'

def getAccessToken():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + appsecret
    response = json.loads(requests.get(url, verify=False).content)
    return response['access_token']

