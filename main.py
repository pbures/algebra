from optparse import OptionParser
import random
from playsound import playsound
import time
import msvcrt
import time
import sys
import enum
import re


def match_range(range_string):
    z = re.match(r'([0-9]+)\.\.([0-9]+)', range_string)
    a1 = int(z.group(1))
    a2 = int(z.group(2))
    return (a1, a2)

class TimeoutExpired(Exception):
    pass

class Operation(enum.Enum):
    Addition = 'a'
    Subtraction = 's'
    Multiplication = 'm'
    Division = 'd'

print("Hello")

parser = OptionParser(usage="nasobeni.py [-a <num..num>] [-b <num..num>] [-o <operations>] [-t <timeout secs>] [-h] [-g] ")
parser.add_option("-t", "--timeout", dest="timeout", type="int", default=60*60, help = "TIMEOUT is number of seconds. If not provided, 3600 is taken as default.")
parser.add_option("-a", dest="a", type="string", default="1..9", help="A is a range provided as min..max where min and max are integers, default is 1..9. Example: -a 10..95")
parser.add_option("-b", dest="b", type="string", default="1..9", help="B is a range provided as min..max where min and max are integers, default is 1..9. Example: -b 10..95")
parser.add_option("-o", "--operations", dest="operations", type="string", default="asmd",
    help="OPERATIONS is a string containing letters a, s, m, d with a meaning of addition, subtraction, multiplication, division. Default is asdm. Example: -o asd"
)
parser.add_option("-g", "--gamemode", dest="gamemode", action="store_true", default=False, help="If specified, the timeout is decreased when good answers are provided")

(options, args) = parser.parse_args()
rangea = match_range(options.a) if options.a else (1,9)
rangeb = match_range(options.b) if options.b else (1,9)

timeout = options.timeout
good=0
bad=0
best_timeout = timeout
strike_count=0
# speed up after this number of consecutive good answers
speed_up_threshold=2
gamemode = options.gamemode

def get_operation(allowed_operations):
    while True:
        op = ['a','s','m','d'][random.randint(0,3)]
        if op in allowed_operations:
            return Operation(op)

# This is still causing trouble, backspace does not work
def input_with_timeout(prompt, timeout, timer=time.monotonic):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
            if result[-1] == '\r':   #XXX check what Windows returns here
                return ''.join(result[:-1])
        time.sleep(0.04) # just to yield to other processes/threads
    raise TimeoutExpired

def playwtf():
    playsound(("wav/wtf%i.wav") % random.randint(1,3))

def playok():
    playsound(("wav/ok%i.wav") % random.randint(1,3))

def playslow():
    playsound(("wav/slow%i.wav") % random.randint(1,2))

while True:

    operation = get_operation(options.operations)
    r1 = random.randint(rangea[0], rangea[1])
    r2 = random.randint(rangeb[0], rangeb[1])
    r3 = 0

    a = 0
    b = 0
    c = 0
    op_string = ""

    if operation == Operation.Addition:
        (a,b,c) = (r1, r2, r1 + r2)
        op_string = "+"
    elif operation == Operation.Subtraction:
        (a,b,c) = (r1, r2, r1 - r2) if r1 >= r2 else (r2, r1, r2 - r1)
        op_string = "-"
    elif operation == Operation.Multiplication:
        (a,b,c) = (r1, r2, r1 * r2)
        op_string = "*"
    elif operation == Operation.Division:
        (a,b,c) = (r1 * r2, r2, r1)
        op_string = "/"

    while True:
        print( ("GOOD: %i, BAD: %i, timeout: %i, strike: %i") % (good, bad, timeout, strike_count))
        question = ("%i %s %i = ") % (a, op_string, b)

        if options.gamemode:
            # evaluate speed-up
            if (timeout > 1) and (strike_count != 0) and (strike_count % speed_up_threshold == 0):
                timeout -= 1
                print(('Zrychlujem! Ted mas %i s') % timeout)
                playsound("wav/zrychlujem.wav")

        # evaluate best timeout    
        if timeout < best_timeout:
            best_timeout = timeout
            print('NOVY REKORD!')
            playsound("wav/new-record.wav")

        ans = None
        try:
            ans = input_with_timeout(question, timeout)
            print("")
        except TimeoutExpired:
            print('Pomalej, dame ti vic casu!')
            bad += 1
            strike_count = 0
            timeout += 1
            playslow()
            break
        try:
            intans = int(ans)
            if intans == c:
                good += 1
                strike_count += 1
                playok()
                break
            else:
                bad += 1
                strike_count = 0
                playwtf()
        except:
            print(("Napis cislo, ne %s") % ans)
            playwtf()
            bad += 1
            strike_count = 0

   






























