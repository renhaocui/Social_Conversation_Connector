# -*- coding: utf-8 -*-
import utilities
from flask import Flask, jsonify, make_response, request
from wechat_sdk import WechatConf
from wechat_sdk import WechatBasic
from wechat_sdk.exceptions import ParseError
from threading import Thread
from langid.langid import LanguageIdentifier, model
from datetime import datetime
import wechatManager
import xmltodict
import hashlib

app = Flask(__name__)

tempConf = WechatConf(
    token='astute_wechat_test',
    appid='wxc6587a03db4b22c6',
    appsecret='fabd27f90c9a57b375723cb0f796563a',
    encrypt_mode='normal',  # normal/compatible/safe
    # encoding_aes_key='your_encoding_aes_key'  # needs token, appid as well
)
tempWechat = WechatBasic(conf=tempConf)
confList = {'gh_ae02c9f6f14e': tempConf}

global conversationStatusList
conversationStatusList = {'WeChat': {}, 'Facebook': {}}
global topTopics
topTopics = {'WeChat': {'lang': 'en', 'topics': {}}, 'Facebook': {'lang': 'en', 'topics': {}}}
global wechatList
wechatList = {'gh_ae02c9f6f14e': tempWechat}
global accountStatusList
accountStatusList = {'WeChat': {'gh_ae02c9f6f14e': (True, False)},
                     'Facebook': {'129262697152826': (True, False)}}  # (on_help, on_kms_failure)

languageCode_en = 'en-US'
languageCode_zh = 'zh-CN'
identifier = LanguageIdentifier.from_modelstring(model, norm_probs=True)

token = 'EAAB1kFElgToBAHRJmoshPkpQzpEF2FviWyY9GdA5lUZBPwqRVb3tQdz9vlOkkLZBpp0nihxN5yyBJxDEZC3nTROBaosUYhiMWwwPcqUJiFEZA6lqQwcFHwfpWYZB8d7v5OsaZB2YDgLqRmpdNxvHy7s4pPiuPe8xK1MhFdgoRimgZDZD'
messengerTokenList = {'276165652474701': token}

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
    print 'WeChat server verification: Accept'
    return make_response(echostr)


@app.route('/validate_account', methods=['POST'])
def wechatVerifyAccount():
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
    platform = body['platform']
    conversationID = body['conversation_id']
    contentType = body['content_type']
    content = body['content']
    appID = body['app_id']
    secret = body['secret']
    userID = body['user_id']

    temp = conversationID.split(',')
    if temp[0] == userID:
        accountID = temp[1]
    else:
        accountID = temp[0]

    if conversationID not in conversationStatusList[platform]:
        return '', 503
    elif conversationStatusList[platform][conversationID] == 'agent':
        if contentType.lower() == 'text':
            if platform == 'WeChat':
                tempConf = WechatConf(appid=appID, appsecret=secret, encrypt_mode='normal')
                tempWechat = WechatBasic(conf=tempConf)
                tempWechat.send_text_message(user_id=userID, content=content)
                print '[' + platform + ']Message sent to user: ' + userID
                t = Thread(target=utilities.forwardUserMessage,
                           args=(platform, 'agent', conversationID, '', accountID, userID, content, str(datetime.now().isoformat()[:-7]) + 'Z'))
                t.start()
                return '', 200
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
    print '[' + platform + ']Set Account Status for: ' + str(accountID)

    helpFlag = body['escalate_on_help']
    kmsFailureFlag = body['escalate_on_kms_failure']
    accountStatusList[platform][accountID] = (helpFlag, kmsFailureFlag)
    return '', 200


def sendWechatResponse(weChat, response, conversationID, messageID, fromUserName, toUserName):
    responseList = utilities.splitMessage(response, 2000)
    for response in responseList:
        weChat.send_text_message(user_id=fromUserName, content=response)
        utilities.forwardAKMessage('WeChat', 'kms', conversationID, messageID, toUserName, fromUserName, response,
                                   str(datetime.fromtimestamp(weChat.message.time + 1).isoformat()) + 'Z')
    return True


@app.route('/', methods=['POST'])
def wechatProcessRequest():
    global topTopics
    global conversationStatusList
    global wechatList
    global accountStatusList
    try:
        xml_body = request.data
        raw_body = xmltodict.parse(xml_body)
        accountID = raw_body['xml']['ToUserName']
        wechat = wechatList[accountID]
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
        return wechat.response_none()
    elif wechat.message.type == 'click':
        eventKey = wechat.message.key
        if eventKey == 'home_box':
            userLang = wechat.get_user_info(user_id=fromUserName, lang='en')['language']
            # userLang = 'zh'
            richResponse = utilities.generateWeChatHome(lang=userLang)
            return wechat.response_news(richResponse)
    elif wechat.message.type == 'text':
        conversationID = utilities.generateConversationID(toUserName, fromUserName)
        messageID = str(wechat.message.id)
        createdTime = str(datetime.fromtimestamp(wechat.message.time).isoformat()) + 'Z'
        try:
            content = wechat.message.content
        except:
            return wechat.response_text(content='Sorry, I cannot understand you. Please try again.\n对不起，我无法理解您的意思，请再试一次。')

        if content.isdigit() and len(topTopics['WeChat']['topics']) > 0:
            msgLang = topTopics['WeChat']['lang']
        else:
            msgLang = identifier.classify(content)[0]
        if 'zh' not in msgLang.lower():
            print 'English Session'
            # start of agent conversation
            if content.lower() == 'help' and accountStatus[0] and (
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
                    topTopics['WeChat'], response, outputList, status = utilities.AKRequest(content, topTopics['WeChat'], languageCode_en)
                    if status != '1':
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
                    else:
                        utilities.forwardUserMessage('WeChat', 'kms', conversationID, messageID, fromUserName, toUserName, content, createdTime)
                        t = Thread(target=sendWechatResponse,
                                   args=(wechat, response, conversationID, messageID, fromUserName, toUserName)
                                   )
                        t.start()
                        return wechat.response_none()
                except Exception as e:
                    print e
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
                    topTopics['WeChat'], response, outputList, status = utilities.AKRequest(content, topTopics['WeChat'], languageCode_zh)
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
                except:
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
