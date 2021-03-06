# -*- coding: utf-8 -*-
import AKDialog
import requests
import json

socialServiceURL = 'https://api.astutesocial.com/v1/conversation/message'
socialToken = 'RsvANwIcSlIIeimtvc65cQ=='
messengerThreadUrl = "https://graph.facebook.com/v2.6/me/messages?access_token="

def storeTopics(content):
    outputDict = {}
    if content == 'No top topics':
        return outputDict
    for line in content.strip().split('\n'):
        temp = line.split('.')
        outputDict[temp[0]] = temp[1]
    return outputDict


def getAgentResponse(platform, conversationStatus, conversationID, messageID, fromUserName, toUserName, content, createdTime):
    data = {'access_token': socialToken, 'platform': platform, 'conversation_status': conversationStatus,
            'conversation_service_id': conversationID, 'from_id': fromUserName, 'service_id': messageID,
            'to_id': toUserName, 'content': content, 'content_type': 'text', 'created_time': createdTime}
    response = requests.post(socialServiceURL, json=data, verify=False)
    print 'Agent communicating for query: ' + str(content)

    return response


def AKRequest(content, topTopics, languageCode, kbName):
    if 'en' in languageCode:
        if content.lower() == 'top topics':
            response, status, sessionID = AKDialog.topTopics(languageCode, kbName)
            topTopics['topics'] = storeTopics(response)
            topTopics['lang'] = languageCode
            outputList = {'ExpectedAnswers': {}, 'SuggestedTopics': {}}
        elif content.isdigit() and len(topTopics['topics']) > 0 and content.strip() in topTopics['topics']:
            content = topTopics['topics'][content.strip()]
            response, status, outputList, sessionID = AKDialog.getAnswer(content, languageCode, kbName)
        else:
            response, status, outputList, sessionID = AKDialog.getAnswer(content, languageCode, kbName)
    else:
        if unicode(content) == u'热门话题':
            response, status, sessionID = AKDialog.topTopics(languageCode, kbName)
            topTopics['topics'] = storeTopics(response)
            topTopics['lang'] = languageCode
            outputList = {'ExpectedAnswers': {}, 'SuggestedTopics': {}}
        elif content.isdigit() and len(topTopics['topics']) > 0 and content.strip() in topTopics['topics']:
            content = topTopics['topics'][content.strip()]
            response, status, outputList, sessionID = AKDialog.getAnswer(content, languageCode, kbName)
        else:
            response, status, outputList, sessionID = AKDialog.getAnswer(content, languageCode, kbName)
    return topTopics, response, outputList, status, sessionID


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


def getSocialConversations(company_id):
    serviceURL = "https://api.astutesocial.com/v1/conversation"
    data = {'company_id': company_id, 'access_token': socialToken}
    response = requests.get(serviceURL, params=data, verify=False)
    print 'Get Conversations from Social ' + str(response)
    return response


def getSocialConversationMsg(id):
    serviceURL = "https://api.astutesocial.com/v1/conversation/"+str(id)+"/messages"
    data={'access_token': socialToken}
    response = requests.get(serviceURL, params=data, verify=False)
    #print 'Get Conversations Message from Social ' + str(response)
    return response


def getMaxConversationID(company_id, conversationID):
    tempID = ''
    response = getSocialConversations(company_id)
    for item in response.json():
        if item['platformName'] == 'WeChat' and item['serviceId'] == conversationID:
            tempID = item['id']
            break
    response = getSocialConversationMsg(tempID).json()
    maxID = response[len(response)-1]['id']
    return maxID, tempID


def forwardUserMessage(platform, conversationStatus, conversationID, messageID, fromUserName, toUserName, content,
                       createdTime):
    if '**' in content:
        content = content.split('**')[0]
    data = {'access_token': socialToken, 'platform': platform, 'conversation_status': conversationStatus,
            'conversation_service_id': conversationID, 'from_id': fromUserName, 'service_id': messageID,
            'to_id': toUserName, 'content': content, 'content_type': 'text', 'created_time': createdTime}
    response = requests.post(socialServiceURL, json=data, verify=False)
    print 'Forward user messages to Social ' + str(response)
    return response


def forwardAKMessage(platform, conversationStatus, conversationID, messageID, fromUserName, toUserName, content,
                     createdTime):
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


def phraseMatch(content, phrasesList):
    for phrase in phrasesList:
        if phrase in content:
            return True
    return False


if __name__ == "__main__":
    #token = 'EAAB1kFElgToBAHRJmoshPkpQzpEF2FviWyY9GdA5lUZBPwqRVb3tQdz9vlOkkLZBpp0nihxN5yyBJxDEZC3nTROBaosUYhiMWwwPcqUJiFEZA6lqQwcFHwfpWYZB8d7v5OsaZB2YDgLqRmpdNxvHy7s4pPiuPe8xK1MhFdgoRimgZDZD'
    #recipient = "1131072490299142"
    #print sendMessenger(token, recipient, 'test')
    #print sendMessengerHome(token, recipient, lang='en')
    print getMaxConversationID("127", "mpaaaaa,olCTFvw3Ts4knwCsGdMijjDfb-NE")


