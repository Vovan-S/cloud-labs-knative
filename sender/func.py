from parliament import Context
from flask import Request
import json
import os
import telebot
import requests


bot = telebot.TeleBot(os.environ["TG_TOKEN"])
view_url = os.environ["REDIS_VIEW_URL"]


def get_all_ids() -> list[int]:
    r = requests.get(view_url)
    all_data = r.json()
    return [x["id"] for x in all_data]


def send(chat_id, text):
    bot.send_message(chat_id, text)


def main(context: Context):
    if "request" not in context.keys():
        return "{}", 200
    req = context.request
    if req.method != "POST":
        return "Method not allowed", 405
    data = json.loads(req.get_data(as_text=True))
    message = data["message"]
    all_ids = get_all_ids()
    chat_id = data.get("chat_id")
    if chat_id is None:
        for chat_id in all_ids:
            send(chat_id, message)
        return json.dumps(all_ids), 200
    if chat_id not in all_ids:
        return f"Invalid chat id: {chat_id}", 406
    send(chat_id, message)
    return str(chat_id), 200
