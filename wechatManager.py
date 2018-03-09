import requests
import json


def getAccessToken(appid, appsecret):
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + appsecret
    response = json.loads(requests.get(url, verify=False).content)
    return response

def getAccountInfo(accessToken, openID):
    url = 'https://api.weixin.qq.com/cgi-bin/user/info?access_token='+accessToken+'&openid='+openID+'&lang=zh_CN'
    response = requests.get(url, verify=False).content
    return response


if __name__ == "__main__":
    #token = 'astute_wechat_test'
    appid = 'wx29ff8b9de3978795'
    appsecret = '5a4941c7f73a1cbbd91f5ef4a8d26b54'
    accessToken = getAccessToken(appid, appsecret)['access_token']
    print accessToken
    print getAccountInfo(accessToken, 'ozwzgvrHXQ279V3ng6UqovjL2AY0')