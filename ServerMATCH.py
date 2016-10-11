#!/astro/users/tjhillis/anaconda2/bin/python2
from __future__ import print_function
from __future__ import division

import multiprocessing
import os
from Queue import Queue
import signal
import subprocess
import sys
import thread
import threading
import time

from twisted.protocols import basic
from twisted.internet import protocol, reactor
from threading import Thread

import MyLogger

"""
This server runs on port 42424
"""

# Global Variables
CORE_COUNT = multiprocessing.cpu_count()
workQueue = Queue()
activeThreads = {} # this should only every be one more larger than the number of CPUs on the system.
                   # main thread handles incoming data and one thread waits on events and the other threads
                   # execute the bash commands.
doneThreads = []
event = threading.Event() # a single thread waits for set to join a certain thread
log = MyLogger.myLogger("MatchServer", "server")

def getThreadNumber():
    print(activeThreads)
    num = None
    if len(activeThreads) == 0: # no threads yet
        num = '1'
    else: # get the thread number that is missing in the range of 1 to 8
        keys = activeThreads.keys()
        print(keys)
        keys = map(int, keys)
        keys = sorted(keys, key=int)
        print(keys)
        count = 1
        for name in keys:
            if count == name:
                count += 1 
            else:
                break
        num = count
    return num

class MatchExecuter(basic.LineReceiver):
    """
    Class description
    """
    def connectionMade(self):
        """
        Method desc.
        """
        self.sendLine("Welcome to MATCH executer")
        self.factory.clients.append(self)

    def connectionLost(self, reason):
        """
        Method desc.
        """
        self.factory.clients.remove(self)

    def lineReceived(self, line):
        """
        Method desc.
        """
        
        log.info("Received:" +  line)
        input = line.split(" ")
        # If there are enough open threads then assign a command
        if len(activeThreads) + 1 <= CORE_COUNT or input[0] == "cancel" or input[0] == "show": 
            cp = CommandParser()
            data = cp.parse(line)
            if data is not None:
                self.sendData(data)
        else: # If all processes are used put received line in a work Queue
            log.info("All threads taking adding command to queue - " + line)
            workQueue.put(line) 
        
    def sendData(self, data):
        """
        Decorator method to self.sendMessage(...) so that it
        sends the resulting data to every connected client.
        """
        if data is not None:
            self.sendMessage(str(data))

    def sendMessage(self, message):
        """
        Sends message to every connect client.
        """
        for client in self.factory.clients:
            client.sendLine(message)


class MatchExecuterFactory(protocol.ServerFactory):
    """
    Statement
    """
    protocol = MatchExecuter
    clients = []
    
class CommandParser(object):
    def __init__(self):
        self.commands = CommandMethods()
        
    def parse(self, input=None):
        """
        Input must start with a keyword argument. For example, if the user wants to
        cancel a command then they must have the "cancel" key followed by the Matching command.
        """
        line = input
        input = input.split(" ")
        print("Split input:", input)
        
        if input[0] == "calcsfh":
            # find the best dAv but can also pass in lower and upper bounds with a step (e.g. -finddAv=0.0,1.0,0.1)
            if "-finddAv" in line:
                pass

            else:
                log.info("run calcsfh command - " + line)
                t = MatchThread(line, target=self.commands.calcsfh, args=(line,), name=getThreadNumber())
                activeThreads[t.name] = t
                t.start()
            return None
        if input[0] == "ssp":
            return None
        if input[0] == "cancel":
            if input[1] == "all":
                self.commands.clearAll()
            else:
                line = " ".join(input[1:])
                self.commands.cancel(line)
                log.info("canceling command - " + line)
            return None
        if input[0] == "show":
            line = self.commands.show(input)
            return line
        # for testing purposes
        if input[0] == "sleep":
            log.info("starting sleep thread")
            t = MatchThread(line, target=self.commands.sleep, args=(input[1],), name=getThreadNumber())
            activeThreads[t.name] = t
            t.start()
            return None

