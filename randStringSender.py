"""
A micro:bit MicroPython implementation of a random string sender for testing's sake.
"""

from microbit import *
import radio

radio.on() 
radio.config() 

while True:
    radio.send("This is a random test message.")
    sleep(500)