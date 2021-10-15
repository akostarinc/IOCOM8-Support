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

 The robotel.py interface command line options:

    -c          --      print supported devices
    -i          --      interface board (def: robotell)
    -l          --      listen
    -g          --      bridge
    -v          --      verbose
    -p  port    --      serial port (def: /dev/ttyUSB0)
    -b  bitrate --      bit rate (def: 250000)
    -i  message --      message id (def=0x19EE5504)
    -d  level   --      debug level (0..9)

### Examples:

   An example invocation from our testing process, that turned on the first 16
   LOCAL relays;

    ./robotell.py -p /dev/ttyUSB2  0xff 0xff

   An example invocation from our testing process, that turned on the first
   and second REMOTE relays;

    ./robotell.py -p /dev/ttyUSB2 -g 0x3

      Please note, that the remote relays need a continuous feed of 'ON' signal
    to hold closed. That is provided by the 'bridge' mode. Press Ctrl-C to
    return to the command line.

    An example invocation from our testing process, that monitored the traffic;

    python ./usb-can.py -p /dev/ttyUSB2 -l INFO -s 250000


Screen dump of pressing and releasing button 2:
```
Standard ID: 0x506       DLC: 8  Data: 0x02 0x00 0x00 0x00 0x00 0x00 0x00 0x00
2021-07-08 13:47:55,382 [usb-can.py:476] INFO
Standard ID: 0x506       DLC: 8  Data: 0x00 0x00 0x00 0x00 0x00 0x00 0x00 0x00
2021-07-08 13:47:55,431 [usb-can.py:476] INFO
```

  The examples included are implemented in python. Open source libraries are available for
most every CAN interface. The python examples are provided for showing the IOCOMx
interface details, thus the IOCOMx interface can be easily implemented for other
languages or other systems.

 Please see GUI examples on how to control the IOCOMx from a graphical user interface;

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