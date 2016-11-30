# -*- coding: utf-8 -*-
from suds.client import Client
from bs4 import BeautifulSoup
import HTMLParser
import property

clientList = {}
for account in property.kbList:
    client = Client(property.uriList[account], retxml=True)
    clientList[account] = client


def iniSession(languageCode='en', kbName='FordPass'):
    response = clientList[kbName].service.InitializeSession(TouchPointType=property.touchPointList[kbName], KbName=property.kbList[kbName], Language=languageCode, TopicContexts=property.topicContextList[kbName],
                                                    SecretKey=property.secretKeyList[kbName])
    soup = BeautifulSoup(response, 'xml')
    sessionID = soup.get_text()
    # print 'New session: ' + sessionID
    return sessionID


def topTopics(sessionID, languageCode, kbName):
    response = clientList[kbName].service.GetTopTopics(SessionID=sessionID, NumberOfDays=30, NumberOfTopics=5, SecretKey=property.secretKeyList[kbName])
    soup = BeautifulSoup(response, 'xml')
    topics = soup.find_all('Text')
    if len(topics) > 0:
        out = ''
        for index, topic in enumerate(topics):
            out += str(index + 1) + '. ' + topic.get_text() + '\n'
    else:
        if 'en' in languageCode:
            out = 'No top topics'
        else:
            out = '没有热门话题'
    return out, '1'


'''
def autoComplete(sessionID, client):
    autoComplete = client.service.GetAutoComplete(SessionID=sessionID, Utterance='how', SecretKey=secretKey_FordPass)
    print 'Auto Complete'
    output = ''
    if len(autoComplete) > 0:
        for line in autoComplete[0]:
            output += line + '; '
        return output[:-2]
    else:
        return 'NONE'
'''


def getAnswer(sessionID, question, languageCode, kbName):
    if '**' in question:
        temp = question.split('**')
        sessionID = temp[2]
        response = clientList[kbName].service.GetDialogResponse(SessionID=sessionID, RequestUtterance=temp[0], QuestionID=temp[1], SecretKey=property.secretKeyList[kbName])
    else:
        response = clientList[kbName].service.GetDialogResponse(SessionID=sessionID, RequestUtterance=question, SecretKey=property.secretKeyList[kbName])
    #print clientList[kbName].last_sent()
    soup = BeautifulSoup(response, 'xml')
    status = soup.find('GetDialogResponseResult')['Status']
    #print soup
    outputList = {'ExpectedAnswers': {}, 'SuggestedTopics': {}}
    if status == '1':
        temp = soup.find('Utterance')
        temp = HTMLParser.HTMLParser().unescape(temp.get_text())
        temp = ' '.join(temp.split())
        response = BeautifulSoup(temp, 'xml').get_text()
        if len(soup.select('ExpectedAnswers')) > 0:
            expectList = []
            questionList = []
            for item in soup.ExpectedAnswers.find_all('Text'):
                expectList.append(item.string)
            for item in soup.ExpectedAnswers.find_all('QuestionID'):
                questionList.append(item.string)
            for index, item in enumerate(expectList):
                outputList['ExpectedAnswers'][item] = questionList[index]
        if len(soup.select('SuggestedTopics')) > 0:
            suggestList = []
            intentList = []
            for item in soup.SuggestedTopics.find_all('Text'):
                suggestList.append(item.string)
            for item in soup.SuggestedTopics.find_all('Intent'):
                intentList.append(item.string)
            for index, item in enumerate(suggestList):
                outputList['SuggestedTopics'][item] = intentList[index]
    elif status == '2':
        if 'en' in languageCode:
            response = 'Sorry, I cannot find a match to your question. Here are some related topics: \n'
        else:
            response = '对不起，我找不到适合的答案。以下是一些相关主题：\n'
        if len(soup.select('SuggestedTopics')) > 0:
            suggestList = []
            intentList = []
            for item in soup.SuggestedTopics.find_all('Text'):
                suggestList.append(item.string)
            for item in soup.SuggestedTopics.find_all('Intent'):
                intentList.append(item.string)
            for index, item in enumerate(suggestList):
                outputList['SuggestedTopics'][item] = intentList[index]
    else:
        if 'en' in languageCode:
            response = 'Sorry, I am having trouble finding an answer for you.'
        else:
            response = '对不起，我找不到适合的答案'
        print 'no matched question'
    return response, status, outputList, sessionID


def destSession(sessionID, kbName):
    response = clientList[kbName].service.DestroySession(SessionID=sessionID, SecretKey=property.secretKeyList[kbName])
    soup = BeautifulSoup(response, 'xml')
    result = soup.get_text()
    if result:
        print 'Session closed: ' + str(sessionID)
    else:
        print 'Error in close session: ' + str(sessionID)
    return result


#sessionID = iniSession(languageCode='en', kbName='McDonalds')
#print sessionID
#response, status, outputList, sessionID = getAnswer(sessionID, 'cannot connect to wifi', 'en', 'McDonalds')
#print status
#print response
#print outputList
#print topTopics(sessionID, 'en', 0)
# destSession(sessionID, client)