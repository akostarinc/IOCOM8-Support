#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import print_function

import os, sys, getopt, signal, random, time, warnings

from pymenu import  *

sys.path.append('../pycommon')

import iocomx

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

verbose = 0
pgdebug = 0
mw = None
port = ""

# ------------------------------------------------------------------------
# Basic comm definitions to can  (replicated from can.h Fri 15.Oct.2021)

MSG_SWITCHES =   0x19EE5501  #// Intra IOCOMx msg to funnel to RF
MSG_RFTOCAN  =   0x19EE5502  #// Intra IOCOMx msg via RF
MSG_RELAYS   =   0x19EE5503  #// Control local relays  (note: timeout)
MSG_BRIDGE   =   0x19EE5504  #// Control remote relays (note: timeout)

class _Spacer(Gtk.HBox):

    def __init__(self, sp = None):
        GObject.GObject.__init__(self)
        #self.pack_start()
        #if gui_testmode:
        #    col = randcolstr(100, 200)
        #    self.modify_bg(Gtk.StateType.NORMAL, Gdk.color_parse(col))
        if sp == None:
            sp = 6
        self.set_size_request(sp, sp)

def _colbox(col):

    frame = Gtk.Frame()
    frame.set_can_focus(False)
    #rame.set_margin_top(10)
    frame.set_margin_left(10)
    frame.set_margin_right(10)
    frame.set_margin_bottom(10)

    label = Gtk.Label(label="     ")
    #label.can_set_focus(False)
    frame.label = label
    frame.label.modify_bg(Gtk.StateFlags.NORMAL, col)
    frame.add(label)
    return frame

# ------------------------------------------------------------------------

