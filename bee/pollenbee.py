## THIS FILE IS MINIFIED TO KEEP BYTES UNDER 8188. APOLOGIES.
## SEE CLIENT CODE (COMMENTED) IN MB-B.PY

# Function to send computed function response to Queen, using comms schema
def sendResponse(procName, *responses):
    resp = procName + " " + macAddr
    for val in responses:
        resp += " " + str(val)
    radio.send(resp)

# Sends an error
def sendError(errNum, errMessage):
    radio.send("err " + str(errNum) + " " + str(errMessage))

# Holds the worker
def hold(*args):
    heldByQueen = True
    return heldByQueen

# Releases the worker
def release(*args):
    heldByQueen = False
    return heldByQueen

########################
## POLLEN INTERPRETER ##
########################
import math as maths
import operator as ops

### POLLEN ENVIRONMENT VARIABLES ##

# Gets back the standard global environment.
def getStandardEnvironment():
    env = {}
    env.update(vars(maths))
    default_env = {
        '+': ops.add,
        '-': ops.sub,
        '*': ops.mul,
        '/': ops.truediv,
        '%': ops.mod,
        '<': ops.lt,
        '>': ops.gt,
        '<=': ops.le,
        '>=': ops.ge,
        '=': ops.eq,
        'rem': ops.mod,
        'true': True,
        'false': False,
        'abs': abs,
        'append': ops.add,
        'max': max,
        'min': min,
        'not': ops.not_,
        'round': round
    }
    env.update(default_env)

    return env

# Resets the current environment.
env = getStandardEnvironment()
def resetEnv():
    env = getStandardEnvironment()

def getLocalEnv(localDict, globalDict):
    returnEnv = {}
    # For each item, take the global from duplicated vars.
    for item, value in globalDict.items():
        if item not in localDict:
            returnEnv[item] = value
    returnEnv.update(localDict)
    return returnEnv

# A lambda procedure call.
class Procedure(object):
    def __init__(self, params, body, env):
        self.params = params
        self.body = body
        self.env = params, body, env
    def __call__(self, *args):
        # Need to separate global namespace from local namespace.
        local_env =  getLocalEnv(dict(zip(self.params, args)), env)
        return evaluate(self.body, local_env)

# "Atomizes" the given token, to convert from all symbols to numbers and symbols.
def atomize(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

# Evaluates the set of instructions parsed by tokenparse.
Number = (int, float)
def evaluate(instr, currentEnv):
    # Referencing a variable.
    if isinstance(instr, str):
        return currentEnv[instr]
    # Referencing a constant.
    elif isinstance(instr, int):
        return instr
    # A conditional statement.
    elif instr[0]=="if":
        # Check against a tuple, which is made up of the current list.
        (_, test, conseq, alt) = instr
        exp = (conseq if evaluate(test, currentEnv) else alt)
        return evaluate(exp, currentEnv)
    elif instr[0]=="cond":
        # Get a tuple with the required params.
        (_, t, tproc) = instr
        conds = instr[3:]

        # TVAL for checking is equal to cond or cond2.
        val_t = evaluate(t, currentEnv)

        for cond in conds:
            check = (cond[1] if evaluate(cond[0], currentEnv) else None)
            if (check==val_t):
                return evaluate(tproc, currentEnv)
            elif check!=None:
                return check
    # Defines a variable on the current environment.
    elif instr[0]=="def":
        (_, var, exp) = instr
        currentEnv[var] = evaluate(exp, currentEnv)
    # Defining or executing a lambda.
    elif instr[0] == 'lambda':
        (_, params, body) = instr
        return Procedure(params, body, currentEnv)
    elif isinstance(instr, list) and len(instr)==1:
        return evaluate(instr[0], currentEnv)
    else:
        # Existing process that needs to be run. Get process and arguments, then return.
        proc = evaluate(instr[0], currentEnv)
        args = [evaluate(arg, currentEnv) for arg in instr[1:]]
        return proc(*args)

# Tokenizes a given script, returns.
def tokenize(script):
    # Use a char hack to split the string into bracket operations.
    return script.replace('(', ' ( ').replace(')', ' ) ').replace('\n', '').replace('\t', '').strip().split()

# Parses the given set of tokens into instructions.
def tokenparse(tokens):
    # Checking no EOF.
    if len(tokens) == 0:
        return "p_err 0"
    
    # Getting token.
    token = tokens.pop(0)

    # Checking for open bracket.
    if token=="(":
        child = []
        # Only go until end bracket.
        while tokens[0] != ")":
            child.append(tokenparse(tokens))
        # Pop off the end ")".
        tokens.pop(0)
        return child
    elif token==")":
        return "p_err 1"
    else:
        return atomize(token)


def parsePollenLine(script):
    # Tokenizing the pollen script.
    tokens = tokenize(script)
    print(tokens)

    # Parsing the tokens.
    parsed = tokenparse(tokens)

    # Evaluating the tokens.
    return evaluate(parsed, env)

def execPollen(*script):
    return parsePollen(" ".join(script))

def parsePollen(script):
    # Removing junk from start and end.
    for char in script:
        if char!="\n" and char!=" ":
            break
        script = script.replace(char, "", 1)
    for char in reversed(script):
        if char!="\n" and char!=" ":
            break
        script = script[:-1]

    # Splitting string by ";".
    lines = script.split(";")
    for index, line in enumerate(lines):
        lines[index] = line.replace("\n", "")
        if line=="" or line.count(" ") == len(line):
            lines.remove(line)
        elif line[0]=="#":
            lines.remove(line)

    # Executing all lines apart from last.
    nonReturnLines = lines[:-1]
    for line in nonReturnLines:
        parsePollenLine(line)
    
    # Returning last.
    return parsePollenLine(lines[-1])

#### END POLLEN INTERPRETER ####

from microbit import *
import machine
import random
import radio

GROUP = 1
ALLOWED_FUNCS = [
    "sum",
    "testPrime",
    "release",
    "hold",
    "spyRSA",
    "getNFactor_RSA",
    "getD_RSA",
    "execPollen"
]

macAddr = machine.unique_id()
macAddr = '{:02x}{:02x}{:02x}{:02x}'.format(macAddr[0], macAddr[1], macAddr[2], macAddr[3])
heldByQueen = False

primeNumList = []

def resetRadio():
    radio.on()
    radio.config(channel=7, group=GROUP)
resetRadio()
display.on()


def startProcess():
    display.show(Image.SQUARE_SMALL)
def endProcess():
    display.clear()

while True:
    if heldByQueen:
        display.show("H")
    else:
        display.clear()
    recv = radio.receive()
    if recv is not None:
        params = str(recv).split(" ")
        if params[0] == "ping":
            if not heldByQueen:
                radio.send("pong " + macAddr)
        elif params[0] == macAddr:
            if (params[1] in locals()) and (params[1] in ALLOWED_FUNCS):
                startProcess()
                response = locals()[params[1]](*params[2:])
                endProcess()
                if response is not None:
                    if type(response) is tuple or type(response) is list:
                        response = [str(item) for item in response]
                        response = " ".join(response)
                    sendResponse(params[1], response)
            else:
                sendError(2, "Invalid function '" + params[1] + "'")