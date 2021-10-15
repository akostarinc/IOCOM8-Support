#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

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

# ------------------------------------------------------------------------
# Basic comm definitions to can  (replicated from can.h Fri 15.Oct.2021)

MSG_SWITCHES =   0x19EE5501  #// Intra IOCOMx msg to funnel to RF
MSG_RFTOCAN  =   0x19EE5502  #// Intra IOCOMx msg via RF
MSG_RELAYS   =   0x19EE5503  #// Control local relays  (note: timeout)
MSG_BRIDGE   =   0x19EE5504  #// Control remote relays (note: timeout)

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

def send_vals(bus, arr2, bridge):

    #global globx
    #globx.data = arr2
    #if bridge:
    #    globx.msgid = MSG_BRIDGE
    #else:
    #    globx.msgid = MSG_RELAYS

    if bridge:
        msgid =  MSG_BRIDGE
    else:
        msgid =  MSG_RELAYS

    # Send value
    message2 = can.Message(arbitration_id=msgid, is_extended_id=True,
                        check=True, data=arr2)
    sendit(bus, message2)

    #GLib.timeout_add(30, sustain_send)


# ------------------------------------------------------------------------

def  sustain_send():

    global globx

    # Send value
    message2 = can.Message(arbitration_id=globx.msgid, is_extended_id=True,
                        check=True, data=globx.data )
    sendit(bus, message2)

    '''if not globx.cnt:
        print("Sustaining transmission, CTRL-C to exit ... ")
        sys.stdout.flush()
    globx.cnt += 1

    if globx.data[0] != 0:
        GLib.timeout_add(300, sustain_send)
    '''

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

    if not bus:
        print("No bus to connect to:", serport)
        return

    serno = bus.get_serial_number(0)
    if verbose:
        print ("USB CAN Serial number:", serno)

    bus.set_bitrate(bitrate)

    return serno, bus