class CommandMethods(object):
    """
    This method executes the commands that are sent to this server.  Examples include calcsfh and the find best
    dAv script.
    """
    def __init__(self):
        pass

    def calcsfh(self, line):
        """
        This runs caclsfh commands of all types.  Users should make sure to specify paths to their files in
        the arguments.
        """
        t = threading.current_thread()
        
        pipe = subprocess.Popen(line, shell=True, preexec_fn=os.setsid)
        
        while pipe.poll() is None:
            if t.cancel:
                os.killpg(os.getpgid(pipe.pid), signal.SIGTERM) # kills group of processes when present
                break
            time.sleep(0.5)

        
        if not t.cancel:
            print("ENTERED NEXT STAGE")
            if "-ssp" in line:
                # run sspcombine
                outputFile = line.split()[-1]
                fitName = outputFile.split("/")[-1].split(".")[0]
                print(outputFile)
                # get rid of the first bit so sspcombine will run properly
                subprocess.call("tail -n +11 %s > %s" % (outputFile, outputFile), shell=True)
                # make command
                sspCommand = "sspcombine %s > %s.ssp" % (outputFile, fitName)
                print(sspCommand)

                pipe = subprocess.Popen(sspCommand, shell=True, preexec_fn=os.setsid)
                while pipe.poll() is None:
                    if t.cancel:
                        os.killpg(os.getpgid(pipe.pid), signal.SIGTERM)
                        break
                    time.sleep(0.5)
            else:
                # run zcombine
                outPutFile = line.split()[-1]
                fitName = outputFile.split("/")[-1].split(".")[0]

                # make command
                zcCommand = "zcombine -bestonly %s > %s.zc" % (fitName, fitName)

                pipe = subprocess.Popen(zcCommand, shell=True, preexec_fn=os.setsid)
                while pipe.poll() is None:
                    if t.cancel:
                        os.killpg(os.getpgid(pipe.pid), signal.SIGTERM)
                        break
                    time.sleep(0.5)
            
        if not t.cancel:
            log.info("Completed computation of command - " + line)
            # get directory of where the files are being put
            directory = line.split(" ")[1] # second arg points to parameter file in the local directly
            paramFile = directory.split("/") # collect everything but parameter file name
            directory = "/".join(paramFile[:-1]) + "/"
            f = open(directory + "run_log.log", 'a')
            stripLine = stripCalcsfh(line)
            f.write("completed: %s\n" % stripLine)
            param = open("/".join(paramFile), 'r')
            lines = param.readlines()
            f.writelines(lines)

            f.write("\n\n")
            f.close()
            
        t.cancel = True
        doneThreads.append(activeThreads.pop(t.name))
        
        event.set()
        event.clear()

    def findBestdAv(self, line, lower=0.0, upper=1.0, step=0.1):
        """
        This method takes in a line and will find the best dAv by iterating through several calcsfh runs to search
        for the best solution.  The user should specify a lower, upper and step for dAv otherwise it will take on 
        defualt values.
        """
        pass

    def show(self, input):
        try:
            input[1] # test if there is another key
            if input[1] == "queue":
                size = workQueue.qsize()
                line = ""
                # show all the commands from the queue
                if size > 0:
                    tempQ = Queue()
                    # get and print all queue commands
                    for i in range(size):
                        command = workQueue.get()
                        line += command + "\n"
                        tempQ.put(command)
                    # requeue commands
                    for i in range(size):
                        workQueue.put(tempQ.get())
                else:
                    line += "no queued commands"
                return line
            if input[1] == "threads":
                # show all the commands being run on active threads
                keys = activeThreads.keys()
                line = ""
                if len(keys) > 0:
                    for key in keys:
                        t = activeThreads[key]
                        line += t.command + "\n"
                else:
                    line += "no current threads running"
                return line
        except IndexError:
            # show all commands in queue and in thread
            line = ""
            size = workQueue.qsize()
            # show all the commands from the queue
            if size > 0:
                tempQ = Queue()
                # get and print all queue commands
                for i in range(size):
                    command = workQueue.get()
                    line += command + "\n"
                    tempQ.put(command)
                # requeue commands
                for i in range(size):
                    workQueue.put(tempQ.get())

            keys = activeThreads.keys()
            if len(keys) > 0:
                for key in keys:
                    t = activeThreads[key]
                    line += t.command + "\n"

            if line == "":
                return "no commands to show"
            else:
                return line



        
    def sleep(self, stime):
        """
        Testing command by running a script that sleeps a process.
        """
        t = threading.current_thread()
        
        pipe = subprocess.Popen("./sleep.sh %s" % stime, shell=True, preexec_fn=os.setsid)
        
        while pipe.poll() is None:
            if t.cancel:
                os.killpg(os.getpgid(pipe.pid), signal.SIGTERM) # kills group of processes when present
                break
            time.sleep(0.5) # add sleep so this isn't as intensive
            
        t.cancel = True # says this thread is ready to be joined and removed from the dictionary
        doneThreads.append(activeThreads.pop(t.name))
        
        event.set()
        event.clear()

    def clearAll(self):
        """
        This method, when called, will clear all the commands to be run in the queue as well as the threads.
        """
    
        if workQueue.qsize() > 0:
            # empty queue
            size = workQueue.qsize()
            for i in range(size):
                workQueue.get()
                
        for key in activeThreads:
            # cancel all the threads
            t = activeThreads[key]
            t.cancel = True
    
        return
        
    def cancel(self, line):
        """
        Matches the sent line to the internally set thread variable command.  If the same
        it will set this to cancel
        TODO: Add cleanup of files for the command that is being canceled. Calcsfh's have predictable pattern
        for grabing the fit name.
        """

        for key in activeThreads:
            t = activeThreads[key]
            if line == t.command:
                log.info("Canceled command in running thread (%s)" % line)
                t.cancel = True
                return
            
        if workQueue.qsize() > 0:
            # empty queue into temporary one and check for the right command to get rid of.
            # at end put tempQ commands back into the workQueue
            tempQ = Queue()
            size = workQueue.qsize()
            for i in range(size):
                command = workQueue.get()
                print(command)
                if line == command:
                    log.info("Canceled command in queue (%s)" % line)
                else:
                    tempQ.put(command)
            size = tempQ.qsize()
            
            # refill work queue
            for i in range(size):
                print(command)
                workQueue.put(tempQ.get())
            return

        # if a return was not reached then there was no similarly found command
        log.info("Couldn't find command to cancel (%s)" % line)

