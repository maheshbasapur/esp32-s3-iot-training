from machine import Pin
from neopixel import NeoPixel
from time import sleep

print(f"Srating RGB program")

np = NeoPixel(Pin(48), 1)  # Onboard RGB LED

colors = [(255,0,0), (0,255,0), (0,0,255),
          (255,255,0), (255,0,255), (0,255,255)]

while True:
    for color in colors:
        np[0] = color
        np.write()
        sleep(0.5)