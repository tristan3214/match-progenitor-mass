# Underwork
This code is still not ready for wide spread use and only truly works for my specific tasks.

Please feel free to submit issues as "enhancements" to describe your usage of the program and I will work to code those MATCH commands AND flags in.

Lots of documentation still needed.

## Description
This encapsulates MATCH functionality into Python scripts so one doesn't need to write files by hand.  It includes
an automatic pipeline that will run the MATCH command and reduce the output with basic commands.  These basic commands should
be overwriteable to do more complex commands.

The underlining code is a multi-threaded twisted server utilizing Python's "subprocess" library to run commands in the bash shell of a system
with MATCH installed.

Automatic logging is including to show what the server is doing internally.


## Running Server
I suggest using `screen` within an ssh connection on Eagle.  With a screen running you can start the server detach from the session and log
out of the ssh connection with the server still running.

Take these steps:
* Log into Eagle: `ssh eagle`
* Start screen: `screen`
* Navigate to *MatchExecuter*
* Start server: `./ServerMatch.py` (for best compatability run only as executable)
* Detach from screen: `C-a C-d'
* Continue working on Eagle or log out; the server will continue to run in a screen session.
* If you want to get back to the server you need to reattach to the screen session.
  ** Log back into Eagle and run `screen -r`.  Now you are back in the server.

## Killing Server
Future work will intercept the keyboard interupt and kill all running processes normally, but for now it doesn't shut down running fits.
This has to be done with **telnetSend.py**.
* Run telnetSend.py.  The code is agnostic to which Python interpreter is used.
* This will connect you to the server as a user.
* Type `cancel all`.  This will kill all jobs, except for Condor, which will be resolved in the future.

## Using Condor


## Ports in use
Tristan Hillis - 42424
Ben Williams - 42423
Kristen Garofali - 42426
