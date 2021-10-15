#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, select, socket, time, struct
import random, stat

import mainwin
from pgutil import  *

# ------------------------------------------------------------------------
# Globals

version = "0.00"

# ------------------------------------------------------------------------

def phelp():

    print()
    print( "Usage: " + os.path.basename(sys.argv[0]) + " [options]")
    print()
    print( "Options:");
    print( "   -d level  --debug    Debug level 0-10   0 = None; 10 = Noisy;")
    print( "   -p port   --port     Serial Port to use. Example: /dev/ttyUSB0")
    print( "   -v        --verbose  Verbose.  Print some useful event info.")
    print( "   -b        --bridge   Verbose.  Print some useful event info.")
    print( "   -V        --version  Print version info.")
    print( "   -q        --quiet    Quiet. Do not print much to the console.")
    print( "   -h        --help.    This message")
    print()
    sys.exit(0)

# ------------------------------------------------------------------------
def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option_letter, variable_name, initial_value, function
    # option letter has ":" for arguments; None denotes missing entry
optarr = \
    ["d:",  "debug=",   "pgdebug",  0,      None],      \
    ["p:",  "port=",    "port",     "",     None],      \
    ["v",   "verbose",  "verbose",  0,      None],      \
    ["q",   "quiet",    "quiet",    0,      None],      \
    ["t",   "test",     "test",     "x",    None],      \
    ["V",   "version",  "version",  None,   pversion],  \
    ["h",   "help",     "help",     None,   phelp]      \

# Just to check if vars arrived

def printmain():
    for aa in dir(mainwin):
        if aa.isupper():
            continue
        ttt = getattr(mainwin, aa)

        #if type(ttt) == type(""):
        #    pass
        if type(ttt) == type(0):
            print(aa, ttt)

if __name__ == '__main__':

    global mw
    conf = ConfigLong(optarr)
    args = conf.comline(sys.argv[1:])
    #conf.printvars()

    mw = mainwin.MainWin()
    conf.cpvars(mainwin)
    mainwin.mw = mw

    #printmain()
    Gtk.main()
    sys.exit(0)

# EOF










