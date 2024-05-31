#include <WiFiNINA.h>
#include <Wire.h>
#include <CCS811.h>
#include "DHT.h"
#include "Secret.h"

#define DHTPIN 7     // Pin connected to the DHT11 sensor
#define DHTTYPE DHT11   // DHT 11

CCS811 sensor;
DHT dht(DHTPIN, DHTTYPE);
const int soundSensorPin = A0;

char ssid[] = SECRET_SSID;        // Your network SSID (name)
char pass[] = SECRET_PASS;        // Your network password
int status = WL_IDLE_STATUS;      // The WiFi radio's status
WiFiClient client;

// Raspberry Pi IP and port
const char* server = "172.20.10.9"; // Use your Raspberry Pi's IP address or hostname
const int serverPort = 5000;          // Port for Flask server

void setup() {
    Serial.begin(115200);
    while (status != WL_CONNECTED) {
        Serial.print("Attempting to connect to WPA SSID: ");
        Serial.println(ssid);
        status = WiFi.begin(ssid, pass);
        delay(10000);
    }
    Serial.println("Connected to WiFi");

    while (sensor.begin() != 0) {
        Serial.println("Failed to init CCS811 sensor, please check if the chip connection is fine");
        delay(1000);
    }
    sensor.setMeasCycle(CCS811::eCycle_250ms);
    dht.begin();
    pinMode(soundSensorPin, INPUT);
}

void loop() {
    delay(1000);
    Serial.println("--------------------------------------------------");
    if (sensor.checkDataReady() == true) {
        int co2 = sensor.getCO2PPM();
        int tvoc = sensor.getTVOCPPB();
        float temp = dht.readTemperature();
        int soundLevel = analogRead(soundSensorPin);

        Serial.print("CO2: ");
        Serial.print(co2);
        Serial.println(" ppm");

        Serial.print("TVOC: ");
        Serial.print(tvoc);
        Serial.println(" ppb");

        if (!isnan(temp)) {
            Serial.print("Temperature: ");
            Serial.print(temp);
            Serial.println(" C");
        } else {
            Serial.println("Failed to read temperature from DHT sensor!");
        }

        Serial.print("Sound Level: ");
        Serial.println(soundLevel);

        if (client.connect(server, serverPort)) {
            String url = "/update?temp=" + String(temp) + "&co2=" + String(co2) + "&tvoc=" + String(tvoc) + "&sound=" + String(soundLevel);
            client.print("GET " + url + " HTTP/1.1\r\n");
            client.print("Host: " + String(server) + "\r\n");
            client.print("Connection: close\r\n\r\n");
            client.stop();
            Serial.println("Data sent to Raspberry Pi");
        } else {
            Serial.println("Failed to connect to Raspberry Pi");
        }
    } else {
        Serial.println("Data is not ready!");
    }
    Serial.println("--------------------------------------------------");

    sensor.writeBaseLine(0x847B);

    delay(1000);
}