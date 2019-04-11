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
        'abs': abs,
        'append': ops.add,
        'max': max,
        'min': min,
        'not': ops.not_,
        'round': round
    }
    env.update(default_env)

    return env

# Initializes the current Pollen standard library.
def initStdLib():
    parsePollen(
        """
        """
    )

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

# Evaluates the set of instructions parsed by tokenparse.
Number = (int, float)
def evaluate(instr, currentEnv):
    # Referencing a variable.
    if isinstance(instr, str):
        return currentEnv[instr]
    # Referencing a constant.
    elif isinstance(instr, Number):
        return instr
    # A conditional statement.
    elif instr[0]=="if":
        # Check against a tuple, which is made up of the current list.
        (_, test, conseq, alt) = instr
        exp = (conseq if evaluate(test, currentEnv) else alt)
        return evaluate(exp, currentEnv)
    # Defines a variable on the current environment.
    elif instr[0]=="def":
        (_, var, exp) = instr
        currentEnv[var] = evaluate(exp, currentEnv)
    # Defining or executing a lambda.
    elif instr[0] == 'lambda':
        (_, params, body) = instr
        return Procedure(params, body, currentEnv)
    else:
        # Existing process that needs to be run. Get process and arguments, then return.
        proc = evaluate(instr[0], currentEnv)
        args = [evaluate(arg, currentEnv) for arg in instr[1:]]
        return proc(*args)

# Tokenizes a given script, returns.
def tokenize(script):
    # Use a char hack to split the string into bracket operations.
    return script.replace('(', ' ( ').replace(')', ' ) ').replace('\n', '').replace('\t', '').strip().split()

# "Atomizes" the given token, to convert from all symbols to numbers and symbols.
def atomize(token):
    try:
        return int(token)
    except ValueError:
        try:
            return float(token)
        except ValueError:
            return token

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

    # Parsing the tokens.
    parsed = tokenparse(tokens)

    # Evaluating the tokens.
    return evaluate(parsed, env)

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

    # Remove any lines beginning with comment characters.
    # Removing all \ns from lines, deleting blank ones.
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

print(parsePollen("""
# You gotta end comments with a semi;
(def square (lambda (x) (* x x)));
(def mod_sq (lambda (x y) (% (square x) y)));
(mod_sq 4 5);
"""))

#### END POLLEN INTERPRETER ####