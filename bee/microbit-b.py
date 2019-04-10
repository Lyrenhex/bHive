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
    "testPrime",
    "release",
    "hold"
]

# set up mac address-based unique id
macAddr = machine.unique_id()
macAddr = '{:02x}{:02x}{:02x}{:02x}'.format(macAddr[0], macAddr[1], macAddr[2], macAddr[3])

# flag denoting whether the worker is currently working for a queen or has been released and is available to pings
heldByQueen = False

# init list of known Prime numbers for this worker
primeNumList = []

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

def hold(*args):
    heldByQueen = True
    return heldByQueen
def release(*args):
    heldByQueen = False
    return heldByQueen

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

# Tests testNum based on prime factorisation
# If any Prime is a factor, then the number is not
# a Prime number, so we return False. Else, True.
def testPrime(*testNums):
    testNum = testNums[0]
    primeNumList = testNums[1:]
    for prime in primeNumList:
        # if mod prime = 0, we aren't a Prime
        if (testNum % prime) == 0:
            return False
    return True

# Main loop
while True:
    # keep polling BLE for data
    recv = radio.receive()
    # if not empty
    if recv is not None:
        # parse the radio data into something useful
        params = str(recv).split(" ")
                
        if params[0] == "ping": # queen looking for available workers
            if not heldByQueen:
                radio.send("pong " + macAddr) # let them know we're free and our unique ID for future interaction
        # check that the instruction is intended for us
        elif params[0] == macAddr:
            if (params[1] in locals()) and (params[1] in ALLOWED_FUNCS):
                # compute the task requested (and note that we're busy and haven't broken)
                startProcess()
                response = locals()[params[1]](*params[2:])
                endProcess()

                # if something goes wrong (error, etc), all computations should return None. DO NOT SEND RESULT TO SERVER IF RESULT IS NONE
                if response is not None:
                    sendResponse(params[1], response)
            else:
                sendError(2, "Invalid function '" + params[1] + "'")
