from urequests import post

URL = "https://api.telegram.org/bot<YOUR_BOT_TOKEN>"
DEFAULT_HANDLER = None
MESSAGE_OFFSET = 0
SLEEP_BTW_UPDATES = 3


def send(chat_id, text):
    data = {"chat_id": chat_id, "text": text}
    try:
        headers = {"Content-type": "application/json", "Accept": "text/plain"}
        response = post(URL + "/sendMessage", json=data, headers=headers)
        response.close()
        return True
    except Exception as e:
        print(e)
        return False


def reply_wol(message):
    import socket

    print("Sending Magic Packet")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, 0x20, 1)
        sock.connect(("<BROADCAST_IP>", 9))
        sock.send(bytes.fromhex("F" * 12 + "<TARGET_MAC_ADDRESS>" * 16))
        print("Magic Packet sent!")
    except Exception as e:
        print(e)
    finally:
        sock.close()

    send(message["message"]["chat"]["id"], "Magic Packet sent!")


COMMANDS = {"/wol": reply_wol}


def read_messages():
    result = []
    query_updates = {
        "offset": MESSAGE_OFFSET + 1,
        "limit": 1,
        "timeout": 30,
        "allowed_updates": ["message"],
    }

    try:
        update_messages = post(URL + "/getUpdates", json=query_updates).json()
        if "result" in update_messages:
            for item in update_messages["result"]:
                result.append(item)
        return result
    except ValueError:
        return None
    except OSError:
        print("OSError: request timed out")
        return None


def message_handler(message):
    allowed_user = 0  # Your user id
    user_id = None
    try:
        user_id = message["message"]["from"]["id"]
    except KeyError:
        pass
    if user_id is None:
        try:
            user_id = message["chat"]["id"]
        except KeyError:
            print("No user id found")
            return
    if user_id != allowed_user:
        return
    if "text" not in message["message"]:
        return
    action = message["message"]["text"][:4]
    if action != "/wol":
        return
    COMMANDS["/wol"](message)


def read_once():
    global MESSAGE_OFFSET
    messages = read_messages()
    if messages:
        print("Messages received")
        if MESSAGE_OFFSET == 0:
            MESSAGE_OFFSET = messages[-1]["update_id"]
            message_handler(messages[-1])
        else:
            for message in messages:
                if message["update_id"] >= MESSAGE_OFFSET:
                    MESSAGE_OFFSET = message["update_id"]
                    message_handler(message)
                    break


def listen():
    import gc
    import time

    print("Bot is listening")

    while True:
        read_once()
        time.sleep(SLEEP_BTW_UPDATES)
        gc.collect()


listen()
