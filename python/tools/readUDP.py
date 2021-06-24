#!/usr/local/bin/python3.8
# readUDP.py
# 
# Simple UDP listener.

from socket import *
import logging
import sys
import argparse
import shlex

def UDP_listener(opts):
    logging.basicConfig(datefmt = "%Y-%m-%d %H:%M:%S",
                        format = "%(asctime)s.%(msecs)03dZ %(name)-10s %(levelno)s %(filename)s:%(lineno)d %(message)s")
    
    logger = logging.getLogger('udp')
    logger.setLevel(opts.logLevel)

    s=socket(AF_INET, SOCK_DGRAM)
    s.bind(('',opts.udpPort))

    while True:
        # tuple( MESSAGE( byteString ) , ADDRESS( tuple( IP_ADDRESS, PORT )))
        m=s.recvfrom(1024)
        msg = m[0].decode()
        addr = m[1]
        IPaddr = addr[0]
        port = addr[1]
        logger.info(f'{IPaddr}:{port}: {msg}')

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if isinstance(argv, str):
        argv = shlex.split(argv)

    parser = argparse.ArgumentParser(sys.argv[0])
    parser.add_argument('--logLevel', type=int, default=logging.INFO,
                        help='logging threshold. 10=debug, 20=info, 30=warn')
    parser.add_argument('--udpAddress', type=str, default='192.168.1.255',
                        help='the UDP broadcast address')
    parser.add_argument('--udpPort', type=str, default=8888,
                        help='the UDP broadcast port')

    opts = parser.parse_args(argv)
    try:
        UDP_listener(opts)
    except KeyboardInterrupt:
        print('Exiting Program...')

if __name__ == "__main__":
    main()