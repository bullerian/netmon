#!/usr/bin/env python3

import argparse
import ipaddress
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor as TPool
from concurrent.futures import as_completed


import ping

MAX_THREADS = 4 #number of threads
DEFAULT_TIMEOUT_SEC = 1
ARP_NAME = 'arp'
ICMP_NAME = 'icmp'

HOST_WIDTH = 18
STATUS_WIDTH = 12
MILISECOND = 'ms'
STATUS_TEMPALE = '[{}]'
HEDER = 'Host              Status      Time'
DEFAULT_TIME_OUTPUT = "---"

def print_heder():
    """Print title for output"""
    print(HEDER)


def print_result(host, status, time):
    """Format and print result"""
    host = str(host).ljust(HOST_WIDTH)
    status = STATUS_TEMPALE.format(str(status)).ljust(STATUS_WIDTH)
    if time:
        time = str(round(time*1000, 2)) + MILISECOND
    else:
        time = DEFAULT_TIME_OUTPUT
    print(host, status, time, sep='')


def print_online(host, status, time):
    if status == "ONLINE":
        print_result(host, status, time)


class Utilities:
    IPV4 = 4

    @staticmethod
    def _ipnet(net_str):
        """
        This function is used for argparse module to verify validness of
        entered network. Valid networks are IPv4 networks in form
        A.B.C.D/prefix
        :param net_str: string that represents IPv4 net. Example A.B.C.D/prefix.
        :return: ipaddress.ip_network object or raises exception on fail
        """
        try:
            the_net = ipaddress.ip_network(net_str)
        except ValueError:
            msg = '{} is not a valid IP network address'.format(net_str)
            raise argparse.ArgumentTypeError(msg)

        if the_net.version != Utilities.IPV4:
            msg = 'Only IPv4 addresses are supported'
            raise argparse.ArgumentTypeError(msg)

        return the_net

    @staticmethod
    def _raw_ip_list(ip_list_path):
        """
        Import IP adresses from file as list.
        Duplicate checking can be added here.
        :param ip_list_path: path to file with IP adresses
        :return: list of IP adresses
        """
        with (open(ip_list_path, 'r')) as in_file:
            addrList = in_file.read().split()

        return addrList

    @staticmethod
    def input_parser():
        parser = argparse.ArgumentParser(
            description='Scans status of network hosts')
        parser.add_argument('ip_network',
                            type=Utilities._ipnet,
                            help='IPv4 network address in form A.B.C.D/mask')
        parser.add_argument('-n',
                            '--p_hostname',
                            action='store_true',
                            help='Show host IPs instead of names')
        parser.add_argument('-t',
                            '--timeout',
                            type=int,
                            default=DEFAULT_TIMEOUT_SEC,
                            metavar='timeout',
                            help='Timeout in seconds')
        parser.add_argument('-a',
                            '--ARP',
                            action='store_const',
                            const=ARP_NAME,
                            default=ICMP_NAME,
                            help='Use ARP instead if ICMP')
        parser.add_argument('-r',
                            '--refresh',
                            type=int,
                            metavar='refresh rate',
                            help='Refresh rate in seconds')
        parser.add_argument('-l',
                            '--IP_list',
                            type=Utilities._raw_ip_list,
                            metavar='list',
                            help='Path to list of host IPs to check')

        return parser.parse_args()


class AddressIter:
    """
    Instance of this class will return all valid IPv4 addresses in string
    representation. Address related errors are printed unless verbose is set to
    False.
    """
    def __init__(self, raw_list, network_obj, verbose=True):
        """
        Initializes object
        :param raw_list: list of probable IP addresses strings
        :param network_obj: network object
        :param verbose: print error output
        """
        self._raw_ip_list = raw_list
        self._ip_net_obj = network_obj
        self._verbose = verbose
        self.__index = 0

    def __iter__(self):
        """
        If there are no host IP list then return all valid host IPs in network.
        Else return only those addresses that are in network.
        :return:
        """
        if not self._raw_ip_list:
            return self._ip_net_obj.hosts()
        else:
            return self

    def __next__(self):
        while self.__index < len(self._raw_ip_list):
            addr_str = self._raw_ip_list[self.__index]

            try:
                self.__index += 1
                addrs_obj = ipaddress.ip_address(addr_str)
            except (ValueError, UnboundLocalError):
                self.__print_out('"{}" is not a valid IPv4 address and '
                                 'will be ignored.'.format(addr_str))
                continue

            if not self.is_acceptable(addrs_obj):
                self.__print_out('"{}" is not in network "{}" and will be '
                                 'ignored.'.format(addr_str, self._ip_net_obj))
                continue

            return addr_str

        self.__index = 0
        raise StopIteration

    def __print_out(self, text):
        """
        Prints text if self._verbose is set
        :param text:
        :return:
        """
        if self._verbose:
            print(text)

    def is_acceptable(self, ip_obj):
        """
        If ip_obj is not None and it is in network and it is not broadcast
        address then return True
        :param ip_obj: IP class instance
        :return: True or False
        """
        return ip_obj and ip_obj in self._ip_net_obj and ip_obj != \
                                        self._ip_net_obj.broadcast_address


def main():
    args = Utilities.input_parser()

    # object for iteration
    ip_iter_obj = AddressIter(args.IP_list, args.ip_network)

    proto = args.ARP
    pinger = ping.Ping(proto,
                       args.timeout,
                       args.p_hostname)

    network = args.ip_network

    print_heder()

    with TPool() as TManager:
        future_to_ping = [
            TManager.submit(pinger.ping_host, str(ip)) for ip in
            network.hosts()
        ]
        for thread in as_completed(future_to_ping):
            try:
                host, st, time = thread.result()
                # print_result(host, st, time)
                print_online(host, st, time)
            except ping.PermissionException:
                print('You need to have root rights to run this.')
                break


if __name__ == '__main__':
    main()


