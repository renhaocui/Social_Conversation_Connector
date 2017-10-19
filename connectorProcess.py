# -*- coding: utf-8 -*-
import traceback
import utilities
from flask import Flask, jsonify, make_response, request
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from threading import Thread
from langid.langid import LanguageIdentifier, model
from datetime import datetime, timedelta
import wechatManager
import xmltodict
import hashlib
import messageCreator
import property
import sys, os
import json
import specialCases
import time

logFile = open('debug.log', 'a')

app = Flask(__name__)

digitMapper = {'one': '1', 'two': '2', 'three': '3', 'four': '4', 'five': '5', 'six': '6', 'seven': '7', 'eight': '8', 'nine': '9', 'ten': '10', 'eleven': '11', 'twelve': '12'}

accountList = ['FordPass', 'OmegaAir', 'McDonalds', 'Colgate', 'Colgate']

WeChatMPMapper = {'Renhao': 'olCTFvw3Ts4knwCsGdMijjDfb-NE', 'astute ': 'olCTFvz20szF5JueVAzO9PfcVJO0', 'Alex George': 'olCTFv2CuBeD6rcwAS3SgElETyvM'}

wechatInstList = {}
for account in accountList:
    tempConf = WechatConf(token=property.wechatTokenList[account], appid=property.wechatAppIdList[account], appsecret=property.wechatAppSecretList[account], encrypt_mode='normal')
    tempWechat = WechatBasic(conf=tempConf)
    wechatInstList[account] = tempWechat
wechatAccountMapper = {'gh_ae02c9f6f14e': 'FordPass', 'gh_80d79803a408': 'OmegaAir'}

languageCode_en = 'en-US'
languageCode_zh = 'zh-CN'
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)
global accountStatusList
accountStatusList = {'WeChat': {'gh_ae02c9f6f14e': (True, False), 'gh_80d79803a408': (True, False)},
                     'Facebook': {'276165652474701': (True, False), '1673794586266685': (True, False)},
                     'Alexa': {(True, False)},
                     'mp00000': (True, False)}  # (on_help, on_kms_failure)
# Doug Alexa userId: amzn1.ask.account.AGU7QUCAQU2SC57PI22T74X5ACWYORNEXRMNYYS32PPWPHVSV3WGHUS3ULVEPMTTPK4PSYPSKFYJIQO7DASINBRVVKFDMLPLXAACCMC2BF74BNY5CGI6CY2K2ESYECWPBWPFPDMSHY5QHE3H7FR2QSLNRWAZZYHUCJGE73EHW2BNIKJ5NODIHAQBMWVU3O47AL3ZDLBL2OXG6YA

topTopicsInfo = {'WeChat': {}, 'Facebook': {}}
suggestionInfo = {'WeChat': {}, 'Facebook': {}}
for account in accountList:
    topTopicsInfo['WeChat'][account] = {}
    suggestionInfo['WeChat'][account] = {}
    topTopicsInfo['Facebook'][account] = {}
    suggestionInfo['Facebook'][account] = {}
global conversationStatusList
conversationStatusList = {'WeChat': {}, 'Facebook': {}, 'Alexa': 'kms'}

global userLocation
userLocation={'WeChat': {}, 'Facebook': {}}


if app.debug is not True:
    import logging
    from logging import Formatter
    from logging.handlers import RotatingFileHandler

    TEXT_MAX_PRINT_LENGTH = 25
    LOG_FILENAME = 'wechat_test.log'

    handler = RotatingFileHandler(LOG_FILENAME, maxBytes=10000000, backupCount=10)

    formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    app.logger.setLevel(logging.INFO)
    app.logger.addHandler(handler)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'not found'}), 404)


@app.route('/', methods=['GET'])
def wechatServerVerifier():
    verification_token = 'astute_wechat_test'
    signature = request.args['signature']
    timestamp = request.args['timestamp']
    nonce = request.args['nonce']
    echostr = request.args['echostr']
    if (signature is None) or (timestamp is None) or (nonce is None) or (echostr is None):
        return 'ERROR'
    if not signature or not timestamp or not nonce:
        return 'Error'
    tmp_list = [verification_token, timestamp, nonce]
    tmp_list.sort()
    tmp_str = ''.join(tmp_list)
    if signature != hashlib.sha1(tmp_str.encode('utf-8')).hexdigest():
        return 'Error'
    print 'WeChat server 1 verification: Accept'
    return make_response(echostr)


@app.route('/FBmessenger', methods=['GET'])
def messengerServerVerifier():
    verification_token = 'astute_messenger_test'
    if request.args['hub.mode'] == 'subscribe' and request.args['hub.verify_token'] == verification_token:
        print 'Messenger verification passed'
        return request.args['hub.challenge'], 200
    else:
        return 'ERROR', 200


@app.route('/validate_account', methods=['POST'])
def wechatValidateAccount():
    body = request.get_json()
    appID = body['app_id']
    secret = body['secret']
    print 'Account Verification for appID: ' + appID
    response = wechatManager.getAccessToken(appID, secret)
    if 'access_token' in response:
        return '', 200
    else:
        return '', 503


@app.route('/lookup_user', methods=['POST'])
def wechatLookupUser():
    body = request.get_json()
    userID = body['user_id']
    appID = body['app_id']
    secret = body['secret']
    print 'Looking up user info for: ' + userID
    try:
        accessToken = wechatManager.getAccessToken(appID, secret)['access_token']
        response = wechatManager.getAccountInfo(accessToken, userID)

        if 'errcode' in response:
            return '', 503
        else:
            return response, 200
    except:
        return '', 503


