import sys
import os
import select
from subprocess import Popen, PIPE, STDOUT
import fcntl
from time import sleep
import termios
import pty
import tty
import re

def setecho(fd, state=True):
    attrs = termios.tcgetattr(fd)

    if state:
        attrs[3] = attrs[3] | termios.ECHO | termios.ECHONL
    else:
        attrs[3] = attrs[3] & ~termios.ECHO & ~termios.ECHONL

    termios.tcsetattr(fd, termios.TCSAFLUSH, attrs)


def expect(args=[], expectations=[], exact=True):
    def match(x, y):
        if exact:
            return x == y
        return re.compile(x).match(y)

    def expecting(msg, discard=False):
        for idx, item in enumerate(expectations):
            k, v = item
            if match(k, msg):
                if discard is True:
                    # print("***Removed value..")
                    expectations.pop(idx)
                return v
        return None

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

        os.execlp(args[0], args[0], *args[1:])
    else:
        os.close(slave)
        if not expectations:
            return master, pid
        shouldreturn = False
        # tty.setraw(slave)
        while not shouldreturn and expectations:
            # print("first select")
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
                    except EOFError:
                        print("EOF ERROR")
                        shouldreturn = True
                    msg += out
                    if expecting(msg):
                        break
                    if out == "" or "\n" in out:  # Line buffering.
                        break

            except IOError as e:
                shouldreturn = True
            if msg:
                # print("*** received msg: ", msg)
                towritenext = expecting(msg, discard=True)
            if towritenext is not None:
                towritenext += "\n"
                # print("*** sending ", towritenext)
                os.write(master, towritenext.encode("utf-8"))

    return master, pid


def interact(master):
    doneinteract = False
    stdfd = sys.stdin.fileno()
    orig = termios.tcgetattr(stdfd)
    tty.setraw(stdfd)
    while not doneinteract:
        rds, wds, eds = select.select([stdfd, master], [], [], 0.01)
        if  master in rds:
            try:
                msg = os.read(master, 1024)
            except Exception:
                doneinteract = True

            os.write(sys.stdout.fileno(), msg)

        if stdfd in rds:
            msg = os.read(stdfd, 1024)
            os.write(master, msg)

    termios.tcsetattr(stdfd, termios.TCSAFLUSH, orig)


def main():
    expectations = [
        ('name:', 'ahmed'),
        ('password:', 'ahardpassword'),
    ]
    p = expect(["./test_expect.py"], expectations=expectations)
    p = expect(["./hello"], expectations=[('name', 'ahmed')])
    # interact(p[0])
    p = expect(["ssh", "-T", "mie@10.147.19.169", "ls /home"], expectations=[("mie@10.147.19.169's password:", 'mie')])
    
    p = expect(["python3"])
    interact(p[0])
    # #
    p = expect(["ssh", "-T", "mie@10.147.19.169"], expectations=[("mie@10.147.19.169's password:", 'mie')])
    interact(p[0])


if __name__ == '__main__':
    main()
