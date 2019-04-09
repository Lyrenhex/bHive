from microbit import *
import radio

radio.on()
radio.config(group=1)
display.on()
while True:
    recv = radio.receive()
    if recv == "FOO":
        display.on()
        display.scroll("FOO")
