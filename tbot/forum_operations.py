from bs4 import BeautifulSoup
import requests
import logging
from HTMLParser import HTMLParseError
from .config import TPO_url #TPO URL
from .config import TPO_forum_user_id #FORUM User Name
from .config import TPO_forum_user_passwd
from .config import TPO_top_forum_id #TPO Forum, top most 3 in this case
from .config import push_bullet_token
from .config import push_bullet_url
from .config import push_bullet_group

def forum_direct_login():
    """To Login into the forum, using username and password"""
    logging.debug("Inside forum_direct_login")
    
    global TPO_url ,TPO_forum_user_passwd ,TPO_forum_user_id
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    
    #URL for TPO Forum
    url = TPO_url + "/forum/ucp.php?mode=login"
    logging.info("URL For Login : "+url)
    #Request Body
    body_data = "username="  + TPO_forum_user_id +"&password=" + TPO_forum_user_passwd + "&login=Login"
    logging.info("Trying To Login")
    try:
        req = requests.post(url,data=body_data,headers=headers)
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        return None
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        return None
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        return None
    
    logging.info("Request was successful, now trying to extract cookie")
    try:
        cookie_list =  req.headers['set-cookie'].split(", ")
    except KeyError:
        logging.error("Unable to extract cookie from the request ")


    sid_php_possible_keys_with_body = filter(lambda stri: stri[:18]=="iitbhu_phpbb3_sid=", cookie_list)
    
    sid_php =  [ each_elem.split("=")[1].split(";")[0] for each_elem in  sid_php_possible_keys_with_body ]
    
    try:
        return sid_php[1]
    except KeyError:
        logging.error("Second Sid missing")
        return None

def check_valid_sid(sid_php):
    """To check if previous login is valid"""
    logging.debug("Inside check_valid_sid")
    if not sid_php :
        logging.error("Authetication cookienot found, shouldnt have reached here")
        return None
    global TPO_url 
    global TPO_top_forum_id

    url = TPO_url + "/forum/viewforum.php?f=" + str(TPO_top_forum_id) +  "&sid=" + sid_php
    logging.info("URL For checking : "+url)
    logging.info("Trying To get the forum page")
    try:
        req = requests.get(url,headers=headers)
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        return False
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        return False
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        return False
    logging.info("Request was successful, valid sid_php")

    return True

    
def get_top_forums_ids(sid_php):
    """To extract forum_ids from the top forum page, as of time it contains Session information"""
    logging.debug("Inside get_top_forums_ids")

    if not sid_php :
        logging.error("Authetication cookienot found, shouldnt have reached here")
        return None

    global TPO_url 
    global TPO_top_forum_id
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    #URL for TPO Forum

    url = TPO_url + "/forum/viewforum.php?f=" + str(TPO_top_forum_id) +  "&sid=" + sid_php
    logging.info("URL For geting forumids : "+url)


    logging.info("Trying To get the forum page")
    try:
        req = requests.get(url,headers=headers)
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        return None
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        return None
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        return None
    

    logging.info("Request was successful, valid sid_php")

    try: 
        bs = BeautifulSoup(req.text,"html.parser")
    except HTMLParseError as e:
        logging.error("HTML Parse Error"+str(e))
        return None

    logging.info("Trying to extract class 'forumtitle'")

    forumtitle = bs.findAll("a",{"class":"forumtitle"})
    # print forumtitle[0]["href"].split("&")
    # print help(forumtitle[0])
    # print forumtitle[0].getText()
    if not forumtitle :
        logging.error("Unable to get forumtitle from the request ")
        return None
    list_of_forum_ids = list()
    logging.info("Trying to extract forum|_id and title")
    for each_elem in forumtitle:
        temp = each_elem["href"].split("&") #[u'./viewforum.php?f=164', u'sid=e4510f7b1f060a9cd4c06e3755768b16']
        forum_url_extract = temp[0] # u'./viewforum.php?f=164'
        forum_url_extract = forum_url_extract.split("=")[1] #164
        forum_title =  each_elem.getText() #Session 2015-16
        logging.debug("Extracted "+str((forum_url_extract,forum_title)))
        list_of_forum_ids.append((forum_url_extract,forum_title))
    
    return list_of_forum_ids

