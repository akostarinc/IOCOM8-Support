#!/usr/bin/env python3
#
# Please see the ORIGINAL supporting documentation at:
#     https://python-can.readthedocs.io/en/develop/interfaces/robotell.html
#
#   If the 'pip install python-can' does not have the robotell code, install it from:
#
#   https://github.com/hardbyte/python-can
#
# History:
#       Fri 16.Jul.2021         initial
#       Mon 18.Oct.2021         added protocol description
#
# By the time you read this, the robotell code may be integrated)

from __future__ import absolute_import
from __future__ import print_function

import array, time, threading, getopt, sys
import can, can.interfaces

# Just in case one needs to know
#print(dir(can.interfaces))
#print (can.interfaces.BACKENDS)

# ------------------------------------------------------------------------
# Basic comm definitions to can  (replicated from can.h Fri 16.Jul.2021)

MSG_SWITCHES  =  0x19EE5501  #// Intra IOCOMx msg to funnel to RF
MSG_RFTOCAN   =  0x19EE5502  #// Intra IOCOMx msg via RF
MSG_RELAYS    =  0x19EE5503  #// Control local relays
MSG_BRIDGE    =  0x19EE5504  #// Control remote relays (note: timeout)

class _globals:
    msgid    =  MSG_RELAYS
    msgmask  =  MSG_BRIDGE

globx = _globals()

serport     = '/dev/ttyUSB0'
bitrate     = 250000
ifacename   = 'robotell'

maskx   = 0
valuex  = 0
ordx    = 0

pgdebug = 0
verbose = 0
listen  = 0
bridge  = 0
count = 0

old_rx = can.Message()

# ------------------------------------------------------------------------
# Convert in str NNN and  0xNNN str to number

def hexint(nnn):
    if nnn[:2].lower() == "0x":
        return int(nnn[2:], 16)
    elif nnn[:2].lower() == "0y" or nnn[:2].lower() == "0b":
        return int(nnn[2:], 2)
    else:
        return int(nnn)

def pdevices():
    print ("Valid CAN interfaces:")
    for aa in can.interfaces.VALID_INTERFACES:
        print(aa, end = " ")
    print()

def _(aa):
    return aa

# ------------------------------------------------------------------------

def receive(bus, stop_event):
    """The loop for receiving."""

    if verbose:
        print("Start receiving messages")

    global old_rx, count

    while not stop_event.is_set():
        rx_msg = bus.recv(1)
        if rx_msg is not None:
            if rx_msg.data != old_rx.data:
                print("rx:{0} {1}\n".format(count, rx_msg))
                count = 0
                old_rx = rx_msg
            else:
                #print("filtered", rx_msg.data)
                count += 1
    if verbose:
        print("Stopped receiving messages")

# ------------------------------------------------------------------------

def sendit(bus, messagex):

    if messagex is not None:
        if verbose:
            print("tx: {}".format(messagex))
        pass
    if verbose:
        print("sending:", hex(messagex.arbitration_id), messagex.data)
        #print("globals", hex(globx.msgid))
        pass
    bus.send(messagex, timeout=0)
    #time.sleep(0.250)

# ------------------------------------------------------------------------

def is_allzero(msgx):

    allzero = 1
    for aa in msgx.data:
        if aa: allzero = 0
    return allzero

# ------------------------------------------------------------------------

def send_vals(bus, strx):


    # If passed as one argument, split it
    if len(strx) == 1:
        strx = str.split(strx[0])

    if pgdebug > 2:
        print("processing: ", strx)

    arr2 = []
    for aa in strx:
        arr2.append(hexint(aa))
    arr2.append((arr2[0]^0x55) & 0xff)            # Checksum

    # Second integer blank (may contain random number on the IOCOMx)
    for aa in range(4):
        arr2.append(0)

    if bridge:
        globx.msgid = MSG_BRIDGE
        #print("doing bridge, mask", hex(globx.msgmask))

    if verbose:
        print("Sending", arr2)

    cnt = 0

    # The original was a loop ...
    while True:
        # Send value
        message2 = can.Message(arbitration_id=globx.msgid, is_extended_id=True,
                            check=True, data=arr2)
        sendit(bus, message2)
        break

        #if not bridge:
        #    break;
        #if bridge and not cnt:
        #    print("Sustaining BRIDGE transmission, CTRL-C to exit ... ")
        #    sys.stdout.flush()
        #cnt+= 1
        #
        #if is_allzero(message2):
        #    break

def errexit(err_str, exitval = 0):
    print(err_str)
    sys.exit(exitval)

# ------------------------------------------------------------------------
# Many other interfaces are supported as well (see below)

def mainx():

    global bus

    # Create a bus instance
    bus = None
    try:
        bus = can.Bus(interface=ifacename,
                  channel=serport,
                  receive_own_messages=True)
    except:
        print("Cannot connect to interface:", serport)
        if verbose:
            print(sys.exc_info())
        sys.exit(1)

    if not bus:
        print("No bus to connect to:", serport)
        sys.exit(2)

    serno = bus.get_serial_number(0)
    if verbose:
        print ("USB CAN Serial number:", serno)

    bus.set_bitrate(bitrate)


