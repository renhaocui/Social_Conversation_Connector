import requests
import json


def getAccessToken(appid, appsecret):
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + appsecret
    response = json.loads(requests.get(url, verify=False).content)
    return response

def getAccountInfo(accessToken, openID):
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token='+accessToken+'&openid='+openID+'&lang=en'
    response = requests.get(url, verify=False).content
    return response

'''
if __name__ == "__main__":
    token = 'astute_wechat_test'
    appid = 'wxc6587a03db4b22c6'
    appsecret = 'fabd27f90c9a57b375723cb0f796563a'
    accessToken = getAccessToken(appid, appsecret)['access_token']
    print accessToken
    print getAccountInfo(accessToken, 'olCTFv7SWdm-Kqmw1jk41uh1FB90')
'''