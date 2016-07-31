from celery import Celery
from tbot.config import mongo_db_url
from tbot.config import fb_tpobot_access_code
import requests

CELERY_BROKER = mongo_db_url 
celery_app = Celery(__name__)

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
def add(x, y):
    return x + y

@celery_app.task()
def fb_messenger_reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    try:
    	resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + fb_tpobot_access_code, json=data,headers={"Content-Type": "application/json"})
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        self.retry(countdown=2, exc=e, max_retries=10)
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        self.retry(countdown=2, exc=e, max_retries=10)
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        self.retry(countdown=2, exc=e, max_retries=10)
    