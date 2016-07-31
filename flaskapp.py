#dummy program


from flask import Flask, request
from tasks import add
from tasks import fb_messenger_reply
import requests
from tbot.facebook_messenger import get_users_name, check_user_activation, get_fourms_ids_user, generate_short_forum_texts, get_fourms_ids_search, register_user
from tbot.config import  db_tpobot
import pymongo
import time
from pprint import pprint
flask_app = Flask(__name__)
from time import sleep


# print fb_tpobot_access_code




def is_number(s):
    try:
        return int(s)
    except ValueError:
        return False

@flask_app.route('/v', methods=['GET'])
def handle_v():
    k = add.delay(23,23)
    res = k.get(timeout=5)
    print res
    return str(res)


@flask_app.route('/messenger/webhook', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']


@flask_app.route('/messenger/webhook', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    # pprint( data)
    for each_entry in data['entry']:
        for each_message in each_entry['messaging']:
            try:
                sender = each_message['sender']['id']
                user_name = get_users_name(sender)
                message = each_message['message']['text']
                store_dict_this_chat = dict()
                store_dict_this_chat['sender'] = sender
                store_dict_this_chat["received"] = message
                store_dict_this_chat["fb_timestamp"] = each_message["timestamp"]

                print store_dict_this_chat
                reply_message = ""
                if ("register" in message.lower()):
                    store_dict_this_chat["type"] = "register"
                    user_name = get_users_name(sender)
                    if check_user_activation(sender) is True:
                        reply_message = "Captain, You have already have registered\n\nI am afraid to say you cannot re-register at this time"
                        # print reply_message
                    else:
                        reply_message = "Yet to be implemented" #TODO Add to get previous register chain and question user
                        # print reply_message
                        register_user(fb_user_id=sender, first_name = user_name[0], last_name =user_name[1], group ="cse12", 
                                        emailid="sainyam.kapoor.cse12@iitbhu.ac.in", forum_batch_code=165, last_forum_id=2560)
                        reply_message +="\n Temp done"
                    # print reply_message
                elif  check_user_activation(sender) is False: 
                    reply_message = "sharks, you have not registered to this bot \nAfraid not, type register to begin"
                    store_dict_this_chat["type"] = "not_registered"
                    
                    last_chat = db_tpobot.chat_history.find_one({"type":"forum_list","sender":sender} ,sort=[("reply_timestamp", pymongo.DESCENDING)] )
                
                #if numbers   
                elif  is_number(message) is not False:
                    last_chat = db_tpobot.chat_history.find_one({"type":"forum_list","sender":sender} ,sort=[("reply_timestamp", pymongo.DESCENDING)] )
                    reply_message = "Not Implemented"

                elif (len(message.split("-")) == 2 
                    and is_number(message.split("-")[0]) is not False
                    and is_number(message.split("-")[1]) is not False
                    and is_number(message.split("-")[1]) > is_number(message.split("-")[0])):

                    last_chat = db_tpobot.chat_history.find_one({"type":"forum_list","sender":sender} ,sort=[("reply_timestamp", pymongo.DESCENDING)] )
                    reply_message = "Not Implemented"


                elif ("search" in message.lower()[:6] or "find" in message.lower()[:6]):
                    query_url = message[:7].replace("search","")
                    query_url = query_url[:7].replace("find","")
                    query_url = query_url + message.lower()[7:]
                    forum_ids = get_fourms_ids_search(query_url)
                    reply_message = "Not Implemented "+str(forum_ids)
                    #TODO
                
                    #TODO
                elif ("more" in message.lower() or ("next" in message.lower())):
                    reply_message = "Not Implemented"
                    #TODO

                elif ("hi" in message.lower() or "hey" in message.lower() or "hello" in message.lower() or
                        "howdy" in  message.lower()):
                    print "received_heelo"
                    forum_ids,top_forum_code = get_fourms_ids_user(sender)
                    store_dict_this_chat["forum_list"] = reply_message
                    store_dict_this_chat["type"] = "forum_list"
                    print forum_ids
                    if len(forum_ids)==0:
                        user_name = get_users_name(sender)
                        reply_message = "Yay "+user_name[0]+ "!!!, no new updates\n"
                    else:
                        
                        store_dict_this_chat["forum_list_length"] = len(forum_ids)
                        temp_str = ""
                        for each_title in generate_short_forum_texts(forum_ids[:10] ):
                            msg = str(each_title[0])+"): " + each_title[1]
                            temp_str = temp_str + "\n\n" + msg
                            # sleep(0.1)
                            # fb_messenger_reply.apply_async((sender, msg))
                        reply_message = temp_str
                        reply_message += "Type the number of required forum"
                        if len(forum_ids)>10:
                            store_dict_this_chat["forum_list_last_count"] = 10
                            reply_message ="type 'more' to get more posts"
                

                else:
                    reply_message = "Either that's too cryptic or I am an idiot. \nIn either case, I am Sorry"
                
                store_dict_this_chat["reply_timestamp"] = int(time.time())
                store_dict_this_chat["reply"] = reply_message
                print store_dict_this_chat
                db_tpobot.chat_history.insert(store_dict_this_chat)
                fb_messenger_reply.apply_async((sender, reply_message))
                fb_messenger_reply.apply_async((sender, "Hello "+ str(user_name[0])+",\n "+ message[::-1]))
            except KeyError:

                pass
    return "ok"
