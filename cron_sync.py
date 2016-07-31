from bs4 import BeautifulSoup
import requests
import logging
from pprint import pprint
from HTMLParser import HTMLParseError
from tbot.config import mongo_client
from tbot.config import TPO_forum_user_id #FORUM User Name
from tbot.config import TPO_forum_user_passwd
from tbot.config import TPO_top_forum_id #TPO Forum, top most 3 in this case

from tbot.forum_operations import forum_direct_login
from tbot.forum_operations import check_valid_sid
from tbot.forum_operations import get_top_forums_ids
from tbot.forum_operations import forum_post_ids
from tbot.forum_operations import get_forum_text


db = mongo_client["tpobot_db"]

def update_db():
    global db
    sid_php = forum_direct_login()

    if  not sid_php:
        print "ERROR"
        return None
    top_forum_tuple = get_top_forums_ids(sid_php)
    if  not top_forum_tuple:
        print "ERROR"
        return None

    for each_ele in top_forum_tuple:
        if  db.forum_top.find({"forum_id":int(each_ele[0])}).count() == 0 :
            db.forum_top.insert({"batch":each_ele[1],"forum_id":int(each_ele[0])})
        
        list_sub_forum = forum_post_ids(sid_php,each_ele[0])
        if  not top_forum_tuple:
            print "ERROR"
            continue

        for each_forum in list_sub_forum:
            if  db.forum_posts.find({"post_id":int(each_forum)}).count() == 0 :
                forum_posts_data = get_forum_text(sid_php,each_ele[0],each_forum)
                if not forum_posts_data:
                    print "ERROR" , each_ele[0], each_forum
                    continue
                db.forum_posts.insert({"title":forum_posts_data[0],
                                      "body":forum_posts_data[1],
                                      "url":forum_posts_data[2],
                                      "parent_forum":int(each_ele[0]),
                                      "post_id":int(each_forum)})
                print each_ele[0], each_forum

if __name__ == "__main__":
    update_db()