#dummy program


from flask import Flask, request
from tbot.config import fb_tpobot_access_code
import requests

from pprint import pprint
app = Flask(__name__)

# print fb_tpobot_access_code
def reply(user_id, msg):
    data = {
        "recipient": {"id": user_id},
        "message": {"text": msg}
    }
    resp = requests.post("https://graph.facebook.com/v2.6/me/messages?access_token=" + fb_tpobot_access_code, json=data)
    print(resp.content)
@app.route('/', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']

@app.route('/', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    pprint( data)
    for each_entry in data['entry']:
        for each_message in each_entry['messaging']:
            try:
                sender = each_message['sender']['id']
                message = each_message['message']['text']
                reply(sender, message[::-1])
            except KeyError:
                pass
    return "ok"
