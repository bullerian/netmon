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
DEFAULT_RESOLV = False
DEFAULT_SCAPY_VERBOUS = 0
DEFAUTL_TIME_PREC = 2

FIRST_INDEX = 0
REQUEST_INDEX = 0
RESPONSE_INDEX = 1
HOST_NAME_INDEX = 0


class PermissionException(Exception):
    """Exception that is raised when root rights needed"""

    pass


class Ping:
    """This class is used for pinging certain ip address.
    It send and receive ICMP or ARP packets from the host.
    Return value of ping_host() method is tuple that contain
    host ip, status and response time"""

    # dictionary of expressions used
    # to generate packets to ping host by ip
    packets_generators = {
        ARP_NAME: lambda ip: scapy.Ether(
            dst=BROADCATS_MAC) / scapy.ARP(pdst=ip),
        ICMP_NAME: lambda ip: scapy.Ether(
            dst=BROADCATS_MAC) / scapy.IP(
            dst=ip) / scapy.ICMP()
    }

    def __init__(self,
                 iface,
                 proto_type=ICMP_NAME,
                 timeout=DEFAULT_TIMEOUT,
                 resolve_names=DEFAULT_RESOLV):
        """Constructor of Ping class objects initialize several private
        variables :
            - __iface         - interface that will be used to send packets
            - __timeout       - time to break down waiting for host response
            - __resolve_names - resolve host ip instead of it name
            - __gen_packet    - expression to generate packet due to
                                protocol we use"""

        self.__iface = iface
        self.__timeout = timeout
        self.__resolve_names = resolve_names
        self.__gen_packet = Ping.packets_generators[proto_type]

        # alias to scapy send_receive packet method
        self.__send_recv = partial(scapy.srp,
                                   iface=self.__iface,
                                   filter=proto_type,
                                   timeout=self.__timeout,
                                   verbose=DEFAULT_SCAPY_VERBOUS)

    def ping_host(self, ip):
        """method to send ICMP/ARP requests and receive response
        from the host with @ip address.
        Returns a tuple (ip/host name, ONLINE/OFFLINE, response time)"""

        # form an ICMP or ARP packet
        packet = self.__gen_packet(ip)

        try:
            # send and wait for response
            answers, unanswers = self.__send_recv(packet)
        except PermissionError:
            raise PermissionException

        if self.__resolve_names:
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