def forum_post_ids(sid_php,forum_sub_id):
    global TPO_url 
    global TPO_top_forum_id
    
    if not sid_php :
        logging.error("Authetication cookienot found, shouldnt have reached here")
        return None

    logging.debug("Inside forum_data checking for : "+str(forum_sub_id))
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    list_of_forum_ids = None
    for start_forum in xrange(0,1000,25):
        url = TPO_url+"/forum/viewforum.php?f="+str(forum_sub_id)+"&sid="+sid_php+"&start="+str(start_forum)
        logging.info("URL For forum_sub_id : "+url)


        logging.info("Trying To get the internal forum page")
        try:
            req = requests.get(url,headers=headers)
        except requests.exceptions.Timeout:
            logging.error("Request Timed Out, maybe server is busy")
            return list_of_forum_ids
        except requests.exceptions.HTTPError as ee:
            logging.error("HTTPError Raise : " + str(ee))
            return list_of_forum_ids
        except requests.exceptions.RequestException as e:
            logging.error("RequestException : Something very terrible : "+str(e))
            return list_of_forum_ids

        
        try: 
            bs = BeautifulSoup(req.text,"html.parser")
        except HTMLParseError as e:
            logging.error("HTML Parse Error"+str(e))
            return list_of_forum_ids
        
        forum_ids =bs.findAll("a",{"class":"topictitle"})
        
        if not forum_ids :
            logging.error("Unable to forum_ids from the request ")
            return list_of_forum_ids
        if not list_of_forum_ids:
            list_of_forum_ids = list()
        for each_elem in forum_ids:
            temp = each_elem["href"].split("&") #[u'./viewtopic.php?f=165', u't=2558', u'sid=8e33e46ff9acbf94ad8e3daf710b77ff']
            temp =temp[1] #'t=2558'
            temp = temp [2:] #'2558'
            if temp not in list_of_forum_ids:
                list_of_forum_ids.append(temp)
            else:
                return list_of_forum_ids

        # list_of_forum_ids =[filter(lambda stri: stri[:2]=="t=", )[0][2:] for each_elem in forum_ids]
        

    return list_of_forum_ids

def get_forum_text (sid_php, forum_sub_id,forum_post_id):
    global TPO_url 
    global TPO_top_forum_id
    logging.debug("Inside forum_data checking for : "+str(forum_sub_id) +" : "+ str(forum_post_id))
    
    if not sid_php :
        logging.error("Authetication cookienot found, shouldnt have reached here")
        return None
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    url = TPO_url+"/forum/viewtopic.php?f="+str(forum_sub_id)+"&t="+str(forum_post_id)+"&sid="+sid_php
    
    logging.info("URL For forum_post_id : "+url)


    logging.info("Trying To get the forum text page")
    try:
        req = requests.get(url,headers=headers)
    except requests.exceptions.Timeout:
        logging.error("Request Timed Out, maybe server is busy")
        return None
    except requests.exceptions.HTTPError as ee:
        logging.error("HTTPError Raise : " + str(ee))
        return None
    except requests.exceptions.RequestException as e:
        logging.error("RequestException : Something very terrible : "+str(e))
        return None
    try: 
        bs = BeautifulSoup(req.text,"html.parser")
    except HTMLParseError as e:
        logging.error("HTML Parse Error"+str(e))
        return None

    try:
        body_text= bs.findAll("div",{"class":"content"})[0]
        title_text= bs.findAll("h3",{"class":"first"})[0]
    except IndexError:
        logging.error("Post doesnot exist")
        return None

    if not body_text  or not title_text:
        logging.error("Unable to body_text or title_text from the request ")
        return None
    
    forum_url = TPO_url+"/forum/viewtopic.php?f="+str(forum_sub_id)+"&t="+str(forum_post_id)
    return title_text.getText(),body_text.getText(),forum_url




if __name__ == "__main__":
    sid_php = forum_direct_login()
    k =  get_top_forums_ids(sid_php)
    print k
    print forum_post_ids(sid_php,k[0][0])
    # for each_elem in k:
    #     print forum_data(sid_php,each_elem[0])
    print get_forum_text(sid_php,165,2562)