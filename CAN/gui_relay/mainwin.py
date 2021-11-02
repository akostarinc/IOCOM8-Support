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

import iocomx

pgdebug = 0
verbose = 0
stop_loop = 0

buttarr_all = []
buttarr2_all= []

# ------------------------------------------------------------------------
# Basic comm definitions to can  (replicated from can.h Fri 16.Jul.2021)

MSG_SWITCHES =   0x19EE5501  #// Intra IOCOMx msg to funnel to RF
MSG_RFTOCAN  =   0x19EE5502  #// Intra IOCOMx msg via RF
MSG_RELAYS   =   0x19EE5503  #// Control local relays
MSG_BRIDGE   =   0x19EE5504  #// Control remote relays (note: timeout)
MSG_PING     =   0x19EE550a  #// IOCOM CAN heartbeat

MSG_INPUTS   =   0x19EE5505  #// Broadcast the status of the inputs
MSG_OUTPUTS  =   0x19EE5506  #// The status of the outputs

class _globals:
    pass
    #msgid    =  MSG_AUX
    #msgmask  =  MSG_MASKAUX

globx = _globals()

currport = "/dev/ttyUSB0"
bitrate     = 250000
ifacename   = 'robotell'
bus = None

col2 = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)
col1 = Gdk.Color(0xeeee, 0xeeee, 0xeeee)

class zSpacer(Gtk.HBox):

    def __init__(self, sp = None):
        GObject.GObject.__init__(self)
        #self.pack_start()
        #if gui_testmode:
        #    col = randcolstr(100, 200)
        #    self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))
        if sp == None:
            sp = 6
        self.set_size_request(sp, sp)

def colbox(col):

    frame = Gtk.Frame()
    frame.set_can_focus(False)
    #rame.set_margin_top(10)
    #frame.set_margin_left(10)
    #frame.set_margin_right(10)
    #frame.set_margin_bottom(10)

    label = Gtk.Label(label="     ")
    #label.can_set_focus(False)
    frame.label = label
    frame.label.modify_bg(Gtk.StateFlags.NORMAL, col)
    frame.add(label)
    return frame


def handle_relays(rx_msg):

    if pgdebug > 2:
        print("relay data", rx_msg.data)

    ord = rx_msg.data[2] -1

    if ord < 0 or ord > 8:
        print("Ordinal out of range")
        #continue;
        return

    if pgdebug > 2:
        print("ord", ord)

    buttarr = buttarr_all[ord];
    buttarr2 = buttarr2_all[ord]

    for aa in range(len(buttarr)):
        mask = 0x80 >> aa
        if rx_msg.data[0] & mask:
            buttarr[aa].cbarr[0].label.modify_bg(
                                 Gtk.StateType.NORMAL, col1)
            buttarr2[aa].cbarr[0].label.modify_bg(
                                 Gtk.StateType.NORMAL, col2)
            buttarr[aa].cbarr[0].label.set_text( "ON ")
            buttarr2[aa].cbarr[0].label.set_text("- - -")
        else:
            buttarr[aa].cbarr[0].label.modify_bg(
                                 Gtk.StateType.NORMAL, col2)
            buttarr2[aa].cbarr[0].label.modify_bg(
                                 Gtk.StateType.NORMAL, col1)
            buttarr[aa].cbarr[0].label.set_text( "- - -")
            buttarr2[aa].cbarr[0].label.set_text("OFF")


def handle_msg(rx_msg):

    if pgdebug > 5:
        print("rx:{0} {1} {2}\n".format("", rx_msg, rx_msg.arbitration_id))

    #if rx_msg.arbitration_id ==  MSG_SWITCHES:
    #    handle_switches(rx_msg)

    if rx_msg.arbitration_id ==  MSG_RFTOCAN:
        handle_relays(rx_msg)


Gdk.threads_init()

class Listenx(can.Listener):
    global myqueue
    def on_message_received(self, msg):
        #print("notified class", msg)
        Gdk.threads_enter()
        handle_msg(msg)
        Gdk.threads_leave()

def start_listen(bus):
    global stop_event
    listener = Listenx()
    noti = can.Notifier(bus, [listener,], 0)
    if(verbose):
        print("Set listener to ", listener)

    # This is a good time to send the IOCOM a 'broadcast switches' message
    endval = []
    for aa in range(8):
        endval.append(0)
    endval[3] = endval[0] ^ 0x55

    # Might need more than one
    for aa in range(4):
        iocomx.send_vals(bus, endval, MSG_INPUTS)

