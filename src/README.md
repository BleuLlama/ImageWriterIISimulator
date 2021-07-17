# Source

Contained in here are a few software bits for this project;

# Unknowns

Apple IIc printer port starts up as:

9600 baud
8 data bits and no parity
2 stop bits ?
80 chars per line
LF after CR
Command character is CTRL-I
Hardware (DTR flow control protocol) handshake.

Printer expects:
9600 baud, 8N1, "7 or 8 bits graphics"

From IIc, we need to open the printer port with 1 stop bit.  ?

IIc basic sets high bit on print.


## Arduino/

In this directory is just a simple sketch to output serial data. This is so
I can use one of my tiny Arduinos while i hack on the couch, without needing
to be connected to a computer, at least until I get the basic serial stuff 
working. ;)

## ConnectionTest.py

A simple tool to connect to the serial port, with the same parameters
as an IW2.  

Also will have ability to capture to a file for offline playback/testing


## LlamaWriter/

This directory contains the simulator itself.  It contains a subdirectory 
containing the webroot directory, where all printouts will go


