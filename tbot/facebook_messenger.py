import requests
import logging
from HTMLParser import HTMLParseError
from .config import mongo_client
from .config import fb_tpobot_access_code
import time
import re


db = mongo_client["facebook_messenger_user"]

def check_user_activation(fb_user_id):
    user_data = db.userinfo.find_one({"_id":fb_user_id})
    if not user_data:
        return False
    if user_data["isvalid"] == False:
        return False
    return True

def register_user(fb_user_id, user_name, group, emailid, forum_batch_code, last_forum_id):
    if  not check_user_activation(fb_user_id) :
        return False

    user_dict = {
            "_id":fb_user_id,
            "name":user_name,
            "group":group,
            "email_id":emailid,
            "batch_forum_code":forum_batch_code,
            "last_forum_id":last_forum_id,
            "register_timestamp":time.time(),
            "last_active":time.time()
    }
    tmp = db.userinfo.insert_one(user_dict)

    return True

def get_fourms_ids_user(fb_user_id):
    
    if check_user_activation(fb_user_id):
        return False


    user_data = db.userinfo.find_one({"_id":fb_user_id})
    forum_data = db.forum_post.find({"forum_id":  {"$gt":user_data["last_forum_id"]}  })
    last_forum_data = db.forum_post.find_one({}, sort=[("forum_id", pymongo.DESCENDING)])

    user_data["last_forum_id"] = last_forum_data["forum_id"]
    user_data["last_active"] = time.time()
    db.userinfo.update_one(user_data)
    forum_ids = [ each_el["forum_id"] for each_el in forum_data]
    return forum_ids, user_data["batch_forum_code"]


def get_fourms_ids_search(search_string):
    regx = re.compile(search_string, re.IGNORECASE)
    matching_forum_data = db.forum_post.find({
        "$or": [{
                    "body": {'$regex':regx}
                }, 
                {
                    "title": {'$regex':regx}
                }]
    }).sort([("forum_id", pymongo.DESCENDING)])

    forum_ids = [ each_el["forum_id"] for each_el in matching_forum_data]
    return forum_ids




def generate_short_forum_texts(forum_ids, top_forum_code ):
    if len(forum_ids) ==1:
        return db.forum_post.find_one({"forum_id":forum_ids[0],"parent_forum":top_forum_code})["body"]
    else:
        return_str =""
        for forum_number,forum_id in enumerate(forum_ids):
            if forum_number>9:
                break
            forum_body = db.forum_post.find_one({"forum_ids":forum_ids[0],"parent_forum":top_forum_code})["body"]
            new_forum_body = forum_body [:100]
            new_forum_body = " ".join(new_forum_body.split(" ")[:-1])
            return_str = return_str + "\n" +  str(forum_number+1) + str(new_forum_body)
            if len(forum_body)>100:
                return_str += "...."
        return return_str

def get_forum_text(forum_id, top_forum_code):
    t =  db.forum_post.find_one({"forum_id":forum_id,"parent_forum":top_forum_code})
    if not t:
        return False
    return t["body"]

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