# Akostar IOCOMx CAN

## The IOCOMx system can be controlled and monitored from the CAN bus.

 Below, the messages defined from the device's firmware, and a short description.

The IOCOMx can bus speed is set to:

`can_timing_config_t t_config = CAN_TIMING_CONFIG_250KBITS();`

as this is the most ofter used setting in the industrial sector. If custom setting
is needed, please talk to our tech team.

 The items of control:
```
 Internal:
    MSG_SWITCHES =   0x19EE5501  #// Intra IOCOMx msg to tunnel to RF
    MSG_RFTOCAN  =   0x19EE5502  #// Intra IOCOMx msg to tunnel from RF

 External:
    MSG_RELAYS   =   0x19EE5503  #// Control local relays  (note: timeout)
    MSG_BRIDGE   =   0x19EE5504  #// Control remote relays (note: timeout)

```

The above external items can be sent to the IOCOMx device. The I/O data format:

Data Byte | Data Mask  | Ordinal | Checksum   | Fill | Fill | Fill | Fill
------    | -------    | ---     | ---        | ---  | --   | --   | ---
0-0xff    | 0-0xff     | 1-8     |  data^0x55 | Any  | Any  | Any  | Any

 The bit arrangement is big-endian, bit_0 is port_1, bit_1 is port_2 ... bit 7 is port_8

  The internal items of monitor:

```
    MSG_SWITCHES =   0x19EE5501  #// Intra IOCOMx msg to tunnel to RF
    MSG_RFTOCAN  =   0x19EE5502  #// Intra IOCOMx msg to tunnel from RF

```

  The Bit arrangement is identical to the control format's bit arrangement. Please note, that the
 RF unit does not broadcast its state to the CAN bus.

 CAN example(s) directory structure:

Directory                   |  Description
--------------------------- |  --------------------------------
CAN                         | This directory
gui                         | graphical user interface to control
gui_mon                     | graphical user interface to monitor
robotel                     | Example control with the robotel CAN interface
robotel/python-can          | The python CAN interface from PIP at Thu 08.Jul.2021
USB_CAN_ORG                 | The original open source drivers

Code examples:

  see: robotel.py; see: usb-can.py [usb-can is open source]

 The robotel.py interface command line help options:

      Akostar CAN test utility. (C) Akostar Inc; See README for copying.
    Use: robotell.py [options] bits masks ord [ ... bits masks ord ]
       Where options can be:
         -V          --version    print version
         -h          --help       print help
         -c          --devices    print supported devices
         -t          --timing     show timing
         -i          --interface  interface board (default: robotell)
         -l          --listen     listen
         -g          --bridge     bridge
         -v          --verbose    verbose
         -p  port    --port       serial port (def: /dev/ttyUSB0)
         -b  bitrate --bitrate    bit rate (def: 250000)
         -i  message --message    message id (def=0x19EE5504 )
         -d  level   --debug      debug level
     Arguments for short options also needed for the long options.
     Use '0x' as hex prefix or '0y' or '0b' as bin prefix.

### Examples:

   An example invocation from our testing process, that turned on all relays of unit 8 (ord 8)

   LOCAL relays;

    ./robotell.py -p /dev/ttyUSB2  0xff 0xff 0x8

    An example invocation from our testing process, that turned on the first
   and second REMOTE relays on unit 7;

    ./robotell.py -p /dev/ttyUSB2 -g 0x3 0x3 0x7

    An example invocation from our testing process, that monitored the traffic;

    python ./usb-can.py -p /dev/ttyUSB2 -l INFO -s 250000


  The examples included are implemented in python. Open source libraries are available for
most every CAN interface. The python examples are provided for showing the IOCOMx
interface details, thus the IOCOMx interface can be easily implemented for other
languages or other systems.

 Please see GUI examples on how to control the IOCOMx from a graphical user interface in the
gui directory;

Usage: rtellgui.py [options]

Options:
   -d level  --debug    Debug level 0-10   0 = None; 10 = Noisy;
   -p port   --port     Serial Port to use. Example: /dev/ttyUSB0
   -v        --verbose  Verbose.  Print some useful event info.
   -b        --bridge   Verbose.  Print some useful event info.
   -V        --version  Print version info.
   -q        --quiet    Quiet. Do not print much to the console.
   -h        --help.    This message

// EOF

