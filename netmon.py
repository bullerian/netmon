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


def ipnet(net_str):
    """
    This function is used for argparse module to verify validness of
    entered network. Valid networks are IPv4 networks in form
    A.B.C.D/prefix
    :param net_str: string that represents IPv4 net. Example A.B.C.D/prefix.
    :return: ipaddress.ip_network object or raises exception on fail
    """
    try:
        thenet = ipaddress.ip_network(net_str)
    except ValueError:
        msg = '%r is not a valid IP network address' % net_str
        raise argparse.ArgumentTypeError(msg)

    if not thenet.version == 4:
        msg = 'Only IPv4 addresses are supported'
        raise argparse.ArgumentTypeError(msg)

    return thenet


def rawIPlist(ip_list_path):
    """
    Import IP adresses from file as list.
    Duplicate checking can be added here.
    :param ip_list_path: path to file with IP adresses
    :return: list of IP adresses
    """
    with (open(ip_list_path, 'r')) as in_file:
        addrList = in_file.read().split()

    return addrList


def finalIPiter(rawList, networkObj):
    """
    Should return intersection of IPs in rawList and networkObject in form
    of ipaddress.ip_address object iterator
    (or list iterator). Drops invalid strings or adresses.
    If rawList is not provided returns ipaddress.ip_address object
    iterator generated from networkObj.
    NOTE: network itself and broadcast IP are excluded from list
    :param rawList: list of IP address strings
    :param networkObj: the network object
    :return:
    """
    if not rawList:
        return networkObj.hosts()

    for addrStr in rawList:
        try:
            addrsObj = ipaddress.ip_address(addrStr)
        except ValueError:
            print('%s is not valid IPv4 address. It will be ignored.'.format(addrStr))

        if addrsObj in networkObj and addrStr != networkObj.broadcast_address:
            # TODO: this generator has to be replaced by iterator
            yield addrsObj
        else:
            print('{} is not in {} network. It will be ignored.'.format(addrStr, str(networkObj)))


def create_argparser():
    parser = argparse.ArgumentParser(description='Scans status of network hosts')
    parser.add_argument('ip_network',
                        type=ipnet,
                        help='IPv4 network address in form A.B.C.D/mask')
    parser.add_argument('-n',
                        '--p_hostname',
                        action='store_true',
                        default=False,
                        help='Show host IPs instead of names')
    parser.add_argument('-t',
                        type=int,
                        default=DEFAULT_TIMEOUT_SEC,
                        metavar='timeout',
                        help='Timeout in seconds')
    parser.add_argument('-a',
                        '--ARP',
                        action='store_const',
                        default=ICMP_NAME,
                        const=ARP_NAME,
                        help='Use ARP instead if ICMP')
    parser.add_argument('-r',
                        type=int,
                        metavar='refresh rate',
                        help='Refresh rate in seconds')
    parser.add_argument('-l',
                        '--list',
                        type=rawIPlist,
                        metavar='list',
                        help='Path to list of host IPs to check')
    return parser


def main():
    args = create_argparser().parse_args()

    proto = args.ARP
    pinger = ping.Ping(proto,
                       args.t,
                       args.p_hostname)

    network = ipnet(args.ip_network)

    print_heder()

    with TPool() as TManager:
        future_to_ping = [
            TManager.submit(pinger.ping_host,str(ip)) for ip in network.hosts()
        ]
        for thread in as_completed(future_to_ping):
            host, st, time = thread.result()
            # print_result(host, st, time)
            print_online(host, st, time)

if __name__ == '__main__':
    main()
