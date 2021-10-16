from telebot.credentials import bot_token, bot_user_name, URL
import re
import os
import psycopg2
from time import sleep
from flask import Flask, request, render_template
import telegram
import telebot.ai as ai
from telebot.credentials import bot_token, bot_user_name, URL
from telegram.ext import Updater, CommandHandler


global bot
global TOKEN
TOKEN = bot_token
bot = telegram.Bot(token=TOKEN)

app = Flask(__name__)

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():

   # retrieve the message in JSON and then transform it to Telegram object
   update = telegram.Update.de_json(request.get_json(force=True), bot)

   chat_id = update.message.chat.id
   msg_id = update.message.message_id
   
   #connect to postgresql and create cursor object to execute sql
   database_url = <postgres database Url>
   DATABASE_URL = os.environ['DATABASE_URL']
   conn = psycopg2.connect(DATABASE_URL, sslmode='require')
   cur = conn.cursor()
   
   #insert new chat details in DB
   def insert(cur, chat_id_inr,name):
    cur.execute("INSERT INTO users(chat_id,change,name) VALUES (%(chat)s,%(ch)s,%(name)s)", {
        'chat': chat_id_inr, 'ch': 1, 'name': name})

   def insert_ask(cur, chat_id_inr,str):
    cur.execute("INSERT INTO users_ask(chat_id,asked) VALUES (%(chat)s,%(ask)s)", {
        'chat': chat_id_inr,'ask':str })
   
   #update user choice in DB
   def update_change(cur, chat_id, ch):
    cur.execute("UPDATE users SET change=(%(new)s) WHERE chat_id = (%(chat)s)", {
        'new': ch, 'chat': chat_id})

   #available commands and their help for bot
   command_dict = {
       "/cool": 1,
       "/check": 2,
       "/ip": 3,
       "/Eliza": 41,
       "/Iesha":42,
       "/Rude":43,
       "/Suntsu":44,
       "/Zen":45
   }
   command_help={
       1: "Based on your text You will get a random Avatar.",
       2: "You will get your chat id and massage id.",
       3: """Text your I.P. Address and get your location.
       Or, send "bot" to get this bot location.
       go to https://www.google.com/search?q=what+is+my+ip+address for your device I.P.""",
       41: """Eliza - psycho-Therapist,
Iesha - teen anime junky,
Rude - abusive ,
Suntsu - Quotes from Sun Tsu’s The Art      of War ,
Zen - Zen wisdom
       The chatbot structure is based on that of Eliza.
       ELIZA is a computer program that emulates a Rogerian psychotherapist.
       ELIZA is an early natural language processing computer program created from 1964 to 1966 at the MIT Artificial Intelligence Laboratory by Joseph Weizenbaum.
       Thus, it uses a translation table to convert from question to response i.e. “I am” –> “you are”
       Of course, since Chatbot does not understand the meaning of any words, responses are very limited. Chatbot will usually answer very vaguely, or respond to a question by asking a different question.
       """
   }
   command_help[42] = command_help[43] = command_help[44] = command_help[45] = command_help[41]
   
   line = 1
   # Telegram understands UTF-8, so encode text for unicode compatibility
   text = update.message.text.encode('utf-8').decode()

   #every new connection start by sending "/start" ; insert new chat in DB if not exits
   if text.lower() == "/start":
        # print the welcoming message
        cur.execute("SELECT * FROM users where chat_id = (%(chat_id_sql)s)", {
            'chat_id_sql': chat_id})
        if cur.rowcount == 0:
            #insert the row with chat_id name and /start
            first = update.message.chat.first_name
            name = first + ' ' + update.message.chat.last_name
            insert(cur, chat_id, name)

        bot_welcome = ai.start_reply()
        # send the welcoming message
        bot.sendMessage(chat_id=chat_id, text=bot_welcome,reply_to_message_id=msg_id)

   #to show available commands
   elif text.lower()=="/change":
       msg = "choose one of this \nFor help type '/help </your command>"
       for i in command_dict[values]:
          msg = msg +"\n" + i
       bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
   
   #change command in DB or show their help
   elif "/" == text[0].lower() or text in command_dict:
       if "/help" in text.lower():
           text=text.replace("/help"," ").strip()
           if text in command_dict:
               msg=command_help[command_dict[text]]
           elif not text:
                cur.execute("SELECT * FROM users where chat_id = (%(chat_id_sql)s)", {
                   'chat_id_sql': chat_id})
                ch = cur.fetchone()
                choice = ch[1]
                msg = command_help[choice]
           else:
               msg = "type /change"
       elif text in command_dict:
           # update the ask array
           update_change(cur, chat_id, command_dict[text])
           msg = "done!"
       else:
           msg = "type /change"

       bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id, disable_web_page_preview=True)

   else:
       #get the user choice from DB
       cur.execute("SELECT * FROM users where chat_id = (%(chat_id_sql)s)", {
           'chat_id_sql': chat_id})
       ch = cur.fetchone()
       choice=ch[1]
       
       
       
       if choice==1:
            text = re.sub(r"\W", "_", text)
            msg = ai.avatar(text)
            if msg:
                bot.sendChatAction(chat_id=chat_id, action="upload_photo")
                bot.sendPhoto(chat_id=chat_id, photo=msg,
                                reply_to_message_id=msg_id)
            else:
                bot.sendMessage(
                    chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)
        
       elif choice==2:
            details = "chat_id - " + str(chat_id) + '\nmsg_id - '+str(msg_id)
            #bot.sendChatAction(chat_id=chat_id, action="typing ")
            bot.sendMessage(chat_id=chat_id, text=details, reply_to_message_id=msg_id)
    
       elif choice==3:
            ch,msg,lat,long=ai.ip_location(text)
            bot.sendMessage(chat_id=chat_id, text=msg, reply_to_message_id=msg_id)
            if ch==1:
                bot.sendLocation(chat_id=chat_id, latitude=lat, longitude=long)
        
       elif choice>=41 and choice<=45:
            msg=ai.chatbot((choice%10),text)
            bot.sendMessage(chat_id=chat_id, text=msg)
                

       """ 
       if(len(text) > 49):
	        text=text[0:49]
       insert_ask(cur, chat_id, text)
       """
   #debug massage
   print(text)
   
   #commit to save any change and close DB connection
   conn.commit()
   conn.close()
   return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
   s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN)) 
   if s:
       return "webhook setup ok"
   else:
       return "webhook setup failed"


@app.route('/')
def index():
   return '.'

'''
@app.route('/game')
def game():
   return render_template('game.html')
'''
if __name__ == '__main__':
   app.run(threaded=True)
