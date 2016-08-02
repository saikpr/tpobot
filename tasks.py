from celery import Celery
from tbot.config import mongo_db_url
from tbot.config import fb_tpobot_access_code, db_tpobot
from tbot.forum_operations import forum_direct_login
from tbot.forum_operations import check_valid_sid
from tbot.forum_operations import get_top_forums_ids
from tbot.forum_operations import get_forum_text
from tbot.forum_operations import forum_post_ids
import requests
import logging
from celery.utils.log import get_task_logger
from time import sleep
logger = get_task_logger(__name__)
CELERY_BROKER = mongo_db_url 
celery_app = Celery(__name__)

sid_php = None


celery_app.conf.update(
    #BROKER_URL='ironmq://<project_id>:<token>@',
    BROKER_URL=CELERY_BROKER,
    #BROKER_URL='redis://localhost:6379/0',
    BROKER_POOL_LIMIT=2,
    CELERY_TASK_SERIALIZER='json',
    CELERY_RESULT_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT = ['json'],
    CELERY_RESULT_BACKEND=mongo_db_url,
    BROKER_VHOST = "celery",
	CELERY_MONGODB_BACKEND_SETTINGS = {
	    'database': 'celery_db_run',
	    'taskmeta_collection': 'my_taskmeta_collection',
	}

)


@celery_app.task
def cron_task():
    global sid_php
    if not sid_php:
        sid_php = forum_direct_login()
    if not check_valid_sid(sid_php):
        sid_php = forum_direct_login()
    if  not sid_php:
        print "ERROR"
        return None
    top_forum_tuple = get_top_forums_ids(sid_php)
    if  not top_forum_tuple:
        print "ERROR"
        return None
    return_str = ""
    for each_ele in top_forum_tuple:
        if  db_tpobot.forum_top.find({"forum_id":int(each_ele[0])}).count() == 0 :
            db_tpobot.forum_top.insert({"batch":each_ele[1],"forum_id":int(each_ele[0])})
        
        list_sub_forum = forum_post_ids(sid_php,each_ele[0],onlyonce=True)
        if  not top_forum_tuple:
            print "ERROR"
            continue

        for each_forum in list_sub_forum:
            if  db_tpobot.forum_posts.find({"post_id":int(each_forum)}).count() == 0 :
                forum_posts_data = get_forum_text(sid_php,each_ele[0],each_forum)
                if not forum_posts_data:
                    print "ERROR" , each_ele[0], each_forum
                    continue
                db_tpobot.forum_posts.insert({"title":forum_posts_data[0],
                                      "body":forum_posts_data[1],
                                      "url":forum_posts_data[2],
                                      "parent_forum":int(each_ele[0]),
                                      "post_id":int(each_forum)})
        return_str += str(list_sub_forum)
    logging.info(return_str)
    logging.info("Cron RUN")
def fb_send_message(user_id,msg,url=None,button=None,button_str="More"):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    # print msg
    if  url:
        data["message"]={"attachment":
                            {
                              "type":"template",
                              "payload":
                              {
                                "template_type":"button",
                                "text":msg,
                                "buttons":
                                [
                                  {
                                    "type":"web_url",
                                    "url":url,
                                    "title":"Visit Forum"
                                  }
                                ]
                              }
                            }
                        }
    if url and button:
        data["message"]={"attachment":
                            {
                              "type":"template",
                              "payload":
                              {
                                "template_type":"button",
                                "text":msg,
                                "buttons":
                                [
                                  {
                                    "type":"web_url",
                                    "url":url,
                                    "title":"Visit Forum"
                                  },
                                  {
                                    "type":"postback",
                                    "title":button_str,
                                    "payload":button
                                  }
                                ]
                              }
                            }
                        }
    elif button:
        data["message"]={"attachment":
                            {
                              "type":"template",
                              "payload":
                              {
                                "template_type":"button",
                                "text":msg,
                                "buttons":
                                [
                                  {
                                    "type":"postback",
                                    "title":button_str,
                                    "payload":button
                                  }
                                ]
                              }
                            }
                        }
    try:
        resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + fb_tpobot_access_code, json=data,headers={"Content-Type": "application/json"})
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        self.retry(countdown=2, exc=e, max_retries=3)
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        self.retry(countdown=2, exc=e, max_retries=3)
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        self.retry(countdown=2, exc=e, max_retries=3)

@celery_app.task()
def fb_messenger_reply(user_id, msg, url=None,button=None,button_str="More"):
    if isinstance(msg, basestring):
        fb_send_message(user_id,msg,url,button,button_str)
    else:
        for each_msg in msg:
            sleep(0.1)
            fb_send_message(user_id,each_msg)
    

