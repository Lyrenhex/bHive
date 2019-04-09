"""
Worker accepts a space-delimited string sent over BLE radio.
Format: function param1 param2 ...

Response: "ERROR"|"SUCCESS" respVal
"""

from microbit import *
import machine
import radio

# define constants
GROUP = 1

macAddr = machine.unique_id()
macAddr = '{:02x}{:02x}{:02x}{:02x}'.format(macAddr[0], macAddr[1], macAddr[2], macAddr[3])

radio.on()
radio.config(group=GROUP)
display.on()

def sum(a, b):
    a = int(a)
    b = int(b)
    return a + b

while True:
    recv = radio.receive()
    if recv is not None:
        msg = str(recv)
        params = msg.split(" ")
        if params[0] == "ping": # ping check -- we're available -- pong!
            radio.send("pong " + macAddr)
        elif params[1] == "sum":
            if params[0] == macAddr:
                display.scroll(sum(params[2], params[3]))

primeNumList = [2,3,5]
testNum = 3

def findPrime(TestNum):
    prime = 0
    for i in range(0, len(primeNumList)):
        remainder = testNum % (primeNumList[i])
        if remainder == 0:
            prime += 1
    if prime == 0:
        primeTrue = True
    else:
        primeTrue = False
    return primeTrue

def addPrime(newPrime):
    primeNumList.append(newPrime)

primeTrue = findPrime(testNum)
addPrime(testNum)

print(primeTrue)
