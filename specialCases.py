import messageCreator


def caseHandler(content, facebookToken, sender, specialCase, locationObj):
    sendStatus = ''
    responseContent = ''
    handeled = True
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
    elif content.lower() == 'yes please':
        statusCode = 500
        index = 0
        while statusCode != 200 and index < 3:
            sendStatus, responseContent = messageCreator.sendMessengerStructure3(facebookToken, sender)
            statusCode = sendStatus.status_code
            index += 1
    elif 'show me the nearest location' in content.lower():
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
    elif 'in fbm' in content.lower():
        statusCode = 500
        index = 0
        while statusCode != 200 and index < 3:
            sendStatus, responseContent = messageCreator.sendOmegaAir1(facebookToken, sender)
            statusCode = sendStatus.status_code
            index += 1
    elif specialCase == 'Location':
        statusCode = 500
        index = 0
        while statusCode != 200 and index < 3:
            sendStatus, responseContent = messageCreator.sendMessengerLocation(facebookToken, sender, locationObj['lat'], locationObj['lon'],
                                                                               "McDonald's")
            statusCode = sendStatus.status_code
            index += 1
    else:
        handeled = False

    return sendStatus, responseContent, handeled