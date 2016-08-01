import requests
from .config import fb_tpobot_access_code
from .config import  persistent_button_settings
from .facebook_messenger import check_access_code
from .config import register_access_code
from .config import  db_tpobot

def fb_persistent_button(persistent_button_settings):
    
    try:
        resp = requests.post("https://graph.facebook.com/v2.6/me/thread_settings?access_token=" + fb_tpobot_access_code, json=persistent_button_settings,headers={"Content-Type": "application/json"})
        print resp.text
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        self.retry(countdown=2, exc=e, max_retries=10)
        return False
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        self.retry(countdown=2, exc=e, max_retries=10)
        return False
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        self.retry(countdown=2, exc=e, max_retries=10)
        return False
    return True

def push_access_code(access_code):
    if not access_code:
        return False
    t =  check_access_code(access_code)
    if not t:
        db_tpobot.fb_access_codes.insert_one({"access_code":access_code,"isvalid":True})
    
    return True

if fb_persistent_button(persistent_button_settings):
    print "persistent button set"
if push_access_code(register_access_code):
    print "Access Code Added to DB or Already Present"

    print __name__