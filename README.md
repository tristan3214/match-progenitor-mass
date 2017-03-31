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
* Detach from screen: `C-a C-d`
* Continue working on Eagle or log out.  The server will continue to run in a screen session.
* If you want to get back to the server you need to reattach to the screen session.
  * Log back into Eagle and run `screen -r`.  Now you are back in the server.

Most of you will simply run the fits you need right from Eagle.  However, one key advantage to using a server that sits on an open port and the fact that the Astro file system is the same on whatever computer you log in, fits can be sent to run on Eagle without being on Eagle.  *MatchRunner.py* connects to Eagle's IP and sends commands through the user specified port.  For those running on their local UW-Astro computer just start the server on Eagle and run your commands through *MatchRunner.py* saving the time of sshing to run commands on the server.

## Killing Server
Future work will intercept the keyboard interupt and kill all running processes normally, but for now it doesn't shut down running fits.
This has to be done with **telnetSend.py**.
* Run telnetSend.py.  The code is agnostic to which Python interpreter is used.
* This will connect you to the server as a user.
* Type `cancel all`.  This will kill all jobs, except for Condor, which will be resolved in the future.

## Using Condor
**Important**: Make sure your ssh keys are setup so that you can type `ssh condor` and log in without a password.  The server assumes keys are setup so I don't have
to come up with a way to deal with passwords or store them for that matter.

These are the steps to take to run Condor jobs:
* Edit *UserParameters.py*, set `CONDOR_ON = True`, and the max size of your job queue for Condor.
* Decide whether you want Eagle to process fits at the same time as Condor.
  * If yes then set `CORE_COUNT` to a non-zero number, else set it to zero.
* That is all there is.  Send commands like normal, to the server, and I will run Condor for you.

Only one Condor configuration file is ever run at one time.  This means once you send all your commands and the server sets up Condor to run
then you won't be able to add more jobs to Condor until the first run is done.  This doesn't stop you from sending commands to the server, which will
store them in a work queue, but they won't run in Condor until it goes through all the jobs in the config file.

There is a bug with Conor currently where it periodiacally holds jobs and then doesn't release them.  This requires user intervention by releasing the held
jobs.  Do this by sshing into condor (`ssh condor`) and running `condor_release your_username`.  One can check if there are held jobs by running
`condor_q -sub your_username` and seeing if there the *held* count is non-zero.

## Ports in use
Tristan Hillis - 42424
Ben Williams - 42423
Kristen Garofali - 42426
