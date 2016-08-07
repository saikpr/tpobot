import traceback
from flask import Flask, request
from tasks import cron_task
from tasks import fb_messenger_reply
from tasks import push_post_sender
import requests
from tbot.facebook_messenger import get_users_name
from tbot.facebook_messenger import check_user_activation
from tbot.facebook_messenger import get_fourms_ids_user
from tbot.facebook_messenger import generate_short_forum_texts
from tbot.facebook_messenger import get_fourms_ids_search
from tbot.facebook_messenger import register_user
from tbot.facebook_messenger import help_message
from tbot.facebook_messenger import get_registration_help
from tbot.facebook_messenger import get_last_forum
from tbot.facebook_messenger import hello_message
from tbot.facebook_messenger import get_forum_body
from tbot.facebook_messenger import check_access_code 
from tbot.facebook_messenger import activate_push_notification 
from tbot.facebook_messenger import deactivate_push_notification 
from tbot.facebook_messenger import check_push_notification
from tbot.config import db_tpobot
from tbot.config import strings_return_dict, MY_FB_ID
import pymongo
import os
import time
from pprint import pprint
flask_app = Flask(__name__)
from time import sleep
from tbot.forum_operations import forum_direct_login
from tbot.forum_operations import check_valid_sid
from tbot.forum_operations import get_top_forums_ids
from tbot.forum_operations import forum_post_ids
from tbot.forum_operations import get_forum_text
# db_tpobot = mongo_client["tpobot_db"]


FORUM_COUNT = 5
# print fb_tpobot_access_code




def is_number(s):
    try:
        return int(s)
    except ValueError:
        return False


# def got_number(post_number,sender):
#     last_chat = db_tpobot.chat_history.find_one({"type":"forum_list","sender":sender} ,
#                                                  sort=[("reply_timestamp", pymongo.DESCENDING)] )
#     reply_message = ""
#     try:
#         previous_forum_list = last_chat["forum_list"]
#         requested_post = previous_forum_list[post_number-1]
#         reply_message = push_post_sender(requested_post,sender)
        

#     except KeyError:
#         reply_message = strings_return_dict["incorrect_number"]
#         fb_messenger_reply.apply_async((sender,reply_message))
#     except TypeError:
#         reply_message = strings_return_dict["incorrect_number"]
#         fb_messenger_reply.apply_async((sender,reply_message))
#     except IndexError:
#         reply_message = strings_return_dict["incorrect_number"]
#         fb_messenger_reply.apply_async((sender,reply_message))
#     return reply_message


def push_forum_ids(sender,forum_ids,start_count=0):
    temp_list = list()
    print forum_ids[start_count:start_count+FORUM_COUNT]
    for each_title in generate_short_forum_texts(forum_ids[start_count:start_count+FORUM_COUNT] ):
        # print each_title
        msg =  each_title[1]
        temp_list.append(msg)
        sleep(0.1)
        fb_messenger_reply.apply_async((sender, msg),dict(url=each_title[2],button="GET_BODY_POST_"+str(each_title[3]),button_str="View"))   
    if len(forum_ids) - start_count>FORUM_COUNT:
        fb_messenger_reply.apply_async((sender, strings_return_dict["get_more"]),dict(button="GET_MORE",button_str="More"))
        # strings_return_dict["get_more"]
        temp_list.append(strings_return_dict["get_more"])
    return temp_list
    

