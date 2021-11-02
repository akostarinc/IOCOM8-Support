#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

'''
   This module extracts the IOCOM specific bit manipulation from the
GUI trunk. The bits/bytes are arranged as follows:

    byte[0]     =    payload  (bits set to 0 for OFF, set to 1 for ON)
    byte[1]     =    mask of transaction (influence only bits that are set)
    byte[2]     =    ordinal (1-8 for which unit to talk to)
    byte[3]     =    checksum payload ^ 0x55 -- prevents corrupted packets

    This format is also used in the internal communication of the CAN's
    board to board transactions. One may listen to the CAN bus to monitor
    said transactions. (see Message IDs below)

    The primary board (one with the RF) does not interact with the internal
    CAN messages to the other boards.

'''

import os, sys, getopt, signal, random, time, warnings

from pymenu import  *

sys.path.append('../pycommon')

from pgutil import  *
from pgui import  *
from pgcombo import  *

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GLib
from gi.repository import GObject
from gi.repository import Pango

import array, time, threading, getopt, sys
import can, can.interfaces

currport = "/dev/ttyUSB0"
bitrate     = 250000
ifacename   = 'robotell'

verbose = 0

def sendit(bus, messagex):

    if messagex is not None:
        if verbose:
            print("tx: {}".format(messagex))
        pass
    if verbose:
        print("sending:", hex(messagex.arbitration_id), messagex.data)
        #print("globals", hex(globx.msgid))
        pass
    bus.send(messagex, timeout=0.2)
    #time.sleep(0.250)

def is_allzero(msgx):

    allzero = 1
    for aa in msgx.data:
        if aa: allzero = 0
    return allzero

def send_vals(bus, arr2, msgid):

    # Send value
    message2 = can.Message(arbitration_id=msgid, is_extended_id=True,
                        check=True, data=arr2)
    sendit(bus, message2)

# ------------------------------------------------------------------------

def     opencan(serport):

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
        return [0, 0]

    if not bus:
        print("No bus to connect to:", serport)
        return [0, 0]

    serno = bus.get_serial_number(0)
    if verbose:
        print ("USB CAN Serial number:", serno)

    bus.set_bitrate(bitrate)

    return serno, bus

# ------------------------------------------------------------------------
# This routine builds the bit/bytes mask for the CAN transaction
# input:
#        num          array that contains the instruction ON / OFF
#        bitx         bit in the stack to set / reset
#        bytex        byte postion or ordinal
#
# return array of integers for CAN

def     build_bits(num, bitx, bytex):

    mask =  1 << bitx           # Always on for this bit
    endval = []
    if "OFF" in num:
        val = 0
    elif "ON" in num:
        val = 1 << bitx
    else:
        print("Invalid ON / OFF string")

    # This (below) replicates to 'C' language almost exactly

    endval.append(val)                          # Value
    endval.append(mask)                         # Mask
    endval.append(bytex+1)                      # Ordinal
    endval.append((val^0x55) & 0xff)            # Checksum

    # Second integer blank (may contain random number)
    for aa in range(4):
        endval.append(0)
    return endval

# -----------------------------------------------------------------
#  Build mask and value for ALL bits

def     build_all(xord):

    val = 0xff; mask = 0xff; endval = []
    endval.append(val)                          # Value
    endval.append(mask)                         # Mask
    endval.append(xord+1)                       # Ordinal
    endval.append((val^0x55) & 0xff)            # Checksum
    # Second integer blank (may contain random number)
    for aa in range(4):
        endval.append(0)
    return endval

# EOF

