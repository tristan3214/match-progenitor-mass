#!/astro/users/tjhillis/anaconda2/bin/python2
from __future__ import print_function, division

import sys
import telnetlib
import threading

HOST = "10.155.88.139"
PORT = 42424

def main():
    tn = telnetlib.Telnet(HOST, PORT)

    # start take commands method
    t = threading.Thread(target=takeCommands, args=(tn,))
    t.daemon = True
    t.start()

    # any incoming data will be printed
    print(tn.read_all())


def printAll(tn):
    print(tn.read_all())

def takeCommands(tn):
    while True:
        command = raw_input("Command: ")
        tn.write(command + "\r\n") # twisted server appears to need the \r\n at the end

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print()
        sys.exit(0)