# ------------------------------------------------------------------------

def     opencan(serport):

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

    if not bus:
        print("No bus to connect to:", serport)

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

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self, conf):

        global verbose, pgdebug

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.conf = conf
        verbose = self.conf.verbose
        pgdebug = self.conf.pgdebug

        self.timex = 0
        #self = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        #Gtk.register_stock_icons()

        #print("conf", dir(self.conf))

        self.set_title("Akostar IOCOMx / CAN Output Monitor")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)

        #ic = Gtk.Image(); ic.set_from_stock(Gtk.STOCK_DIALOG_INFO, Gtk.ICON_SIZE_BUTTON)
        #window.set_icon(ic.get_pixbuf())

        www = Gdk.Screen.width(); hhh = Gdk.Screen.height();

        disp2 = Gdk.Display()
        disp = disp2.get_default()
        #print( disp)
        scr = disp.get_default_screen()
        ptr = disp.get_pointer()
        mon = scr.get_monitor_at_point(ptr[1], ptr[2])
        geo = scr.get_monitor_geometry(mon)
        www = geo.width; hhh = geo.height
        xxx = geo.x;     yyy = geo.y

        # Resort to old means of getting screen w / h
        if www == 0 or hhh == 0:
            www = Gdk.screen_width(); hhh = Gdk.screen_height();

        if www / hhh > 2:
            self.set_default_size(4*www/8, 200) # 3*hhh/16)
        else:
            self.set_default_size(6*www/8, 200) #3*hhh/16)

        self.connect("destroy", self.OnExit)
        self.connect("key-press-event", self.key_press_event)
        self.connect("button-press-event", self.button_press_event)

        try:
            self.set_icon_from_file("icon.png")
        except:
            pass

        vbox = Gtk.VBox();

        merge = Gtk.UIManager()
        #self.mywin.set_data("ui-manager", merge)

        aa = create_action_group(self)
        merge.insert_action_group(aa, 0)
        self.add_accel_group(merge.get_accel_group())

        merge_id = merge.new_merge_id()

        try:
            mergeid = merge.add_ui_from_string(ui_info)
        except GLib.GError as msg:
            print("Building menus failed: %s" % msg)

        self.mbar = merge.get_widget("/MenuBar")
        #self.mbar.show()

        self.tbar = merge.get_widget("/ToolBar");
        #self.tbar.show()

        bbox = Gtk.VBox()
        bbox.pack_start(self.mbar, 0, 0, 0)
        bbox.pack_start(self.tbar, 0, 0, 0)
        #vbox.pack_start(bbox, 0, 0, 0)

        vbox.pack_start(Gtk.Label(" "), 0, 0, 2)

        hbox2 = Gtk.HBox()
        lab3 = Gtk.Label("1");  hbox2.pack_start(lab3, 0, 0, 0)
        lab4 = Gtk.Label("Top");  hbox2.pack_start(lab4, 1, 1, 0)
        lab5 = Gtk.Label("2");      hbox2.pack_start(lab5, 0, 0, 0)
        #vbox.pack_start(hbox2, False, 0, 0)

        global buttarr_all
        global buttarr2_all

        hbox3a = Gtk.HBox()
        hbox3a.pack_start(Gtk.Label("           "), 0, 0, 2)
        for aa in range(8):
            lab = Gtk.Label("Output %d " % (aa+1))
            lab.set_justify(Gtk.Justification.CENTER)
            #lab.override_background_color(Gtk.StateFlags.NORMAL, Gdk.RGBA(.5, .3, .5))
            hbox3a.pack_start(lab, 1, 1, 2)

        vbox.pack_start(hbox3a, 0, 0, 2)
        vbox.pack_start(zSpacer(), 0, 0, 0)

        for bb in range(8):
            hbox3 = Gtk.HBox()
            hbox3.pack_start(Gtk.Label("  Unit %d:   " % (bb+1)), 0, 0, 0)
            #hbox3 = Gtk.VBox()

            buttarr = [];  buttarr2 = []
            buttarr_all.append(buttarr)
            buttarr2_all.append(buttarr2)

            for aa in range(8):
                buttarr.append([])
            for aa in range(8):
                buttarr2.append([])

            for aa in range(8):

                buttarr[aa] = self.fill_row(aa*8, "ON ")
                hbox3.pack_start(buttarr[aa], True, True, 0)

                buttarr2[aa] = self.fill_row(aa*8, "OFF")
                hbox3.pack_start(buttarr2[aa], True, True, 0)

                hbox3.pack_start(Gtk.Label("   "), 0, 0, 0)

            vbox.pack_start(hbox3, True, True, 2)

        # Buttom row
        hbox4 = Gtk.HBox()
        hbox4.pack_start(Gtk.Label("  Status:   "), 0, 0, 0)
        self.status = Gtk.Label("Idle ");
        self.status.set_xalign(0)
        hbox4.pack_start(self.status, 1, 1, 0)

        '''butt3 = Gtk.Button.new_with_mnemonic("    All ON    ")
        butt3.connect("clicked", self.allon, self)
        hbox4.pack_start(butt3, False, 0, 2)

        butt4 = Gtk.Button.new_with_mnemonic("    ALL OFF    ")
        butt4.connect("clicked", self.alloff, self)
        hbox4.pack_start(butt4, False, 0, 2)

        self.checkbox = Gtk.CheckButton("Bridge mode")
        self.checkbox.set_tooltip_text("Transmits to Remote")
        hbox4.pack_start(self.checkbox, 0, 0, 0)
        '''

        #butt1 = Gtk.Button.new_with_mnemonic("    _New    ")
        #butt1.connect("clicked", self.show_new, window)
        #hbox4.pack_start(butt1, False, 0, 2)

        stdir = "/dev/"
        sss = os.listdir(stdir)
        ddd = []
        for aa in sss:
            if "ttyUSB" in aa:
                ddd.append(stdir + aa)

        #print("ddd", ddd)
        self.cbb = ComboBox(ddd, self.combox)
        self.cbb.set_tooltip_text("Connect to serial port")

        hbox4.pack_start(self.cbb, False, 0, 2)

        butt2 = Gtk.Button.new_with_mnemonic("    E_xit    ")
        butt2.connect("clicked", self.OnExit, self)
        hbox4.pack_start(butt2, False, 0, 2)
        lab2b = Gtk.Label("   ");  hbox4.pack_start(lab2b, 0, 0, 0)
        vbox.pack_start(hbox4, False, 0, 6)

        GLib.timeout_add(1000, self.timeout_status)
        GLib.timeout_add(100, self.timeout_open)

        self.add(vbox)
        self.show_all()

    def timeout_open(self):
        if  self.conf.port:
            if verbose:
                print("Opening", self.conf.port)
            self.cbb.sel_text(self.conf.port)

    def alloff(self, arg, arg2):
        print("Pressed ALLOFF")
        args = []
        for aa in range(8):
            args.append(0xff)
        for aa in range(8):
            args.append(0x0)
        send_vals(bus, args, self.checkbox.get_active())

        col = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)
        col2 = Gdk.Color(0xeeee, 0xeeee, 0xeeee)
        for aa in range(8):
            for bb in range(8):
                buttarr[aa].cbarr[bb].label.modify_bg(
                                            Gtk.StateType.NORMAL, col)
                buttarr[aa].cbarr[bb].label.set_text("")

                buttarr2[aa].cbarr[bb].label.modify_bg(
                                            Gtk.StateType.NORMAL, col2)
                buttarr2[aa].cbarr[bb].label.set_text("OFF")


    def butt_press(self, butt, num):
        #print("Pressed %s" % num)
        if not bus:
            print("Please connect first")
            self.status_set_text("Not connected")
            return

        args = []
        parms = num.split()
        bytex = int(parms[0]) // 8;
        bitx  = int(parms[0]) % 8;

        print("Parms",  parms, "bytex", bytex, "bitx", bitx)

        self.status_set_text("Sending %s" % num)

        if "OFF" in num:
            buttarr[bytex].cbarr[bitx].label.set_text("")
            buttarr2[bytex].cbarr[bitx].label.set_text("OFF")
            col = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)
            col2 = Gdk.Color(0xeeee, 0xeeee, 0xeeee)
        else:
            buttarr[bytex].cbarr[bitx].label.set_text("ON")
            buttarr2[bytex].cbarr[bitx].label.set_text("")
            col = Gdk.Color(0xeeee, 0xeeee, 0xeeee)
            col2 = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)

        buttarr[bytex].cbarr[bitx].label.modify_bg(
                                            Gtk.StateType.NORMAL, col)

        buttarr2[bytex].cbarr[bitx].label.modify_bg(
                                            Gtk.StateType.NORMAL, col2)

        # Build bit mask
        val = 1 << bitx
        for aa in range(8):
            if aa == bytex:
                args.append(val)
            else:
                args.append(0)
        # Build values
        for aa in range(8):
            if aa == bytex:
                if "OFF" in num:
                    args.append(0)
                else:
                    args.append(val)
            else:
                args.append(0)

        # Finally, send
        send_vals(bus, args, self.checkbox.get_active())

    def combox(self, arg):

        #global currport, status

        currport = arg.getcursel()
        self.status_set_text("Opening Port - '%s'" % currport)
        #print("sel:", currport)
        ser = opencan(currport)
        if ser:
            self.status_set_text("Opened CAN, Serial '%s'" % ser[0])
        else:
            self.status_set_text("Failed opening %s" % currport)

        global bus
        start_listen(bus)


    def fill_row(self, startn, strx):
        #hbox = Gtk.Grid()
        hbox = Gtk.HBox()
        #hbox = Gtk.FlowBox()
        #hbox.set_can_focus(False)
        #hbox.set_selection_mode(Gtk.SelectionMode.NONE)
        #hbox.set_homogeneous(False)

        hbox.arr = []
        hbox.cbarr = []
        left = 0
        for aa in range(1):
            bbox = Gtk.VBox()
            if "OFF" in strx:
                cb = colbox(Gdk.Color(0xeeee, 0xeeee, 0xeeee))
                cb.label.set_text("OFF")
            else:
                cb = colbox(Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa))
                cb.label.set_text("- - -")

            hbox.cbarr.append(cb)

            bbox.pack_start(zSpacer(), 0, 0, 0)
            bbox.pack_start(cb, 1, 1, 0)

            #hbox.insert(cb,  -1)
            #hbox.insert(zSpacer(1),  -1)

            bbox.pack_start(zSpacer(), 0, 0, 0)
            #hbox.attach(zSpacer(), left, 0, 1, 1); left += 1

            #hbox.insert(bbox, -1)
            hbox.pack_start(bbox, 1, 1, 4)

            #hbox.attach(bbox, left, 0, 1, 1);  left += 1
            #hbox.attach(zSpacer(), left, 0, 1, 1)

            #hbox.pack_start(zSpacer(), 0, 0, 4)

            #left += 1

        return hbox

    def  OnExit(self, arg, srg2 = None):

        try:
            global  stop_event
            stop_event.set()
            stop_loop = True

        except:
            pass

        self.exit_all()

    def exit_all(self):
        Gtk.main_quit()

    def key_press_event(self, win, event):
        #print( "key_press_event", win, event)
        pass

    def button_press_event(self, win, event):
        #print( "button_press_event", win, event)
        pass

    def activate_action(self, action):

        #dialog = Gtk.MessageDialog(None, Gtk.DIALOG_DESTROY_WITH_PARENT,
        #    Gtk.MESSAGE_INFO, Gtk.BUTTONS_CLOSE,
        #    'Action: "%s" of type "%s"' % (action.get_name(), type(action)))
        # Close dialog on user response
        #dialog.connect ("response", lambda d, r: d.destroy())
        #dialog.show()

        warnings.simplefilter("ignore")
        strx = action.get_name()
        warnings.simplefilter("default")

        print ("activate_action", strx)

    def activate_quit(self, action):
        print( "activate_quit called")
        self.OnExit(False)

    def activate_exit(self, action):
        print( "activate_exit called" )
        self.OnExit(False)

    def activate_about(self, action):
        print( "activate_about called")
        pass

    def read_can(self):

        pass

    def timeout_status(self):
        try:
            if self.timex:
                self.timex -= 1
                if self.timex == 1:
                    self.status.set_text("idle")
        except:
            pass
            print("in timer", sys.exc_info())

        self.read_can()

        return True

    def status_set_text(self, strx):
        self.status.set_text(strx)
        self.timex = 5

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    Gtk.main()

# EOF