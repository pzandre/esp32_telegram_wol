# ESP32 WoL via Telegram

The Micropython Telegram code was forked from [Jordi Prats MicroPython UTelegram repository](https://github.com/jordiprats/micropython-utelegram) and later modified.

This is an oversimplified way to send WoL packages over a Telegram Bot. Notice that I've built this only for personal use and with a single use in mind, therefore things such as using multiple targets are not available, but can be accomplished by simply changing some functions to use parameters instead of hardcoded values.

There's a C++ and a MicroPython version of the code.

## Setting up

### MicroPython

1) Make sure to [flash the latest MicroPython firmware to your board](https://docs.micropython.org/en/latest/esp32/tutorial/intro.html).
2) You can use [AMPY](https://pypi.org/project/adafruit-ampy/) to deploy the Python files to your board.
3) To simplify serial monitoring, you can use [Arduino IDE](https://www.arduino.cc/en/software).

### C++ (Arduino)

Use [Arduino IDE](https://www.arduino.cc/en/software).

### Telegram Bot

Use the [official quickstart guide](https://core.telegram.org/bots/tutorial) to learn Bot creation process, configurations and basic interactions.

### Telegram Chat ID

To avoid other people triggering your WoL setup, it's necessary to get your Telegram Chat ID. While there are numerous bots that can get this ID for you, I recommend using the board serial monitor to log a message sent from your profile.

### Other necessary data

- SSID -> Your wifi name
- Wifi Password
- Broadcast IP -> Usually 255.255.255.255
- Target MAC Address -> remove the ":" from it (e.g.: "aa126400ffee")
