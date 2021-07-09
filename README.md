# ImageWriterIISimulator
A serial-reading simulation of an Apple ImageWriterII printer.

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

* The ability to print from Print Shop on my Apple IIc and have it go to
a modern system as a common graphic format (BMP, PGM)

* The ability to print from text applications on the IIc and have it go
to some sort of formatted text file. (Markdown, HTML, etc)


### Additional test cases

* Print from MacWrite, MacDraw, ClarisWorks, TextEdit, etc from a 68k Mac 
running System 6 or 7

* Print from Deluxe Paint III on an Amiga with its ImageWriterII driver.


## Secondary Goals

These are "quality of life" upgrades.

* Files should be made available through a web interface

* Graphic printouts should be made available in modern formats.

* Web interface should link to HTML versions of the documents


## Tertiary Goals

These are "sure would be nifty" upgrades.

* Web interface is run within the software package itself, on a predefined port so as to not compete with existing services

* Use extracted or similar bitmap fonts to render the text 


## Definitely Not Happening Goals

These are nice things to polish up the output... or something.

* Paper simulation
* Dot-matrix ink simulation 


# Timeline of Development

Here's the rough outline of stuff I have planned and when I'm gonna do it.

Timeline for Hackfest 2021 is:

* Contest starts Friday, July 16, 8am CDT
* Contest ends Thursday July 22, 5pm CDT

Which determines my general schedule:

* Now through July 14 - Prep work, Design, Research, Cabling
* July 14 (eve) - Shoot and upload a video showing the dev setup
* July 15-July 22 - Primary Software development and testing
* July 22 (eve) - Shoot and upload the video to youtube
* July 23-24 - KansasFest 2021
* July 25- - Additional dev work and polish.  ;)

## Before KansasFest HackFest 2021

This section of this document will be populated as I work on it.

# Design and Research

* Basic sketches of the system and how it works... all of the Software Engineering-ey stuff to get my brain in order.
* Figure out what languages to use for each component. (probably python)
* Determine directory structure, etc.
* Set up git repository (this)

# Hardware Confirmation For Testing

* Document and confirm cabling to go from my Apple IIc to my dev machine
* Document and confirm cabling to go from a 68k Mac to my dev machine


# Video presentation Setup

* Make sure I have the ability to produce a nice video demonstrating the project
* perhaps make a video showing my test and development setup before July 15

## During KansasFest HackFest 2021

# Primary Software

All of the parts from "listening on a serial port" through to the local
file generation will be generated during the Hackfest per the rules.
