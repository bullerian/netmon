#!/usr/bin/env python3

import os
import sys
# disable scapy warning with IPv6
# sorry PEP8 (
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
import scapy.all as scapy
from abc import ABC, abstractmethod
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


class Ping(ABC):
    """This class is a base class for sending request packets
    and receiveing response packets from pinged host and it puts
    tuple with host ip, status (ONLINE/OFFLINE) and response time
    to the queue"""

    def __init__(self, iface, timeout, resolve_names=False):
        """init timeout parametr"""

        self._timeout = timeout
        self._iface = iface
        self._resolve_names = resolve_names

    @abstractmethod
    def ping_host(self, ip):
        """abstract method for ping"""

        pass


class ARPPing(Ping):
    """Ping using ARP protocol"""

    def __init__(self, iface, timeout=DEFAULT_TIMEOUT, resolve_names=False):
        """init queue and timeout; form a template of Ethernet packet
        and make alias for scapy.srp function"""

        # call base Ping class constructor
        super().__init__(iface, timeout, resolve_names)

        # form a template packet
        self.__packet_template = scapy.Ether(dst=BROADCATS_MAC)

        # alias for scapy.srp
        self.__send_recv_ARP = partial(
            scapy.srp,
            iface=self._iface,
            filter=ARP_NAME,
            timeout=self._timeout,
            verbose=DEFAULT_SCAPY_VERBOUS)

    def ping_host(self, ip):
        """method to create ARP packet, send and receive response
        from the host with @ip address with timeout"""

        # form an ARP packet
        arp_packet = self.__packet_template / scapy.ARP(pdst=ip)

        try:
            # send and wait for response
            answers, unanswers = self.__send_recv_ARP(arp_packet)
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


class ICMPPing(Ping):
    """Ping using ICMP protocol"""

    def __init__(self, iface, timeout=DEFAULT_TIMEOUT, resolve_names=False):
        """init queue and timeout; form a template of Ethernet packet
        and make alias for scapy.srp function"""

        # call base Ping class constructor
        super().__init__(iface, timeout, resolve_names)

        # form a template packet
        self.__packet_template = scapy.Ether(dst=BROADCATS_MAC)

        # alias for scapy.srp
        self.__send_recv_ICMP = partial(
            scapy.srp,
            iface=self._iface,
            filter=ICMP_NAME,
            timeout=self._timeout,
            verbose=DEFAULT_SCAPY_VERBOUS)

    def ping_host(self, ip):
        """method to create ICMP packet, send and receive response
        from the host with @io address with timeout"""

        # form an ICMP packet
        icmp_packet = self.__packet_template / scapy.IP(dst=ip) / scapy.ICMP()

        try:
            # send and wait for response
            answers, unanswers = self.__send_recv_ICMP(icmp_packet)
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
            return host, OFFLINE