def stripCalcsfh(line):
    """
    This takes a calcsfh command line and will strip away the directory information and return
    a less verbose version.  The command that is returned will only run in the respective directory
    when calling calcsfh.
    """
    line = line.split()

    # first entry is parameter file
    line[1] = line[1].split("/")[-1]
    # second entry is photometry file
    line[2] = line[2].split("/")[-1]
    # third entry is fake file
    line[3] = line[3].split("/")[-1]
    # fourth entry is fit name
    line[4] = line[4].split("/")[-1]
    # last entry is output file name
    line[-1] = line[-1].split("/")[-1]

    return " ".join(line)

class MatchThread(threading.Thread):
    """
    This acts like a regular Thread object and is called the same only there are custom class variables.
    """
    def __init__(self, line, target=None, args=(), name=None):
        """
        Initializes Thread the same way just with an additive class variable.
        Takes in a single string line that will be parsed by the target method
        """
        threading.Thread.__init__(self, target=target, args=args, name=name)
        self.cancel = False # This gets set to True if the bash command is to be canceled
        self.command = line # Saves the command sent to this thread
        self.name = name

        
def threadWatcher():
    """
    This method waits for a thread to set an event and will then join that thread.  An example of
    such an event is sending a command for the thread to be canceled or if the thread encounters an error.
    """
    while True:
        event.wait()
        # find thread that activated event using "cancel" internal boolean
        for t in doneThreads:
            # join thread
            t.join()
            
            # if something is in the work queue set another thread to the task
            if workQueue.qsize() > 0:
                print(workQueue)
                cp = CommandParser()
                cp.parse(workQueue.get())

    
if __name__ == "__main__":
    watcher = Thread(target=threadWatcher, name="watcher")
    watcher.daemon = True
    watcher.start()
    reactor.listenTCP(42424, MatchExecuterFactory())
    reactor.run()
