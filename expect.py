import sys
import os
import select
from subprocess import Popen, PIPE, STDOUT
import fcntl
from time import sleep

import pty 


def expect(args=[], expectations={}):
    print(expectations)
    master, slave = pty.openpty()
    p = Popen(args=args, shell=False, stdin=PIPE, stdout=master, bufsize=0, cwd=os.getcwd(), universal_newlines=True)
    while expectations:
        rds, wds, eds = select.select([master], [], [], 0.1)
        towritenext = None

        for r in rds:

            #print(rds, wds, eds)
            msg = ""
            # msg = p.stdout.readline()
            while True:
                out = os.read(r, 1).decode("utf-8")
                print(out)

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
            os.write(p.stdin.fileno(), towritenext.encode())
    sleep(0.1)
    print("Done expecting")
    # return p


def main():
    expectations = {
        'name:': 'auser',
        'pass:': 'password',
    }
    p = expect(["./test_expect.py"], expectations=expectations)
    #print(p.stdout.read())  # see the process stdout.


    # p=expect(["/usr/bin/ssh","-T", "ahmed@10.147.19.169", "'ls'"], expectations={'yes':'yes', "ahmed@10.147.19.169's password:":'dmdm'})
    # print(p.stdout.read())

if __name__ == '__main__':
    main()
