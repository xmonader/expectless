import sys
import os
import select
from subprocess import Popen, PIPE, STDOUT
import fcntl
from time import sleep
import termios
import pty
import tty

def setecho(fd, state=True):
    attrs = termios.tcgetattr(fd)

    if state:
        attrs[3] = attrs[3] | termios.ECHO | termios.ECHONL
    else:
        attrs[3] = attrs[3] & ~termios.ECHO & ~termios.ECHONL & ~termios.ICANON

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

        os.execlp(args[0], *args)
    else:
        os.close(slave)
        if not expectations: return master, pid
        shouldreturn = False
        # tty.setraw(slave)
        while not shouldreturn and expectations:
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
                        # os.close(master)
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


def interact(master):
    doneinteract = False
    # setecho(master, False)
    # tty.setraw(master)
    stdfd = sys.stdin.fileno()
    # orig = tty.tcgetattr(stdfd)
    # tty.setraw(stdfd)

    while not doneinteract:
        rds, wds, eds = select.select([master, stdfd], [], [], 0.01)
        if master in rds:
            try:
                msg = os.read(master, 1024)
            except IOError:
                doneinteract = True
            os.write(sys.stdout.fileno(), msg)
            # continue
        if stdfd in rds:
            msg = os.read(stdfd, 1024)
            os.write(master, msg)
    # tty.tcsetattr(stdfd, tty.TCSAFLUSH, orig)
def main():
    expectations = {
        'name:': 'my name',
        'password:': 'my password',
    }
    p = expect(["./test_expect.py"], expectations=expectations)
    p = expect(["./hello"], expectations={'name':'ahmed'})
    p = expect(["ssh", "-T", "mie@localhost", "ls /home"], expectations={"mie@localhost's password:":'mie'})
    # p = expect(["python3"])
    # interact(p[0])
    # p = expect(["ssh", "-T", "mie@localhost"], expectations={"mie@localhost's password:":'mie'})
    # interact(p[0])

if __name__ == '__main__':
    # try:
    #     main()
    # except Exception as e:
    #     sys.stdout.write(str(e))
    #     #import ipdb; ipdb.set_trace()
    main()
