# -*- coding: utf-8 -*-
import requests
import json

messengerThreadUrl = "https://graph.facebook.com/v2.6/me/messages?access_token="
googleMapSearchKey = 'AIzaSyCGpVm1F2ueoIxmbzMT0s_ESpFNBxLq9eM'
googleMapStaticKey = 'AIzaSyDR--n9MX3Cd634s4ito5yNBylbEKYLWtc'


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


def constructAlexaText(status, content, inputList, lang='en'):
    out = content.replace('\n', '. ')
    if status == '2':
        out += ' '
        if len(inputList['SuggestedTopics']) > 0:
            for index, title in enumerate(inputList['SuggestedTopics'].keys()):
                out += str(index+1) + ': '+title+'. '

    return out


def sendMessengerAKButton(token, recipient, content, inputList, mode, sessionID, lang='en'):
    messengerSendURL = messengerThreadUrl + token
    buttons = []
    for key, value in inputList[mode].items():
        buttons.append({"type": "postback",
                        "title": key,
                        "payload": key + '**' + value + '**' + sessionID
                        })
    data = {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": content,
                    "buttons": buttons
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)


def askMessengerLocation(token, recipient):
    messengerSendURL = messengerThreadUrl + token
    data = {
        "recipient": {
            "id": recipient
        },
        "message": {
            "text": "Please share your location:",
            "quick_replies": [
                {
                    "content_type": "location",
                }
            ]
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)


def sendMessengerLocation(token, recipient, lat, lon, query):
    messengerSendURL = messengerThreadUrl + token
    # staticMapUrl = 'https://maps.googleapis.com/maps/api/staticmap?zoom=13&size=500x400&center'+str(lat)+','+str(lon)+'&key='+googleMapStaticKey
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
                            "title": "Your Nearest McDonald's",
                            # "image_url": staticMapUrl,
                            "image_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/3/36/McDonald%27s_Golden_Arches.svg/274px-McDonald%27s_Golden_Arches.svg.png",
                            "item_url": "http://maps.apple.com/maps?q=" + query + '&sll=' + str(lat) + ',' + str(lon)
                            # "http://maps.apple.com/maps?q=McDonald's&near=40.133896213994,%20-83.019637707698"
                            # "http://maps.apple.com/maps?q="+query+'&near='+str(lat)+','+str(lon)
                        }
                    ]
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)


