# Akostar CAN example for the robotell CAN interface

  This example drives the Akostar IOCOMx device from the can bus. The general theory of driving he IOCOMx
from the can bus is to transmit the bit mask of the switches we want to operate on,
and the bit mask of the switches we want to torn on /off; The can bus operates on an eight byte
packet with, we transmit eight bytes of MASK and eight bytes of VALUE.

  Simple Usage:

      ./robotell.pl -p /dev/TTYUSB0 --ord 0 --mask 255 --value 255

            to switch on all swithes on the first unit (switches 1-8)

      ./robotell.pl -p /dev/TTYUSB0 --ord 0 --mask 255 --value 0

            to switch off all swithes on the first unit (switches 1-8)

      ./robotell.pl -p /dev/TTYUSB0 --ord 1 --mask 255 --value 255

            to switch on all swithes on the second unit (switches 9-16)

      ./robotell.pl -p /dev/TTYUSB0 --ord 2 --mask 0xff --value 255

            to switch on all swithes on the third unit (switches 17-24)

  Other Usages:

      ./robotell.pl -p /dev/TTYUSB0 0 0 0 255   0  0  0 255

            to switch on all switches on the fourth unit

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

    #define MSG_SWITCHES    0x19EE5501  // Intra IOCOMx msg to funnel to RF
    #define MSG_TID         0x19EE5502  // Intra IOCOMx msg / presence check
    #define MSG_MASKS       0x19EE5503  // Intra IOCOMx msg mask
    #define MSG_RELAYS      0x19EE5504  // Control local relays
    #define MSG_BRIDGE      0x19EE5505  // Control remote relays (note: timeout)
    #define MSG_INPUTS      0x19EE5506  // The status of the inputs
    #define MSG_OUTPUTS     0x19EE5507  // The status of the outputs
    #define MSG_MASKAUX     0x19EE5508  // IOCOM auxiliary mask
    #define MSG_AUX         0x19EE5509  // IOCOM auxiliary command
    #define MSG_RESERVED    0x19EE550a  // IOCOM reserved for future use

 The items marked 'intra' are used internally between IOCOMx modules. The status on the inputs / outputs
are mirrored to the CAN BUS (broadcast on delta). The AUX commands control the local
outputs, and the BRIDGE command control the remote outputs.

./robotell.py has a monitor (listen) mode, where the CAN transmission can
be monitored on the BUS; here is an example output:

    rx:0 Timestamp: 1626469011.385363    ID: 19ee5501    X Rx                DLC:  8    00 00 00 00 00 00 00 00
    rx:0 Timestamp: 1626469011.393061    ID: 19ee5503    X Rx                DLC:  8    01 00 00 00 00 00 00 00
    rx:0 Timestamp: 1626469011.393403    ID: 19ee5504    X Rx                DLC:  8    00 00 00 00 00 00 00 00
    rx:0 Timestamp: 1626469009.347454    ID: 19ee5507    X Rx                DLC:  8    ef 00 ff 00 00 00 00 00
    rx:0 Timestamp: 1626469009.487352    ID: 19ee5506    X Rx                DLC:  8    00 00 00 00 00 00 00 00

 Just for completeness the python USB drivers are included here in the python_can
subdirectory.

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
