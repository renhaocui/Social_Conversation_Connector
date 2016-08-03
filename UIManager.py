# -*- coding: utf-8 -*-
import requests
import json

messengerThreadUrl = "https://graph.facebook.com/v2.6/me/thread_settings?access_token="


def setMessengerGetStarted(token):
    threadSettingURL = messengerThreadUrl + token
    data = {
        "setting_type": "call_to_actions",
        "thread_state": "new_thread",
        "call_to_actions": [
            {
                "payload": "get_started"
            }
        ]
    }
    response = requests.post(threadSettingURL, json=data, verify=False)

    return response, json.loads(response.text)


def setMessengerGreeting(token):
    threadSettingURL = messengerThreadUrl + token
    data = {
        "setting_type": "greeting",
        "greeting": {
            "text": "Welcome!"
        }
    }
    response = requests.post(threadSettingURL, json=data, verify=False)

    return response, json.loads(response.text)


def setMessengerMenu(token):
    threadSettingURL = messengerThreadUrl + token
    data = {
        "setting_type": "call_to_actions",
        "thread_state": "existing_thread",
        "call_to_actions": [
            {
                "type": "postback",
                "title": "Home",
                "payload": "home_page"
            },
            {
                "type": "web_url",
                "title": "Guides",
                "url": "https://dl.dropboxusercontent.com/u/93550717/site/GuidesHome.html"
            },
            {
                "type": "web_url",
                "title": "Roadside",
                "url": "https://dl.dropboxusercontent.com/u/93550717/site/test2.html"
            }
        ]
    }
    response = requests.post(threadSettingURL, json=data, verify=False)

    return response, json.loads(response.text)


def getWeChatAccessToken(appid, appsecret):
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=' + appid + '&secret=' + appsecret
    response = json.loads(requests.get(url, verify=False).content)
    return response['access_token']


def setWeChatMenu(accessToken, lang):
    url = 'https://api.weixin.qq.com/cgi-bin/menu/create?access_token=' + accessToken
    if lang == 'en':
        menu_data = {'button': [{'type': 'click', 'name': 'Home', 'key': 'home_box'},
                            {'type': 'view', 'name': 'Guides',
                             'url': 'https://dl.dropboxusercontent.com/u/93550717/site/GuidesHome.html'},
                            {'type': 'view', 'name': 'Roadside',
                             'url': 'https://dl.dropboxusercontent.com/u/93550717/site/test2.html'}]}
    else:
        menu_data = {'button': [{'type': 'click', 'name': "主页", 'key': 'home_box'},
                            {'type': 'view', 'name': "目录",
                             'url': 'https://dl.dropboxusercontent.com/u/93550717/site/GuidesHome.html'},
                            {'type': 'view', 'name': "道路救援",
                             'url': 'https://dl.dropboxusercontent.com/u/93550717/site/test2.html'}]}
    response = requests.post(url, data=json.dumps(menu_data, ensure_ascii=False), verify=False).content
    return response


if __name__ == "__main__":
    appid = 'wxc6587a03db4b22c6'
    appsecret = 'fabd27f90c9a57b375723cb0f796563a'
    messenger_token = 'EAAB1kFElgToBAHRJmoshPkpQzpEF2FviWyY9GdA5lUZBPwqRVb3tQdz9vlOkkLZBpp0nihxN5yyBJxDEZC3nTROBaosUYhiMWwwPcqUJiFEZA6lqQwcFHwfpWYZB8d7v5OsaZB2YDgLqRmpdNxvHy7s4pPiuPe8xK1MhFdgoRimgZDZD'

    accessToken = getWeChatAccessToken(appid, appsecret)
    print setWeChatMenu(accessToken, 'en')
    #print setMessengerMenu(messenger_token)
    #print setMessengerGreeting(messenger_token)
    #print setMessengerGetStarted(messenger_token)