def sendMessengerStructure1(token, recipient):
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
                            "title": "Eleven Madison Park",
                            "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/LdksHnnLXrazkmBK2ohRKA/o.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "More",
                                    "url": "http://www.elevenmadisonpark.com/"
                                },
                                {
                                    "type": "web_url",
                                    "title": "Make Reservations",
                                    "url": "https://elevenmadisonpark.tocktix.com/"
                                }
                            ]
                        },
                        {
                            "title": "Gramercy Tavern",
                            "image_url": "https://s3-media3.fl.yelpcdn.com/bphoto/yr_BNXJ57Q66IgSppMy1Qw/o.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "More",
                                    "url": "http://www.gramercytavern.com/"
                                },
                                {
                                    "type": "web_url",
                                    "title": "Make Reservations",
                                    "url": "http://www.opentable.com/gramercy-tavern-reservations-new-york?restref=942"
                                }
                            ]
                        },
                        {
                            "title": "Le Bernardin",
                            "image_url": "https://s3-media2.fl.yelpcdn.com/bphoto/O2auTfVN7mp7qSMoKQ81hQ/o.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "More",
                                    "url": "https://www.le-bernardin.com/"
                                },
                                {
                                    "type": "web_url",
                                    "title": "Make Reservations",
                                    "url": "https://www.le-bernardin.com/reservations"
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


def sendMessengerStructure2(token, recipient):
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
                            "title": "Italian Food",
                            "image_url": "http://www.publicdomainpictures.net/pictures/40000/velka/italian-pizza.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": " Find More",
                                    "url": "https://www.yelp.com/search?find_desc=italian+food&find_loc=new+york%2C+NY&ns=1"
                                }
                            ]
                        },
                        {
                            "title": "Steakhouse",
                            "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/Q64sD2LigWvvrIDjPqruuw/o.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Find More",
                                    "url": "https://www.yelp.com/search?find_desc=steakhouse&find_loc=new+york,+NY"
                                }
                            ]
                        },
                        {
                            "title": "Seafood",
                            "image_url": "http://www.publicdomainpictures.net/pictures/50000/velka/fresh-seafood-on-ice.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Find More",
                                    "url": "https://www.yelp.com/search?find_desc=seafood&find_loc=new+york,+NY"
                                }
                            ]
                        },
                        {
                            "title": "Japanese",
                            "image_url": "https://s3-media4.fl.yelpcdn.com/bphoto/kf9aL4keeINdWxDdvjl1rg/o.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Find More",
                                    "url": "https://www.yelp.com/search?find_desc=japanese&find_loc=new+york,+NY"
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


def sendMessengerStructure3(token, recipient):
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
                            "title": "Grand Hyatt Singapore",
                            "image_url": "http://r-ec.bstatic.com/images/hotel/840x460/524/52471275.jpg",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Book",
                                    "payload": "Book a hotel room in Singapore"
                                },
                                {
                                    "type": "postback",
                                    "title": "Hold",
                                    "payload": "Put on hold"
                                }
                            ]
                        },
                        {
                            "title": "Hilton Singapore",
                            "image_url": "http://www3.hilton.com/resources/media/hi/SINHITW/en_US/img/shared/full_page_image_gallery/main/HL_skybarview_675x359_FitToBoxSmallDimension_Center.jpg",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Book",
                                    "payload": "Book a hotel room in Singapore"
                                },
                                {
                                    "type": "postback",
                                    "title": "Hold",
                                    "payload": "Put on hold"
                                }
                            ]
                        },
                        {
                            "title": "Mandarin Orchard Singapore",
                            "image_url": "http://q-ec.bstatic.com/images/hotel/840x460/340/34007512.jpg",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Book",
                                    "payload": "Book a hotel room in Singapore"
                                },
                                {
                                    "type": "postback",
                                    "title": "Hold",
                                    "payload": "Put on hold"
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


def sendOmegaAir1(token, recipient):
    messengerSendURL = messengerThreadUrl + token
    data = {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "image",
                "payload": {
                    "url": "http://web.cse.ohio-state.edu/~cuir/src/boardingcard.png"
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)

def sendMessengerMcD1(token, recipient):
    messengerSendURL = messengerThreadUrl + token
    data = {
        "recipient": {
            "id": recipient
        },
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "list",
                    "top_element_style": "compact",
                    "elements": [
                        {
                            "title": "Big Mac",
                            "image_url": "https://www.mcdonalds.com/content/dam/usa/nutrition/items/thumbnail/t-mcdonalds-Big-Mac.png",
                            "subtitle": "540 Calories",
                        },
                        {
                            "title": "Quarter Pounder with Cheese",
                            "image_url": "https://www.mcdonalds.com/content/dam/usa/nutrition/items/thumbnail/t-mcdonalds-Quarter-Pounder-with-Cheese.png",
                            "subtitle": "540 Calories",
                        },
                        {
                            "title": "Double Quarter Pounder with Cheese",
                            "image_url": "https://www.mcdonalds.com/content/dam/usa/nutrition/items/thumbnail/t-mcdonalds-Double-Quarter-Pounder-with-Cheese.png",
                            "subtitle": "780 Calories",
                        },
                        {
                            "title": "Hamburger",
                            "image_url": "https://www.mcdonalds.com/content/dam/usa/nutrition/items/thumbnail/t-mcdonalds-Hamburger.png",
                            "subtitle": "250 Calories",
                        }
                    ],
                    "buttons": [
                        {
                            "title": "Find out More",
                            "type": "web_url",
                            "url": "https://www.mcdonalds.com/us/en-us/about-our-food/nutrition-calculator.html"
                        }
                    ]
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)



def sendMessengerMcD2(token, recipient):
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
                            "title": "$1 OFF LARGE FRIES",
                            "image_url": "https://www.mcdonalds.com/dam/usa/promotions/desktop/GMA_FryFriday_Deals_d_640x640.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Details",
                                    "url": "https://www.mcdonalds.com/us/en-us/deals.html"
                                }
                            ]
                        },
                        {
                            "title": "$1 OFF McCAFE BEVERAGES",
                            "image_url": "https://www.mcdonalds.com/content/dam/usa/promotions/mobile/MCCafe_1_Deals_m_750x500.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Details",
                                    "url": "https://www.mcdonalds.com/us/en-us/deals.html"
                                }
                            ]
                        },
                        {
                            "title": "FREE HASH BROWNS",
                            "image_url": "https://www.mcdonalds.com/content/dam/usa/promotions/mobile/McD_DealsLandPg_HashFries_750x500.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Details",
                                    "url": "https://www.mcdonalds.com/us/en-us/deals.html"
                                }
                            ]
                        },
                    ]
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)