@app.route('/set_conversation_status', methods=['POST'])
def setConversationStatus():
    global conversationStatusList
    body = request.get_json()
    platform = body['platform']
    conversationID = body['conversation_id']
    status = body['status']
    print '[' + platform + ']Conversation status update for conversationID: [' + conversationID + ']'

    conversationStatusList[platform][conversationID] = status
    return '', 200


@app.route('/send_message', methods=['POST'])
def sendMessage():
    global conversationStatusList
    body = request.get_json()
    access_token = body['access_token']
    platform = body['platform']
    conversationID = body['conversation_id']
    contentType = body['content_type']
    content = body['content']
    appID = body['app_id']
    secret = body['secret']
    userID = body['user_id']
    temp = conversationID.split(',')
    print 'Send message to user for platform: '+platform
    if temp[0] == userID:
        accountID = temp[1]
    else:
        accountID = temp[0]

    if 'mpaaaaa,' in conversationID:
        utilities.forwardUserMessage(platform, 'agent', conversationID, '', accountID, userID, content,
                                     str(datetime.now().isoformat()[:-7]) + 'Z')
        return '', 200
    elif conversationID not in conversationStatusList[platform]:
        return '', 503
    elif conversationStatusList[platform][conversationID] == 'agent':
        if contentType.lower() == 'text':
            if platform == 'WeChat':
                #tempWechat = wechatInstList[wechatAccountMapper[accountID]]
                tempConf = WechatConf(appid=appID, appsecret=secret, encrypt_mode='normal')
                tempWechat = WechatBasic(conf=tempConf)
                contentList = utilities.splitMessage(content, 400)
                for content in contentList:
                    tempWechat.send_text_message(user_id=userID, content=content)
                    utilities.forwardUserMessage(platform, 'agent', conversationID, '', accountID, userID, content, str(datetime.now().isoformat()[:-7]) + 'Z')
                print 'send message to WeChat, success'
                return '', 200
            else:
                contentList = utilities.splitMessage(content, 320)
                status = True
                for content in contentList:
                    try:
                        sendStatus, responseContent = utilities.sendMessenger(access_token, userID, content)
                        print sendStatus
                        if sendStatus.status_code != 200:
                            status = False
                        else:
                            utilities.forwardUserMessage(platform, 'agent', conversationID, responseContent['message_id'], accountID, userID, content,
                                                         str(datetime.now().isoformat()[:-7]) + 'Z')
                    except Exception as e:
                        print e
                        continue
                if status:
                    print 'send message to Messenger, success'
                    statusCode = 200
                else:
                    statusCode = 503
                return '', statusCode
        else:
            return '', 503
    else:
        return '', 503


@app.route('/set_account_status', methods=['POST'])
def setAccountStatus():
    global accountStatusList
    body = request.get_json()
    platform = body['platform']
    accountID = body['user_id']
    print '[' + platform + '] Set Account Status for: ' + str(accountID)

    helpFlag = body['escalate_on_help']
    kmsFailureFlag = body['escalate_on_kms_failure']
    accountStatusList[platform][accountID] = (helpFlag, kmsFailureFlag)
    return '', 200


def sendWechatResponse(weChat, response, conversationID, messageID, fromUserName, toUserName):
    responseList = utilities.splitMessage(response, 400)
    for response in responseList:
        weChat.send_text_message(user_id=fromUserName, content=response)
        utilities.forwardAKMessage('WeChat', 'kms', conversationID, messageID, toUserName, fromUserName, response,
                                   str(datetime.fromtimestamp(weChat.message.time + 1).isoformat()) + 'Z')
    return True


