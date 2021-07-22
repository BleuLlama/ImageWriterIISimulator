# Source

Contained in here are a few software bits for this project;


## LlamaWriter.py

This is the actual simulator.  run it with python3.  you may need to
install a few packages:

- pip3 install pyserial
- pip3 install playsound

playsound is optional.  If it is not installed, mpg123 will be used to 
play sounds.  If that fails, no sounds will be played.


## Printouts/

When things get printed, this is where they go.

- FILE.html - these are resulting printouts
- FILE.png  - these are printed graphics (future)
- FILE.raw  - these are raw captures from the serial port (no time data)
- FILE.hex  - initial dumps from the system.

RAW files can be used for the 'reprint' function of LlamaWriter.  This was done
for debugging purposes.

## Templates/

This directory contains all of the files needed for building a completed 
printout.

## Arduino/

In this directory is just a simple sketch to output serial data. This is so
I can use one of my tiny Arduinos while I hack on the couch, without needing
to be connected to a computer, at least until I get the basic serial stuff 
working. ;)

It pretends to send a printout as captured from a real printer.


## ConnectionTest.py

A simple tool to connect to the serial port, with the same parameters
as an IW2.  

Also will have ability to capture to a file for offline playback/testing
