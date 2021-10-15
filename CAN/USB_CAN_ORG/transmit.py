#!/usr/bin/env python3

import socket, sys

#HOST, PORT = "255.255.255.255", 8200
HOST, PORT = "127.0.0.1", 8200

#jsonString = '{"name":"VideoStreamStatus","parameters":{"name":"video_0_0"}}'
#echo "$json"  | socat - udp-datagram:255.255.255.255:8200,broadcast

sw_flag = 0
sw_flag2 = 0

def radixint(strx):
    if strx[:2].lower() == "0x":
        return int(strx[2:], 16)
    else:
        return int(strx)

def     sendsw():

    jsonString='''
        {
          "request": "Transmit",
          "id": "0x19EE5504",
          "type": "extData",
          "data": [%d, %d, 0, 0, 0, 0, 0, 0]
        }
        ''' % (sw_flag, sw_flag2);

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        sock.sendto(jsonString.encode(), (HOST, PORT))
        print ("Control Data %x %x sent" % (sw_flag, sw_flag2))

    finally:
        sock.close()

    print ("Sent:     {}".format(jsonString))

if __name__ == '__main__':

    if len(sys.argv) > 1:
        sw_flag = radixint(sys.argv[1])

    if len(sys.argv) > 2:
        sw_flag2 = radixint(sys.argv[2])

    sendsw()

# eof