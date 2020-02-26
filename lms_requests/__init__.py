import telebot
from flask import Flask, request
from lms_requests.globals import bot_token, bot, heroku_url

app = Flask(__name__)


@app.route('/' + bot_token, methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode('utf-8'))])
    return 'Ok'


@app.route('/')
def set_web_hook():
    bot.remove_webhook()
    bot.set_webhook(url=heroku_url + bot_token)