class MainWin(Gtk.Window):

    def __init__(self):

        Gtk.Window.__init__(self, Gtk.WindowType.TOPLEVEL)

        self.timex = 0
        #self = Gtk.Window(Gtk.WindowType.TOPLEVEL)
        #Gtk.register_stock_icons()

        self.set_title("Akostar IOCOMx / CAN Controller / Driver")
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
            self.set_default_size(4*www/8, 5*hhh/8)
        else:
            self.set_default_size(6*www/8, 6*hhh/8)

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
        lab5 = Gtk.Label("2");  hbox2.pack_start(lab5, 0, 0, 0)
        #vbox.pack_start(hbox2, False, 0, 0)

        hbox3a = Gtk.HBox()
        for aa in range(8):
            hbox3a.pack_start(Gtk.Label("Ord " + str(aa+1)), 1, 1, 0)

        vbox.pack_start(hbox3a, 0, 0, 2)
        vbox.pack_start(_Spacer(), 0, 0, 0)

        hbox3 = Gtk.HBox()
        #hbox3 = Gtk.VBox()
        self.buttarr = []
        for aa in range(8): self.buttarr.append(0)
        self.buttarr2 = []
        for aa in range(8): self.buttarr2.append(0)

        for aa in range(8):
            self.buttarr[aa] = self.fill(aa*8, "ON ")
            hbox3.pack_start(self.buttarr[aa], True, True, 0)

            self.buttarr2[aa] = self.fill(aa*8, "OFF")
            hbox3.pack_start(self.buttarr2[aa], True, True, 0)

            hbox3.pack_start(Gtk.Label("    "), 0, 0, 0)

        vbox.pack_start(hbox3, True, True, 2)

        # Buttom row
        hbox4 = Gtk.HBox()
        hbox4.pack_start(Gtk.Label("  Status:   "), 0, 0, 0)
        self.status = Gtk.Label("Idle ");
        self.status.set_xalign(0)
        hbox4.pack_start(self.status, 1, 1, 0)

        butt3 = Gtk.Button.new_with_mnemonic("    All ON    ")
        butt3.connect("clicked", self.allon, self)
        hbox4.pack_start(butt3, False, 0, 2)

        butt4 = Gtk.Button.new_with_mnemonic("    ALL OFF    ")
        butt4.connect("clicked", self.alloff, self)
        hbox4.pack_start(butt4, False, 0, 2)

        self.checkbox = Gtk.CheckButton("Wireless Bridge mode")
        self.checkbox.set_tooltip_text("Transmits to Remote")
        hbox4.pack_start(self.checkbox, 0, 0, 0)

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

    def allon(self, arg, arg2):
        print("Pressed ALLON")

        for aa in range(8):
            val = 0xff; mask = 0xff; endval = []
            endval.append(val)                          # Value
            endval.append(mask)                         # Mask
            endval.append(aa+1)                         # Ordinal
            endval.append((val^0x55) & 0xff)            # Checksum

            for aa in range(4):
                endval.append(0)

            iocomx.send_vals(self.ser[1], endval, self.checkbox.get_active())

        col2 = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)
        col = Gdk.Color(0xeeee, 0xeeee, 0xeeee)
        for aa in range(8):
            for bb in range(8):
                self.buttarr[aa].cbarr[bb].label.modify_bg(
                                            Gtk.StateType.NORMAL, col)
                self.buttarr[aa].cbarr[bb].label.set_text("ON")

                self.buttarr2[aa].cbarr[bb].label.modify_bg(
                                            Gtk.StateType.NORMAL, col2)
                self.buttarr2[aa].cbarr[bb].label.set_text("")


    def alloff(self, arg, arg2):
        print("Pressed ALLOFF")

        for aa in range(8):
            val = 0x00; mask = 0xff; endval = []
            endval.append(val)                          # Value
            endval.append(mask)                         # Mask
            endval.append(aa+1)                         # Ordinal
            endval.append((val^0x55) & 0xff)            # Checksum

            for aa in range(4):
                endval.append(0)

            iocomx.send_vals(self.ser[1], endval, self.checkbox.get_active())

        col = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)
        col2 = Gdk.Color(0xeeee, 0xeeee, 0xeeee)
        for aa in range(8):
            for bb in range(8):
                self.buttarr[aa].cbarr[bb].label.modify_bg(
                                            Gtk.StateType.NORMAL, col)
                self.buttarr[aa].cbarr[bb].label.set_text("")

                self.buttarr2[aa].cbarr[bb].label.modify_bg(
                                            Gtk.StateType.NORMAL, col2)
                self.buttarr2[aa].cbarr[bb].label.set_text("OFF")

    def butt_press(self, butt, num):
        if verbose:
            print("Pressed %s" % num)

        args = []
        parms = num.split()
        bytex = int(parms[0]) // 8;
        bitx  = int(parms[0]) % 8;

        if verbose:
            print("Parms",  parms, "bytex", bytex, "bitx", bitx)

        self.status_set_text("Sending %s" % num)

        if "OFF" in num:
            self.buttarr[bytex].cbarr[bitx].label.set_text("")
            self.buttarr2[bytex].cbarr[bitx].label.set_text("OFF")
            col = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)
            col2 = Gdk.Color(0xeeee, 0xeeee, 0xeeee)
        else:
            self.buttarr[bytex].cbarr[bitx].label.set_text("ON")
            self.buttarr2[bytex].cbarr[bitx].label.set_text("")
            col = Gdk.Color(0xeeee, 0xeeee, 0xeeee)
            col2 = Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa)

        self.buttarr[bytex].cbarr[bitx].label.modify_bg(
                                            Gtk.StateType.NORMAL, col)

        self.buttarr2[bytex].cbarr[bitx].label.modify_bg(
                                            Gtk.StateType.NORMAL, col2)

        # Build bit mask
        endval = []
        mask =  1 << bitx
        if "OFF" in num:
            val = 0
        elif "ON" in num:
            val = 1 << bitx
        else:
            print("Invalid on off string")

        # This (below) relicates to 'C' language almost exactly

        endval.append(val)                          # Value
        endval.append(mask)                         # Mask
        endval.append(bytex+1)                      # Ordinal
        endval.append((val^0x55) & 0xff)           # Checksum

        for aa in range(4):
            endval.append(0)

        print("Assembled", endval)

        if not self.ser[1]:
            print("Please connect first")
            self.status_set_text("Not connected, please connect first.")
            xmessage("\nPlease connect to a CAN controller first.")
            return

        # Finally, send
        iocomx.send_vals(self.ser[1], endval, self.checkbox.get_active())

    def combox(self, arg):

        #global currport, status

        currport = arg.getcursel()
        self.status_set_text("Opening Port - '%s'" % currport)
        #print("sel:", currport)
        self.ser = iocomx.opencan(currport)

        if self.ser[0] and self.ser[1]:
            self.status_set_text("Opened CAN, Serial '%s'" % self.ser[0])
        else:
            self.status_set_text("Failed opening %s" % currport)

    def fill(self, startn, strx):
        #hbox = Gtk.HBox()
        hbox = Gtk.FlowBox()
        #hbox.set_can_focus(False)
        hbox.set_selection_mode(Gtk.SelectionMode.NONE)
        hbox.set_homogeneous(False)

        hbox.arr = []
        hbox.cbarr = []
        for aa in range(8):
            bbox = Gtk.VBox()

            butt = Gtk.Button("  %d %s  " % (startn + aa + 1, strx))
            butt.connect("pressed", self.butt_press, str(startn+aa) + " " + strx)
            bbox.pack_start(butt, 1, 1, 0)

            hbox.arr.append(butt)
            #hbox.insert(butt, -1)

            #cb = _colbox(Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa))
            if "OFF" in strx:
                cb = _colbox(Gdk.Color(0xeeee, 0xeeee, 0xeeee))
                cb.label.set_text("OFF")
            else:
                cb = _colbox(Gdk.Color(0xaaaa, 0xaaaa, 0xaaaa))

            hbox.cbarr.append(cb)

            bbox.pack_start(_Spacer(), 0, 0, 0)
            bbox.pack_start(cb, 1, 1, 0)
            #hbox.insert(cb,  -1)
            #hbox.insert(_Spacer(1),  -1)
            bbox.pack_start(_Spacer(), 0, 0, 0)

            hbox.insert(bbox, -1)

        return hbox

    def  OnExit(self, arg, srg2 = None):
        try:
            self.alloff(0, 0)
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

    def timeout_open(self):
        global port
        if  port:
            #print("Opening", port)
            self.cbb.sel_text(port)

            #ser = iocomx.opencan(port)
            #if ser[0] and ser[1]:
            #    self.status_set_text("Opened CAN, Serial '%s'" % ser[0])
            #else:
            #    self.status_set_text("Failed opening %s" % currport)

    def timeout_status(self):
        try:
            if self.timex:
                self.timex -= 1
                if self.timex == 1:
                    self.status.set_text("idle")
        except:
            pass
            print("in timer", sys.exc_info())
        return True

    def status_set_text(self, strx):
        self.status.set_text(strx)
        self.timex = 5

# Start of program:

if __name__ == '__main__':

    mainwin = MainWin()
    Gtk.main()


# EOF