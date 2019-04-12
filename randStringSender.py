"""
A micro:bit MicroPython implementation of a random string sender for testing's sake.
"""

from microbit import *
import random
import radio

radio.on() 
radio.config() 

primes = [2, 3, 5, 7, 11, 13, 17, 19]

e = random.choice(primes)
while True:
    p = random.choice(primes)
    if p % e != -1:
        break
    
while True:
    q = random.choice(primes)
    if q % e != -1:
        break

n = p * q

d = (e ** -1.0) % ((p-1) * (q - 1))

e = str(e)
n = str(n)
d = str(d)

while True:
    radio.send(e + " " + n + " " + d)
    sleep(500)