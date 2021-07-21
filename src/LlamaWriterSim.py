#!/usr/bin/env python3
#
# LlamaWriter - An ImageWriter II simulator of sorts
#
#   (c)2021 Scott Lawrence / yorgle@gmail.com
#


VERSION = '0.05'
VERS_DATE = '2021-07-21'

# v0.05 - 2021-07-21 - Audio moved to a class, toggleable via cmd line, autoconfigures
# v0.04 - 2021-07-20 - Reorganization, Initial audio support
# v0.03 - 2021-07-19 - Changed how logging reprints works
# v0.02 - 2021-07-19 - Added reprinting
# v0.01 - 2021-07-18 - indev version


# Control panel
#
#  [ e1 ][ p1 ]  [     on/off    ]            
#  [ s1 ][ s2 ]  [     select    ]
#  [ q1 ][ q2 ]  [ print quality ]
#                [   line feed   ]
#                [   form feed   ]

#  e1 - error - red
#       solid - paper out
#       blink - cover off or print jam
#  p1 - power - green
#  s1,s2 - select enabled - green

#  q1  q2 - both green
# [ON][  ]  draft
# [  ][ON]  standard
# [ON][ON]  nlq


# general application configuration stuff
config = {
    'audio' : True,     # should we output audio?
}


import sys
import serial
import serial.threaded
import time
import os

import subprocess

from serial.tools.list_ports import comports
from serial.tools import hexlify_codec

from os import listdir
from os.path import isfile, join

# python libraries "needed":
#   pip3 install pyserial
#   pip3 install playsound
#   pip3 install AppKit


class LlamaAudio():

    def __init__( self, startupEnabled ):
        self.audioMethod = None
        self.enabled = startupEnabled

        if startupEnabled:
            self.AutoConfigure();


    def AutoConfigure( self ):
        # attempt to autoconfigure for audio

        self.audioMethod = None;

        try: 
            # attempt to use playsound library
            from playsound import playsound
            playsound( 'Audio/Startup.mp3', False ) # should work
            self.enabled = True
            self.audioMethod = 'playsound'

        except:
            # something went wrong... attempt to use mpg123 via shell
            self.enabled = True
            self.audioMethod = 'mpg123'
            success = self.Play( 'Audio/Startup.mp3' )
            if not success:
                # something went wronger... just forget the whole thing,
                self.audioMethod = None
                self.enabled = False
            pass

        if not self.enabled:
            print( "--- Unable to autoconfigure audio playback. Sorry." )

        return self.enabled


    def Play( self, fname ):
        """ Play the specified sound file.
            returns False if it was unable to.
            """
        if not self.enabled:
            return False

        if self.audioMethod == 'playsound':
            playsound( fname, False )

        elif self.audioMethod == 'mpg123':
            try:
                aproc = subprocess.Popen( [ 'mpg123', fname ],
                    True, # background.
                    close_fds=True,  # suppress all output
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL )
            except: 
                pass
                return False

        else:
            print( ' *** ERROR: {}: Unknown audio method.'.format( self.audioMethod ))
            return False

        return True


