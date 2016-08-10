import requests
import logging
from HTMLParser import HTMLParseError
from .config import mongo_client
from .config import fb_tpobot_access_code
from .config import  db_tpobot
from .config import  strings_return_dict
import time
import re
import pymongo
import os
import hashlib


def check_user_activation(fb_user_id):
    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    
    try:
        return user_data["isvalid"] 
    except KeyError:
        pass
    return True


def create_activation(fd_user_id):
    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    rand_string = os.urandom(8)
    rand_code = hashlib.md5(rand_string).hexdigest()
    db_tpobot.userinfo.update_one(  
        {"_id": fb_user_id},
        {
            "$set": {
                "isvalid": False,
                "access_code":rand_code
            }
        })
    return True


def activate_users(fd_user_id,access_code):
    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    if access_code is not user_data.get("access_code",None):
        return False
    db_tpobot.userinfo.update_one(  
        {"_id": fb_user_id},
        {
            "$set": {
                "isvalid": True
            }
        })
    return True


def register_user(fb_user_id, first_name, last_name, email_id=None, group=None, forum_batch_code=None, last_forum_id=None):
    if  check_user_activation(fb_user_id) :
        return False

    user_dict = {
            "_id":fb_user_id,
            "first_name":first_name,
            "last_name":last_name,
            "register_timestamp":time.time(),
            "last_active":time.time()
    }
    if group:
        user_dict["group"]=group
    if email_id:    
        user_dict["email_id"]=email_id
    if forum_batch_code:        
        user_dict["batch_forum_code"]=forum_batch_code
    if last_forum_id:
        user_dict["last_forum_id"]=last_forum_id
    else:
        user_dict["last_forum_id"]=get_last_forum()-2
    tmp = db_tpobot.userinfo.insert_one(user_dict)
    # create_activation(fd_user_id)
    return True

def get_fourms_ids_user(fb_user_id):
    
    # if not check_user_activation(fb_user_id):
    #     return False


    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    # print user_data
    forum_data = db_tpobot.forum_posts.find({"post_id":  {"$gt":user_data["last_forum_id"]}  })
    # print "forum_data"
    # print forum_data
    # last_forum_data = db_tpobot.forum_posts.find_one( sort=[("post_id", pymongo.DESCENDING)])
    
    # print "last_forum_data"
    # print last_forum_data
    forum_ids = [ each_el["post_id"] for each_el in forum_data]
    if forum_ids:
        # print forum_ids
        last_forum_id = sorted(forum_ids,reverse=True)[0]

        db_tpobot.userinfo.update_one(  
            {"_id": fb_user_id},
            {
                "$set": {
                    "last_forum_id": last_forum_id,
                    "last_active":int(time.time())
                }
            })
    # print forum_ids 
    return forum_ids

def get_last_forum():
    try:
        return db_tpobot.forum_posts.find_one( sort=[("post_id", pymongo.DESCENDING)])["post_id" ]
    except KeyError:
        return 0


def get_fourms_ids_search(search_string):
    print list(search_string)
    matching_forum_data = db_tpobot.forum_posts.find({
        "$or": [{
                    "body": {'$regex':search_string,"$options":"i"}
                }, 
                {
                    "title": {'$regex':search_string,"$options":"i"}
                }]
    }).sort([("post_id", pymongo.DESCENDING)])

    forum_ids = [ each_el["post_id"] for each_el in matching_forum_data]
    print forum_ids
    return forum_ids




def generate_short_forum_texts(forum_ids ):
    for forum_position,each_forum in enumerate(forum_ids):
        t = get_forum_title(each_forum)
        yield forum_position+1,t[0],t[1],each_forum

def get_forum_body(forum_id):
    t =  db_tpobot.forum_posts.find_one({"post_id":forum_id})
    if not t:
        return None
    # strings_return_dict["view_deactivated"]
    # return t["body"],t["url"]
    return strings_return_dict["view_deactivated"],t["url"]


def get_forum_title(forum_id):
    t =  db_tpobot.forum_posts.find_one({"post_id":forum_id})
    if not t:
        return None
    return t["title"],t["url"]


def get_users_name(fb_user_id):
    logging.debug('inside get_users_name with :'+str(fb_user_id))
    user_details_url = "https://graph.facebook.com/v2.6/%s"%fb_user_id
    user_details_params = {'fields':'first_name,last_name,profile_pic', 'access_token':fb_tpobot_access_code}
    try:
        user_details = requests.get(user_details_url, user_details_params).json()
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        return None
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        return None
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        return None
    except Exception as e:
        logging.error("Captain something horribly gone wrong Here's the error " + str(e))
        return None
    
    return user_details['first_name'],user_details['last_name']
    # ..... code to post message ...


def help_message(user_name,fb_user_id):
    if not check_user_activation(fb_user_id):
        reply_message = [strings_return_dict["my_intro"],get_registration_help(user_name)[1],
                    strings_return_dict["help_str"]]
    else:
        reply_message = [strings_return_dict["my_intro"], strings_return_dict["help_str"]]
    return reply_message


def hello_message(user_name,fb_user_id):
    if not check_user_activation(fb_user_id):
        reply_message = "Hii "+user_name[0]+ "\n\nOh sharks!!!, I dont know anything about you!\nType 'help' for more info and registration"
    else:
        reply_message = "Hii "+user_name[0]+ "\n\nWhat can I do for you???"
    return reply_message

def get_top_forums():
    top_forums = db_tpobot.forum_top.find().sort([("forum_id",pymongo.DESCENDING)])
    return [(el["forum_id"],el["batch"]) for el in top_forums]

def get_registration_help(user_name=None):
    if not user_name:
        user_name = ["Charlie","I dont know"]
    top_forums = get_top_forums()
    print top_forums
    top_forumstr = ""
    for each_rl in top_forums:
        top_forumstr = top_forumstr + str(each_rl[0]) +" : "+str(each_rl[1]) +"\n"
    reply_message = ["Hi "+(user_name[0])+"""\n\nThis is wrong, its all going wrong. \nI am unable to understand it""",
        """To register type \n\n'register access_code'\n(Without quotes) """ ]
    return reply_message

def check_access_code(access_code):
    t =  db_tpobot.fb_access_codes.find_one({"access_code":access_code})
    if not t:
        return False
    try:
        return t["isvalid"]
    except KeyError:
        pass
    return True

def activate_push_notification(fb_user_id):
    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    get_fourms_ids_user(fb_user_id)
    db_tpobot.userinfo.update_one(  
            {"_id": fb_user_id},
            {
                "$set": {
                    "pushnotifications": True
                }
            })
    return True

def deactivate_push_notification(fb_user_id):
    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    db_tpobot.userinfo.update_one(  
            {"_id": fb_user_id},
            {
                "$set": {
                    "pushnotifications": False
                }
            })
    return True

def check_push_notification(fb_user_id):
    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    try:
        return user_data["pushnotifications"] 
    except KeyError:
        pass
    return False

