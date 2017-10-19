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


def sendMessengerAKStructure(token, recipient, content, inputList, mode, sessionID, lang='en'):
    messengerSendURL = messengerThreadUrl + token
    if content.startswith('   {'):
        structure = json.loads(content[3:])
        if structure['view'] == 'list':
            elements = []
            temp = sorted(inputList[mode].items())
            for key, value in temp:
                items = key.split('@')
                if len(items[2]) > 2:
                    subtitle = items[2] + ' @ '+items[3]
                else:
                    subtitle = '@ '+items[3]
                elements.append({"title": items[1],
                                 "subtitle": subtitle,
                                 "buttons": [
                                     {
                                         "title": "View",
                                         "type": "postback",
                                         "payload": key + '**' + value + '**' + sessionID
                                     }
                                 ]
                                 })
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
                            "elements": elements,
                            "buttons": [
                                {
                                    "title": "Full Schedule",
                                    "type": "web_url",
                                    "url": "https://www.astutesolutions.com/distributable-assets/Astute_Connect_Agenda-2017.pdf?version=4"
                                }
                            ]
                        }
                    }
                }
            }
        elif structure['view'] == 'buttons':
            buttons = []
            temp = sorted(inputList[mode].items())
            for key, value in temp:
                buttons.append({"type": "postback",
                                "title": key.split('.')[1],
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
                            "text": structure["title"],
                            "buttons": buttons
                        }
                    }
                }
            }
    else:
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


def sendMessengerMap(token, recipient, lat, lon, query):
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
                            "title": "Your Nearest CVS",
                            # "image_url": staticMapUrl,
                            "image_url": "https://lh6.ggpht.com/CjEZ8jZFKllIBzyg6Y884kwpsJ5qh92PxWOZBoZp5aI7okXgpC-7o91DrNSBNTBofIMo=w300",
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


def sendMessengerMapTower(token, recipient, query):
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
                            "title": "Tower of the Americas",
                            "image_url": "https://cdn.wedding-spot.com/images/venues/1440/Chart-House-Towers-of-America-San-Antonio-TX-1_main.1418287881.jpg",
                            "item_url": "http://maps.apple.com/maps?q="+query

                        }
                    ]
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)


def sendMessengerPicStructure(token, recipient, content):
    temp = content.split('@@')
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
                            "title": temp[1] + ' - click to enlarge',
                            "image_url": temp[2],
                            "item_url": temp[2]
                        }
                    ]
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)



def sendMessengerMapStructure(token, recipient, content):
    '''
    imageMapper = {"1.Alex - Café Ole": "http://www.riverwalkguide.com/wp-content/uploads/2011/11/cafe-ole-on-the-River-Walk.png",
                    "2.Joe - Michelino's": "http://riverwalkguide.zippykid.netdna-cdn.com/wp-content/uploads/2015/02/Michelinos.png",
                    "3.Ray - Lone Star Café": "http://riverwalkguide.zippykid.netdna-cdn.com/wp-content/uploads/2013/02/lonestarcafelogo-300x144.png",
                   "4.Shellie - Rio Rio Cantina": "http://riorioriverwalk.com/wp-content/uploads/2014/08/logo.png"
                   }
    addressMapper = {"1.Alex - Café Ole": "521 River Walk St, San Antonio, TX 78205",
                    "2.Joe - Michelino's": "521 River Walk St, San Antonio, TX 78205",
                    "3.Ray - Lone Star Café": "237 Losoya St, San Antonio, TX 78205",
                   "4.Shellie - Rio Rio Cantina": "421 E Commerce St, San Antonio, TX 78205"
                   }
    '''
    temp = content.split('@@')
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
                            "title": temp[1],
                            "image_url": temp[2],
                            "item_url": "http://maps.apple.com/maps?address="+temp[3]

                        }
                    ]
                }
            }
        }
    }

    response = requests.post(messengerSendURL, json=data, verify=False)

    return response, json.loads(response.text)


def sendConfHotelMap(token, recipient):
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
                            "title": "Hyatt Regency San Antonio Riverwalk",
                            "image_url": "http://tdr.aaa.com/tdr-images/images/property_photo/accommodation/31125H1.jpg",
                            "item_url": "http://maps.apple.com/maps?address=123%20Losoya%20San%20Antonio,%20TX%2078205"

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