@app.route('/wechatMP', methods=['POST'])
def wechatMPProcessRequest():
    global conversationStatusList
    global accountStatusList
    print 'Request received from WechatMP...'
    body = request.json
    print body
    if 'text' in body:
        content = body['text']
        msgLang = identifier.classify(content)[0]
        userID = WeChatMPMapper[body['userInfo']['nickName']]
        accountID = 'mpaaaaa'
        conversationID = utilities.generateConversationID(accountID, userID)
        print "ConversationID: "+conversationID
        if accountID in accountStatusList['WeChat']:
            accountStatus = accountStatusList['WeChat'][userID]
        else:
            accountStatus = (True, False)
        userMsgTime = str(datetime.now().isoformat()[:-7]) + 'Z'
        messageID = 'mp' + str(time.time())
        if 'zh' not in msgLang.lower():
            response, rspFlag = specialCases.caseHandlerMP(content, lang='en')
            if rspFlag == 'Valid':
                rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                t = Thread(target=utilities.forwardConversation,
                           args=(
                           'WeChat', 'kms', conversationID, messageID, userID, accountID, content, userMsgTime, response,
                           rspTime, messageID + 'r'))
                t.start()
                return response, 200
            elif content.lower() == 'help' and accountStatus[0] and (
                        (conversationID not in conversationStatusList['WeChat']) or (
                                conversationStatusList['WeChat'][conversationID] == 'kms')):
                conversationStatusList['WeChat'][conversationID] = 'agent'
                response = 'Agent service requested, please describe your request. \n Type END to disconnect.'
                rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                try:
                    t = Thread(target=utilities.forwardConversation,
                               args=('WeChat', 'agent', conversationID, messageID, userID, accountID, content, userMsgTime, response, rspTime, messageID + 'r'))
                    t.start()
                except Exception as e:
                    print e
                    print 'Error in forwarding messages to social'
                return response, 200
            elif content.lower() == 'end' and (conversationID in conversationStatusList['WeChat']) and \
                            conversationStatusList['WeChat'][conversationID] == 'agent':
                conversationStatusList['WeChat'][conversationID] = 'kms'
                response = 'Agent Disconnected, Goodbye'
                rspTime = str((datetime.now()+timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                try:
                    t = Thread(target=utilities.forwardConversation,
                               args=('WeChat', 'kms', conversationID, messageID, userID, accountID, content,
                                              userMsgTime, response,
                                              rspTime, messageID + 'r'))
                    t.start()
                except Exception as e:
                    print e
                    print 'Error in forwarding messages to social'
                return response, 200
                # agent conversation
            elif (conversationID in conversationStatusList['WeChat']) and conversationStatusList['WeChat'][
                                                                                    conversationID] == 'agent':
                maxID, tempID = utilities.getMaxConversationID("127", conversationID)

                t = Thread(target=utilities.forwardUserMessage,
                           args=('WeChat', 'agent', conversationID, messageID, userID, accountID, content,
                                             userMsgTime))
                t.start()
                # do something here and return the response
                responded = False
                response = ''
                print 'Waiting for agent to response, maxID: ' + str(maxID)
                waitingTime = 0
                while (not responded):
                    time.sleep(1)
                    waitingTime += 1
                    responseObj = utilities.getSocialConversationMsg(tempID).json()
                    if waitingTime > 300:
                        response = 'All agents are busy at this moment, please try again later.'
                        conversationStatusList['WeChat'][conversationID] = 'kms'
                        rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                        t = Thread(target=utilities.forwardAKMessage,
                                   args=('WeChat', 'kms', conversationID, messageID, userID, accountID, response,
                                         rspTime))
                        t.start()
                        break
                    for item in responseObj:
                        if item['id'] > maxID and item["fromServiceId"] == accountID:
                            response += item['content'] + ' '
                            print 'Agent response received '
                            responded = True
                return response, 200
            else:
                try:
                    print 'Asking through KnowledgeBase'
                    topTopics, response, outputList, status, sessionID = utilities.AKRequest(content, {}, languageCode_en, 'FordPass')
                    rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                    try:
                        t = Thread(target=utilities.forwardConversation,
                                   args=('WeChat', 'kms', conversationID, messageID, userID, accountID, content, userMsgTime, response, rspTime, messageID + 'r'))
                        t.start()
                    except Exception as e:
                        print e
                        print 'Error in forwarding messages to social'

                except Exception as e:
                    print e
                    response = 'Cannot connect to Astute Knowledge Server. Type HELP for a real agent.'
                    return response, 200

        else:
            response, rspFlag = specialCases.caseHandlerMP(content, lang='zh')
            if rspFlag == 'Valid':
                rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                t = Thread(target=utilities.forwardConversation,
                           args=(
                               'WeChat', 'kms', conversationID, messageID, userID, accountID, content, userMsgTime,
                               response,
                               rspTime, messageID + 'r'))
                t.start()
                return response, 200
            if content.lower() == u'求助' and accountStatus[0] and (
                        (conversationID not in conversationStatusList['WeChat']) or (
                                conversationStatusList['WeChat'][conversationID] == 'kms')):
                conversationStatusList['WeChat'][conversationID] = 'agent'
                response = '客服连接中，请描述您的问题。\n输入【结束】将结束本次服务。'
                rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                try:
                    t = Thread(target=utilities.forwardConversation,
                               args=('WeChat', 'agent', conversationID, messageID, userID, accountID, content, userMsgTime, response, rspTime, messageID + 'r'))
                    t.start()
                except Exception as e:
                    print e
                    print 'Error in forwarding messages to social'
                return response, 200
            elif content.lower() == u'结束' and (conversationID in conversationStatusList['WeChat']) and \
                            conversationStatusList['WeChat'][conversationID] == 'agent':
                conversationStatusList['WeChat'][conversationID] = 'kms'
                response = '本次服务结束，谢谢。'
                rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                try:
                    t = Thread(target=utilities.forwardConversation,
                               args=
                               ('WeChat', 'kms', conversationID, messageID, userID, accountID, content, userMsgTime, response, rspTime, messageID + 'r'))
                    t.start()
                except Exception as e:
                    print e
                    print 'Error in forwarding messages to social'
                return response, 200
            elif (conversationID in conversationStatusList['WeChat']) and conversationStatusList['WeChat'][
                                                                                    conversationID] == 'agent':
                maxID, tempID = utilities.getMaxConversationID("127", conversationID)
                t = Thread(target=utilities.forwardUserMessage,
                           args=('WeChat', 'agent', conversationID, messageID, userID, accountID, content,
                                             userMsgTime))
                t.start()
                # do something here and return the response
                responded = False
                response = ''
                print 'Waiting for agent to response, maxID: ' + str(maxID)
                waitingTime = 0
                while (not responded):
                    time.sleep(1)
                    waitingTime += 1
                    responseObj = utilities.getSocialConversationMsg(tempID).json()
                    if waitingTime > 300:
                        response = 'All agents are busy at this moment, please try again later.'
                        conversationStatusList['WeChat'][conversationID] = 'kms'
                        rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                        t = Thread(target=utilities.forwardAKMessage,
                                   args=('WeChat', 'kms', conversationID, messageID, userID, accountID, content,
                                         rspTime))
                        t.start()
                        break
                    for item in responseObj:
                        if item["id"] > maxID and item["fromServiceId"] == accountID:
                            response += item['content'] + ' '
                            print 'Agent response received '
                            responded = True
                return response, 200
            else:
                try:
                    topTopics, response, outputList, status, sessionID = utilities.AKRequest(content, {}, languageCode_zh, 'FordPass')
                    rspTime = str((datetime.now() + timedelta(seconds=1)).isoformat()[:-7]) + 'Z'
                    try:
                        t = Thread(target=utilities.forwardConversation,
                                   args=('WeChat', 'kms', conversationID, messageID, userID, accountID, content, userMsgTime, response, rspTime, messageID + 'r'))
                        t.start()
                    except Exception as e:
                        print e
                        print 'Error in forwarding messages to social'
                except Exception as e:
                    print e
                    response = '无法连接数据服务器。 输入【求助】将为您安排客服。'
                    return response, 200

        return response, 200


@app.route('/AmazonAlexa', methods=['POST'])
def alexaProcessRequest():
    global conversationStatusList
    body = request.json
    logFile.write(str(body['request'])+'\n')
    out = {
        "version": "1.0",
        "sessionAttributes": {
            "supportedHoriscopePeriods": {
                "daily": True,
                "weekly": False,
                "monthly": False
            }
        },
        "response": {
            "outputSpeech": {
                "type": "PlainText",
                "text": "Dummy response"
            },
            "card": {
                "type": "Simple",
                "title": "Connection Test",
                "content": "Dummy response"
            },
            "reprompt": {
                "outputSpeech": {
                    "type": "PlainText",
                    "text": "Can I help you with anything else?"
                }
            },
            "shouldEndSession": True
        }
    }

    if body['request']['intent']['name'] == 'Connectivity':
        out['response']['outputSpeech']['text'] = "This response confirms the connectivity of the server. The response function works as expected."
        out['response']['card']['content'] = "This response confirms the connectivity of the server. The response function works as expected."
    elif body['request']['intent']['name'] == 'GetAnswer':
        query = body['request']['intent']['slots']['Query']['value']
        # agent escalation
        #print query
        if 'can i talk to the tooth fairy' in query.lower() and conversationStatusList['Alexa'] == 'kms':
            conversationStatusList['Alexa'] = 'agent'
            #sender = body['session']['user']['userId']
            #recipient = 'AstuteAlexa'
            #conversationID = utilities.generateConversationID(recipient, sender)
            #createdTime = body['request']['timestamp']
            #messageID = body['request']['requestId']
            response = raw_input('User ask: ' + query+'\n')
            out['response']['outputSpeech']['text'] = response
            out['response']['card']['content'] = response
            out['response']['card']['title'] = query
            out['response']['shouldEndSession'] = False
            print 'Agent Answer Sent'
        elif 'can i speak with someone' in query.lower() and conversationStatusList['Alexa'] == 'kms':
            conversationStatusList['Alexa'] = 'agent'
            response = 'Yes, what is your question?'
            out['response']['outputSpeech']['text'] = response
            out['response']['card']['content'] = response
            out['response']['card']['title'] = 'Agent Connecting'
            out['response']['shouldEndSession'] = False
        elif query.lower().endswith('goodbye') and conversationStatusList['Alexa'] == 'agent':
            conversationStatusList['Alexa'] = 'kms'
            out['response']['outputSpeech']['text'] = 'Bye'
            out['response']['card']['content'] = 'Bye'
            out['response']['card']['title'] = query
            print 'Agent disconnected'
        elif conversationStatusList['Alexa'] == 'agent':
            response = raw_input('User ask: ' + query + '\n')
            out['response']['outputSpeech']['text'] = response
            out['response']['card']['content'] = response
            out['response']['card']['title'] = query
            out['response']['shouldEndSession'] = False
            print 'Agent Answer Sent'
        elif 'pull out a wiggly tooth' in query.lower():
            out['response']['outputSpeech']['text'] = 'Is it an adult tooth or a baby tooth?'
            out['response']['card']['content'] = 'Is it an adult tooth or a baby tooth?'
            out['response']['card']['title'] = query
            out['response']['shouldEndSession'] = False
        elif 'baby tooth' in query.lower():
            out['response']['outputSpeech']['text'] = 'Phew. If you and your child can handle the inconvenience, it is best not to pull a loose tooth, but rather let them wiggle it until it falls out on its own.'
            out['response']['card']['content'] = 'Phew. If you and your child can handle the inconvenience, it is best not to pull a loose tooth, but rather let them wiggle it until it falls out on its own.'
            out['response']['card']['title'] = query
        elif 'remind the kids to brush their teeth this evening' in query.lower():
            out['response']['outputSpeech']['text'] = 'Sure, at what time?'
            out['response']['card']['content'] = 'Sure, at what time?'
            out['response']['card']['title'] = query
            out['response']['shouldEndSession'] = False
        #elif query.lower in ['one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten', 'eleven', 'twelve']:
        elif query.lower() in digitMapper:
            out['response']['outputSpeech']['text'] = 'Ok, I will remind them at ' + query + ' tonight'
            out['response']['card']['content'] = 'Ok, I will remind them at ' + digitMapper[query] + ' tonight'
            out['response']['card']['title'] = query
        elif 'make an appointment at my dealer' in query.lower():
            out['response']['outputSpeech']['text'] = 'Agent service requested, please wait. Say end to disconnect.'
            out['response']['card']['content'] = 'Agent service requested, please wait. Say end to disconnect.'
            out['response']['card']['title'] = 'Agent Requested'
        elif 'use my ford pass perks at mcdonalds' in query.lower():
            out['response']['outputSpeech']['text'] = 'Yes, at participating mcdonalds restaurants'
            out['response']['card']['content'] = 'Yes, at participating mcdonalds restaurants'
            out['response']['card']['title'] = 'Use FordPass'
        elif 'book a parking spot near the office' in query.lower():
            out['response']['outputSpeech']['text'] = 'Which office?'
            out['response']['card']['content'] = 'Which office?'
            out['response']['card']['title'] = ''
        elif 'twenty four hundred corporate exchange' in query.lower():
            out['response']['outputSpeech']['text'] = 'yes, the parking will be 10 dollar a day. You will see confirmation in the app.'
            out['response']['card']['content'] = 'yes, the parking will be 10 dollar a day. You will see confirmation in the app.'
            out['response']['card']['title'] = 'Cost'
        else:
            topTopics, response, outputList, status, sessionID = utilities.AKRequest(query, {}, languageCode_en, 'Colgate')
            topTopics, responseCard, outputListCard, statusCard, sessionID = utilities.AKRequest(query, {}, languageCode_en, 'ColgateCard')
            out['response']['outputSpeech']['text'] = messageCreator.constructAlexaText(status, response, outputList)
            out['response']['card']['content'] = messageCreator.constructAlexaText(statusCard, responseCard, outputListCard)
            out['response']['card']['title'] = query
            #utilities.forwardUserMessage('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime)
            #utilities.forwardAKMessage('Facebook', 'kms', conversationID, responseContent['message_id'], recipient, sender, response,
            #                           str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z')

    return json.dumps(out), 200


@app.route('/FBmessenger', methods=['POST'])
def messengerProcessRequest():
    agentPhrases = ['how do i schedule an appointment', 'i want to schedule an appointment', 'what time is my appointment']
    global accountStatusList
    global conversationStatusList
    body = request.json
    locationObj = {}
    if 'messaging' in body['entry'][0]:
        specialCase = 'None'
        if 'postback' in body['entry'][0]['messaging'][0]:
            payload = body['entry'][0]['messaging'][0]['postback']['payload']
            if '**' in payload:
                specialCase = 'Click'
        if 'postback' in body['entry'][0]['messaging'][0] and specialCase == 'None':
            recipient = body['entry'][0]['messaging'][0]['recipient']['id']
            if recipient in property.facebookAccountMapper:
                facebookToken = property.facebookTokenList[property.facebookAccountMapper[recipient]]
                sender = body['entry'][0]['messaging'][0]['sender']['id']
                payload = body['entry'][0]['messaging'][0]['postback']['payload']
                statusCode = 500
                if payload == 'home_page':
                    index = 0
                    while statusCode != 200 and index < 3:
                        sendStatus, responseContent = messageCreator.sendMessengerHome(facebookToken, sender)
                        statusCode = sendStatus.status_code
                        index += 1
                    print 'User [' + sender + '] request for home page. ' + str(sendStatus)
                    return '', 200
                elif payload == 'get_started':
                    sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender,
                                                                          'Welcome! How can I help you?')
                    print 'User [' + sender + '] get started.' + str(sendStatus)
                    return '', 200
                else:
                    specialCase = 'Click'
        if 'message' in body['entry'][0]['messaging'][0] or specialCase != 'None':
            #print body
            recipient = body['entry'][0]['messaging'][0]['recipient']['id']
            '''
            print 'Recipient: ' + str(recipient)
            try:
                facebookToken = property.facebookTokenList[property.facebookAccountMapper[recipient]]
            except Exception as e:
                print 'Recipient not found: '+str(recipient)
                print e
            '''
            if recipient in property.facebookAccountMapper:
                print 'Recipient: ' + str(recipient)
                facebookToken = property.facebookTokenList[property.facebookAccountMapper[recipient]]
                logFile.write(str(body)+'\n')
                sender = body['entry'][0]['messaging'][0]['sender']['id']
                timestamp = body['entry'][0]['messaging'][0]['timestamp'] / 1000
                conversationID = utilities.generateConversationID(recipient, sender)
                createdTime = str(datetime.fromtimestamp(timestamp).isoformat()) + 'Z'
                if specialCase == 'Click':
                    messageID = body['entry'][0]['id']
                    content = payload
                elif 'attachments' in body['entry'][0]['messaging'][0]['message']:
                    if body['entry'][0]['messaging'][0]['message']['attachments'][0]['type'] == 'location':
                        lat = body['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['lat']
                        lon = body['entry'][0]['messaging'][0]['message']['attachments'][0]['payload']['coordinates']['long']
                        locationObj = {'lat': lat, 'lon': lon}
                        content = ''
                        specialCase = 'Location'
                        if property.facebookAccountMapper[recipient] == 'Colgate':
                            specialCase = 'Location_Colgate'
                    elif body['entry'][0]['messaging'][0]['message']['attachments'][0]['type'] == 'image':
                        content = '0987654321'
                        messageID = body['entry'][0]['messaging'][0]['message']['mid']
                        specialCase = 'image'
                else:
                    content = body['entry'][0]['messaging'][0]['message']['text']
                    messageID = body['entry'][0]['messaging'][0]['message']['mid']

                #msgLang = identifier.classify(content)[0]
                msgLang = 'en'

                if recipient in accountStatusList['Facebook']:
                    accountStatus = accountStatusList['Facebook'][recipient]
                else:
                    accountStatus = (True, False)
                if sender not in topTopicsInfo['Facebook'][property.facebookAccountMapper[recipient]]:
                    topTopics = {'lang': msgLang, 'topics': {}}
                    topTopicsInfo['Facebook'][property.facebookAccountMapper[recipient]][sender] = topTopics
                else:
                    topTopics = topTopicsInfo['Facebook'][property.facebookAccountMapper[recipient]][sender]
                if content.isdigit() and len(topTopics['topics']) > 0:
                    msgLang = topTopics['lang']

                if 'zh' not in msgLang:
                    #print 'English Session'
                    # hard coded cases
                    sendStatus, responseContent, handeled = specialCases.caseHandler_facebook(content, facebookToken, sender, property.facebookAccountMapper[recipient], specialCase, locationObj)
                    if not handeled:
                        # start of agent conversation
                        if (content.lower() == 'help' or utilities.phraseMatch(content.lower(), agentPhrases)) and accountStatus[0] and (
                                    (conversationID not in conversationStatusList['Facebook']) or (
                                            conversationStatusList['Facebook'][conversationID] == 'kms')):
                            conversationStatusList['Facebook'][conversationID] = 'agent'
                            response = 'Agent service requested, please wait...\n Type END to disconnect.'
                            sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                            if sendStatus.status_code == 200:
                                utilities.forwardConversation('Facebook', 'agent', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                              str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                        # end of agent conversation
                        elif content.lower() == 'end' and (conversationID in conversationStatusList['Facebook']) \
                                and conversationStatusList['Facebook'][conversationID] == 'agent':
                            conversationStatusList['Facebook'][conversationID] = 'kms'
                            response = 'Agent Disconnected, Goodbye'
                            sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                            if sendStatus.status_code == 200:
                                utilities.forwardConversation('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                              str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                        # agent conversation
                        elif (conversationID in conversationStatusList['Facebook']) and conversationStatusList['Facebook'][conversationID] == 'agent':
                            utilities.forwardUserMessage('Facebook', 'agent', conversationID, messageID, sender, recipient, content, createdTime)
                        # AstuteKnowledge
                        else:
                            try:
                                topTopics, response, outputList, status, sessionID = utilities.AKRequest(content, topTopics, languageCode_en, property.facebookAccountMapper[recipient])
                                topTopicsInfo['Facebook'][property.facebookAccountMapper[recipient]][sender] = topTopics
                                if len(outputList['ExpectedAnswers']) > 0 and status == '1':
                                    utilities.forwardUserMessage('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime)
                                    sendStatus, responseContent = messageCreator.sendMessengerAKStructure(facebookToken, sender, response, outputList, 'ExpectedAnswers', sessionID)
                                    utilities.forwardAKMessage('Facebook', 'kms', conversationID, responseContent['message_id'], recipient, sender, response,
                                                                       str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z')
                                else:
                                    if status == '1':
                                        utilities.forwardUserMessage('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime)
                                        if '[map]' in response:
                                            statusCode = 500
                                            index = 0
                                            while statusCode != 200 and index < 3:
                                                sendStatus, responseContent = messageCreator.sendMessengerMapStructure(
                                                    facebookToken, sender, response)
                                                statusCode = sendStatus.status_code
                                                index += 1
                                        elif '[pic]' in response:
                                            statusCode = 500
                                            index = 0
                                            while statusCode != 200 and index < 3:
                                                sendStatus, responseContent = messageCreator.sendMessengerPicStructure(
                                                    facebookToken, sender, response)
                                                statusCode = sendStatus.status_code
                                                index += 1
                                        else:
                                            contentList = utilities.splitMessage(response, 320)
                                            for content in contentList:
                                                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, content)
                                                if sendStatus.status_code == 200:
                                                    utilities.forwardAKMessage('Facebook', 'kms', conversationID, responseContent['message_id'], recipient, sender, content,
                                                                           str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z')
                                    elif status == '2':
                                        response += '\n Or you can type HELP for a real agent.'
                                        utilities.forwardUserMessage('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime)
                                        sendStatus, responseContent = messageCreator.sendMessengerAKStructure(facebookToken, sender, response, outputList, 'SuggestedTopics', sessionID)
                                        if sendStatus.status_code == 200:
                                            utilities.forwardAKMessage('Facebook', 'kms', conversationID, responseContent['message_id'], recipient, sender, response,
                                                                           str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z')
                                    else:
                                        if accountStatus[1]:
                                            response += ' An agent will be with you shortly.'
                                            conversationStatusList['Facebook'][conversationID] = 'agent'
                                            sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                                            if sendStatus.status_code == 200:
                                                utilities.forwardConversation('Facebook', 'agent', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                                              str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                                        else:
                                            if accountStatus[0]:
                                                response += ' Type HELP for a real agent.'
                                            sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                                            if sendStatus.status_code == 200:
                                                utilities.forwardConversation('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                                              str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                            except Exception as e:
                                print e
                                exc_type, exc_obj, exc_tb = sys.exc_info()
                                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                                print(exc_type, fname, exc_tb.tb_lineno)
                                response = 'Cannot connect to Astute Knowledge Server. Type HELP for a real agent.'
                                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                                if sendStatus.status_code == 200:
                                    t = Thread(target=utilities.forwardConversation,
                                               args=('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                     str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id']))
                                    t.start()
                                return '', 200
                else:
                    print 'Chinese Session'
                    # start of agent conversation
                    if content == u'求助' and accountStatus[0] and (
                                (conversationID not in conversationStatusList['Facebook']) or (
                                        conversationStatusList['Facebook'][conversationID] == 'kms')):
                        conversationStatusList['Facebook'][conversationID] = 'agent'
                        response = '客服连接中，请稍后...\n输入【结束】将结束本次服务。'
                        sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                        if sendStatus.status_code == 200:
                            utilities.forwardConversation('Facebook', 'agent', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                          str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                    # end of agent conversation
                    elif content == u'结束' and (conversationID in conversationStatusList['Facebook']) and \
                                    conversationStatusList['Facebook'][conversationID] == 'agent':
                        conversationStatusList['Facebook'][conversationID] = 'kms'
                        response = '本次服务结束，谢谢。'
                        sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                        if sendStatus.status_code == 200:
                            utilities.forwardConversation('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                          str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                    # agent conversation
                    elif (conversationID in conversationStatusList['Facebook']) and conversationStatusList['Facebook'][
                        conversationID] == 'agent':
                        utilities.forwardUserMessage('Facebook', 'agent', conversationID, messageID, sender, recipient, content,
                                                     createdTime)
                    else:
                        try:
                            topTopics, response, outputList, status, sessionID = utilities.AKRequest(content, topTopics, languageCode_zh, property.facebookAccountMapper[recipient])
                            topTopicsInfo['Facebook'][property.facebookAccountMapper[recipient]][sender] = topTopics
                            if len(outputList['ExpectedAnswers']) > 0 and status == '1':
                                utilities.forwardUserMessage('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime)
                                sendStatus, responseContent = messageCreator.sendMessengerAKStructure(facebookToken, sender, response, outputList, 'ExpectedAnswers', sessionID, lang='zh')
                                utilities.forwardAKMessage('Facebook', 'kms', conversationID, responseContent['message_id'], recipient, sender, response,
                                                                   str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z')
                            else:
                                if status == '1':
                                    utilities.forwardUserMessage('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime)
                                    if len(outputList) > 0:
                                        messageCreator.sendMessengerAKStructure(facebookToken, sender, response, outputList, lang='zh')
                                    else:
                                        contentList = utilities.splitMessage(response, 320)
                                        for content in contentList:
                                            sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, content)
                                            if sendStatus.status_code == 200:
                                                utilities.forwardAKMessage('Facebook', 'kms', conversationID, responseContent['message_id'], recipient, sender, content,
                                                                           str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z')
                                elif status == '2':
                                    response += '\n  或者您也可以输入【求助】，我们将为您安排客服。'
                                    utilities.forwardUserMessage('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime)
                                    sendStatus, responseContent = messageCreator.sendMessengerAKStructure(facebookToken, sender, response, outputList, 'SuggestedTopics', sessionID, lang='zh')
                                    if sendStatus.status_code == 200:
                                        utilities.forwardAKMessage('Facebook', 'kms', conversationID, responseContent['message_id'], recipient, sender, response,
                                                                   str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z')
                                else:
                                    if accountStatus[1]:
                                        response += ' 正在为您转接客服，请稍候。'
                                        conversationStatusList['Facebook'][conversationID] = 'agent'
                                        sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                                        if sendStatus.status_code == 200:
                                            utilities.forwardConversation('Facebook', 'agent', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                                          str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                                    else:
                                        if accountStatus[0]:
                                            response += ' 输入【求助】将为您安排客服。'
                                        sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                                        if sendStatus.status_code == 200:
                                            utilities.forwardConversation('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                                          str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id'])
                        except Exception as e:
                            print e
                            response = '无法连接数据服务器。 输入【求助】将为您安排客服。'
                            sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, response)
                            if sendStatus.status_code == 200:
                                t = Thread(target=utilities.forwardConversation,
                                           args=('Facebook', 'kms', conversationID, messageID, sender, recipient, content, createdTime, response,
                                                 str(datetime.fromtimestamp(timestamp + 1).isoformat()) + 'Z', responseContent['message_id']))
                                t.start()
                            return '', 200
                        return '', 200
                    return '', 200
                return '', 200
            return '', 200
        return '', 200
    return '', 200


@app.route('/', methods=['POST'])
def wechatProcessRequest():
    global conversationStatusList
    global accountStatusList
    global userLocation
    try:
        xml_body = request.data
        raw_body = xmltodict.parse(xml_body)
        accountID = raw_body['xml']['ToUserName']
        wechat = wechatInstList[wechatAccountMapper[accountID]]
        wechat.parse_data(xml_body)
        if accountID in accountStatusList['WeChat']:
            accountStatus = accountStatusList['WeChat'][accountID]
        else:
            accountStatus = (True, False)
    except ParseError as pError:
        print 'Invalid Body Text: ' + str(pError)
        print xml_body

    fromUserName = str(wechat.message.source)
    toUserName = str(wechat.message.target)
    print str(wechat.message.type) + ' service request received from user [' + fromUserName + ']'

    if wechat.message.type == 'location':
        print 'User [' + fromUserName + '] enter the Wechat conversation'
        lat = raw_body['xml']['Latitude']
        lon = raw_body['xml']['Longitude']
        if fromUserName not in userLocation['WeChat']:
            userLocation['WeChat'][fromUserName] = {'lat': lat, 'lon': lon}
        else:
            userLocation['WeChat'][fromUserName] = {'lat': lat, 'lon': lon}
        return wechat.response_none()
    elif wechat.message.type == 'click':
        eventKey = wechat.message.key
        if eventKey == 'home_box':
            userLang = wechat.get_user_info(user_id=fromUserName, lang='en')['language']
            # userLang = 'zh'
            richResponse = messageCreator.generateWeChatHome(lang=userLang, name=wechatAccountMapper[toUserName])
            return wechat.response_news(richResponse)
    elif wechat.message.type == 'text':
        conversationID = utilities.generateConversationID(toUserName, fromUserName)
        messageID = str(wechat.message.id)
        createdTime = str(datetime.fromtimestamp(wechat.message.time).isoformat()) + 'Z'
        try:
            content = wechat.message.content
        except:
            return wechat.response_text(content='Sorry, I cannot understand you. Please try again.\n对不起，我无法理解您的意思，请再试一次。')

        msgLang = identifier.classify(content)[0]
        if fromUserName not in topTopicsInfo['WeChat'][wechatAccountMapper[toUserName]]:
            topTopics = {}
            topTopicsInfo['WeChat'][wechatAccountMapper[toUserName]][fromUserName] = {'lang': msgLang, 'topics': topTopics}
        else:
            topTopics = topTopicsInfo['WeChat'][wechatAccountMapper[toUserName]][fromUserName]

        if 'zh' not in msgLang.lower():
            #print 'English Session'
            # start of agent conversation
            if 'overnight parking' in content.lower():
                location = userLocation['WeChat'][fromUserName]
                print 'User Location: ' + str(location)
                article = messageCreator.generateWeChatMapResponse('parking lot', location['lat'], location['lon'])
                return wechat.response_news(article)
            elif content.lower() == 'help' and accountStatus[0] and (
                        (conversationID not in conversationStatusList['WeChat']) or (
                                conversationStatusList['WeChat'][conversationID] == 'kms')):
                conversationStatusList['WeChat'][conversationID] = 'agent'
                response = 'Agent service requested, please wait...\n Type END to disconnect.'
                t = Thread(target=utilities.forwardConversation,
                           args=['WeChat', 'agent', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                 str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'])
                t.start()
                return wechat.response_text(response)
            # end of agent conversation
            elif content.lower() == 'end' and (conversationID in conversationStatusList['WeChat']) and \
                            conversationStatusList['WeChat'][conversationID] == 'agent':
                conversationStatusList['WeChat'][conversationID] = 'kms'
                response = 'Agent Disconnected, Goodbye'
                t = Thread(target=utilities.forwardConversation,
                           args=['WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                 str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'])
                t.start()
                return wechat.response_text(response)
            # agent conversation
            elif (conversationID in conversationStatusList['WeChat']) and conversationStatusList['WeChat'][
                conversationID] == 'agent':
                t = Thread(target=utilities.forwardUserMessage,
                           args=('WeChat', 'agent', conversationID, messageID, fromUserName, toUserName, content, createdTime))
                t.start()
                return wechat.response_none()
            else:  # AK bot
                try:
                    topTopics, response, outputList, status, sessionID = utilities.AKRequest(content, topTopics, languageCode_en, wechatAccountMapper[toUserName])
                    topTopicsInfo['WeChat'][wechatAccountMapper[toUserName]][fromUserName] = topTopics
                    if status == '1':
                        utilities.forwardUserMessage('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime)
                        t = Thread(target=sendWechatResponse,
                                   args=(wechat, response, conversationID, messageID, fromUserName, toUserName)
                                   )
                        t.start()
                        return wechat.response_none()
                    elif status == '2':
                        response += '\n Or you can type HELP for a real agent.'
                        utilities.forwardUserMessage('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime)
                        t = Thread(target=sendWechatResponse,
                                   args=(wechat, response, conversationID, messageID, fromUserName, toUserName)
                                   )
                        t.start()
                        return wechat.response_none()
                    else:
                        if accountStatus[1]:
                            response += ' An agent will be with you shortly.'
                            conversationStatusList['WeChat'][conversationID] = 'agent'
                            t = Thread(target=utilities.forwardConversation,
                                       args=('WeChat', 'agent', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                             str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'))
                            t.start()
                        else:
                            if accountStatus[0]:
                                response += ' Type HELP for a real agent.'
                            t = Thread(target=utilities.forwardConversation,
                                       args=('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                             str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'))
                            t.start()
                except Exception as e:
                    print e
                    print traceback.print_exc()
                    response = 'Cannot connect to Astute Knowledge Server. Type HELP for a real agent.'
                    t = Thread(target=utilities.forwardConversation,
                               args=('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                     str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'))
                    t.start()
                    return wechat.response_text(
                        content=response)
                return wechat.response_text(response)
        else:
            print 'Chinese Session'
            # start of agent conversation
            if content == u'求助' and accountStatus[0] and (
                        (conversationID not in conversationStatusList['WeChat']) or (conversationStatusList['WeChat'][conversationID] == 'kms')):
                conversationStatusList['WeChat'][conversationID] = 'agent'
                response = '客服连接中，请稍后...\n输入【结束】将结束本次服务。'
                t = Thread(target=utilities.forwardConversation,
                           args=['WeChat', 'agent', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                 str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'])
                t.start()
                return wechat.response_text(response)
            # end of agent conversation
            elif content == u'结束' and (conversationID in conversationStatusList['WeChat']) and \
                            conversationStatusList['WeChat'][
                                conversationID] == 'agent':
                conversationStatusList['WeChat'][conversationID] = 'kms'
                response = '本次服务结束，谢谢。'
                t = Thread(target=utilities.forwardConversation,
                           args=('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                 str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'))
                t.start()
                return wechat.response_text(response)
            # agent conversation
            elif (conversationID in conversationStatusList['WeChat']) and conversationStatusList['WeChat'][conversationID] == 'agent':
                t = Thread(target=utilities.forwardUserMessage,
                           args=('WeChat', 'agent', conversationID, messageID, fromUserName, toUserName, content,
                                 createdTime))
                t.start()
                return wechat.response_none()
            else:
                try:
                    topTopics, response, outputList, status, sessionID = utilities.AKRequest(content, topTopics, languageCode_zh, wechatAccountMapper[toUserName])
                    topTopicsInfo['WeChat'][wechatAccountMapper[toUserName]][fromUserName] = topTopics
                    if status != '1':
                        if accountStatus[1]:
                            response += ' 我们会为您安排客服解答。'
                            conversationStatusList['WeChat'][conversationID] = 'agent'
                            t = Thread(target=utilities.forwardConversation,
                                       args=('WeChat', 'agent', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                             str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'))
                            t.start()
                        else:
                            if accountStatus[0]:
                                response += ' 输入【求助】将为您安排客服。'
                            t = Thread(target=utilities.forwardConversation,
                                       args=('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                             str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'))
                            t.start()
                    else:
                        utilities.forwardUserMessage('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime)
                        t = Thread(target=sendWechatResponse,
                                   args=(wechat, response, conversationID, messageID, fromUserName, toUserName)
                                   )
                        t.start()
                        return wechat.response_none()
                except Exception as e:
                    print e
                    response = '无法连接数据服务器。 输入【求助】将为您安排客服。'
                    t = Thread(target=utilities.forwardConversation,
                               args=('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime, response,
                                     str(datetime.fromtimestamp(wechat.message.time + 1).isoformat()) + 'Z'))
                    t.start()
                    return wechat.response_text(content=response)
                return wechat.response_text(response)
    else:
        return wechat.response_none()
    return wechat.response_none()


if __name__ == "__main__":
    app.run(port=80)