def generateWeChatMapResponse(query, lat, lon, lang='en'):
    if 'en' in lang.lower():
        data = [{
            'title': 'Parking',
            'description': 'Parking lot around you',
            'picurl': 'https://cdn.pixabay.com/photo/2012/04/28/18/02/parking-43797_960_720.png',
            'url': "http://maps.apple.com/maps?q=" + query + '&sll=' + str(lat) + ',' + str(lon)
        }]
    else:
        data = [{
            'title': u'停车',
            'description': u'第一条新闻描述，这条新闻没有预览图',
            'picurl': 'https://cdn.pixabay.com/photo/2012/04/28/18/02/parking-43797_960_720.png',
            'url': "http://maps.apple.com/maps?q=" + query + '&sll=' + str(lat) + ',' + str(lon)
        }]
    return data


def generateWeChatHome(lang='en', name='FordPass'):
    outputList = []
    if name == 'FordPass':
        temp = {'title': 'FordPass', 'description': 'Ford Pass',
                'picurl': 'http://web.cse.ohio-state.edu/~cuir/site/fordpasslogo.png',
                'url': 'https://www.fordpass.com/'}
        outputList.append(temp)

        temp = {'title': 'My Vehicles', 'description': 'my vehicles',
                # 'picurl': 'https://dl.dropboxusercontent.com/u/93550717/site/myvehicles.png',
                'picurl': 'http://web.cse.ohio-state.edu/~cuir/site/myvehicles.png',
                'url': 'http://web.cse.ohio-state.edu/~cuir/site/test.html'}
        if lang != 'en':
            temp['title'] = u'我的车辆'
            temp['url'] = 'http://web.cse.ohio-state.edu/~cuir/site copy/test.html'
        outputList.append(temp)

        temp = {'title': 'My Dealer', 'description': 'dealer',
                # 'picurl': 'https://dl.dropboxusercontent.com/u/93550717/site/mydealer.png',
                'picurl': 'http://web.cse.ohio-state.edu/~cuir/site/mydealer.png',
                'url': 'http://web.cse.ohio-state.edu/~cuir/site/test1.html'}
        if lang != 'en':
            temp['title'] = u'经销商'
            temp['url'] = 'http://web.cse.ohio-state.edu/~cuir/site copy/test1.html'
        outputList.append(temp)

        temp = {'title': 'Park', 'description': 'parking',
                # 'picurl': 'https://dl.dropboxusercontent.com/u/93550717/site/park.png',
                'picurl': 'http://web.cse.ohio-state.edu/~cuir/site/park.png',
                'url': 'http://www.bing.com/mapspreview'}
        if lang != 'en':
            temp['title'] = u'停车'
            # temp['url'] = 'https://www.gaode.com/'
        outputList.append(temp)

    return outputList

'''
if __name__ == '__main__':
    token = 'EAAB1kFElgToBAABPzz9mep4Cv8J7JZBfkqARmXTuyL9IrnFyyckHjEXdAS1TeF1aeN4AAJ5U3IjNPSuYq7UWjwf93YoQwnZBGhwuEpZC1orwf0v7nZCZAZCwnjeMTmAoqd5cfJk6TKOUnTpR1ocZAiGhBgbLKu5hDGyCIsLSqd5LgZDZD'
    sender = '1165153443564941'
    sendStatus, responseContent = sendMessengerMcD2(token, sender)
    print sendStatus
    print responseContent
'''