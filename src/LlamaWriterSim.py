#!/usr/bin/env python3
#
# LlamaWriterSim - An ImageWriter II simulator of sorts
#
#   (c)2021 Scott Lawrence / yorgle@gmail.com
#


VERSION = '0.02'
VERS_DATE = '2021-07-19'

# v0.02 - 2021-07-19 - Added reprinting
# v0.01 - 2021-07-18 - indev version


import sys
import serial
import serial.threaded
import time
import os

from serial.tools.list_ports import comports
from serial.tools import hexlify_codec

from os import listdir
from os.path import isfile, join


class LlamaWriterSim( serial.threaded.Protocol ):
    """serial/file to file/outputs/etc"""

    def __init__(self):
        self.count = 0
        self.tick = 0
        self.rbuf = ""

        self.file = None
        self.fSize = 0

        self.Printouts = "Printouts/"

        # esc - escaped 
        self.escRemaining = 0        # number of chars left in escape sequence
        # if it's 0, pass characters through...
        self.escIdx = 0
        self.escSequence = self.ClearEscapeSequence()

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
        #
        #   0x1F N    - feed 1..15 lines 1-9 : ; = > ?

    def __call__(self):
        return self


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

    def Reprint( self, request ):
        theList = self.DirList( self.Printouts, ".raw" )

        if( request == '' ):
            print( "No printout selected.  Usage: r <number>" )
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
            self.HandleByte( int( ord( fbyte )))
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
            print( "[EOT]" ) #End loading new characters" )

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


    def HandleEscapeSequence( self, seq ):
        """ When the code gets to here, we have a completed escape sequence. """

        # [0] is the base command. [1]..[5] are arguments.
        if( seq[0] == 0x63 ):   print( "Reset Defaults" )
        elif( seq[0] == 0x3F ):   print( "Send ID String" )

        elif( seq[0] >= 0x01 and seq[0] <= 0x06 ):
            print( "Insert {} dot spaces".format( seq[0]) )

        elif( seq[0] == 0x24 ):   print( "Switch to Standard ASCII characters *" )
        elif( seq[0] == 0x26 ):   print( "Remap MouseText To Low Ascii" )
        elif( seq[0] == 0x27 ):   print( "Switch to custom character font" )
        elif( seq[0] == 0x2a ):   print( "Switch to custom character font (high vals)" )
        elif( seq[0] == 0x2b ):   print( "Max width of custom chars: 16 dots")
        elif( seq[0] == 0x2d ):   print( "Max width of custom chars: 8 dots *" )
        
        elif( seq[0] == 0x58 ):   print( "Start Underline" )
        elif( seq[0] == 0x59 ):   print( "Stop Underline *" )
        elif( seq[0] == 0x21 ):   print( "Start Bold" )
        elif( seq[0] == 0x22 ):   print( "Stop Bold *" )

        elif( seq[0] == 0x77 ):   print( "Start Half-Height" )
        elif( seq[0] == 0x57 ):   print( "Stop Half-Height *" )
        
        elif( seq[0] == 0x78 ):   print( "Start Superscript" )
        elif( seq[0] == 0x79 ):   print( "Start Subscript" )
        elif( seq[0] == 0x7a ):   print( "Stop Super/Subscript *" )
        

        elif( seq[0] == 0x6e ):   print( "9 cpi - extended" )
        elif( seq[0] == 0x4e ):   print( "10 cpi - pica" )
        elif( seq[0] == 0x45 ):   print( "12 cpi - elite" )
        elif( seq[0] == 0x65 ):   print( "13.4 cpi - semicondensed" )
        elif( seq[0] == 0x71 ):   print( "15 cpi - condensed" )
        elif( seq[0] == 0x51 ):   print( "17 cpi - ultracondensed" )
        
        elif( seq[0] == 0x70 ):   print( "144 dpi - pica proportional" )
        elif( seq[0] == 0x50 ):   print( "160 cpi - elite proportional" )
        
        elif( seq[0] == 0x41 ):   print( "6 lines per inch *" )
        elif( seq[0] == 0x42 ):   print( "8 lines per inch" )
        elif( seq[0] == 0x54 ):   print( "Distance between lines" )
        
        elif( seq[0] == 0x66 ):   print( "Forward line feeding *" )
        elif( seq[0] == 0x72 ):   print( "Reverse line feeding" )
        elif( seq[0] == 0x76 ):   print( "Set TOF to current pos" )
        
        elif( seq[0] == 0x3e ):   print( "Unidirectional printing" )
        elif( seq[0] == 0x3c ):   print( "Bidirectional printing *" )
        
        elif( seq[0] == 0x4f ):   print( "Paper out sensor off" )
        elif( seq[0] == 0x6f ):   print( "Paper out sensor on *" )

        elif( seq[0] == 0x28 ):   print( "Set Tabstops" )
        elif( seq[0] == 0x75 ):   print( "Set One Tabstop" )
        elif( seq[0] == 0x29 ):   print( "Clear Tabstops" )
        elif( seq[0] == 0x30 ):   print( "Clear All Tabs" )

        elif( seq[0] == 0x6c ):
            if( seq[1] == 0x30 ):
                print( "Insert CR before LF and FF *" )
            elif( seq[1] == 0x31 ): 
                print( "No CR before LF and FF" )

        elif( seq[0] == 0x49 ):
            print( "Start Load custom characters" )
            # ends with 0x04

        elif( seq[0] == 0x46 ):
            print( "Place Print Head from left margin" )
        elif( seq[0] == 0x73 ):
            print( "Set dot spacing to {}".format( seq[1] ))
        elif( seq[0] == 0x47 ):
            print( "Print a line of graphics" )
        elif( seq[0] == 0x53 ):
            print( "Print a line of graphics" )
        elif( seq[0] == 0x67 ):
            print( "Print a line of graphics *8" )
        elif( seq[0] == 0x56 ):
            print( "Print repetitions of dots" )
        
        elif( seq[0] == 0x52 ):
            print( "Repeat character N times" )
        
        elif( seq[0] == 0x61 ):
            if( seq[1] == 0x30 ):
                print( "FONT: Correspondence" )
            elif( seq[1] == 0x31 ):
                print( "FONT: Draft *" )
            elif( seq[1] ==  0x32 ):
                print( "FONT: NLQ" )
        elif( seq[0] == 0x6d ):
            print( "FONT: Correspondence" )
        elif( seq[0] == 0x4d ):
            print( "FONT: Draft *" )


        elif( seq[0] == 0x44 ):
            if( seq[1] == 0x00 and seq[2] == 0x20 ):
                print( "IGNORE 8th data bit *" )
            # additional ones will set character sets.

        elif( seq[0] == 0x5A ):
            if( seq[1] == 0x00 and seq[2] == 0x20 ):
                print( "INCLUDE 8th data bit" )
            # additional ones will set character sets.

        elif( seq[0] == 0x4c ):
            print( "Set left margin..." )
        elif( seq[0] == 0x48 ):
            print( "Set page length..." )

        elif( seq[0] == 0x4b ):
            if( seq[1] == 0x30 ): 
                print( "Color: Black *" )
            elif( seq[1] == 0x31 ): 
                print( "Color: Yellow" )
            elif( seq[1] == 0x32 ): 
                print( "Color: Magenta" )
            elif( seq[1] == 0x33 ): 
                print( "Color: Cyan" )
            elif( seq[1] == 0x34 ): 
                print( "Color: Orange (YM)" )
            elif( seq[1] == 0x35 ): 
                print( "Color: Green (YC)" )
            elif( seq[1] == 0x36 ): 
                print( "Color: Purple (MC)" )

        elif( seq[0] >= 0x31 and seq[0] < 0x3f ):
            print( "Feed {} lines blank paper".format( seq[0] - 0x30 ))

        else:
            sys.stdout.write( "UNK ESC: {} {} {} {} {} {} \n".format( 
            self.Hex( seq[0] ), self.Hex( seq[1] ), 
            self.Hex( seq[2] ), self.Hex( seq[3] ),  
            self.Hex( seq[4] ), self.Hex( seq[5] ), ))


    def HandleByte( self, ch ):
        """ primary valve for the stream of bytes """
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

        # and log it to the output file
        if not self.file == None:
            self.file.write( data )
            self.fSize += 1



# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def RequestPortOrDirectory():
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
        port = input('--- Enter port index, full name, directory, or hit return: ')

        if port == '' or int( port ) == 0:
            return 'Printouts/'

        try:
            index = int(port) - 1
            if not 0 <= index < len(ports):
                sys.stderr.write('--- Invalid index!\n')
                continue
        except ValueError:
            pass
        else:
            port = ports[index]

        return port



if __name__ == '__main__':  # noqa
    import argparse

    print( '## LlamaWriterSim - An ImageWriterII simulator of sorts.' )
    print( '##    v{} {}'.format( VERSION, VERS_DATE ))
    print( '##   (c) Scott Lawrence - yorgle@gmail.com' )

    parser = argparse.ArgumentParser(
        description='Handle IW2 escape sequences.',
        epilog="""\
First attempt at making this thing do the thing.
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



    args = parser.parse_args()

    if args.SERIALPORT is False:
        args.SERIALPORT = RequestPortOrDirectory()

    runmode = None
    serial_worker = None

    if os.path.isdir( args.SERIALPORT ):
        runmode = 'offline'

        if not args.quiet:
            sys.stderr.write( 
                '\n'
                ' >>  Operating in offline mode using "Printouts/" directory\n'
                ' >>  Ctrl-C / BREAK / [q] to quit, [?] for help\n' 
                )

    else:
        runmode = 'serial'

        # connect to serial port
        ser = serial.serial_for_url(args.SERIALPORT, do_not_open=True)

        ser.baudrate = args.BAUDRATE
        ser.bytesize = args.bytesize
        ser.parity = args.parity
        ser.stopbits = args.stopbits
        ser.rtscts = args.rtscts
        ser.xonxoff = args.xonxoff

        if args.rts is not None:
            ser.rts = args.rts

        if args.dtr is not None:
            ser.dtr = args.dtr

        if not args.quiet:
            sys.stderr.write(
                ' >>  Operating on {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits} ---\n'
                ' >>  Ctrl-C / BREAK / [q] to quit, [?] for help\n'.format(p=ser))

        try:
            ser.open()
        except serial.SerialException as e:
            sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
            sys.exit(1)

    # both need the handler.
    llamawriter_sim = LlamaWriterSim();

    # if we're in serial mode, connect this object to the serial port.
    if runmode == 'serial':
        serial_worker = serial.threaded.ReaderThread(ser, llamawriter_sim)
        # ser_to_net = SerialToNet()
        # serial_worker = serial.threaded.ReaderThread(ser, ser_to_net)
        serial_worker.start()

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
                    print( "   t          tear off page, saving it based on timestamp" );
                    print( "   t<NAME>   ... or save it as Printouts/<NAME>" );

                elif cmd[0]  == "t": # tear off page
                    llamawriter_sim.TearOffPage( arg )

                elif cmd[0]  == "r": # reprint a file
                    llamawriter_sim.Reprint( arg )

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
    llamawriter_sim.CloseFile( None )

    # shut down the serial worker.
    if runmode == 'serial':
        serial_worker.stop()


    sys.stderr.write('\n--- exit ---\n')
