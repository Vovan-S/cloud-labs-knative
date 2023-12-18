from parliament import Context
from flask import Request
import json
import os
import telebot
import requests


bot = telebot.TeleBot(os.environ["TG_TOKEN"])
view_url = os.environ["REDIS_VIEW_URL"]


@bot.message_handler(commands=["start"])
def start_message(message):
    requests.post(
        view_url,
        json={
            "id": message.chat.id,
            "title": message.chat.title,
            "first_name": message.chat.first_name,
            "last_name": message.chat.last_name,
            "username": message.chat.username,
        },
    )
    bot.send_message(
        message.chat.id,
        "Привет! Вы подписались на рассылку полезной информации от деканата!",
    )

bot.infinity_polling()

def main(context: Context):
    return "{}", 200
