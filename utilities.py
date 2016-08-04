# -*- coding: utf-8 -*-
import AKDialog
import requests
import json

socialServiceURL = 'https://api.astutesocial.com/v1/conversation/message'
socialToken = 'RsvANwIcSlIIeimtvc65cQ=='
messengerThreadUrl = "https://graph.facebook.com/v2.6/me/messages?access_token="

def sendMessengerHome(token, recipient, lang='en'):
    messengerSendURL = messengerThreadUrl + token
    data = {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "generic",
                    "elements": [
                        {
                            "title": "FordPass",
                            "image_url": "https://dl.dropboxusercontent.com/u/93550717/site/fordpasslogo.png",
                            "subtitle": "Making your journey easier, propels us further.",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "My Vehicles",
                                    "url": "https://dl.dropboxusercontent.com/u/93550717/site/test.html"
                                },
                                {
                                    "type": "web_url",
                                    "title": "My Dealer",
                                    "url": "https://dl.dropboxusercontent.com/u/93550717/site/test1.html"
                                },
                                {
                                    "type": "web_url",
                                    "url": "https://www.bing.com/mapspreview",
                                    "title": "Park"
                                }
                            ]
                        }
                    ]
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)


def generateWeChatHome(lang='en'):
    outputList = []

    temp = {'title': 'FordPass', 'description': 'Ford Pass',
            'picurl': 'https://dl.dropboxusercontent.com/u/93550717/site/fordpasslogo.png',
            'url': 'https://www.fordpass.com/'}
    outputList.append(temp)

    temp = {'title': 'My Vehicles', 'description': 'my vehicles',
            'picurl': 'https://dl.dropboxusercontent.com/u/93550717/site/myvehicles.png',
            'url': 'https://dl.dropboxusercontent.com/u/93550717/site/test.html'}
    if 'en' not in lang:
        temp['title'] = u'我的车辆'
        temp['url'] = 'https://dl.dropboxusercontent.com/u/93550717/site copy/test.html'
    outputList.append(temp)

    temp = {'title': 'My Dealer', 'description': 'dealer',
            'picurl': 'https://dl.dropboxusercontent.com/u/93550717/site/mydealer.png',
            'url': 'https://dl.dropboxusercontent.com/u/93550717/site/test1.html'}
    if 'en' not in lang:
        temp['title'] = u'经销商'
        temp['url'] = 'https://dl.dropboxusercontent.com/u/93550717/site copy/test1.html'
    outputList.append(temp)

    temp = {'title': 'Park', 'description': 'parking',
            'picurl': 'https://dl.dropboxusercontent.com/u/93550717/site/park.png',
            'url': 'https://www.bing.com/mapspreview'}
    if 'en' not in lang:
        temp['title'] = u'停车'
        #temp['url'] = 'https://www.gaode.com/'
    outputList.append(temp)

    return outputList


def storeTopics(content):
    outputDict = {}
    for line in content.strip().split('\n'):
        temp = line.split('.')
        outputDict[temp[0]] = temp[1]
    return outputDict


def AKRequest(content, topTopics, languageCode):
    if 'en' in languageCode:
        sessionID = AKDialog.iniSession(languageCode=languageCode)
        if content.lower() == 'top topics':
            response, status = AKDialog.topTopics(sessionID, languageCode)
            topTopics['topics'] = storeTopics(response)
            topTopics['lang'] = languageCode
        elif content.isdigit() and len(topTopics['topics']) > 0 and content.strip() in topTopics['topics']:
            content = topTopics['topics'][content.strip()]
            response, status = AKDialog.getAnswer(sessionID, content, languageCode)
        else:
            response, status = AKDialog.getAnswer(sessionID, content, languageCode)
    else:
        sessionID = AKDialog.iniSession(languageCode=languageCode)
        if unicode(content) == u'热门话题':
            response, status = AKDialog.topTopics(sessionID, languageCode)
            topTopics['topics'] = storeTopics(response)
            topTopics['lang'] = languageCode
        elif content.isdigit() and len(topTopics['topics']) > 0 and content.strip() in topTopics['topics']:
            content = topTopics['topics'][content.strip()]
            response, status = AKDialog.getAnswer(sessionID, content, languageCode)
        else:
            response, status = AKDialog.getAnswer(sessionID, content, languageCode)
    return topTopics, response, status


def generateConversationID(toUserName, fromUserName):
    temp = [toUserName, fromUserName]
    temp.sort()
    output = temp[0] + ',' + temp[1]

    return output


def splitMessage(inputMsg, limit):
    contentList = []
    while len(inputMsg) > limit:
        contentList.append(inputMsg[:limit])
        inputMsg = inputMsg[limit:]
    contentList.append(inputMsg)
    return contentList


def sendMessenger(token, recipient, content):
    messengerSendURL = messengerThreadUrl + token
    data = {'recipient': {'id': recipient}, 'message': {'text': content}}
    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)


def forwardUserMessage(platform, conversationStatus, conversationID, messageID, fromUserName, toUserName, content,
                       createdTime):
    data = {'access_token': socialToken, 'platform': platform, 'conversation_status': conversationStatus,
            'conversation_service_id': conversationID, 'from_id': fromUserName, 'service_id': messageID,
            'to_id': toUserName, 'content': content, 'content_type': 'text', 'created_time': createdTime}
    response = requests.post(socialServiceURL, json=data, verify=False)
    print 'Forward user messages to Social ' + str(response)
    return response


def forwardAKMessage(platform, conversationStatus, conversationID, messageID, fromUserName, toUserName, content,
                     createdTime):
    print content + ': ' + str(type(content))
    data = {'access_token': socialToken, 'platform': platform, 'conversation_status': conversationStatus,
            'conversation_service_id': conversationID, 'from_id': fromUserName, 'service_id': messageID,
            'to_id': toUserName, 'content': content, 'content_type': 'text', 'created_time': createdTime}
    #print data['content']
    response = requests.post(socialServiceURL, json=data, verify=False)
    print 'Forward knowledge message to Social ' + str(response)
    return response


def forwardConversation(platform, conversationStatus, conversationID, messageID, fromUserName, toUserName, content,
                        createdTime1, answer, createdTime2, mid=''):

    response1 = forwardUserMessage(platform, conversationStatus, conversationID, messageID, fromUserName, toUserName, content, createdTime1)
    response2 = forwardAKMessage(platform, conversationStatus, conversationID, mid, toUserName, fromUserName, answer, createdTime2)

    return response1, response2


#token = 'EAAB1kFElgToBAHRJmoshPkpQzpEF2FviWyY9GdA5lUZBPwqRVb3tQdz9vlOkkLZBpp0nihxN5yyBJxDEZC3nTROBaosUYhiMWwwPcqUJiFEZA6lqQwcFHwfpWYZB8d7v5OsaZB2YDgLqRmpdNxvHy7s4pPiuPe8xK1MhFdgoRimgZDZD'
#recipient = "1131072490299142"
#print sendMessenger(token, recipient, 'test')
#print sendMessengerHome(token, recipient, lang='en')
