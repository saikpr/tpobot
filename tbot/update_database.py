from bs4 import BeautifulSoup
import requests
import logging
from .config import TPO_url
from .config import TPO_forum_user_id
from .config import TPO_forum_user_passwd
from .config import TPO_top_forum_id
from .config import push_bullet_token,push_bullet_url,push_bullet_group

def forum_direct_login():
    global TPO_url ,TPO_forum_user_passwd ,TPO_forum_user_id
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    url = TPO_url + "/forum/ucp.php?mode=login"
    body_data = "username="+TPO_forum_user_id+"&password="+TPO_forum_user_passwd+"&login=Login"
    try:
        req = requests.post(url,data=body_data,headers=headers)
    except requests.exceptions.Timeout:
        return None
    cookie_list =  req.headers['set-cookie'].split(", ")
    sid_php =  [ each_elem.split("=")[1].split(";")[0] for each_elem in filter(lambda stri: stri[:18]=="iitbhu_phpbb3_sid=", cookie_list) ]
    return sid_php[1]

def get_top_forums_ids(sid_php):
    global TPO_url 
    global TPO_top_forum_id
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    url = TPO_url + "/forum/viewforum.php?f="+str(TPO_top_forum_id)+"&sid="+sid_php

    try:
        req = requests.get(url,headers=headers)
    except requests.exceptions.Timeout:
        return None
    bs = BeautifulSoup(req.text,"html.parser")
    forumtitle = bs.findAll("a",{"class":"forumtitle"})
    # print forumtitle[0]["href"].split("&")
    # print help(forumtitle[0])
    # print forumtitle[0].getText()
    list_of_forum_ids =[(filter(lambda stri: "f=" in stri, each_elem["href"].split("&"))[0].split("=")[1],each_elem.getText()) for each_elem in forumtitle]
    return list_of_forum_ids

def forum_data(sid_php,forum_sub_id):
    global TPO_url 
    global TPO_top_forum_id
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    
    url = TPO_url+"/forum/viewforum.php?f="+str(forum_sub_id)+"&sid="+sid_php
    
    logging.info("Trying url "+ url)
    try:
        req = requests.get(url,headers=headers)
    except requests.exceptions.Timeout:
        return None
    
    bs = BeautifulSoup(req.text,"html.parser")
    forum_ids =bs.findAll("a",{"class":"topictitle"})
    list_of_forum_ids =[filter(lambda stri: stri[:2]=="t=", each_elem["href"].split("&"))[0][2:] for each_elem in forum_ids]
    

    return list_of_forum_ids

def get_forum_text (forum_sub_id,forum_post_id,sid_php):
    global TPO_url 
    global TPO_top_forum_id

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
        "Content-Type": "application/x-www-form-urlencoded",
        }
    url = TPO_url+"/forum/viewtopic.php?f="+str(forum_sub_id)+"&t="+str(forum_post_id)+"&sid="+sid_php
    
    logging.info("Trying url "+ url)
    try:
        req = requests.get(url,headers=headers)
    except requests.exceptions.Timeout:
        return None
    bs = BeautifulSoup(req.text,"html.parser")

    body_text= bs.findAll("div",{"class":"content"})[0]
    title_text= bs.findAll("h3",{"class":"first"})[0]
    
    forum_url = TPO_url+"/forum/viewtopic.php?f="+str(forum_sub_id)+"&t="+str(forum_post_id)
    return title_text.getText(),body_text.getText(),forum_url

def push_to_pushbullet(title_text,body_text,forum_url):
    global push_bullet_token
    global push_bullet_url
    global push_bullet_group
    headers ={
              "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:47.0) Gecko/20100101 Firefox/47.0",
              "Access-Token":push_bullet_token,
              "Content-Type": "application/json",
             }
    body ={"body":body_text,"title":title_text,"type":"link","channel_tag":push_bullet_group,"url":forum_url}
    req = requests.post(push_bullet_url,data=json.dumps(body),headers = headers)
    return True


if __name__ == "__main__":
    sid_php = forum_direct_login()
    k =  get_top_forums_ids(sid_php)
    print k
    for each_elem in k:
        print forum_data(sid_php,each_elem[0])
    print get_forum_text(165,2562,sid_php)