def sendConfLocationInfo(token, recipient):
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
                            "title": "Hyatt Regency San Antonio Riverwalk",
                            "image_url": "http://tdr.aaa.com/tdr-images/images/property_photo/accommodation/31125H1.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Hotel Info",
                                    "url": "https://aws.passkey.com/reg/32FTQ6CB-G490"
                                },
                                {
                                    "type": "postback",
                                    "title": "Direction",
                                    "payload": "Map info for conference hotel"
                                }
                            ]
                        },
                        {
                            "title": "Tower of the Americas",
                            "image_url": "https://cdn.wedding-spot.com/images/venues/1440/Chart-House-Towers-of-America-San-Antonio-TX-1_main.1418287881.jpg",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "Location Info",
                                    "url": "http://www.toweroftheamericas.com/"
                                },
                                {
                                    "type": "postback",
                                    "title": "Direction",
                                    "payload": "Map info for tower of americas"
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


def sendAC2017Schedule(token, recipient):
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
                            "title": "Sunday, April 2",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Welcome Reception",
                                    "payload": "welcome reception on sunday"
                                }
                            ]
                        },
                        {
                            "title": "Monday, April 3",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Morning Sessions",
                                    "payload": "morning sessions on monday"

                                },
                                {
                                    "type": "postback",
                                    "title": "Afternoon Sessions",
                                    "payload": "afternoon sessions on monday"

                                },
                                {
                                    "type": "postback",
                                    "title": "Dining",
                                    "payload": "dining on monday"
                                }
                            ]
                        },
                        {
                            "title": "Tuesday, April 4",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Morning Sessions",
                                    "payload": "morning sessions on tuesday"

                                },
                                {
                                    "type": "postback",
                                    "title": "Afternoon Sessions",
                                    "payload": "afternoon sessions on tuesday"

                                },
                                {
                                    "type": "postback",
                                    "title": "Dining",
                                    "payload": "dining on tuesday"
                                }
                            ]
                        },
                        {
                            "title": "Wednesday, April 5",
                            "buttons": [
                                {
                                    "type": "postback",
                                    "title": "Breakfast",
                                    "payload": "breakfast on wednesday"
                                },
                                {
                                    "type": "postback",
                                    "title": "Product Roadmaps",
                                    "payload": "roadmaps on wednesday"
                                },
                                {
                                    "type": "postback",
                                    "title": "Closing Comments",
                                    "payload": "closing on wednesday"
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


def sendMessengerColgate1(token, recipient):
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
                            "title": "Optic White® High Impact White",
                            "image_url": "https://ll-us-i5.wal.co/asr/ba1544ca-77a4-47bb-860b-3f50308cee68_1.1ce6c0c826fe59fcf4494bad270748e0.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "More",
                                    "url": "http://www.colgateopticwhite.com/whitening-toothpaste/fluoride-toothpaste-whitening"
                                },
                                {
                                    "type": "postback",
                                    "title": "Find in store",
                                    "payload": "Colgate_Optic_White"
                                }
                            ]
                        },
                        {
                            "title": "Optic White® Express White",
                            "image_url": "https://i5.walmartimages.com/asr/11536ea3-3552-4c40-9dc9-49caacc06e87_1.67e6c1c7ed64c77d4441c6e69d62be34.jpeg?odnHeight=450&odnWidth=450&odnBg=FFFFFF",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "More",
                                    "url": "http://www.colgateopticwhite.com/whitening-toothpaste/express-white"
                                },
                                {
                                    "type": "postback",
                                    "title": "Find in store",
                                    "payload": "Colgate_Optic_White"
                                }
                            ]
                        },
                        {
                            "title": "Optic White® Lasting White",
                            "image_url": "http://www.colgateopticwhite.com/ColgateOralCare/Whitening/ColgateOpticWhite_v2/US/EN/locale-assets/images/products/opticLastingWhite.png",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "More",
                                    "url": "http://www.colgateopticwhite.com/whitening-toothpaste/lasting-white"
                                },
                                {
                                    "type": "postback",
                                    "title": "Find in store",
                                    "payload": "Colgate_Optic_White"
                                }
                            ]
                        },
                        {
                            "title": "Optic White® Toothpaste",
                            "image_url": "https://images.freshop.com/00035000763747/5a1cf8ecfea2555a7b33cceedd5852a6_medium.png",
                            "buttons": [
                                {
                                    "type": "web_url",
                                    "title": "More",
                                    "url": "http://www.colgateopticwhite.com/whitening-toothpaste/optic-white"
                                },
                                {
                                    "type": "postback",
                                    "title": "Find in store",
                                    "payload": "Colgate_Optic_White"
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


def sendMessengerColgateConsultation(options, body, token, recipient):
    messengerSendURL = messengerThreadUrl + token
    buttons = []
    for value in options:
        buttons.append({"type": "postback",
                        "title": value,
                        "payload": value
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
                    "text": body,
                    "buttons": buttons
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