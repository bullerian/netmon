import argparse
import ipaddress
import concurrent.futures

MAX_THREADS = 4 #number of threads
DEFAULT_TIMEOUT_SEC = 1


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


#testing purposes
def dummy_ping(ip):
    return ("127.0.0."+str(ip), "online", 0)


def main(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scans status of network hosts')
    parser.add_argument('ip_network',
                        type=ipnet,
                        help='IPv4 network address in form A.B.C.D/mask')
    parser.add_argument('-n',
                        action='store_true',
                        help='Show host IPs instead of names')
    parser.add_argument('-t',
                        type=int,
                        default=DEFAULT_TIMEOUT_SEC,
                        metavar='timeout',
                        help='Timeout in seconds')
    parser.add_argument('-a',
                        action='store_true',
                        help='Use ARP instead if ICMP')
    parser.add_argument('-r',
                        type=int,
                        metavar='refresh rate',
                        help='Refresh rate in seconds')
    parser.add_argument('-l',
                        type=rawIPlist,
                        metavar='list',
                        help='Path to list of host IPs to check')
    parser.add_argument('-i',
                        type=str,
                        metavar='interface',
                        help='Name if network interface')

    #args_ = parser.parse_args()

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_THREADS) as ThreadManager:
    future_to_ping = {ThreadManager.submit(dummy_ping, ip): ip for ip in range(25)}
    for future in concurrent.futures.as_completed(future_to_ping):
        res = future.result()
        print(res)

    main(args_)
