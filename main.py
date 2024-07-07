from urequests import post


class ubot:
    def __init__(self):
        self.url = "https://api.telegram.org/bot<YOUR_BOT_TOKEN>"
        self.commands = {}
        self.default_handler = None
        self.message_offset = 0
        self.sleep_btw_updates = 3

        messages = self.read_messages()
        if messages:
            if self.message_offset == 0:
                self.message_offset = messages[-1]["update_id"]
            else:
                for message in messages:
                    if message["update_id"] >= self.message_offset:
                        self.message_offset = message["update_id"]
                        break

    def send(self, chat_id, text):
        data = {"chat_id": chat_id, "text": text}
        try:
            headers = {"Content-type": "application/json", "Accept": "text/plain"}
            response = post(self.url + "/sendMessage", json=data, headers=headers)
            response.close()
            return True
        except Exception as e:
            print(e)
            return False

    def read_messages(self):
        result = []
        self.query_updates = {
            "offset": self.message_offset + 1,
            "limit": 1,
            "timeout": 30,
            "allowed_updates": ["message"],
        }

        try:
            update_messages = post(
                self.url + "/getUpdates", json=self.query_updates
            ).json()
            if "result" in update_messages:
                for item in update_messages["result"]:
                    result.append(item)
            return result
        except ValueError:
            return None
        except OSError:
            print("OSError: request timed out")
            return None

    def listen(self):
        import gc
        import time

        print("Bot is listening")

        while True:
            self.read_once()
            time.sleep(self.sleep_btw_updates)
            gc.collect()

    def read_once(self):
        messages = self.read_messages()
        if messages:
            print("Messages received")
            if self.message_offset == 0:
                self.message_offset = messages[-1]["update_id"]
                self.message_handler(messages[-1])
            else:
                for message in messages:
                    if message["update_id"] >= self.message_offset:
                        self.message_offset = message["update_id"]
                        self.message_handler(message)
                        break

    def register(self, command, handler):
        self.commands[command] = handler

    def message_handler(self, message):
        allowed_user = 79138823
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
        self.commands["/wol"](message)


def reply_wol(message):
    import socket

    print("Sending Magic Packet")
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, 0x20, 1)
        sock.connect(("<YOUR_BROADCAST_IP>", 9))
        sock.send(bytes.fromhex("F" * 12 + "<YOUR_MAC_ADDRESS>" * 16))
        print("Magic Packet sent!")
    except Exception as e:
        print(e)
    finally:
        sock.close()

    bot.send(message["message"]["chat"]["id"], "Magic Packet sent!")


bot = ubot()
bot.register("/wol", reply_wol)
bot.listen()
