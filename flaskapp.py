#dummy program


from flask import Flask, request
from tasks import add
from tasks import fb_messenger_reply
import requests
from tbot.facebook_messenger import get_users_name

from pprint import pprint
flask_app = Flask(__name__)



# print fb_tpobot_access_code





@flask_app.route('/v', methods=['GET'])
def handle_v():
    k = add.delay(23,23)
    res = k.get(timeout=5)
    print res
    return str(res)

@flask_app.route('/messenger/webhook', methods=['GET'])
def handle_verification():
    return request.args['hub.challenge']
@flask_app.route('/messenger/webhook', methods=['POST'])
def handle_incoming_messages():
    data = request.json
    pprint( data)
    for each_entry in data['entry']:
        for each_message in each_entry['messaging']:
            try:
                sender = each_message['sender']['id']
                user_name = get_users_name(sender)

                message = each_message['message']['text']
                fb_messenger_reply.apply_async((sender, "Hello "+ str(user_name[0])+",\n "+ message[::-1]))
            except KeyError:
                pass
    return "ok"
