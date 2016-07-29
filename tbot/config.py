import os


try:
    application_url = os.environ["OPENSHIFT_APP_DNS"]
except KeyError:
    application_url = ""

try:
    mongo_db_url = os.environ["OPENSHIFT_MONGODB_DB_URL"]
except KeyError:
    mongo_db_url = ""


try:
    mongo_db_port = os.environ["OPENSHIFT_MONGODB_DB_PORT"]
except KeyError:
    mongo_db_port = ""




TPO_forum_user_id = os.environ["TPO_FORUM_USER_ID"]
TPO_forum_user_passwd = os.environ["TPO_FORUM_USER_PASSWD"]
TPO_url = os.environ["TPO_URL"]
TPO_top_forum_id = 3


push_bullet_url = "https://api.pushbullet.com/v2/pushes"
push_bullet_group = "tpo_2016"

try:
    push_bullet_token = os.environ["PUSHBULLET_AUTH_TOKEN"]
except:
    push_bullet_token = ""