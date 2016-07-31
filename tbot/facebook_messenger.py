import requests
import logging
from HTMLParser import HTMLParseError
from .config import mongo_client
from .config import fb_tpobot_access_code, db_tpobot
import time
import re
import pymongo

# db_tpobot = mongo_client["tpobot_db"]

def check_user_activation(fb_user_id):
    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    
    try:
        return user_data["isvalid"] 
    except KeyError:
        pass
    return True

def register_user(fb_user_id, first_name, last_name, group, emailid, forum_batch_code, last_forum_id):
    if  check_user_activation(fb_user_id) :
        return False

    user_dict = {
            "_id":fb_user_id,
            "first_name":first_name,
            "last_name":last_name,
            "group":group,
            "email_id":emailid,
            "batch_forum_code":forum_batch_code,
            "last_forum_id":last_forum_id,
            "register_timestamp":time.time(),
            "last_active":time.time()
    }
    tmp = db_tpobot.userinfo.insert_one(user_dict)

    return True

def get_fourms_ids_user(fb_user_id):
    
    if not check_user_activation(fb_user_id):
        return False


    user_data = db_tpobot.userinfo.find_one({"_id":fb_user_id})
    print user_data
    forum_data = db_tpobot.forum_posts.find({"post_id":  {"$gt":user_data["last_forum_id"]}  })
    print "forum_data"
    print forum_data
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
        
    return forum_ids, user_data["batch_forum_code"]



def get_fourms_ids_search(search_string):
    print search_string
    regx = re.compile(search_string, re.IGNORECASE)
    print regx
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
    for forum_number,each_forum in enumerate(forum_ids):
        t = get_forum_title(each_forum)
        yield forum_number+1,t

def get_forum_body(forum_id):
    t =  db_tpobot.forum_posts.find_one({"post_id":forum_id})
    if not t:
        return None
    return t["body"]


def get_forum_title(forum_id):
    t =  db_tpobot.forum_posts.find_one({"post_id":forum_id})
    if not t:
        return None
    return t["title"]


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