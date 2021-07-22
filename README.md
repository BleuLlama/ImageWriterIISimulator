# LlamaWriter - An Apple ImageWriter II Simulator

This is a serial-port based simulation of an Apple ImageWriterII 
printer.  It also probably supports all ImageWriter I control 
sequences too.

The project is provided with an MIT License, however the sound files
provided in the "Sounds" directory are provided with a Creative
Commons - Attribution license.

# CURRENT STATE

July 19, 2021 - This project is being currently developed RIGHT NOW!  It is 
not functional yet.

# Background...

This project was created as an entry for
[KansasFest 2021](https://www.kansasfest.org/), but also just
because I want to be able to print banners and cards from my Apple II.

The project will be developed in accordance with the 
[KansasFest Hackfest Rules](https://www.kansasfest.org/hackfest-rules/)

This document is a live document, so some aspects in it may change over
time before, during and after Hackfest 2021.


# Goals / Test Cases

These are the things I'll use to determine sucess of the project and/or
to know when to stop. ;D

## Primary

This covers the "gotta haves" of the project. Without these, I don't
think I can consider the project a success at all.

* The ability to print from text applications on the IIc and have it go
to some sort of formatted text file. (Markdown, HTML, etc)

* The ability to print from Print Shop on my Apple IIc and have it go to
a modern system as a common graphic format (BMP, PGM)


### Additional test cases

* Print from MacWrite, MacDraw, ClarisWorks, TextEdit, etc from a 68k Mac 
running System 6 or 7

* Print from Deluxe Paint III on an Amiga with its ImageWriterII driver.


## Secondary Goals

These are "quality of life" upgrades.

* Printed files should be made available through a web interface

* Graphic printouts should be made available as modern formats. (PNG)

* Web interface should link to HTML+CSS versions of the documents


## Tertiary Goals

These are "sure would be nifty" upgrades.

* Use extracted or similar bitmap fonts to render the text 
	For this, existing TTF Imagewriter and MouseFont fonts will be used


## Probably Not Happening Goals

These are nice things to polish up the output... or something.

* Paper simulation
* Dot-matrix ink simulation 


# Timeline of Development

Here's the rough outline of stuff I have planned and when I'm gonna do it.

Timeline for Hackfest 2021 is:

* Contest starts Friday, July 16, 8am CDT
* Contest ends Thursday July 22, 5pm CDT

Which determines my general schedule:

* Now through July 15 - Prep work, Design, Research, Cabling
* July 15 (eve) - Shoot and upload a video showing the dev setup
* July 16-July 22 - Primary Software development and testing
* July 22 (eve) - Shoot and upload the video to youtube
* July 23-24 - KansasFest 2021
* July 25- - Additional dev work and polish.  ;)

## Before KansasFest HackFest 2021

In keeping with the rules, none of the software development was done 
before HF21, only collecting of stuff, wiring up cables, and making sure
that things all work:

### Design and Research

* Basic sketches of the system and how it works... all of the Software Engineering-ey stuff to get my brain in order.
* Figure out what languages to use for each component. (probably python)
* Determine directory structure, etc.
* Set up git repository (this)

### Hardware Confirmation For Testing

* Document and confirm cabling to go from my Apple IIc to my dev machine
* Document and confirm cabling to go from a 68k Mac to my dev machine
* Look for (or create) a STL of an ImageWriter II to shove a Raspberry Pi into, because it'd be neat.

NOTE: All three of these are complete. The IW2 model is on Thingiverse. ;D


### Software for testing

* word processor(s) on Apple
* Print Shop on Apple

### Video presentation Setup

* Make sure I have the ability to produce a nice video demonstrating the project
* perhaps make a video showing my test and development setup before July 16

## During KansasFest HackFest 2021

### Primary Software

All of the parts from "listening on a serial port" through to the local
file generation will be generated during the Hackfest per the rules.

### Preliminary plan of attack

This section will roughly cover the individual specific tasks I'll need to
tackle to make this happen.  I'll be using Python3 and the PySerial library.

- Create a python3 program that will read from the serial port
- extend it to save the captured data to a file (for testing without hardware)
- Write Apple //c basic program that opens 9600 8N1 and outputs some text
- Confirm it works and stores the data properly.
- When it does, print from Print Shop, capture to file

As of Jul-19, all of the above have been accomplished.


# Sounds

The Sounds directory contains a bunch of audio recordings from an
actual ImageWriter II printer.  They were recorded by me using a 
borrowed IW2 printer.  They are released here with a Creative 
Commons - Attribution license.
