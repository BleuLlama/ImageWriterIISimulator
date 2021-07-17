# Pinouts

This document will contain all of the related pinouts I use on all of my
cabling.

All pinout numberings are based on standard pinouts, as embossed
on the plastics of the connectors.  

Apple documents show the 5 pin din with non-standard numbering.
(1,2,3,4,5 in order, CW or ACW) I will be using the industry standard
where the ordering is alternating, for ease of making cables etc.
(1,4,2,5,3) which is based on a 3 pin DIN as the starting point and
additional numbered pins being added to it.  This adds to confusion,
especially when the Apple pin numbers differ from the embossed/standard
numbering.


* Text mode: 9600 Baud, 8 bits, no parity, 1 stop bit
* Graphics mode: "8 or 7 bits"
* Binary mode: "8 bits"



# PC-standard 9 pin Serial


The host computer side has a DE-9, 9 Pin Din Male connector, and is wired
as such. Please refer to embossed plastics or existing pin ordering for 
details about which side is which.

Please refer to [Wikipedia](https://en.wikipedia.org/wiki/RS-232) for
more details.

## Host computer / DTE

DE-9 Male or DB-25 Male 

(DB-25 pin equivalents shown in parens.)

1. CD (DB25.8)
2. RX (Receiving data from the device) (DB25.3)
3. TX (Transmitting data to the device) (DB25.2)
4. DTR (DB25.20)
5. GND (DB25.7)
6. DSR (DB25.6)
7. RTS (DB25.4)
8. CTS (DB25.5)
9. RI (DB25.22)

## Device / DCE

DE-9 Female

DB-25 pin equivalents the same as the above.

1. CD
2. TX (Transmitting data to the host)
3. RX (Receiving data from the host)
4. DTR
5. GND
6. DSR
7. CTS
8. RTS
9. RI


#  Other System Serial Pinouts

## Apple IIc DTE - 5 pin 180degree Female DIN 

Please refer to standard pinouts/plastic embossing for pin ordering.

1. DTR (Apple IIc is ready to go online)
2. TX (Transmitting data to the device)
3. GND
4. RX (Teceiving data from the device)
5. DSR (Device is ready to send)

Notes: 
	
- Printer port defaults to 9600 baud, in slot #1
- Comms port defaults to 300 baud., in slot #2
- Both ports default to 8N2, with DTR flow control.

## Apple Macintosh RS-422 - 8 pin mini-DIN

Parens show RS-232 usage.

1. HSO (handshake out) (RS-232: DTR)
2. HSI (handshake in) (RS-232: DSR)
3. TX- (RS-232: TX)
4. GND (RS-232: GNDX)
5. RX- (RS-232: RX)
6. TX+ (RS-232: n/c)
7. GPi (general purpose in) (RS-232: CD)
8. RX+ (RS-232: n/c)

## ImageWriter DCE - 8 pin mini-DIN

* - 2. HSi/DSR (from DTR on host) 
* - 5. RX (from TX on host)
* - 4,8. GND, RX+
* - 3. TX (to RX on host)
* - 1 HSo/DTR (to DSR on host)

### Apple IIc to Imagewriter Cable

* IIc.1 to IW.2
* IIc.4 to IW.5
* IIc.2 to IW.4 and IW.8
* IIc.5 to IW.3
* IIc.3 to IW.1


## Amiga DTE - DB-25 Male

Amiga 100 is DB-25 Female.  Amiga provides additional outputs on unlabelled 
pins (audio, +-12v, +5v, etc) so do not connect unused pins!)

2. TX
3. RX
4. RTS
5. CTS
6. DSR
7. GND
8. CD
20. DTR
22. RI (not available on A1000)


# Related pinouts

## Null Modem

This is defined using the 9 pin connector above. It should be DE-9 Female
to DE-9 Female, converting the DTE on the "other side" into a DCE.

### Full Handshaking

Partial handshaking is shown in parens

1. CD tied to 6 locally
2. RX to 3. TX
3. TX to 2. RX
4. DTR to 6. DSR (tie to 1 locally for partial)
5. GND to 5. GND
6. DSR from 4. DTR (tie to 1 locally for partial)
7. CTS to 8. RTS 
8. DTS to 7. CTS
9. n/c

### Loopback Handshaking

1. CD - tied to local DTR(4) and DSR(6) 
2. TX - To remote RX(3)
3. RX - To remote TX(2)
4. DTR - tied to local CD(1) and DSR(6) 
5. GND - to remote GND
6. DSR - tied to local CD(1) and DTR(4)
7. CTS - tied to local RTS(8)
8. RTS - tied to local CTS(7)
9. RI - n/c

## Loopback

For a full loopback, tie RX and TX together.  The loopback is itself
the DCE.

## FTDI connector

This is used for TTL level serial connections. For explanations of the pins,
the USB host that the FTDI adapter is being plugged into is considered to
be the Host/DTE, and the TTL level RS-232 is considered to be the
Device/DCE.

The connector is a .1" spacing pin header.  It is not defined if the
device or the host has the pins or sockets.


### On the USB-FTDI adapter

Note: On the device, all are the same, but TX and RX are reversed, of course.

1. Black - GND
2. Brown - CTS# (often connected to ground)
3. Red  - +5v (+3v3 on some systems)
4. Orange - TX (Transmit data to the device)
5. Yellow - RX (Receive data from the device)
6. Green - DTR (Used for RESET on Arduino)
