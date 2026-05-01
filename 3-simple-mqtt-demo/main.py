# main.py - Improved WiFi Debugging + MQTT

import network
import time
import machine
from ubinascii import hexlify
from machine import Pin
from neopixel import NeoPixel
from umqttsimple import MQTTClient

# ================== CONFIG ==================
WIFI_SSID = "<Your WiFi Name>"      # ←←← Double-check this
WIFI_PASS = "<Your WiFi Password>"  # ←←← Double-check this

MQTT_BROKER = "<IPv4 address of the broker>"
CLIENT_ID   = "esp32s3_demo_" + hexlify(machine.unique_id()[:4]).decode()
TOPIC       = "esp32/rgb/status"
# ===========================================

np = NeoPixel(Pin(48), 1)

def set_color(r, g, b):
    np[0] = (r, g, b)
    np.write()

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    print("WiFi MAC Address:", wlan.config('mac').hex())
    print(f"Trying to connect to: '{WIFI_SSID}'")
    
    set_color(0, 0, 100)   # Blue = trying
    
    wlan.connect(WIFI_SSID, WIFI_PASS)
    
    for i in range(30):          # Increased timeout
        if wlan.isconnected():
            print("\n✅ WiFi Connected!")
            print("IP Address:", wlan.ifconfig()[0])
            set_color(0, 100, 0)   # Green
            return True
        
        status = wlan.status()
        print(f"Status: {status} | Attempt {i+1}/30", end="\r")
        
        if status == -1:
            print("  → Failed to connect (wrong password?)")
        elif status == -2:
            print("  → No AP found (wrong SSID or out of range?)")
        
        time.sleep(1)
    
    print("\n❌ WiFi Connection Failed!")
    print("Final Status:", wlan.status())
    set_color(255, 0, 0)
    return False

# ===================== MAIN =====================
set_color(100, 100, 0)   # Yellow = booting

print("=== Starting WiFi Connection Test ===")

if not connect_wifi():
    print("🔴 WiFi failed. Check SSID, Password, and signal strength.")
    # Blink red forever
    while True:
        set_color(255, 0, 0)
        time.sleep(0.4)
        set_color(0, 0, 0)
        time.sleep(0.4)

print("Connecting to MQTT...")
client = MQTTClient(CLIENT_ID, MQTT_BROKER, keepalive=60)
client.connect()
print("MQTT Connected!")
set_color(80, 80, 80)

counter = 0

while True:
    try:
        counter += 1
        message = f"ESP32-S3 alive! Count:{counter} IP:192.168.1.13"
        
        client.publish(TOPIC, message)
        
        # Visual heartbeat
        set_color(0, 255, 0)
        time.sleep(0.1)
        set_color(80, 80, 80)
        
        time.sleep(4)          # Publish every ~4-5 seconds
        
    except Exception as e:
        print("Error:", e)
        set_color(255, 0, 0)
        time.sleep(2)
        try:
            client.connect()   # Try reconnect
        except:
            time.sleep(5)
