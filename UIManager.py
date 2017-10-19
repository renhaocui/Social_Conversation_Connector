# -*- coding: utf-8 -*-
import requests
import json
import property

messengerThreadUrl = "https://graph.facebook.com/v2.6/me/messenger_profile?access_token="

def setMessengerGetStarted(token):
    threadSettingURL = messengerThreadUrl + token
    data = {
        "get_started":{
                "payload": "get_started"
            }

    }
    response = requests.post(threadSettingURL, json=data, verify=False)

    return response, json.loads(response.text)


def setMessengerGreeting(token):
    threadSettingURL = messengerThreadUrl + token
    data = {
        "setting_type": "greeting",
        "greeting": [{
            "locale": "default",
            "text": "Welcome to Astute Connect 2017!"
        }]
    }
    response = requests.post(threadSettingURL, json=data, verify=False)

    return response, json.loads(response.text)

'''
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
                "url": "https://web.cse.ohio-state.edu/~cuir/site/GuidesHome.html"
            },
            {
                "type": "web_url",
                "title": "Roadside",
                "url": "https://web.cse.ohio-state.edu/~cuir/site/test2.html"
            }
        ]
    }
    response = requests.post(threadSettingURL, json=data, verify=False)

    return response, json.loads(response.text)
'''

def setMessengerMenu(token):
    threadSettingURL = messengerThreadUrl + token
    data = {
        "persistent_menu": [
            {
                "locale": "default",
                "composer_input_disabled": False,
                "call_to_actions": [
                    {
                        "type": "postback",
                        "title": "Book",
                        "payload": "make a new flight reservation"
                    },
                    {
                        "type": "nested",
                        "title": "Manage",
                        "call_to_actions": [
                            {
                                "title": "Check in",
                                "type": "postback",
                                "payload": "flight check in EK201"
                            },
                            {
                                "title": "Flight Status",
                                "type": "postback",
                                "payload": "check flight status EK201"
                            },
                            {
                                "title": "Change Flight",
                                "type": "postback",
                                "payload": "change flight EK201"
                            },
                            {
                                "title": "Change Seat",
                                "type": "postback",
                                "payload": "change seat EK201"
                            }
                        ]
                    },
                    {
                        "type": "nested",
                        "title": "Loyalty",
                        "call_to_actions": [
                            {
                                "title": "Join us",
                                "type": "web_url",
                                "url": "https://www.emirates.com/account/english/light-registration/"
                            },
                            {
                                "title": "Log in",
                                "type": "web_url",
                                "url": "https://www.emirates.com/account/english/login/login.aspx"
                            },
                            {
                                "title": "Membership",
                                "type": "web_url",
                                "url": "https://www.emirates.com/english/skywards/about/membership-tiers/membership-tiers.aspx"
                            },
                            {
                                "title": "Partners",
                                "type": "web_url",
                                "url": "https://www.emirates.com/english/skywards/about/partners/our-partners.aspx"
                            },
                            {
                                "title": "Contact us",
                                "type": "web_url",
                                "url": "https://www.emirates.com/english/help/contact-emirates/"
                            }

                        ]
                    }
                ]

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
                             'url': 'http://web.cse.ohio-state.edu/~cuir/site/GuidesHome.html'},
                            {'type': 'view', 'name': 'Roadside',
                             'url': 'http://web.cse.ohio-state.edu/~cuir/site/test2.html'}]}
    else:
        menu_data = {'button': [{'type': 'click', 'name': "主页", 'key': 'home_box'},
                            {'type': 'view', 'name': "目录",
                             'url': 'http://web.cse.ohio-state.edu/~cuir/site copy/GuidesHome.html'},
                            {'type': 'view', 'name': "道路救援",
                             'url': 'http://web.cse.ohio-state.edu/~cuir/site copy/test2.html'}]}
    response = requests.post(url, data=json.dumps(menu_data, ensure_ascii=False), verify=False).content
    return response


if __name__ == "__main__":
    token = 'EAAS7yNVP3rgBAElyTTOJBj4fZCD7iZA0HpR3TVudZBkbZBOWEAI03KUY5MbNAFhu2OGuBgZAAZCKMpulsg0iXUt6ybvcvZC6uaVPZAFjbZCHgsl4ZCZAxt9UB7jRCEuWP78rfcqkxZCZAhcrN6glZCWZAZAqOv9y0BN3GjE8H9lWZBsWvauSY9QZDZD'
    #accessToken = getWeChatAccessToken(appid, appsecret)
    #print setWeChatMenu(accessToken, 'zh')
    print setMessengerGetStarted(token)
    print setMessengerMenu(token)
    #print setMessengerGreeting(property.facebookTokenList['AC2017'])
    #print setMessengerGetStarted(messenger_token)

