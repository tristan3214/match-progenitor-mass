Lots of documentation still needed.

This encapsulates MATCH functionality into Python scripts so one doesn't need to write files by hand.  It includes
an automatic pipeline that will run the MATCH command and reduce the output with basic commands.  These basic commands should
be overwriteable to do more complex commands.

The underlining code is a multi-threaded twisted server utilizing Python's "subprocess" library to run commands in the bash shell of a system
with MATCH installed.

Automatic logging is including to show what the server is doing internally.

