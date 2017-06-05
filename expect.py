import sys
import os
import select
from subprocess import Popen, PIPE, STDOUT
import fcntl
from time import sleep
import termios
import pty


def setecho(fd, state=True):
    attrs = termios.tcgetattr(fd)

    if state:
        attrs[3] = attrs[3] | termios.ECHO | termios.ECHONL
    else:
        attrs[3] = attrs[3] & ~termios.ECHO & ~termios.ECHONL

    termios.tcsetattr(fd, termios.TCSADRAIN, attrs)

def expect(args=[], expectations={}):
    master, slave = pty.openpty()

    pid = os.fork()
    if pid == 0:
        os.setsid()  # lose the controlling termnial
        child_name = os.ttyname(slave)
        fd = os.open(child_name, os.O_RDWR)
        os.close(fd)

        os.close(master) # close the master end

        # close STDIN, STDOUT, STDERR 0, 1, 2
        os.closerange(0, 3)
        # duplicate slave to STDIN, STDOUT, STDERR
        os.dup2(slave, 0)
        os.dup2(slave, 1)
        os.dup2(slave, 2)

        if len(args) == 1:
            os.execlp(args[0], "") # at least 2 args. even if 2nd is empty
        elif len(args) > 1:
            os.execlp(args[0], *args[1:])
    else:
        os.close(slave)
        shouldreturn = False
        while not shouldreturn:
            rds, wds, eds = select.select([master], [master], [], 0.01)
            towritenext = None
            msg = ""
            try:
                while True:
                    if master not in rds:
                        break
                    try:
                        out = os.read(master, 1).decode("utf-8")
                        sys.stdout.write(out)
                        #print("***out -> [{}]".format(out))
                    except EOFError:
                        print("EOF ERROR")
                        shouldreturn = True
                        os.close(master)
                    msg += out
                    if msg in expectations:
                        break
                    if out == "" or "\n" in out: # Line buffering.
                        break
            except IOError as e:
                shouldreturn = True
            if msg:
                # print("*** received msg: ", msg)
                for k in expectations:
                    if msg in k:
                        towritenext = expectations.pop(k, None)
                        break
            for w in wds:
                if towritenext is not None:
                    towritenext += "\n"
                    # print("*** sending ", towritenext)
                    os.write(master, towritenext.encode("utf-8"))
    return master, pid


def main():
    expectations = {
        'name:': 'my name',
        'password:': 'my password',
    }
    p = expect(["./test_expect.py"], expectations=expectations)
    print(p)
    p = expect(["./hello"], expectations={'name':'ahmed'})
    print(p)
    p = expect(["ssh", "-T", "mie@localhost", "ls /home/ahmed"], expectations={"mie@localhost's password:":'mie'})

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        sys.stdout.write(str(e))
        #import ipdb; ipdb.set_trace()
