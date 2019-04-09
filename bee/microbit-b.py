"""
Worker accepts a space-delimited string sent over BLE radio.
Format: macAddr function param1 param2 ...

Response: [ProcName] [Unique MicroBit ID] [...Responses] 
          err [error code] [error message]
"""

from microbit import *
import machine
import radio

# define constants
GROUP = 1
ALLOWED_FUNCS = [
    "sum",
    "findPrime",
    "addPrime"
]

# set up mac address-based unique id
macAddr = machine.unique_id()
macAddr = '{:02x}{:02x}{:02x}{:02x}'.format(macAddr[0], macAddr[1], macAddr[2], macAddr[3])

# init list of known Prime numbers for this worker
primeNumList = [2,3,5]

# enable BLE and Display
radio.on()
radio.config(group=GROUP)
display.on()

# visual marker for when Microbit is busy computing
def startProcess():
    display.show(Image.SQUARE_SMALL)
def endProcess():
    display.clear()

# Function to send computed function response to Queen, using comms schema
def sendResponse(procName, *responses):
    resp = procName + " " + macAddr
    for val in responses:
        resp += " " + str(val)
    radio.send(resp) 
def sendError(errNum, errMessage):
    radio.send("err " + str(errNum) + " " + str(errMessage))

# Exemplar computation function - sum a and b
def sum(*args):
    if len(args) > 1:
        total = 0
        try:
            for i in args:
                total += int(i)
        except TypeError:
            sendError(1, "Non-integer parameter supplied.")
            return None
        return total
    else:
        sendError(1, "Insufficient number of parameters.")
        return None

def findPrime(TestNum):
    prime = 0
    for i in range(len(primeNumList)):
        remainder = testNum % primeNumList[i]
        if remainder == 0:
            prime += 1
    return prime == 0

def addPrime(newPrime):
    if findPrime(newPrime):
        primeNumList.append(newPrime)

# Main loop
while True:
    # keep polling BLE for data
    recv = radio.receive()
    # if not empty
    if recv is not None:
        # parse the radio data into something useful
        msg = str(recv)
        params = msg.split(" ")
        
        # note that we're gonna be computing now
        startProcess()
        if params[0] == "ping": # ping check -- we're available -- pong!
            radio.send("pong " + macAddr)
        # check that the instruction is intended for us
        elif params[0] == macAddr:
            if (params[1] in locals()) and (params[1] in ALLOWED_FUNCS):
                display.show(len(params[2:]))
                response = locals()[params[1]](*params[2:])
                if response is not None:
                    sendResponse(params[1], response)
        endProcess()
