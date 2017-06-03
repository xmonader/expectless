import sys
import os
import select
from subprocess import Popen, PIPE, STDOUT
import fcntl
from time import sleep


def expect(args=[], expectations={}):
    print(expectations)
    p = Popen(args=args, shell=False, stdin=PIPE, stdout=PIPE, bufsize=0, cwd=os.getcwd(), universal_newlines=True)
    while expectations:
        rds, wds, eds = select.select([p.stdout.fileno()], [], [], 0.1)
        #print(rds, wds, eds)
        towritenext = None
        msg = ""
        while True:
            out = p.stdout.read(1)
            # print(out)

            msg += out
            if msg in expectations:
                break
            if out == "" or out == "\n": # Line buffering.
                break

        if msg:
            print(msg)
            towritenext = expectations.pop(msg, None)
        if towritenext is not None:
            towritenext += "\n"
            print("sending ", towritenext)
            p.stdin.write(towritenext)
    sleep(0.1)
    print("Done expecting")
    return p


def main():
    expectations = {
        'name:': 'auser',
        'pass:': 'password',
    }
    p = expect(["./test_expect.py"], expectations=expectations)
    print(p.stdout.read())  # see the process stdout.


if __name__ == '__main__':
    main()
