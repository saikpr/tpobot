import requests
import logging
from .config import push_bullet_token
from .config import push_bullet_url
from .config import push_bullet_group

def push_to_pushbullet(title_text,body_text,forum_url):
    global push_bullet_token
    global push_bullet_url
    global push_bullet_group
    
    ogging.debug("Inside push_to_pushbullet ")
    headers ={
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
              "Access-Token":push_bullet_token,
              "Content-Type": "application/json",
             }
    body ={"body":body_text,"title":title_text,"type":"link","channel_tag":push_bullet_group,"url":forum_url}
    logging.info("Trying To get the forum text page")
    try:
        req = requests.post(push_bullet_url,data=json.dumps(body),headers = headers)
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        return None
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        return None
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        return None
    
    return True