def get_more(sender, store_dict_this_chat):
    last_chat = db_tpobot.chat_history.find_one({"type":"forum_list","sender":sender} ,
                                 sort=[("reply_timestamp", pymongo.DESCENDING)] )
    reply_message = ""
    reply_send = False
    try:

        if last_chat["forum_list_length"]<=last_chat["forum_list_last_count"]:
            reply_message = strings_return_dict["no_more"]
        else:
            forum_ids = last_chat["forum_list"]
            store_dict_this_chat["forum_list"] = forum_ids
            store_dict_this_chat["forum_list_length"] = len(forum_ids)
            store_dict_this_chat["type"] = "forum_list"
            
            reply_message = push_forum_ids(sender,forum_ids,last_chat["forum_list_last_count"])
            if len(forum_ids)==0:
                reply_message = strings_return_dict['found_no_posts']
            else:
                store_dict_this_chat["forum_list_last_count"] = len(forum_ids)
                
                if len(forum_ids) - last_chat["forum_list_last_count"]>FORUM_COUNT:
                    store_dict_this_chat["forum_list_last_count"] = last_chat["forum_list_last_count"] +  FORUM_COUNT
                reply_send =True
    except KeyError:
        reply_message = strings_return_dict["no_more"]

    except TypeError:
        reply_message = strings_return_dict["no_more"]

    except IndexError:
        reply_message = strings_return_dict["no_more"]
    return reply_message, reply_send



def post_search_posts(sender, store_dict_this_chat,message):
    query_message = message[:7].lower().replace("search ","").replace("find ","")+ message.lower()[7:]
    forum_ids = get_fourms_ids_search(query_message)
    store_dict_this_chat["forum_list"] = forum_ids
    store_dict_this_chat["forum_list_length"] = len(forum_ids)
    store_dict_this_chat["type"] = "forum_list"
    reply_send = False
    if len(forum_ids)==0:
        reply_message = strings_return_dict['found_no_posts']
    else:
        store_dict_this_chat["forum_list_last_count"] = len(forum_ids)
        if len(forum_ids)>FORUM_COUNT:
            store_dict_this_chat["forum_list_last_count"] = FORUM_COUNT
        reply_message = push_forum_ids(sender,forum_ids)
        reply_send =True
    return reply_message, reply_send    


def post_get_update(sender, store_dict_this_chat,user_name) :
    forum_ids = get_fourms_ids_user(sender)

                    # store_dict_this_chat["type"] = "not_registered"
    if forum_ids == False:
        reply_message = hello_message(user_name, sender)
        store_dict_this_chat["type"] = "not_registered"
        reply_send =False
        return reply_message, reply_send
    store_dict_this_chat["forum_list"] = forum_ids
    store_dict_this_chat["forum_list_length"] = len(forum_ids)
    store_dict_this_chat["type"] = "forum_list"
    print forum_ids
    reply_send =False


    if len(forum_ids)==0:
       reply_message = strings_return_dict["no_updates"].format(user_name = user_name[0])
    else:
        
        store_dict_this_chat["forum_list_last_count"] = len(forum_ids)
        reply_message = push_forum_ids(sender,forum_ids)
        reply_send =True
        if len(forum_ids)>FORUM_COUNT:
            store_dict_this_chat["forum_list_last_count"] = FORUM_COUNT
            reply_message.append(strings_return_dict["get_more"])
    print str(reply_message)
    # print store_dict_this_chatt
    return reply_message, reply_send


def push_notfication_on(sender):
    reply_message = ""
    if check_user_activation(sender) is False:
        reply_message = "You are not registered"
    else:
        if activate_push_notification(sender):
            reply_message = strings_return_dict["push_activated"]

        else:
            reply_message = "Some Error, try registering"
    return reply_message


def push_notfication_off(sender):
    reply_message = ""
    if check_user_activation(sender) is False:
        reply_message = "You are not registered"
    else:
        if deactivate_push_notification(sender):
            reply_message = strings_return_dict["push_deactivated"]

        else:
            reply_message = "Some Error, try registering"
    return reply_message


@flask_app.route('/v', methods=['GET'])
def handle_v():
    return "Working"

