## Underwork
This code is still not ready for wide spread use and only truely works for my specific tasks.

Please feel free to submit issues as "enhancements" to describe your usage of the program and I will work to code those MATCH commands AND flags in.

Lots of documentation still needed.

##Description
This encapsulates MATCH functionality into Python scripts so one doesn't need to write files by hand.  It includes
an automatic pipeline that will run the MATCH command and reduce the output with basic commands.  These basic commands should
be overwriteable to do more complex commands.

The underlining code is a multi-threaded twisted server utilizing Python's "subprocess" library to run commands in the bash shell of a system
with MATCH installed.

Automatic logging is including to show what the server is doing internally.


## Running
I suggest using `screen` within an ssh connection on Eagle.  With a screen running you can start the server detach from the session and log
out of the ssh connection with the server still running.

Take these steps:
* Log into Eagle

## Ports in use
Tristan Hillis - 42424
Ben Williams - 42423
Kristen Garofali - 42426
