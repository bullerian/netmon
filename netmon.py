import argparse
import ipaddress
import scapy.all as scapy

DEFAULT_TIMEOUT_SEC = 1


class Utilities:

    @staticmethod
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

    @staticmethod
    def raw_ip_list(ip_list_path):
        """
        Import IP adresses from file as list.
        Duplicate checking can be added here.
        :param ip_list_path: path to file with IP adresses
        :return: list of IP adresses
        """
        with (open(ip_list_path, 'r')) as in_file:
            addrList = in_file.read().split()

        return addrList


class AddressIter:
    def __init__(self, raw_list, network_obj, verbose=True):
        self._raw_ip_list = raw_list
        self._ip_net_obj = network_obj
        self._verbose = verbose

    def __iter__(self):
        if not rawList:
            return networkObj.hosts()
        else:
            return self

    def __next__(self):
        x = list()
        x.
        if self._raw_ip_list
        for addrStr in rawList:
            try:
                addrsObj = ipaddress.ip_address(addrStr)
            except ValueError:
                print(
                    '%s is not valid IPv4 address. It will be ignored.'.format(
                        addrStr))

            if addrsObj in networkObj and addrStr != networkObj.broadcast_address:
                # TODO: this generator has to be replaced by iterator
                yield addrsObj
            else:
                print('{} is not in {} network. It will be ignored.'.format(
                    addrStr, str(networkObj)))


    def final_ip_iter(self):
        """
        Should return intersection of IPs in rawList and networkObject in form
        of ipaddress.ip_address object iterator
        (or list iterator). Drops invalid strings or adresses.
        If rawList is not provided returns ipaddress.ip_address object
        iterator generated from networkObj.
        NOTE: network itself and broadcast IP are excluded from list
        :return:
        """
        if not rawList:
            return networkObj.hosts()

        for addrStr in rawList:
            try:
                addrsObj = ipaddress.ip_address(addrStr)
            except ValueError:
                print(
                    '%s is not valid IPv4 address. It will be ignored.'.format(
                        addrStr))

            if addrsObj in networkObj and addrStr != networkObj.broadcast_address:
                # TODO: this generator has to be replaced by iterator
                yield addrsObj
            else:
                print('{} is not in {} network. It will be ignored.'.format(
                    addrStr, str(networkObj)))


def main(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scans status of network hosts')
    parser.add_argument('ip_network',
                        type=Utilities.ipnet,
                        help='IPv4 network address in form A.B.C.D/mask')
    parser.add_argument('-n',
                        action='store_true',
                        help='Show host IPs instead of names')
    parser.add_argument('-t',
                        '--timeout',
                        type=int,
                        default=DEFAULT_TIMEOUT_SEC,
                        metavar='timeout',
                        help='Timeout in seconds')
    parser.add_argument('-a',
                        '--arp',
                        action='store_true',
                        help='Use ARP instead if ICMP')
    parser.add_argument('-r',
                        '--refresh',
                        type=int,
                        metavar='refresh rate',
                        help='Refresh rate in seconds')
    parser.add_argument('-l',
                        type=Utilities.raw_ip_list,
                        metavar='list',
                        help='Path to list of host IPs to check')
    parser.add_argument('-i',
                        type=str,
                        metavar='interface',
                        help='Name if network interface')

    args_ = parser.parse_args()

    main(args_)
