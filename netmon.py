import argparse
import ipaddress

DEFAULT_TIMEOUT_SEC = 1


def ipnet(string):
    try:
        thenet = ipaddress.ip_network(string)
    except ValueError:
        msg = '%r is not a valid IP network address' % string
        raise argparse.ArgumentTypeError(msg)

    if not thenet.version == 4:
        msg = 'Only IPv4 addresses are supported'
        raise argparse.ArgumentTypeError(msg)

    return thenet


def formIPAddrSet(ip_list_path):
    with (open(ip_list_path, 'r')) as in_file:
        addrList = in_file.readlines()



def main(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Scans status of network hosts')
    parser.add_argument('ip_network',
                        type=ipnet,
                        help='IPv4 network address in CIDR notation')
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
                        type=formIPAddrSet,
                        metavar='list',
                        help='Path to list of host IPs to check')  # argparse.FileType('r')

    args_ = parser.parse_args()

    main(args_)
