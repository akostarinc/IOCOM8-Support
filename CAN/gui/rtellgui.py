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
    print( "Options:    -d level  - Debug level 0-10")
    print( "            -p        - Port to use (default: 9999)")
    print( "            -v        - Verbose")
    print( "            -V        - Version")
    print( "            -q        - Quiet")
    print( "            -h        - Help")
    print()
    sys.exit(0)

# ------------------------------------------------------------------------
def pversion():
    print( os.path.basename(sys.argv[0]), "Version", version)
    sys.exit(0)

    # option, var_name, initial_val, function
    # option, var_name, initial_val, function
optarr = \
    ["d:",  "debug=",   "pgdebug",  0,      None],      \
    ["p:",  "port=",    "port",     "",     None],      \
    ["v",   "verbose",  "verbose",  0,      None],      \
    ["q",   "quiet",    "quiet",    0,      None],      \
    ["t",   "test",     "test",     "x",    None],      \
    ["V",   "version",  None,       None,   pversion],  \
    ["h",   "help",     None,       None,   phelp]      \

conf = ConfigLong(optarr)

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
    args = conf.comline(sys.argv[1:])
    #conf.printvars()

    mw = mainwin.MainWin()
    conf.cpvars(mainwin)
    mainwin.mw = mw

    #printmain()
    Gtk.main()
    sys.exit(0)











