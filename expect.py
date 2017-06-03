import sys
import os
import select
from subprocess import Popen, PIPE, STDOUT
import fcntl
from time import sleep
import termios
import pty 
import tty


def expect(args=[], expectations={}):

    master, slave = pty.openpty()
    # sname = os.ttyname(slave)

    # def noechoicanon(fd):
    #     old = termios.tcgetattr(fd)
    #     old[3] = old[3] &~ termios.ECHO &~ termios.ICANON
    #     # &~ termios.ISIG
    #     termios.tcsetattr(fd, termios.TCSADRAIN, old)
    
    # # No echo or buffering over the pty
    # noechoicanon(slave)
    # don't map '\n' to '\r\n' - no echo - INTR is <C-C>
    # attr = termios.tcgetattr(slave)
    # attr[1] = attr[1] & ~termios.ONLCR  # oflag
    # attr[3] = attr[3] & ~termios.ECHO   # lflags
    # #attr[6][termios.VINTR] = self.INTERRUPT_CHAR
    # termios.tcsetattr(slave, termios.TCSADRAIN, attr)

    pid = os.fork()
    if pid == 0: 
        os.setsid()
        # os.close(0)
        # os.close(1)
        # os.close(2)
        # os.close(master)
        # os.dup2(slave)
        # os.dup2(slave)
        # os.dup2(slave)
        # child
        fcntl.fcntl(slave, fcntl.F_SETFL, os.O_NONBLOCK)
        p = Popen(args=args, shell=False, stdin=PIPE, stdout=slave, bufsize=0, cwd=os.getcwd(), universal_newlines=True)
    else:

        # parent.
        #print("Done expecting")
        # print("parent ::: master", master)

        # os.close(0)
        # os.close(1)
        # os.close(2)
        # os.close(slave)
        # # os.close(slave)
        # os.dup()
        # os.dup()
        # os.dup()
        # sys.stdin = os.fdopen(master, 'r')
        # sys.stdout = os.fdopen(master, 'w')
        # print(sys.stdin.fileno())
        # print(sys.stdout.fileno())
        #rd, wd, ed = select.select([master], [], [], 0.1)
        #fcntl.fcntl(master, fcntl.F_SETFL, os.O_NONBLOCK)

        while expectations:
            #print("reached select.")
            rds, wds, eds = select.select([master], [master], [], 0.01)
            #print("done select")
            towritenext = None
            msg = ""

            while True:
                if master not in rds:
                    break
                try:
                    out = os.read(master, 1).decode("utf-8")
                    print("***out -> [{}]".format(out))
                except EOFError:
                    print("EOF ERRORRRR")
                msg += out
                if msg in expectations:
                    break
                if out == "" or out == "\n": # Line buffering.
                    break
                sleep(0.01)
            if msg:
                print("*** received msg: ", msg)
                towritenext = expectations.pop(msg, None)
            if towritenext is not None:
                # towritenext += "\n"
                print("*** sending ", towritenext)
                os.write(master, towritenext.encode("utf-8"))
        #print(os.read(master, 40))
    # termios.tcsetattr(master, termios.TCSADRAIN, old_settings)

def main():
    expectations = {
        'name:': 'auser',
        'password:': 'password',
    }
    p = expect(["./test_expect.py"], expectations=expectations)
    #print(p.stdout.read())  # see the process stdout.

if __name__ == '__main__':
    main()
