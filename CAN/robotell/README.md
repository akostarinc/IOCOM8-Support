# Akostar CAN example

## for the Robotell CAN interface

  This example drives the Akostar IOCOMx device from the can bus. The general theory of driving he IOCOMx
from the can bus is to transmit the values of the outputs, and the bit mask of the outputs we
want to operate / control and the unit number (ordinal number);

  The can bus operates on an eight byte packet width, of which we transmit four bytes of
  payload, and four bytes of arbitrary data. **

  Usage:

      ./robotell.pl -p /dev/ttyUSB0 0xff 0xff 1

            to switch ON all outputs on the first unit (outputs 1-8)


      ./robotell.pl -p /dev/ttyUSB0 0x00 0xff 1

            to switch OFF all outputs on the first unit (outputs 1-8)


      ./robotell.pl -p /dev/ttyUSB0 0xff 0xff 1 0xff 0xff 2

            to switch ON all outputs on the first AND second unit (outputs 9-16)


      ./robotell.pl -p /dev/ttyUSB0

            to switch OFF all outputs on the third unit (outputs 17-24)

  Usage / Help:

    Type ./robotell.py -h for a more elaborate description of the python utility;


  If you are using a language other than python, please do not be discouraged, as
the python code contains all the elements that are important to drive the
CAN bus successfully. This can be ported to any language with ease. While this script was
developed in Linux, it operates on Windows as well. Though untested, it should operate on the MAC platform.

 If you are using an OS other than Linux, substitute the values as your platform
 demands. For instance, using Windows, instead of specifying /dev/ttyUSB0,
substitute ports with COM1 ... COM2 etc.

 The can bus ID are listed below:

  define MSG_SWITCHES    0x19EE5501  // Intra IOCOMx msg to funnel to RF
  define MSG_RFTOCAN     0x19EE5502  // Intra IOCOMx msg via RF
  define MSG_RELAYS      0x19EE5503  // Control local relays
  define MSG_BRIDGE      0x19EE5504  // Control remote relays (note: timeout)

 The items marked 'intra' are used internally between IOCOMx modules. The status on the inputs / outputs
are mirrored to the CAN BUS (broadcast on delta). The AUX commands control the local
outputs, and the BRIDGE command control the remote outputs.

./robotell.py has a monitor (listen) mode, where the CAN transmission can
be monitored on the BUS; use the -l (listen switch) like: ./robotell.py -l -p /dev/ttyUSB0
(adjust port for your system)

Here is an example output:

    rx:1 Timestamp: 1634580646.238603    ID: 19ee5501    X Rx DLC:  8    00 01 07 55 7c 0f 00 00
    rx:1 Timestamp: 1634580646.238688    ID: 19ee5501    X Rx DLC:  8    00 01 03 55 e0 46 00 00
    rx:1 Timestamp: 1634580646.238764    ID: 19ee5501    X Rx DLC:  8    00 01 06 55 37 ee 00 00

 Short field description (of the first line):

  value |  mask |  ordinal | checksum | random | padding
  ----- | ----- | -----    | -----    | -----  | -----
   00   |    01 |     07  |    55     | 7c 0f  | 00 00

 When in listen mode, press CTRL-C to terminate.

 The listen mode allows one to study the CAN communication of the IOCOMx. This may be useful if the IOCOMx
is integrated into a larger system, and it's inputs and outputs are monitored. For instance, it can act
as a translator between switch action and CAN message. Or Remote button press to CAN message.

  Please note, that the TxRx unit (the one designated to RF transmission / reception) does not expose its
events as CAN messages. If such messages are paramount, one may deploy an extra unit to expose it's CAN
messages.

 Just for completeness the python USB drivers are included here in the python_can
subdirectory.

  Please note that these additions are provided as is, unsupported by Akostar. Naturally, we will
answer your questions and respond to request as a courtesy.

## Copying

You are free to use this example as you see fit, provided the original copyright
messages are included.

## The Original message from this example:

### INSTALLING ROBOTELL PYTHON MODULES

  The official python-can repositiry does not contain support for the robotell CAN.

But it can be installed from the github repo from:

    https://github.com/hardbyte/python-can

    python setup.py install    (may need sudo if global install needed)

    [Remove the pip version before installing from source.]

PG
