#!/usr/bin/env python3

import os
import sys
# disable scapy warning with IPv6
# sorry PEP8 (
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import scapy.all as scapy
from functools import partial
from socket import gethostbyaddr, herror

# broadcats mac
BROADCATS_MAC = 'ff:ff:ff:ff:ff:ff'

# protocol names for scapy filtering
ARP_NAME = 'arp'
ICMP_NAME = 'icmp'

ONLINE = 'ONLINE'
OFFLINE = 'OFFLINE'

# default params - should be in config.py
DEFAULT_TIMEOUT = 1
DEFAULT_SCAPY_VERBOUS = 0
DEFAUTL_TIME_PREC = 2

FIRST_INDEX = 0
REQUEST_INDEX = 0
RESPONSE_INDEX = 1
HOST_NAME_INDEX = 0

TO_MS = 1000


class PermissionException(Exception):
    pass


class Ping:
    """This class is used for pinging certain ip address.
    It send and receive ICMP or ARP packets from the host.
    Return value of ping_host() method is tuple that contain
    host ip, status and response time. This value returns to 
    the queue.
    """
    def __init__(self, iface, timeout=DEFAULT_TIMEOUT, resolve_names=False):
        """Constructor of Ping class objects initialize several private 
        variables :
            - __timeout       - time to break down waiting for host response
            - __iface         - interface that will be used to send packets
            - __resolve_names - resolve host ip instead of it name
            - __packet_tem... - template of packet structure at L2
        """
        self.__timeout = timeout
        self.__iface = iface
        self.__resolve_names = resolve_names
        self.__packet_template = scapy.Ether(dst=BROADCATS_MAC)

    def ping_host(self, ip, proto_type=ICMP_NAME):
        """method to create ICMP or ARP packet, send and receive response
        from the host with @ip address with timeout"""

        # form an ICMP or ARP packet
        if proto_type == ICMP_NAME:        
            packet = self.__packet_template / scapy.IP(dst=ip) / scapy.ICMP()
        elif proto_type == ARP_NAME:
            packet = self.__packet_template / scapy.ARP(pdst=ip)      
        else:
            print(" Incorrect proto_type in ping_host() method.")
            return

        # alias to scapy send_receive packet method
        self.__send_recv = partial(scapy.srp,
                                   iface=self.__iface,
                                   filter=proto_type,
                                   timeout=self.__timeout,
                                   verbose=DEFAULT_SCAPY_VERBOUS)

        try:
            # send and wait for response
            answers, unanswers = self.__send_recv(packet)
        except PermissionError:
            raise PermissionException

        if self._resolve_names:
            # resolve host name by ip if resolve_names
            # flag was set
            try:
                host = gethostbyaddr(ip)[HOST_NAME_INDEX]
            except herror:
                host = ip
        else:
            # otherwise show ip
            host = ip

        if answers:
            answer = answers[FIRST_INDEX]
            # get the request object
            req = answer[REQUEST_INDEX]
            # get the response object
            resp = answer[RESPONSE_INDEX]
            # calculate response time and round it
            delta = resp.time - req.sent_time
            return host, ONLINE, delta
        else:
            # return unansered results
            unanswer = unanswers[FIRST_INDEX]
            resp = unanswer[RESPONSE_INDEX]
            return host, OFFLINE, None

