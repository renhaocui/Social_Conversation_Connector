# -*- coding: utf-8 -*-
from suds.client import Client
from bs4 import BeautifulSoup
import HTMLParser


#uri = 'http://rdqa.myastutesolutions.com/RDWeb/RDService/RealDialog.wsdl'
uri = 'https://rdservice.astuteknowledge.com/FederatedSOAP/RDService/RealDialog.wsdl'
#secretKey = 'y1lrpcka'
secretKey = 't5gn26E1GGUVbvemQeT6dG9n'
#kbName = 'WeChat'
kbName = 'FordPassMobile'
#touchpoint = 'default'
touchpoint = '*'
topicContext = 'all'

client = Client(uri, retxml=True)

def iniSession(languageCode='en'):
    response = client.service.InitializeSession(TouchPointType=touchpoint, KbName=kbName, Language=languageCode, TopicContexts=topicContext, SecretKey=secretKey)
    soup = BeautifulSoup(response, 'xml')
    sessionID = soup.get_text()
    #print 'New session: ' + sessionID
    return sessionID

def topTopics(sessionID, languageCode):
    response = client.service.GetTopTopics(SessionID=sessionID, NumberOfDays=30, NumberOfTopics=5, SecretKey=secretKey)
    soup = BeautifulSoup(response, 'xml')
    topics = soup.find_all('Text')
    if len(topics) > 0:
        out = ''
        for index, topic in enumerate(topics):
            out += str(index+1)+'. '+topic.get_text()+'\n'
    else:
        if 'en' in languageCode:
            out = 'No top topics'
        else:
            out = u'没有热门话题'
    return out, '1'

def autoComplete(sessionID):
    autoComplete = client.service.GetAutoComplete(SessionID=sessionID, Utterance='how', SecretKey=secretKey)
    print 'Auto Complete'
    output = ''
    if len(autoComplete) > 0:
        for line in autoComplete[0]:
            output += line + '; '
        return output[:-2]
    else:
        return 'NONE'


def getAnswer(sessionID, question, languageCode):
    response = client.service.GetDialogResponse(SessionID=sessionID, RequestUtterance=question, SecretKey=secretKey)
    soup = BeautifulSoup(response, 'xml')
    status = soup.find('GetDialogResponseResult')['Status']

    if status == '1':
        temp = soup.find('Utterance')
        temp = HTMLParser.HTMLParser().unescape(temp.get_text())
        temp = ' '.join(temp.split())
        soup = BeautifulSoup(temp, 'xml')
        response = soup.get_text()
    else:
        if 'en' in languageCode:
            response = 'Sorry, I am having trouble finding an answer for you.'
        else:
            response = u'对不起，我找不到适合的答案'
        print 'no matched question'
    return response, status


def destSession(sessionID):
    response = client.service.DestroySession(SessionID=sessionID, SecretKey=secretKey)
    soup = BeautifulSoup(response, 'xml')
    result = soup.get_text()
    if result:
        print 'Session closed: ' + str(sessionID)
    else:
        print 'Error in close session: '+str(sessionID)
    return result


#sessionID = iniSession(languageCode='zh')
#print getAnswer(sessionID, 'Remote Start with FordPass App', 'en-US')
#print topTopics(sessionID, 'en-US')
#destSession(sessionID)
