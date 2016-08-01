import os
from pymongo import MongoClient


application_url = os.environ.get("OPENSHIFT_APP_DNS","") 
mongo_db_url = os.environ.get("OPENSHIFT_MONGODB_DB_URL","")
mongo_db_port = os.environ.get("OPENSHIFT_MONGODB_DB_PORT","")
fb_tpobot_access_code = os.environ.get("FB_tpobot_ACCESS_CODE","")

TPO_forum_user_id = os.environ.get("TPO_FORUM_USER_ID","")
TPO_forum_user_passwd = os.environ.get("TPO_FORUM_USER_PASSWD","")
TPO_url = os.environ.get("TPO_URL","")
TPO_top_forum_id = 3

push_bullet_url = "https://api.pushbullet.com/v2/pushes"
push_bullet_group = "tpo_2016"
push_bullet_token = os.environ.get("PUSHBULLET_AUTH_TOKEN","")

register_access_code = os.environ.get("TPOBOT_ACCESS_CODE","")

mongo_client  = MongoClient(mongo_db_url)
db_tpobot = mongo_client["tpobot_db"]

persistent_button_settings = {
  "setting_type" : "call_to_actions",
  "thread_state" : "existing_thread",
  "call_to_actions":[
    {
      "type":"postback",
      "title":"Help",
      "payload":"PAYLOAD_FOR_HELP"
    },
    {
      "type":"postback",
      "title":"Get Updates",
      "payload":"PAYLOAD_FOR_UPDATES"
    },
    {
      "type":"web_url",
      "title":"Visit Placement Forum",
      "url":"http://placement.iitbhu.ac.in/forum/viewforum.php?f=3"
    }
  ]
}



strings_return_dict = {
    "user_registered":"Captain, You have already have registered\n\nI am afraid to say you cannot re-register at this time",
    "registration_success":"Hi {user_name}\n\nYou are set :-)\n\nDisclaimer : This bot is not related to TPO or any other organisation",
    "found_no_posts":"I am afraid, Charlie\n\nI am unable to find any posts, try again maybe?",
    "get_more":"type 'more' to get more posts",
    "incorrect_number":"Charlie, Charlie, Charlie!!! \ntype the correct number or retry the query",
    "no_more":"Charlie, I have no more posts for you",
    "no_updates" : "Yay {user_name}!!!, no new updates\n",
    "my_intro" : """Hi, I am TPO BOT. Your stupid little help.\n\n""",
    "help_str" : """To get updates from previous run, type "get updates" \nTo search, type "search <string>"\nexample: search sainyam\nMisc : Say "hi","""

}

my_user_agent = "tpobot v0.1"