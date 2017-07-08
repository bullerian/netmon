# netmon
The tool that scans status of hosts in network.

Written on Python 3.5.2

    usage: netmon.py [-h] [-n] [-t timeout] [-a] [-r refresh rate] [-l list]
                   [-i interface]
                   ip_network
    positional arguments:
      ip_network       IPv4 network address in form A.B.C.D/mask

    optional arguments:
      -h, --help       show this help message and exit
      -n               Show host IPs instead of names
      -t timeout       Timeout in seconds
      -a               Use ARP instead if ICMP
      -r refresh rate  Refresh rate in seconds
      -l list          Path to list of host IPs to check
      -i interface     Name if network interface
