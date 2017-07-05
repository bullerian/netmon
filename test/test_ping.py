from ping import *
import unittest
import ipaddress
import os

COUNT = 1
TIMEOUT = 1
STATUS_INDEX = 1

TEST_NETWORK = '172.20.8.0/24'


class TestARPPing(unittest.TestCase):
    """Tests for ping"""

    def test_arp_ping(self):
        """test ARP ping - compare to arping utilite"""

        arp_ping = ARPPing('wlp2s0')

        for ip in ipaddress.ip_network(TEST_NETWORK).hosts():
            try:
                # need arping installed
                with os.popen('arping -c {} {}'.format(COUNT, str(ip)), 'r'):
                    # get exit code
                    ec = os.wait()[1] & 0xFF00
                res = arp_ping.ping_host(str(ip))
            except PermissionException:
                print('Need root previlegies')
            if res[STATUS_INDEX] == ONLINE:
                self.assertTrue(ec == 0)
            else:
                self.assertFalse(ec == 0)

class TestICMPPing(unittest.TestCase):
    """Tests for ping"""

    def test_icmp_ping(self):
        """test icmp ping - compare to icmping utilite"""

        icmp_ping = ICMPPing('wlp2s0')

        for ip in ipaddress.ip_network(TEST_NETWORK).hosts():
            try:
                # need arping installed
                with os.popen('ping -c {} {}'.format(COUNT, str(ip)), 'r'):
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
