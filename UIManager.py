# -*- coding: utf-8 -*-
import requests
import json

token = 'astute_wechat_test'
appid = 'wxc6587a03db4b22c6'
appsecret = 'fabd27f90c9a57b375723cb0f796563a'


def getAccessToken():
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + appsecret
    response = json.loads(requests.get(url, verify=False).content)
    return response['access_token']


def createMenu(accessToken):
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + accessToken
    menu_data = {'button': [{'type': 'click', 'name': 'Home', 'key': 'home_box'},
                            {'type': 'view', 'name': 'Guides',
                             'url': 'https://dl.dropboxusercontent.com/u/93550717/site/GuidesHome.html'},
                            {'type': 'view', 'name': 'Roadside',
                             'url': 'https://dl.dropboxusercontent.com/u/93550717/site/test2.html'}]}
    response = requests.post(url, json=menu_data, verify=False).content
    return response


if __name__ == "__main__":
    accessToken = getAccessToken()
    print createMenu(accessToken)
