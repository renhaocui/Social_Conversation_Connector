# -*- coding: utf-8 -*-
import messageCreator
import utilities

def caseHandler_facebook(content, facebookToken, sender, receiver, specialCase, locationObj):
    sendStatus = ''
    responseContent = ''
    handeled = True

    if receiver == 'AC2017':
        if content.lower() in ['conference schedule information', 'schedule information', 'schedule info']:
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendAC2017Schedule(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif content.lower() in ['conference location information', 'location information', 'location info']:
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendConfLocationInfo(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif content.lower() == 'map info for conference hotel':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendConfHotelMap(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif content.lower() == 'map info for tower of americas':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerMapTower(facebookToken, sender, 'tower of the americas')
                statusCode = sendStatus.status_code
                index += 1
        else:
            handeled = False
    elif receiver == 'McDonalds':
        if 'show me the nearest location' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.askMessengerLocation(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif 'how many calories are in big mac' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerMcD1(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif 'what offers do you have' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerMcD2(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif specialCase == 'Location':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerLocation(facebookToken, sender,
                                                                                   locationObj['lat'],
                                                                                   locationObj['lon'],
                                                                                   "McDonald's")
                statusCode = sendStatus.status_code
                index += 1
        else:
            handeled = False
    elif receiver == 'OmegaAir':
        if content.split('**')[0].lower() == 'suggest something':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerStructure1(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif content.split('**')[0].lower() == 'let me choose':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerStructure2(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif 'in fbm' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendOmegaAir1(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif content.lower() == 'yes please':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerStructure3(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        else:
            handeled = False
    elif receiver == 'Colgate':
        if 'burning sensation' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender,
                                                                      'We take these types of issues very seriously, and we recommend directly discuss this with an agent. Please type HELP to reach an agent.')
                statusCode = sendStatus.status_code
                index += 1
        elif 'help me find it' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender,
                                                                      'Here is the list of Colgate Optic White Toothpastes.')
                statusCode = sendStatus.status_code
                index += 1
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerColgate1(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif 'help me find a product' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender, 'Sure, what are you looking for?')
                statusCode = sendStatus.status_code
                index += 1
        elif 'optic white' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender,
                                                                      'Which Colgate Optic White Toothpaste are you looking for?')
                statusCode = sendStatus.status_code
                index += 1
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerColgate1(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1

        elif content == 'Colgate_Optic_White':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.askMessengerLocation(facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif specialCase == 'Location_Colgate':
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerMap(facebookToken, sender, locationObj['lat'], locationObj['lon'],
                                                                                   "CVS")
                statusCode = sendStatus.status_code
                index += 1
        elif 'whitening consultation' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender,
                                                                      'Hi There, do you want to start our whitening consultation now?')
                statusCode = sendStatus.status_code
                index += 1
        elif 'sure' in content.lower():
            statusCode = 500
            index = 0
            options = ['Discoloration', 'Wedding or Big Event', 'Everyday Maintenance']
            body = "Great, what has you interested in teeth whitening?"
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = messageCreator.sendMessengerColgateConsultation(options, body, facebookToken, sender)
                statusCode = sendStatus.status_code
                index += 1
        elif 'wedding or big event' in content.lower():
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender,
                                                                      'Great, how soon is the event?')
                statusCode = sendStatus.status_code
                index += 1
        elif ('2 weeks' in content.lower()) or ('two weeks' in content.lower()):
            statusCode = 500
            index = 0
            while statusCode != 200 and index < 3:
                sendStatus, responseContent = utilities.sendMessenger(facebookToken, sender,
                                                                      'Wow, that is coming up soon.  I’d recommend a Zoom Whitening treatment for the fastest results.  Then follow up with Colgate Optic White line of products to maintain those pearly whites!')
                statusCode = sendStatus.status_code
                index += 1
        else:
            handeled = False

    return sendStatus, responseContent, handeled


def caseHandlerMP(content, lang='en'):
    response = ''
    rspFlag = 'NONE'
    if lang == 'en':
        if 'want to schedule service' in content.lower():
            response = 'OK, do you want to drop off your continental or have it picked up?'
            rspFlag = 'Valid'
        elif 'picked up' in content.lower():
            response = 'Would you like it picked up from your current location or a specific address?'
            rspFlag = 'Valid'
        elif 'current location' in content.lower():
            response = 'Great, can you share your location with me?'
            rspFlag = 'Valid'
        elif 'location shared' in content.lower():
            response = 'Thanks, what time and date would you like your Continental to be serviced.'
            rspFlag = 'Valid'
        elif 'next tuesday' in content.lower():
            response = 'OK, we will see you next Tuesday at 8AM.  If you need to cancel or make alterations feel free to do so by chatting or visiting the service tab.'
            rspFlag = 'Valid'
        elif 'find recall notices' in content.lower():
            response = 'Hi Marc, we will notify you in the alerts option on the home screen if there are any recalls related to your vehicle.'
            rspFlag = 'Valid'
        elif 'do i start my car' in content.lower():
            response = 'Are you trying to start your car with your key fob remote or the app?'
            rspFlag = 'Valid'
        elif 'app' in content.lower():
            response = 'To start your car via the app, go to the Remote Tab and hold down the Start Button.'
            rspFlag = 'Valid'
        elif 'the lease end process' in content.lower():
            response = 'Hi Marc, it looks like you will need to talk to an agent. Type HELP to start the conversation.'
            rspFlag = 'Valid'

    elif lang == 'zh':
        if u'如何发动汽车' in content.lower():
            response = '您想通过智能钥匙还是应用来发动汽车？'
            rspFlag = 'Valid'
        elif u'应用' in content.lower():
            response = '通过应用发动汽车，您需要切换至远程控制页面，长按启动按钮。'
            rspFlag = 'Valid'
        elif u'获得召回消息' in content.lower():
            response = '您可以通过主页上的通知选项来获取任何与您的车辆有关的召回的信息。'
            rspFlag = 'Valid'

    return response, rspFlag