def sendx(args):

    try:
        send_vals(bus, args)

    except KeyboardInterrupt as N:
        print("\rProgram Terminated with Ctrl-C")
        return
    except ValueError as N:
        print("Please use valid numeric values.")
        print("Decimal (0-9) or Hexadecimal (0x prefix) or Binary (0y or 0b prefix)")
        return
    except:
        if pgdebug > 3:
            print("Could not send", sys.exc_info())
            raise
        print("send_vals() error:", sys.exc_info())
        return

    if listen:
        # Thread for sending and receiving messages
        stop_event = threading.Event()
        try:
            t_receive = threading.Thread(target=receive, args=(bus, stop_event))
            t_receive.start()

        except KeyboardInterrupt:
            print()
            print("Received keyboard interrupt, aborting")
        except:
            print("Interrupt")
            pass  # exit normally

def helpx():
    print("Akostar CAN test utility. (C) Akostar Inc; See README for copying.")
    print("Use: robotell.py [options] bits masks ord [ ... bits masks ord ]")
    print("   Where options can be:")
    print("     -V          --version    print version")
    print("     -h          --help       print help")
    print("     -c          --devices    print supported devices")
    print("     -t          --timing     show timing")
    print("     -i          --interface  interface board (default: robotell)")
    print("     -l          --listen     listen")
    print("     -g          --bridge     bridge")
    print("     -v          --verbose    verbose")
    print("     -p  port    --port       serial port (def: /dev/ttyUSB0)")
    print("     -b  bitrate --bitrate    bit rate (def: 250000)")
    print("     -i  message --message    message id (def=0x19EE5504 )")
    print("     -d  level   --debug      debug level")
    print(" Arguments for short options also needed for the long options.")
    print(" Use '0x' as hex prefix or '0y' or '0b' as bin prefix.")
    sys.exit(1)

longopt = ["help", "message=", "version",  "devices", "timing", "bitrate=",
                "interface=", "listen", "bridge", "verbose", "port=",
                    "debug=", "mask=", "value=", "ord=" ]

# ------------------------------------------------------------------------
# Start of program:

if __name__ == '__main__':

    opts = []; args = []

    try:
        opts, args = getopt.getopt(sys.argv[1:], "bd:p:h?fvxctVli:go:m:u:", longopt)
    except getopt.GetoptError as err:
        print(_("Invalid option(s) on command line:"), err)
        sys.exit(1)

    if not len(args) and not len(opts):
        print("No arguments passed, use -h or --help option for usage info.")
        exit(0)

    for aa in opts:
        # in line verbose
        if pgdebug:
            print("parsing:", aa)

        if aa[0] == "-d" or aa[0] == "--debug":
            try:
                pgdebug = int(aa[1])
            except:
                print("Warn: invalid debug level:", "'" + aa[1] + "'")
                pgdebug = 0
            if verbose:
                print( sys.argv[0], "running at debug level",  pgdebug)

        if aa[0] == "-?": helpx()
        if aa[0] == "-h" or aa[0] == "--help": helpx()
        if aa[0] == "-V" or aa[0] == "--version": print("Akostar robotell interface version", 1.0);  sys.exit(0)
        if aa[0] == "-c" or aa[0] == "--devices": pdevices(); sys.exit(0);
        if aa[0] == "-p" or aa[0] == "--port": serport = aa[1]
        if aa[0] == "-b" or aa[0] == "--bitrate": bitrate = int(aa[1])
        if aa[0] == "-i" or aa[0] == "--interface": ifacename = aa[1]
        if aa[0] == "-i" or aa[0] == "--message": globx.msgid = aa[1]
        if aa[0] == "-l" or aa[0] == "--listen": listen = True
        if aa[0] == "-t" or aa[0] == "--timing": show_timing = True
        if aa[0] == "-o" or aa[0] == "--stdout": use_stdout = True
        if aa[0] == "-v" or aa[0] == "--verbose": verbose = True
        if aa[0] == "-g" or aa[0] == "--bridge": bridge = True
        if aa[0] == "-m" or aa[0] == "--mask":  maskx = hexint(aa[1])
        if aa[0] == "-u" or aa[0] == "--value": valuex = hexint(aa[1])
        if aa[0] == "-o" or aa[0] == "--ord": ordx = hexint(aa[1])

    if len(args) < 3:
        print("Not enough arguments. Use robotell.py -h for quick usage summary.")
        #helpx()
        sys.exit(1)

    if pgdebug > 1:
        print ("opts", opts, "args", args)
        print("Comm =", serport)

    mainx();

    for aa in range(len(args)//3):
        arr3 = [args[3 * aa],args[3 * aa+1],args[3 * aa +2] ] ;
        #print(arr3)
        sendx(arr3)

# eof
