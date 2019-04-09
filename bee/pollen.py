########################
## POLLEN INTERPRETER ##
########################

# GLOBAL POLLEN PROPERTIES
# Characters which are to be classed as individual tokens.
iTokenCharacters = ["+", "-", "*", "/", "(", ")", "[", "]", ";", ",", "{", "}", " "]
# Characters which are to be skipped when parsing.
skipCharacters = []
# Tokens which are used as a command.
commandTokens = ["return", "func"]
# User-defined functions.
functions = []

# Action types:
# 0: Add/take
# 1: Multiply/divide
# 2: Function
# 3: Comparison

# State types:
# default: The state the interpreter starts in. No special action.
# funcDefine: Defining a function.
# - funcDefineParams: Defining params in a function.


class Action:
    def __init__(self, actionType, actionValue):
        self.actionType = actionType
        self.actionValue = actionValue

class Function:
    def __init__(self, *funcParams, funcStartPos, funcEndPos, name):
        self.funcParams = funcParams
        self.funcStartPos = funcStartPos
        self.funcEndPos = funcEndPos
        self.name = name

# Tokenizes a given script, returns.
def tokenize(script):
    # Split the string up into tokens.
    tokens = []
    token = ""
    for char in script:
        # Check against token characters here. If individual token, add and reset.
        if char in iTokenCharacters:
            if token != "" and token != " ":
                tokens.append(token)
            if char != " ":
                tokens.append(char)
            token = ""
        elif char not in skipCharacters:
            token += char
    return tokens

# Defines a function.
def defineFunc(tokens, startIndex):
    params = []

    #Finding the start of a bracket, adding params.
    startIndexDelta = -1
    inParams = False
    for token in tokens:
        if token=="(":
            #Start params.
            inParams = True
        if token==")":
            startIndexDelta = tokens.index(token) + 2
            #End params.
            break
        if inParams==True:
            params.append(token)
    
    #Checking start delta has ben found.
    if startIndexDelta==-1:
        return "p_err 1"

    #Finding the end of the func.
    startIndex += startIndexDelta
    endIndex = -1
    for token in tokens:
        if token=="}":
            endIndex = startIndex + tokens.index(token)
    
    #Checking end has been found.
    if endIndex == -1:
        return "p_err 2"

    #Returning func.
    return Function(params, startIndex, endIndex, tokens[0])


# Lexes a set of tokens into actions.
def lex(tokens):
    actionList = []
    state = "default"

    for token in tokens:
        #Default state checks.
        if state=="default":
            if token in iTokenCharacters and token!=";":
                #Calculation where there shouldn't be.
                return "p_err 0"
            elif (token=="func"):
                state = "funcDefine"
        #Currently defining a function.
        if state=="funcDefine":
            #Define elsewhere.
            index = tokens.index(token)
            func = defineFunc(token[index:], index)

            #Errored in func call.
            if type(func) is str:
                return func
            else:
                functions.append(func)

    print("bleh")
    #Return the list.
    return actionList

# Parses a given pollen script as a string.
def parsePollen(script):
    #Tokenizing.
    tokens = tokenize(script)
    print(tokens)

    #Lexing into action list.
    actionList = lex(tokens)
    # If string returned, error in lexing.
    if type(actionList) == str:
        return actionList


print(parsePollen(
    "func b() { }"
))

#### END POLLEN INTERPRETER ####