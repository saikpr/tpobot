#dummy program


from flask import Flask, request
from tasks import add
from tasks import fb_messenger_reply
import requests
from tbot.facebook_messenger import get_users_name, check_user_activation, get_fourms_ids_user, generate_short_forum_texts
from tbot.config import mongo_client

import time
from pprint import pprint
flask_app = Flask(__name__)



# print fb_tpobot_access_code


db = mongo_client["facebook_messenger_user"]


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
                if ("register" in message.lower()):
                    store_dict_this_chat["type"] = "register"

                    pass
                    return "ok"
                if not check_user_activation(sender):
                    return_message = "sharks, you have not registered to this bot \nAfraid not, type register to begin"
                    store_dict_this_chat["type"] = "not_registered"
                    store_dict_this_chat["reply"] = return_message
                    store_dict_this_chat["reply_timestamp"] = int(time.time())
                    db.chat_history.insert(store_dict_this_chat)
                    fb_messenger_reply.apply_async((sender, return_message))
                    return "ok"
                
                if ("search" in message.lower() or "find" in message.lower()):
                    pass
                    return "ok"
                    #TODO
                
                    #TODO
                if ("more" in message.lower() or ("next" in message.lower())):
                    pass
                    return "ok"
                    #TODO

                if ("hi" in message.lower() or "hey" in message.lower() or "hello" in message.lower() or
                        "howdy" in  message.lower()):

                    
                    
                    forum_ids,top_forum_code = get_fourms_ids_user(sender)
                    store_dict_this_chat["forum_list"] = return_message
                    store_dict_this_chat["type"] = "forum_list"
                    
                    if len(forum_ids)==0:
                        user_name = get_users_name(sender)
                        return_message = "Yay "+user_name+ "!!!, no new updates\n"
                        store_dict_this_chat["reply"] = return_message
                        db.chat_history.insert(store_dict_this_chat)
                        fb_messenger_reply.apply_async((sender, return_message))
                        return "ok"
                    else:
                        
                        store_dict_this_chat["forum_list_length"] = len(forum_ids)
                        return_message = generate_short_forum_texts(forum_ids[:10], top_forum_code )
                        
                        if len(forum_ids)>10:
                            store_dict_this_chat["forum_list_last_count"] = 10
                            return_message +="\n\ntype more to get more forums"
                        
                        store_dict_this_chat["reply"] = return_message
                        db.chat_history.insert(store_dict_this_chat)
                        fb_messenger_reply.apply_async((sender, return_message))
                        return "ok"
                
                #if numbers        
                if (len(message.split("-")) == 2 
                    and not is_number(message.split("-")[0])
                    and not is_number(message.split("-")[1])
                    and is_number(message.split("-")[1]) > is_number(message.split("-")[0])):

                    last_chat = db.chat_history.find_one({"type":"forum_list","sender":sender}).sort([("reply_timestamp", pymongo.DESCENDING)])




                





                fb_messenger_reply.apply_async((sender, "Hello "+ str(user_name[0])+",\n "+ message[::-1]))
            except KeyError:
                pass
    return "ok"
