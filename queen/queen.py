from microbit import *
import radio
import ujson

class Command():
    def __init__(self, function, *arg):
        self.function = function
        self.args = arg
    

display.on()
radio.on()
radio.config(group=1)
while True:
    radio.send("sum 2 9")
    display.scroll("EPIC")