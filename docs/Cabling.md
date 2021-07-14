# Cabling

Things get confusing here, since both sides of the cable could be
considered to be the "host" but for simplicity sake, I will call
the retro computer that will be printing the DTE/Host and my
development machine the DCE/Printer.

Although the real ImageWriterII printer has an 8 pin mini-din connector
on it for all serial communications, we're going to have a slightly
different setup.

For ease of development, my dev machine has a USB port, and connected
to that is a USB to TTL Serial "FTDI" adapter.  Although I will not
be implementing flow control, as the real IW2 does, I don't think
it will be a problem as our dev machine is significantly more powerful 
than the original IW2.

From there, I have tested wiring that connects to the target 
retro systems...

## 5 Pin DIN

For testing with my Apple IIc, I have a 5 pin din connector to FTDI. 
It is part of my ADTPro setup, using a FTDI cable from there to my 
modern machine.  This will be used for printing from the Apple IIc.

I also have made a 5 pin din to "DE-9 as PC" which converts it to 
standard 9 pin D Male connector, as found on PCs.


## 9 Pin D / DE-9 Male

For testing all other systems, I will be using a similar adapter,
but this one breaks out directly to a DE-9 connector.

From here, I can use the 8 pin Mini-Din cable I already have to 
print from 68k Macs.

Also, by using 9-to-25 adapters and such, I will be able to print from
my Amiga as well.


## Level Conversion

For my development work, I will be using a homebrew RS-232 adapter
consisting of:

* USB FTDI adapter, presenting the serial data as TTL-level serial
* TTL-RS232 level converter, which brings that to standard RS-232 voltages, and presents the DE-9 or 5-Din connector.