@flask_app.route('/messenger/webhook', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']

@flask_app.route("/crontpocheck")
def cron_update():
    cron_task.apply_async()
    return "Ok"

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
                reply_send = False
                # print store_dict_this_chat
                reply_message = ""
                if ("hi" in message.lower() or "hey" in message.lower() or "hello" in message.lower() or
                        "howdy" in  message.lower()):
                    print "received_hello"
                    reply_message = hello_message(user_name, sender)
                    store_dict_this_chat["type"] = "hello_registered"
                elif ("register" in message.lower()):
                    store_dict_this_chat["type"] = "register"
                    
                    if check_user_activation(sender) is True:
                        reply_message = strings_return_dict["user_registered"]
                    else :
                        reg_message = message.split(" ")
                        if len(reg_message)!= 2:
                            reply_message = get_registration_help(user_name)
                        elif check_access_code(reg_message[1]):
                            
                            register_user(fb_user_id=sender,
                                         first_name = user_name[0],
                                         last_name =user_name[1]
                                         # group =reg_message[2],
                                         # emailid=reg_message[2],
                                         # forum_batch_code=reg_message[4],
                                         # last_forum_id=get_last_forum()
                                         )
                            reply_message = strings_return_dict["registration_success"]
                            fb_messenger_reply.apply_async((sender,reply_message))
                            reply_send = True
                            temp_str = push_notfication_on(sender)
                            reply_message+=temp_str
                            fb_messenger_reply.apply_async((sender,temp_str))
                            fb_messenger_reply.apply_async((MY_FB_ID, "Registered : "+str(user_name)))
                            # reply_message = help_message(user_name,sender)
                        else:
                            reply_message = "Wrong Access_Code\n\n"+get_registration_help(user_name)[1]
                            
                elif (check_access_code(message.replace(" ","").lower())):
                    if check_user_activation(sender) is True:
                        reply_message = strings_return_dict["user_registered"]
                    else:
                        register_user(fb_user_id=sender,
                                             first_name = user_name[0],
                                             last_name =user_name[1]
                                             # group =reg_message[2],
                                             # emailid=reg_message[2],
                                             # forum_batch_code=reg_message[4],
                                             # last_forum_id=get_last_forum()
                                             )
                        reply_message = strings_return_dict["registration_success"]
                        fb_messenger_reply.apply_async((sender,reply_message))
                        reply_send = True
                        temp_str = push_notfication_on(sender)
                        reply_message+=temp_str
                        fb_messenger_reply.apply_async((sender,temp_str))
                        fb_messenger_reply.apply_async((MY_FB_ID, "Registered : "+str(user_name)))
                    # print reply_message
                elif  ("help" in message.lower()):
                    reply_message=help_message(user_name,sender)
                    store_dict_this_chat["type"] = "help"
                elif (("lala" in message.lower() or "jaja" in message.lower()) and (int(sender) == int(os.environ.get("DARLING_ID","")) or int(sender) == int(MY_FB_ID)) ):
                    reply_message = os.environ.get("DARLING_MESSAGE","")
                    reply_send = True
                    fb_messenger_reply.apply_async((sender,reply_message))
                    reply_message=""
                    store_dict_this_chat["type"] = "lov"
                elif check_user_activation(sender) is False: 
                    reply_message = hello_message(user_name, sender)
                    store_dict_this_chat["type"] = "not_registered"
                    
                # #if numbers   
                # elif  is_number(message) is not False:
                #     post_number = is_number(message)
                #     reply_send =True
                #     reply_message =  got_number(post_number,sender)
                    

                # elif (len(message.split("-")) == 2 
                #     and is_number(message.split("-")[0]) is not False
                #     and is_number(message.split("-")[1]) is not False
                #     and is_number(message.split("-")[1]) > is_number(message.split("-")[0])):
                #     reply_message = "Not Implemented"


                elif ("search" in message.lower()[:6] or "find" in message.lower()[:6]):
                    
                    post_search_posts(sender, store_dict_this_chat,message)
                elif ("more" in message.lower() or ("next" in message.lower())):
                    reply_message,reply_send =  get_more(sender, store_dict_this_chat)

                
                    
                elif ("get" in message.lower()):
                    try:
                        reply_message,reply_send =  post_get_update(sender, store_dict_this_chat,user_name)
                    except Exception as e:
                        print e
                    # fb_messenger_reply.apply_async((sender, reply_message))
                elif ("feedback" in message.lower()):
                    reply_message = "Thanks for your feedback"
                    fb_messenger_reply.apply_async((MY_FB_ID, message))
                
                elif ("push" in message.lower() and ("off" in message.lower() or "deactivate" in message.lower())):
                    reply_message = push_notfication_off(sender)

                elif ("push" in message.lower() and ("on" in message.lower() or "activate" in message.lower())):
                    reply_message = push_notfication_on(sender)
                elif ("thank" in message.lower()):
                    reply_message = strings_return_dict["thanks"]
                    fb_messenger_reply.apply_async((MY_FB_ID, str(user_name )+" : "+ str(message)))    
                # elif :
                else:
                    reply_message = strings_return_dict["unable_to_understand"]
                
                store_dict_this_chat["reply_timestamp"] = int(time.time())
                store_dict_this_chat["reply"] = reply_message
                print store_dict_this_chat
                db_tpobot.chat_history.insert(store_dict_this_chat)
                if not reply_send:
                    fb_messenger_reply.apply_async((sender, reply_message))
                # fb_messenger_reply.apply((sender, "Hello "+ str(user_name[0])+",\n "+ message[::-1]))
            except KeyError:
                
                pass
            except Exception as e:
                print "ERROR_FOR_SAINYAM"
                print (traceback.format_exc())
                try:
                    sender = each_message['sender']['id']
                    # user_name = get_users_name(sender)
                    reply_message = strings_return_dict["failing_everything"]
                    fb_messenger_reply.apply_async((sender, reply_message))
                    fb_messenger_reply.apply_async((MY_FB_ID, "I have failed you "+str(e)))
                except KeyError:
                    pass
            try:
                pprint( each_message)
                sender = each_message['sender']['id']
                user_name = get_users_name(sender)
                postback_payload = each_message['postback']['payload']
                store_dict_this_chat = dict()
                store_dict_this_chat['sender'] = sender
                store_dict_this_chat["postback_payload"] = postback_payload
                store_dict_this_chat["fb_timestamp"] = each_message["timestamp"]
                reply_message = ""
                reply_send =False
                if postback_payload == "PAYLOAD_FOR_UPDATES":
                    reply_message,reply_send =  post_get_update(sender, store_dict_this_chat,user_name)

                elif postback_payload == "PAYLOAD_FOR_HELP":
                    # help_message
                    reply_message=help_message(user_name,sender)
                    store_dict_this_chat["type"] = "help"
                elif "GET_BODY_POST_" in postback_payload:
                    forum_id = int(postback_payload.replace("GET_BODY_POST_",""))
                    reply_message = push_post_sender(forum_id,sender)
                    reply_send = True
                    store_dict_this_chat["type"] = "forum_body_return"
                elif "GET_MORE" in postback_payload:
                    reply_message,reply_send =  get_more(sender, store_dict_this_chat)
                elif "GET_STARTED_USER" in postback_payload:
                    reply_message=help_message(user_name,sender)
                    store_dict_this_chat["type"] = "help"
                store_dict_this_chat["reply_timestamp"] = int(time.time())
                store_dict_this_chat["reply"] = reply_message
                # print store_dict_this_chat
                db_tpobot.chat_history.insert(store_dict_this_chat)
                if not reply_send:
                    fb_messenger_reply.apply_async((sender, reply_message))
                # fb_messenger_reply(sender, reply_message)
            except KeyError:
                
                pass
            except Exception as e:
                print "ERROR_FOR_SAINYAM"
                print (traceback.format_exc())
                try:
                    sender = each_message['sender']['id']
                    # user_name = get_users_name(sender)
                    reply_message = strings_return_dict["failing_everything"]
                    fb_messenger_reply.apply_async((sender, reply_message))
                    fb_messenger_reply.apply_async((MY_FB_ID, "I have failed you "+str(e)))
                except KeyError:
                    pass
    return "ok"
