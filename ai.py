import nltk
import requests
import json

#reply when get "/start"
def start_reply():
    bot_welcome = "welcome to Abot.\nYou can try /change"
    return bot_welcome

#use adorable.io Api to send avatar when choice is cool
def avatar(text):
    try:
           url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
           return url
    except Exception:
           # if things went wrong
           return 0

#send ip location of user or bot when choice is ip
def ip_location(text):
    access_key="a19c077c349b3cf8f4a10903a10b2f5e"
    if text.lower() == "bot":
        url = "http://api.ipstack.com/check"
        str="bot location\n"
    else:
        url = "http://api.ipstack.com/"+text
        str="given ip location\n"

    url=url+"?access_key="+access_key+"& fields=type,continent_name,country_name,region_name,city,zip,latitude,longitude"
    try:
            uResponse = requests.get(url)
    except requests.ConnectionError:
        print("Connection Error")  
    Jresponse = uResponse.text
    data = json.loads(Jresponse)

    if not data['type']:
        return 0,"Enter a valid ip address.",0,0
    else:
        str=str+'type - '+data['type']+'\ncontinent - '+data['continent_name']+'\ncountry - '+data['country_name']+'\nregion - '+data['region_name']+'\ncity - '+data['city']+'\nzip - '+data['zip']
        latitude = data['latitude']
        longitude = data['longitude']
        return 1, str, latitude, longitude

def chatbot(no,text):
    if no==1:
        a = nltk.chat.eliza.eliza_chatbot
    elif no==2:
        a = nltk.chat.iesha.iesha_chatbot
    elif no==3:
        a = nltk.chat.rude.rude_chatbot
    elif no==4:
        a = nltk.chat.suntsu.suntsu_chatbot
    elif no==5:
        a = nltk.chat.zen.zen_chatbot

    return a.respond(text)

    
