#!/usr/bin/env python
#
# Handle control codes. (test)

import sys
import serial
import serial.threaded
import time


class SerialToScreen(serial.threaded.Protocol):
    """serial->display"""

    def __init__(self):
        self.count = 0
        self.tick = 0
        self.rbuf = ""

        # esc - escaped 
        self.escRemaining = 0        # number of chars left in escape sequence
        # if it's 0, pass characters through...
        self.escIdx = 0
        self.escSequence = [0,0,0,0] # escape sequence

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
                0x61,   # select font
                0x6c,   # CR/LF toggles
                0x4b,   # Color '0..6': K, Y, M, C, orn(YM), grn(YC), pur(MC)
                ]
            ],
            [ 3, [ # these have two additional parameters
                0x44,   # keyboard, bit select, dipswitches, perf skip
                0x5a,   # more of the same
                0x73,   # dot spacings
                0x54,   # distance between lines NN/144 inch
                0x67,   # print line of graphics NNNx8 bytes
                ]
            ],
            [ 4, [ # these hsve 3 additional parameters
                0x4c,   # set left margin  000
                ]
            ],
            [ 5, [ # these hsve 4 additional parameters
                0x48,   # set page length 0001-9999
                0x46,   # place print head NNNN dot cols from left margin
                0x47,   # print line of graphics NNNN
                0x53,   # same as 0x47
                ]
            ],
            [ 6, [ # these hsve 5 additional parameters
                0x75,   # set one tab stop
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

    def TimeTick( self ):
        if self.tick == 0:
            ser_to_screen.FlushLine()
            ser_to_screen.FlushLine()
        self.tick = 1

    def FlushLine( self ):
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
        return format(ord( ch ), "x")  # for '43'


    def HandleEscapeSequence( self, seq ):
        sys.stdout.write( "\nESC SEQ: {} {} {} {}\n".format( 
            self.Hex( seq[0] ), self.Hex( seq[1] ), 
            self.Hex( seq[2] ), self.Hex( seq[3] ), ))


    def HandleChar( self, ch ):
        self.tick = 0;

        # filter out high bit
        #ch = chr( ord( ch ) & 0x7f)


        if self.escRemaining > 0:
            self.escRemaining = self.escRemaining - 1
            self.escSequence[ self.escIdx ] = ch
            self.escIdx = self.escIdx + 1

            if self.escRemaining == 0:
                self.HandleEscapeSequence( self.escSequence )
        else:
            oc = ord(ch)
            if oc == 0x27: 
                sys.stdout.write( "[ESC]" )
                # it's the start of an escape sequence
                # prep for accumulating it...
                self.escRemaining = 0 # determine
                self.escSequence = [ '\0','\0','\0','\0' ]
                self.escIdx = 0

                # now determine how big the thing is.
            else:
                # it's boring content. just output it.
                sys.stdout.write( ch )


    def data_received(self, data):
        # we got a string of bytes, or perhaps of just one byte
        # so we need to handle each character individually
        for idx in range(0, len(data)):
            self.HandleChar( data[idx] )



if __name__ == '__main__':  # noqa
    import argparse

    parser = argparse.ArgumentParser(
        description='Handle IW2 escape sequences.',
        epilog="""\
First attempt at making this thing do the thing.
""")

    parser.add_argument(
        'SERIALPORT',
        help="serial port name")

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
            '--- Serial Snoop on {p.name}  {p.baudrate},{p.bytesize},{p.parity},{p.stopbits} ---\n'
            '--- type Ctrl-C / BREAK to quit\n'.format(p=ser))

    try:
        ser.open()
    except serial.SerialException as e:
        sys.stderr.write('Could not open serial port {}: {}\n'.format(ser.name, e))
        sys.exit(1)

    ser_to_screen = SerialToScreen();
    serial_worker = serial.threaded.ReaderThread(ser, ser_to_screen)

    # ser_to_net = SerialToNet()
    # serial_worker = serial.threaded.ReaderThread(ser, ser_to_net)
    serial_worker.start()

    try:
        intentional_exit = False
        sys.stdout.write( "Starting serial loop" )

        while True:
            try:
                time.sleep(4)
                ser_to_screen.TimeTick()


            except KeyboardInterrupt:
                    intentional_exit = True
                    raise

    except KeyboardInterrupt:
        pass

    sys.stderr.write('\n--- exit ---\n')
    serial_worker.stop()