class IWProtocolHandler( serial.threaded.Protocol ):
    """serial/file to file/outputs/etc"""

    # Notes:
    #   When printer buffer space < 30, printer sets DTR False "Busy"
    #   When printer buffer space > 100, printer sets DTR True "Ready"
    #   When printer buffer space < 266, printer sends ^S (XOFF)
    #   when printer buffer space > 337, printer sends ^Q (XON)
    #   - this might be why MacWrite prints fail.

    def __init__(self):
        self.count = 0
        self.tick = 0
        self.rbuf = ""

        self.serialport = None

        self.file = None
        self.fSize = 0

        self.Printouts = "Printouts/"

        # esc - escaped 
        self.escRemaining = 0        # number of chars left in escape sequence
        # if it's 0, pass characters through...
        self.escIdx = 0
        self.escSequence = self.ClearEscapeSequence()

        # current printer state
        self.state = {};

        # Length of escape sequences, based on the first byte; after 0x1b
        self.eSeqLen = [
            [ 1, [ # these have no parameters
                0x6d,   # Select correspondence font
                0x4d,   # select NLQ font

                0x26,   # mousetext remap
                0x24,   # ascii

                0x2d,   # user designed characters
                0x2b,
                0x49,
                0x27,
                0x2a,
                0x24,

                0x6e,   # character pitch
                0x4e,
                0x45,
                0x65,
                0x71,
                0x51,
                0x70,
                0x50,

                0x01, 0x02, 0x03, 0x04, 0x05, 0x06, # dot spacings

                0x58,   # text attributes
                0x59,
                0x21,
                0x22,
                0x77,
                0x57,
                0x78,
                0x79,
                0x7a,

                0x3e,   # head motion
                0x3c,

                0x30,   # clear all tabs

                0x41,   # 6lpi (default)
                0x42,   # 8lpi

                0x66,   # forward line feeding (default)
                0x72,   # reverse line feeding
                0x76,   # set TOF to current position

                0x4f,   # paper out sensor off
                0x6f,   # paper out sensor on (default)

                0x63,   # reset to defaults

                0x3f,   # send ident string
                ]
            ],
            [ 2, [ # these have one additional parameter
                0x73,   # dot spacings
                0x61,   # select font
                0x6c,   # CR/LF toggles
                0x4b,   # Color '0..6': K, Y, M, C, orn(YM), grn(YC), pur(MC)
                ]
            ],
            [ 3, [ # these have two additional parameters
                0x44,   # clear dips - keyboard, bit select, perf skip
                0x5a,   # set dipswitches 

                0x54,   # distance between lines NN/144 inch
                0x67,   # print line of graphics NNNx8 bytes
                ]
            ],
            [ 4, [ # these hsve 3 additional parameters
                0x4c,   # set left margin  000
                0x75,   # set one tab stop at HHH
                ]
            ],
            [ 5, [ # these hsve 4 additional parameters
                0x48,   # set page length 0001-9999
                0x46,   # place print head NNNN dot cols from left margin
                0x47,   # print line of graphics NNNN
                0x53,   # same as 0x47
                0x52,   # HHHC  repeat charactr c HHH times 000-999
                ]
            ],
            [ 6, [ # these hsve 5 additional parameters
                ]
            ],
            [ 7, [ # these hsve 6 additional parameters
                0x56,   # print NNNN reps of dot col CC
                ]
            ],
        ]

        # exceptions
        #
        #   0x1b 0x28 - set multiple tabstops
        #   0x1b 0x29 - clear multiple tabstops
        # TODO: handlers for this.
        self.ResetState();


    def __call__(self):
        return self

    def ResetState( self ):
        # this is basically copied from Table A-1/A-2 in the 
        # IWII Technical Reference Manual on page 134-135
        # (PDF page 153-154)
        self.state = { 
            "language"      : "American",
                # Italian, Danish, British, German, Swedish, French, Spanish

            "font"          : "draft",
                # draft
                # correspondence
                # nlq
            "fontwidth"     : "fixed",
                # fixed, proportional

            "pitch"         : 12, 
                #   9 extended
                #  10 pica
                #  12 elite
                #  13.4 semicondensed
                #  15 condensed
                #  17 ultracondensed

                # 144 dpi pica
                # 160 dpi elite prop

            "bit8"          : "ignore",
                # ignore high bit or not

            "charset"       : "ASCII",
                # ASCII, MouseText

            "printdirection": "bidirectional",  
                # bidirectional, unidirectional

            "selecged"      : True,
                # don't remnember what this is

            "color"         : "k",
                # c, m, y, k, o (ym), g(yc), p (mc)

            "ccharwid"      : 8,
                # 8, 16

            "lpi"           : 6,
                # 6, 8

            "leftmargin"    : 0,

            "linefeeding"   : "forward",
                # forward, reverse

            "paperoutsens"  : False,
            "insCRbeforeLF" : True,
            "LFwhenlinefull": False,
            "slashzeroes"   : False,

            # styling
            "doublewidth"   : False,
            "halfheight"    : False,
            "bold"          : False,
            "italic"        : False,
            "underline"     : False,
            "superscript"   : False,
            "subscript"     : False,
        };

    def PowerDown( self ):
        """ do all of the necessfary junk for pilot on the burner """
        self.CloseFile();

    def GetSeqLen( self, firstByte ):
        """ Go through the table above, and find the matching opcode.
            If we found it in the list, return the size byte from that
            So even if we get an escape code we're not handling, we know
            how big it is so we can ignore it
        """
        for l in self.eSeqLen:
            for kb in l[1]:
                if kb == firstByte:
                    return l[0]

        return 0

    def GetNewFilename( self ):
        """ determine the next filename to use """
        i = 0

        # get the integer based on sequential digits
        #if not os.path.isdir( "Printouts" ):
        #    os.makedirs( "Printouts" )
        # get the integer based on current time
        i = time.time()

        while os.path.exists( "Printouts/%04d.raw" % i ):
            i += 1

        return "Printouts/%04d.raw" % i;

    def CloseFile( self, renameTo = None ):
        """ close the open file, if any """
        if self.file == None:
            return; # nothing to do

        self.file.close()
        print( "{}: Ended.  {} bytes stored.".format( self.currentFilename, self.fSize ))

        if self.fSize == 0:
            print( "Removing empty file." )
            os.remove( self.currentFilename )

        else:

            # if a filename was passed in, rename the saved file 
            if not renameTo == None and len( renameTo ) > 0:
                nfn = "Printouts/{}".format( renameTo )
                os.rename( self.currentFilename, nfn )
                print( "--> renamed to {}".format( nfn ))

    def OpenFile( self ):
        """ open a new file for logging """
        self.currentFilename = self.GetNewFilename()

        print("\n{}: Starting new page".format( self.currentFilename ))
        self.file = open( self.currentFilename, "wb" ) 



    def TearOffPage( self, renameFilename = None ):
        """ tear off the existing page, and start a new one """
        self.CloseFile( renameFilename );
        self.OpenFile();

        if self.tick == 0:
            self.FlushLine()
            self.FlushLine()
        self.tick = 1

    def DirList( self, thePath, theExt ):
        theList = []
        i = 0
        for f in listdir( thePath ):
            filename, file_extension = os.path.splitext( f )
            if file_extension == theExt:
                theList.append( f )
                i += 1

        theList.sort()
        return theList

    def PrintList( self, theList ):
        for i in range( len( theList )):
            print( "    {:>2}: {}".format( i, theList[i] ))

    def Reprint( self, request, logging ):
        theList = self.DirList( self.Printouts, ".raw" )

        if( request == '' ):
            print( "No printout chosen.  Usage: r <number>" )
            self.PrintList( theList )
            return;

        try:
            request = int( request )
        except ValueError:
            print( "ERROR: {}: Bad number".format( request ))
            pass
            return

        if( request < 0  or request >= len( theList )):
            print( "ERROR: {}: Out of range 0..{}".format( request, len( theList )-1))
            return

        rFilename = "{}{}".format( self.Printouts, theList[ request ] )
        print( "--- Reprinting {} ---".format( rFilename ))

        file = open( rFilename, "rb" )
        fbyte = file.read(1)
        while fbyte:
            if logging:
                self.data_received( bytes( fbyte ))     # yes logging
            else :
                self.HandleByte( int( ord( fbyte )))   # no logging
            fbyte = file.read(1)
        file.close()
        print( "\n--- Done reprinting! ---" )


    def TimeTick( self ):
        """ time interval update """
        if self.tick == 0:
            self.FlushLine()
            self.FlushLine()
        self.tick = 1



    def FlushLine( self ):
        """ flush out the hex line """
        # fill in missing space..
        for i in range(  self.count, 16 ):
            if i == 8:
                sys.stdout.write( "  " )
            sys.stdout.write( "   " )
        # output the rest of the line..
        sys.stdout.write( "     " )
        sys.stdout.write( self.rbuf )
        sys.stdout.write( "\n" )
        self.rbuf = ""
        self.count = 0

    def Hex( self, ch ):
        h = format( ch, "x" )  # for '43'
        if len( h ) == 1:
            h = '0' + h
        return h


    def ClearEscapeSequence( self ):
        return [ 0, 0, 0, 0, 0, 0 ]


    def HandleControlCharacter( self, ch ):
        """ try handling a control character
        if we used it, return true
        otherwise return false
        """
        if ch == 0x04:
            print( "[EOT]" ) # End loading new character bitmaps

        elif ch == 0x08:
            print( "[BS]" ) # backspace
        elif ch == 0x09:
            print( "[TAB]" ) # tab

        elif ch == 0x0a:
            print( "[LF]" ) # feed paper one line (LF)
        elif ch == 0x0c:
            print( "[FF]" ) # Feed to next Top of page 
        elif ch == 0x0d:
            print( "[CR]" ) # Carriage Return

        elif ch == 0x0e:
            print( "[DW]" ) # Start double-width printing
        elif ch == 0x0f:
            print( "[SDW]" ) # Stop double-width printing

        elif ch == 0x11:
            print( "[XON]" ) # Select Printer * 
        elif ch == 0x13:
            print( "[XOFF]" ) # Deselect Printer
        elif ch == 0x18:
            print( "[CAN]" ) # cancel / Erase current l ine from print buffer

        else:
            return False

        return True


    def SerResponse( self, txt ):
        """ send back a response to the printing computer """
        if self.serialport == None:
            return
        self.serialport.write( txt );


    def CmdPrint( self, txt ):
        """ debug text to show when we get an inline command """
        self.SerResponse( '<{}>'.format( txt ) );


    def HandleEscapeSequence( self, seq ):
        """ When the code gets to here, we have a completed escape sequence. """

        # [0] is the base command. [1]..[5] are arguments.
        if( seq[0] == 0x63 ):   
            self.CmdPrint( "Reset Defaults" )
            self.ResetState()

        elif( seq[0] == 0x3F ):   
            self.CmdPrint( "Send ID String" )
            # IW10CF
            # | | |+--- Sheet feeder installed
            # | | +---- Color ribbon in place
            # | +------ 10 inch carriage
            # +-------- ImageWriter printer

            if not self.serialport == None:
                self.SerResponse( "IW10C" ) 
                # not sure if \n or \r are needed for this. need to test.

        elif( seq[0] >= 0x01 and seq[0] <= 0x06 ):
            self.CmdPrint( "Insert {} dot spaces".format( seq[0]) )

        elif( seq[0] == 0x24 ):   self.CmdPrint( "Switch to Standard ASCII characters *" )
        elif( seq[0] == 0x26 ):   self.CmdPrint( "Remap MouseText To Low Ascii" )
        elif( seq[0] == 0x27 ):   self.CmdPrint( "Switch to custom character font" )
        elif( seq[0] == 0x2a ):   self.CmdPrint( "Switch to custom character font (high vals)" )
        elif( seq[0] == 0x2b ):   self.CmdPrint( "Max width of custom chars: 16 dots")
        elif( seq[0] == 0x2d ):   self.CmdPrint( "Max width of custom chars: 8 dots *" )
        
        elif( seq[0] == 0x58 ):   self.CmdPrint( "Start Underline" )
        elif( seq[0] == 0x59 ):   self.CmdPrint( "Stop Underline *" )
        elif( seq[0] == 0x21 ):   self.CmdPrint( "Start Bold" )
        elif( seq[0] == 0x22 ):   self.CmdPrint( "Stop Bold *" )

        elif( seq[0] == 0x77 ):   self.CmdPrint( "Start Half-Height" )
        elif( seq[0] == 0x57 ):   self.CmdPrint( "Stop Half-Height *" )
        
        elif( seq[0] == 0x78 ):   self.CmdPrint( "Start Superscript" )
        elif( seq[0] == 0x79 ):   self.CmdPrint( "Start Subscript" )
        elif( seq[0] == 0x7a ):   self.CmdPrint( "Stop Super/Subscript *" )
        

        elif( seq[0] == 0x6e ):   self.CmdPrint( "9 cpi - extended" )
        elif( seq[0] == 0x4e ):   self.CmdPrint( "10 cpi - pica" )
        elif( seq[0] == 0x45 ):   self.CmdPrint( "12 cpi - elite" )
        elif( seq[0] == 0x65 ):   self.CmdPrint( "13.4 cpi - semicondensed" )
        elif( seq[0] == 0x71 ):   self.CmdPrint( "15 cpi - condensed" )
        elif( seq[0] == 0x51 ):   self.CmdPrint( "17 cpi - ultracondensed" )
        
        elif( seq[0] == 0x70 ):   self.CmdPrint( "144 dpi - pica proportional" )
        elif( seq[0] == 0x50 ):   self.CmdPrint( "160 cpi - elite proportional" )
        
        elif( seq[0] == 0x41 ):   self.CmdPrint( "6 lines per inch *" )
        elif( seq[0] == 0x42 ):   self.CmdPrint( "8 lines per inch" )
        elif( seq[0] == 0x54 ):   self.CmdPrint( "Distance between lines" )
        
        elif( seq[0] == 0x66 ):   self.CmdPrint( "Forward line feeding *" )
        elif( seq[0] == 0x72 ):   self.CmdPrint( "Reverse line feeding" )
        elif( seq[0] == 0x76 ):   self.CmdPrint( "Set TOF to current pos" )
        
        elif( seq[0] == 0x3e ):   self.CmdPrint( "Unidirectional printing" )
        elif( seq[0] == 0x3c ):   self.CmdPrint( "Bidirectional printing *" )
        
        elif( seq[0] == 0x4f ):   self.CmdPrint( "Paper out sensor off" )
        elif( seq[0] == 0x6f ):   self.CmdPrint( "Paper out sensor on *" )

        elif( seq[0] == 0x28 ):   self.CmdPrint( "Set Tabstops" )
        elif( seq[0] == 0x75 ):   self.CmdPrint( "Set One Tabstop" )
        elif( seq[0] == 0x29 ):   self.CmdPrint( "Clear Tabstops" )
        elif( seq[0] == 0x30 ):   self.CmdPrint( "Clear All Tabs" )

        elif( seq[0] == 0x6c ):
            if( seq[1] == 0x30 ):
                self.CmdPrint( "Insert CR before LF and FF *" )
            elif( seq[1] == 0x31 ): 
                self.CmdPrint( "No CR before LF and FF" )

        elif( seq[0] == 0x49 ):
            self.CmdPrint( "Start Load custom characters" )
            # ends with 0x04

        elif( seq[0] == 0x46 ):
            self.CmdPrint( "Place Print Head from left margin" )
        elif( seq[0] == 0x73 ):
            self.CmdPrint( "Set dot spacing to {}".format( seq[1] ))
        elif( seq[0] == 0x47 ):
            self.CmdPrint( "Print a line of graphics" )
        elif( seq[0] == 0x53 ):
            self.CmdPrint( "Print a line of graphics" )
        elif( seq[0] == 0x67 ):
            self.CmdPrint( "Print a line of graphics *8" )
        elif( seq[0] == 0x56 ):
            self.CmdPrint( "Print repetitions of dots" )
        
        elif( seq[0] == 0x52 ):
            self.CmdPrint( "Repeat character N times" )
        
        elif( seq[0] == 0x61 ):
            if( seq[1] == 0x30 ):
                self.CmdPrint( "FONT: Correspondence" )
            elif( seq[1] == 0x31 ):
                self.CmdPrint( "FONT: Draft *" )
            elif( seq[1] ==  0x32 ):
                self.CmdPrint( "FONT: NLQ" )
        elif( seq[0] == 0x6d ):
            self.CmdPrint( "FONT: Correspondence" )
        elif( seq[0] == 0x4d ):
            self.CmdPrint( "FONT: Draft *" )


        elif( seq[0] == 0x44 ):
            if( seq[1] == 0x00 and seq[2] == 0x20 ):
                self.CmdPrint( "IGNORE 8th data bit *" )
            # additional ones will set character sets.

        elif( seq[0] == 0x5A ):
            if( seq[1] == 0x00 and seq[2] == 0x20 ):
                self.CmdPrint( "INCLUDE 8th data bit" )
            # additional ones will set character sets.

        elif( seq[0] == 0x4c ):
            self.CmdPrint( "Set left margin..." )
        elif( seq[0] == 0x48 ):
            self.CmdPrint( "Set page length..." )

        elif( seq[0] == 0x4b ):
            if( seq[1] == 0x30 ): 
                self.CmdPrint( "Color: Black *" )
            elif( seq[1] == 0x31 ): 
                self.CmdPrint( "Color: Yellow" )
            elif( seq[1] == 0x32 ): 
                self.CmdPrint( "Color: Magenta" )
            elif( seq[1] == 0x33 ): 
                self.CmdPrint( "Color: Cyan" )
            elif( seq[1] == 0x34 ): 
                self.CmdPrint( "Color: Orange (YM)" )
            elif( seq[1] == 0x35 ): 
                self.CmdPrint( "Color: Green (YC)" )
            elif( seq[1] == 0x36 ): 
                self.CmdPrint( "Color: Purple (MC)" )

        elif( seq[0] >= 0x31 and seq[0] < 0x3f ):
            self.CmdPrint( "Feed {} lines blank paper".format( seq[0] - 0x30 ))

        else:
            self.CmdPrint( "UNK ESC: {} {} {} {} {} {} \n".format( 
                self.Hex( seq[0] ), self.Hex( seq[1] ), 
                self.Hex( seq[2] ), self.Hex( seq[3] ),  
                self.Hex( seq[4] ), self.Hex( seq[5] ), ))


    def HandleByte( self, ch ):
        """ primary valve for the stream of data bytes from the printing computer """

        self.tick = 0;
        # python3 - ch is of type 'int'

        # filter out high bit
        #ch = chr( ord( ch ) & 0x7f)

        if self.escRemaining > 0:
            if self.escRemaining == 999:
                # it's the first one in the sequence... we need to set it up
                self.escRemaining = self.GetSeqLen( ch )
                if self.escRemaining == 0:
                    # unknown
                    print( "ERROR: Bad Escape sequence {}".format( ch ))
                    return

            # we know it, so set it up
            self.escRemaining = self.escRemaining - 1
            self.escSequence[ self.escIdx ] = ch
            self.escIdx = self.escIdx + 1

            # check if we've got the whole expected sequence
            if self.escRemaining == 0:
                # yep! hand it off!
                self.HandleEscapeSequence( self.escSequence )
        else:
            if ch == 0x1b: 
                # it's the start of an escape sequence
                # prep for accumulating it...
                self.escRemaining = 999 # determine
                self.escSequence = self.ClearEscapeSequence()
                self.escIdx = 0

                # now determine how big the thing is.
            else:
                if not self.HandleControlCharacter( ch ):
                    # it's boring content. just output it. or something
                    sys.stdout.write( chr(ch) )
                    sys.stdout.flush()


    def data_received(self, data):
        """ input from the serial stream """

        # send it to our handler
        for ch in data:
            self.HandleByte( ch )

        # also log it to the output file
        if not self.file == None:
            self.file.write( data )
            self.fSize += 1



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

