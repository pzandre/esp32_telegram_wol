import network

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
if not wlan.isconnected():
    print("connecting to network...")
    wlan.connect("<YOUR-SSID>", "<YOUR-PASSWORD>")
    while not wlan.isconnected():
        pass
print("connected")
