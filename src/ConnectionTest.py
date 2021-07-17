#!/usr/bin/env python
#
# Dump out contents to screen
# optionally kill bit 8

import sys
import serial
import serial.threaded
import time


class SerialToScreen(serial.threaded.Protocol):
    """serial->display"""

    def __init__(self):
        self.count = 0
        self.rbuf = ""

    def __call__(self):
        return self

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

    def HandleChar( self, ch ):

        # filter out high bit
        ch = chr( ord( ch ) & 0x7f)


        #h = hex( ord( ch ))        # for '0x43;
        h = format(ord( ch ), "x")  # for '43'
        if ord( ch ) < 16:
            h = '0' + h

        sys.stdout.write( "{} ".format( h ))

        self.count = self.count +1

        if ord( ch ) >= 0x20 and ord( ch ) <= 0x7f:
            self.rbuf = self.rbuf + ch
        else: 
            self.rbuf = self.rbuf + '.'

        if self.count == 8:
            sys.stdout.write( "  " )
            self.rbuf = self.rbuf + ' '

        if self.count > 15:
            self.FlushLine()


    def data_received(self, data):
        for idx in range(0, len(data)):
            self.HandleChar( data[idx] )



if __name__ == '__main__':  # noqa
    import argparse

    parser = argparse.ArgumentParser(
        description='Connect and do tests as a printer. or something.',
        epilog="""\
This is not meant to be a final product. just a testbed.
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
                ser_to_screen.FlushLine()
                ser_to_screen.FlushLine()


            except KeyboardInterrupt:
                    intentional_exit = True
                    raise

    except KeyboardInterrupt:
        pass

    sys.stderr.write('\n--- exit ---\n')
    serial_worker.stop()