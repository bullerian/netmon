from ping import *
import unittest
import ipaddress
import os

COUNT = 1
TIMEOUT = 1
STATUS_INDEX = 1

TEST_NETWORK = '192.168.0.0/24'
IFACE = 'wlo1'

class TestPing(unittest.TestCase):
    """Tests for ping"""

    def test_arp_ping(self):
        """test ARP ping - compare to arping utilite"""

        arp_ping = Ping(IFACE, ARP_NAME, TIMEOUT, False)

        for ip in list(ipaddress.ip_network(TEST_NETWORK).hosts())[:5]:
            try:
                # need arping installed
                with os.popen('arping -c {} -t {} {}'.format(COUNT,
                                                             TIMEOUT,
                                                             str(ip)), 'r'):
                    # get exit code
                    ec = os.wait()[1] & 0xFF00
                res = arp_ping.ping_host(str(ip))
            except PermissionException:
                print('Need root previlegies')

            if res[STATUS_INDEX] == ONLINE:
                self.assertTrue(ec == 0)
            else:
                self.assertFalse(ec == 0)

    def test_icmp_ping(self):
        """test icmp ping - compare to icmping utilite"""

        icmp_ping = Ping(IFACE, ICMP_NAME,  TIMEOUT, False)

        for ip in list(ipaddress.ip_network(TEST_NETWORK).hosts())[:5]:
            try:
                # need arping installed
                with os.popen('ping -c {} -t {} {}'.format(COUNT,
                                                           TIMEOUT,
                                                           str(ip)), 'r'):
                    # get exit code
                    ec = os.wait()[1] & 0xFF00
                res = icmp_ping.ping_host(str(ip))
            except PermissionException:
                print('Need root previlegies')
            if res[STATUS_INDEX] == ONLINE:
                self.assertTrue(ec == 0)
            else:
                self.assertFalse(ec == 0)

if __name__ == '__main__':
    unittest.main()
