#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "<YOUR_SSID>";
const char* password = "<YOUR_WIFI_PASSWORD>";
const String botToken = "<YOUR_TELEGRAM_BOT_TOKEN>";
const String chatID = "<YOUR_TELEGRAM_CHAT_ID>";
const String telegramApiUrl = "https://api.telegram.org/bot" + botToken;
unsigned long messageOffset = 0;
const int sleepBetweenUpdates = 3000;

const char* broadcastIp = "<YOUR_BROADCAST_IP>";
const char* macAddress = "<YOUR_MAC_ADDRESS>";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }

  Serial.println("Connected to WiFi");
}

void loop() {
  readOnce();
  delay(sleepBetweenUpdates);
}

void sendMessage(const String& chatId, const String& text) {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = telegramApiUrl + "/sendMessage";
    http.begin(url);
    http.addHeader("Content-Type", "application/json");

    JsonDocument jsonDoc;
    jsonDoc["chat_id"] = chatId;
    jsonDoc["text"] = text;

    String jsonStr;
    serializeJson(jsonDoc, jsonStr);

    int httpResponseCode = http.POST(jsonStr);
    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(response);
    } else {
      Serial.println("Error on sending POST: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void sendMagicPacket() {
  Serial.println("Sending Magic Packet");
  WiFiUDP udp;
  udp.beginPacket(broadcastIp, 9);
  byte packet[102];

  for (int i = 0; i < 6; i++) {
    packet[i] = 0xFF;
  }

  for (int i = 1; i <= 16; i++) {
    for (int j = 0; j < 6; j++) {
      char mac_byte[3] = { macAddress[j * 2], macAddress[j * 2 + 1], '\0' };
      packet[i * 6 + j] = strtol(mac_byte, NULL, 16);
    }
  }

  udp.write(packet, sizeof(packet));
  udp.endPacket();
  Serial.println("Magic Packet sent!");
}

void readOnce() {
  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    String url = telegramApiUrl + "/getUpdates?offset=" + String(messageOffset + 1);
    http.begin(url);
    int httpResponseCode = http.GET();

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.println(response);

      JsonDocument doc;
      DeserializationError error = deserializeJson(doc, response);

      if (error) {
        Serial.println("Failed to parse response");
        return;
      }

      JsonArray results = doc["result"].as<JsonArray>();
      for (JsonObject result : results) {
        messageOffset = result["update_id"].as<unsigned long>();
        handleMessage(result);
      }
    } else {
      Serial.println("Error on sending GET: " + String(httpResponseCode));
    }

    http.end();
  } else {
    Serial.println("WiFi not connected");
  }
}

void handleMessage(JsonObject message) {
  if (!message.containsKey("message")) return;

  JsonObject msg = message["message"];
  if (!msg.containsKey("from")) return;
  if (!msg["from"].containsKey("id")) return;

  long userId = msg["from"]["id"].as<long>();
  if (userId != chatID.toInt()) return;

  if (!msg.containsKey("text")) return;
  String text = msg["text"].as<String>();

  if (text.startsWith("/wol")) {
    sendMagicPacket();
    sendMessage(chatID, "Magic Packet sent!\n\nBroadcast IP: " + String(broadcastIp) + "\nMAC Address: " + String(macAddress) + "\nMessage ID: " + String(messageOffset));
  }
}
