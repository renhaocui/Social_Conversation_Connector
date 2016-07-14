import requests
import json

token = 'astute_wechat_test'
appid = 'wxc6587a03db4b22c6'
appsecret = 'fabd27f90c9a57b375723cb0f796563a'

def getAccessToken():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + appsecret
    response = json.loads(requests.get(url, verify=False).content)
    return response['access_token']


def addAgent(accessToken):
    url = 'https://api.weixin.qq.com/customservice/kfaccount/add?access_token='+accessToken
    data = {'kf_account': 'test1@gh_ae02c9f6f14e', 'nickname': 'testAgent1', 'password': 'e10adc3949ba59abbe56e057f20f883e'}
    response = requests.post(url, json=data, verify=False).content
    return response


def retriveAgentInfo(accessToken):
    url = 'https://api.weixin.qq.com/cgi-bin/customservice/getkflist?access_token='+accessToken
    response = requests.get(url, verify=False).content
    return response

'''
if __name__ == "__main__":
    accessToken = getAccessToken()
    print retriveAgentInfo(accessToken)
    print addAgent(accessToken)
'''