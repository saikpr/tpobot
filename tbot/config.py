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


mongo_client  = MongoClient(mongo_db_url)