class LlamaWriterApp():

    def __init__(self):

        print( '## LlamaWriter - An ImageWriterII simulator of sorts.' )
        print( '##    v{} {}'.format( VERSION, VERS_DATE ))
        print( '##   (c) Scott Lawrence - yorgle@gmail.com' )

    def __call__(self):
        return self

    def ParseArgs( self ):
        """ Read the command line arguments """

        import argparse
        parser = argparse.ArgumentParser(
            description='Handle ImageWriter print sequences.',
            epilog="""\
    Pretend to be a printer.
    """)

        parser.add_argument(
            'SERIALPORT',
            nargs='?',
            help="serial port name",
            default=False)

        parser.add_argument(
            'BAUDRATE',
            type=int,
            nargs='?',
            help='set baud rate, default: %(default)s',
            default=9600)

        parser.add_argument(
            '-q', '--quiet',
            action='store_true',
            help='suppress non error messages',
            default=False)

        parser.add_argument(
            '-s', '--silent',
            action='store_true',
            help='disable audio playback',
            default=True)

        parser.add_argument(
            '--develop',
            action='store_true',
            help='Development mode, prints Python internals on errors',
            default=False)

        group = parser.add_argument_group('serial port')

        group.add_argument(
            "--bytesize",
            choices=[5, 6, 7, 8],
            type=int,
            help="set bytesize, one of {5 6 7 8}, default: 8",
            default=8)

        group.add_argument(
            "--parity",
            choices=['N', 'E', 'O', 'S', 'M'],
            type=lambda c: c.upper(),
            help="set parity, one of {N E O S M}, default: N",
            default='N')

        group.add_argument(
            "--stopbits",
            choices=[1, 1.5, 2],
            type=float,
            help="set stopbits, one of {1 1.5 2}, default: 1",
            default=1)

        group.add_argument(
            '--rtscts',
            action='store_true',
            help='enable RTS/CTS flow control (default off)',
            default=False)

        group.add_argument(
            '--xonxoff',
            action='store_true',
            help='enable software flow control (default off)',
            default=False)

        group.add_argument(
            '--rts',
            type=int,
            help='set initial RTS line state (possible values: 0, 1)',
            default=None)

        group.add_argument(
            '--dtr',
            type=int,
            help='set initial DTR line state (possible values: 0, 1)',
            default=None)

        self.args = parser.parse_args()


        if not self.args.silent:
            audio = LlamaAudio( True )
        else:
            audio = LlamaAudio( False )


    def StartOffline( self ):
        self.runmode = 'offline'
        self.serial_worker = None

        if not self.args.quiet:
            sys.stderr.write( 
                '\n'
                ' >>  Operating in offline mode using "Printouts/" directory\n'
                ' >>  Ctrl-C / BREAK / [q] to quit, [?] for help\n' 
                )


    def StartWithSerial( self, worker ):
        self.runmode = 'serial'
        self.serial_worker = worker

        # connect to serial port
        self.ser = serial.serial_for_url(args.SERIALPORT, do_not_open=True)

        self.ser.baudrate = self.args.BAUDRATE
        self.ser.bytesize = self.args.bytesize
        self.ser.parity = self.args.parity
        self.ser.stopbits = self.args.stopbits
        self.ser.rtscts = self.args.rtscts
        self.ser.xonxoff = self.args.xonxoff

        if self.args.rts is not None:
            self.ser.rts = self.args.rts

        if self.args.dtr is not None:
            self.ser.dtr = self.args.dtr

        if not self.args.quiet:
            sys.stderr.write(
                ' >>  Operating on {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits} ---\n'
                ' >>  Ctrl-C / BREAK / [q] to quit, [?] for help\n'.format(p=ser))

        try:
            self.ser.open()
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(self.ser.name, e))
            sys.exit(1)

        # attach the worker

        self.serial_worker = serial.threaded.ReaderThread( ser, self.iw_protocol_handler )
        # ser_to_net = SerialToNet()
        # serial_worker = serial.threaded.ReaderThread(ser, ser_to_net)
        self.iw_protocol_handler.serialport = serial
        self.serial_worker.start()



    def DoTheThing( self ):
        """ the runloop """

        # if a port was specified, use it.
        if self.args.SERIALPORT is False:
            try:
                self.args.SERIALPORT = self.RequestPortOrDirectory()
            except:
                pass
                print( "Unable to configure interface." )
                print( "Exiting." )
                return;

        # spin up a protocol handler
        self.iw_protocol_handler = IWProtocolHandler();

        # start either offline (reprint mode) or online (serial mode)
        if os.path.isdir( self.args.SERIALPORT ):
            self.StartOffline()
        else:
            self.StartWithSerial( self.iw_protocol_handler )


        # the main run loop..
        try:
            intentional_exit = False
            print( "\nReady." )

            # sit in this loop until we need to quit
            while True:
                try:

                    cmd = input( ">: " ) # does this make you feel lost?
                    arg = ''

                    if len( cmd ) > 1:
                        arg = cmd[1:].strip()

                    if cmd == "": # do nothing
                        print( "" ) 

                    elif cmd[0] == '?': # help
                        print( "Commands: " )
                        print( "   q          Quit" );
                        print( "   r          List available RAW files to reprint" );
                        print( "   r<NUMBER>  Reprint the specified captured printout" );
                        print( "   R<NUMBER>  Reprint with RAW logging" );
                        print( "   t          tear off page, saving it based on timestamp" );
                        print( "   t<NAME>   ... or save it as Printouts/<NAME>" );

                    elif cmd[0] == "t": # tear off page
                        self.iw_protocol_handler.TearOffPage( arg )

                    elif cmd[0] == "r": # reprint a file
                        self.iw_protocol_handler.Reprint( arg, False )

                    elif cmd[0] == "R": # reprint a file
                        self.iw_protocol_handler.Reprint( arg, True )

                    elif cmd[0] == "q": # quit
                        intentional_exit = True
                        raise KeyboardInterrupt

                    else: 
                        print( "{}: Unknown command.".format( cmd ))

                    #time.sleep(4)

                except KeyboardInterrupt:
                        intentional_exit = True
                        raise

        except KeyboardInterrupt:
            pass

        # make sure any files are closed
        self.iw_protocol_handler.PowerDown()

        # shut down the serial worker.
        if self.runmode == 'serial':
            self.serial_worker.stop()



    def RequestPortOrDirectory( self ):
        """\
        Show a list of ports and ask the user for a choice. To make selection
        easier on systems with long device names, also allow the input of an
        index.
        """
        sys.stderr.write('\n--- Source selection options:\n')
        ports = []

        sys.stderr.write('--- {:2}: {:20} {!r} (default)\n'.format(0, 'Printouts/', 'printout directory'))

        for n, (port, desc, hwid) in enumerate(sorted(comports()), 1):
            sys.stderr.write('--- {:2}: {:20} {!r}\n'.format(n, port, desc))
            ports.append(port)

        while True:
            #port = input('--- Enter port index, full name, directory, or hit return:\n ?> ')
            port = input('--- Enter port index, or hit return (0):\n ?> ')

            try:
                chosenNo = 0
                chosenNo = int( port )
            except:
                pass

            if port == '' or port == '0':
                return 'Printouts/'

            try:
                index = chosenNo - 1
                if not 0 <= index < len(ports):
                    sys.stderr.write( " *** Invalid selection!\n" )
                    continue

            except ValueError:
                pass
            else:
                port = ports[index]

            return port



if __name__ == '__main__': 

    # instantiate our application itself
    llamawriter = LlamaWriterApp()

    # parse the command line arguments
    llamawriter.ParseArgs()

    # do the runloop
    llamawriter.DoTheThing()

    sys.stderr.write('\n--- exiting ---\n')
