from parliament import Context
from flask import Request
import json
import redis
import os


REDIS_PREFIX = os.environ.get("REDIS_PREFIX", "TEST:")


redis_host = os.environ.get("REDIS_HOST", "localhost")
redis_port = int(os.environ.get("REDIS_PORT", "6379"))
redis_client = redis.Redis(host=redis_host, port=redis_port, db=0)


print(f"Connecting to redis {redis_host}:{redis_port}...", flush=True)
print("Connected:", redis_client.ping())


def get_chat_ids() -> list[int]:
    data = redis_client.get(f"{REDIS_PREFIX}:all") or b"[]"
    return json.loads(data.decode())


def set_chat_ids(ids: list[int]):
    redis_client.set(f"{REDIS_PREFIX}:all", json.dumps(ids))


def get_chat(chat_id: int) -> dict | None:
    data = redis_client.get(f"{REDIS_PREFIX}:id:{chat_id}")
    return data and json.loads(data.decode())


def set_chat(chat_id: int, chat_data: dict):
    redis_client.set(f"{REDIS_PREFIX}:id:{chat_id}", json.dumps(chat_data))


def main(context: Context):
    if "request" not in context.keys():
        return "{}", 200

    req = context.request
    if req.method == "POST":
        # save chat to db
        chat_data = json.loads(req.get_data(as_text=True))
        chat_id = chat_data["id"]
        ids = get_chat_ids()
        if chat_id in ids:
            return "This chat was already added", 409
        ids.append(chat_id)
        set_chat_ids(ids)
        set_chat(chat_id, chat_data)
        return str(chat_id), 200
    elif req.method == "GET":
        chat_id = req.args.get("id")
        if chat_id is None:
            ids = get_chat_ids()
            result = [get_chat(chat_id) for chat_id in ids]
            return result, 200
        chat_data = get_chat(chat_id)
        if chat_data is None:
            return f"No such chat {chat_id}", 404
        return chat_data, 200
