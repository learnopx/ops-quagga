# -*- coding: utf-8 -*-

# Copyright (C) 2016 Hewlett Packard Enterprise Development LP
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import layer3_common as lib
from time import sleep
from pytest import mark

TOPOLOGY = """
# +-------+
# |  hs1  <---+   +--------+     +--------+
# +-------+   +--->        <----->        |     +-------+
#                 |  ops1  |     |  ops2  <----->  hs3  |
# +-------+   +--->        <----->        |     +-------+
# |  hs2  <---+   +--------+     +--------+
# +-------+

# Nodes
[type=openswitch] ops1
[type=openswitch] ops2
[type=host] hs1
[type=host] hs2
[type=host] hs3

# Links
ops1:if01 -- ops2:if01
ops1:if04 -- ops2:if03
hs1:eth0 -- ops1:if02
hs2:eth0 -- ops1:if03
hs3:eth0 -- ops2:if02
"""


@mark.timeout(500)
def test_ecmp_routing(topology, step):
    """
    Verify ecmp routing.
    """

    ops1 = topology.get('ops1')
    ops2 = topology.get('ops2')
    hs1 = topology.get('hs1')
    hs2 = topology.get('hs2')
    hs3 = topology.get('hs3')

    assert ops1 is not None
    assert ops2 is not None
    assert hs1 is not None
    assert hs2 is not None
    assert hs3 is not None

    # ----------Configure Switches and Hosts----------

    step('Configure Switches and Hosts')
    lib.switch_cfg_iface(ops1, 'if01', '10.0.30.1/24', '1030::1/120')
    lib.switch_cfg_iface(ops1, 'if02', '10.0.10.2/24', '1010::2/120')
    lib.switch_cfg_iface(ops1, 'if03', '10.0.20.2/24', '1020::2/120')
    lib.switch_cfg_iface(ops1, 'if04', '10.0.50.1/24', '1050::1/120')
    lib.switch_cfg_iface(ops2, 'if01', '10.0.30.2/24', '1030::2/120')
    lib.switch_cfg_iface(ops2, 'if02', '10.0.40.2/24', '1040::2/120')
    lib.switch_cfg_iface(ops2, 'if03', '10.0.50.2/24', '1050::2/120')
    sleep(15)

    lib.switch_add_ipv4_route(ops1, '10.0.40.0/24', '10.0.30.2')
    lib.switch_add_ipv4_route(ops1, '10.0.40.0/24', '10.0.50.2')
    lib.switch_add_ipv6_route(ops1, '1040::/120', '1030::2')
    lib.switch_add_ipv6_route(ops1, '1040::/120', '1050::2')
    lib.switch_add_ipv4_route(ops2, '10.0.10.0/24', '10.0.30.1')
    lib.switch_add_ipv4_route(ops2, '10.0.20.0/24', '10.0.30.1')
    lib.switch_add_ipv4_route(ops2, '10.0.10.0/24', '10.0.50.1')
    lib.switch_add_ipv4_route(ops2, '10.0.20.0/24', '10.0.50.1')
    lib.switch_add_ipv6_route(ops2, '1010::/120', '1030::1')
    lib.switch_add_ipv6_route(ops2, '1020::/120', '1030::1')
    lib.switch_add_ipv6_route(ops2, '1010::/120', '1050::1')
    lib.switch_add_ipv6_route(ops2, '1020::/120', '1050::1')

    lib.host_cfg_iface(hs1, 'eth0', '10.0.10.1/24', '1010::1/120')
    lib.host_cfg_iface(hs2, 'eth0', '10.0.20.1/24', '1020::1/120')
    lib.host_cfg_iface(hs3, 'eth0', '10.0.40.1/24', '1040::1/120')

    lib.host_add_route(hs1, '10.0.30.0/24', '10.0.10.2')
    lib.host_add_route(hs1, '10.0.40.0/24', '10.0.10.2')
    lib.host_add_route(hs1, '10.0.50.0/24', '10.0.10.2')
    lib.host_add_route(hs1, '1030::/120', '1010::2')
    lib.host_add_route(hs1, '1040::/120', '1010::2')
    lib.host_add_route(hs1, '1050::/120', '1010::2')
    lib.host_add_route(hs2, '10.0.30.0/24', '10.0.20.2')
    lib.host_add_route(hs2, '10.0.40.0/24', '10.0.20.2')
    lib.host_add_route(hs2, '10.0.50.0/24', '10.0.20.2')
    lib.host_add_route(hs2, '1030::/120', '1020::2')
    lib.host_add_route(hs2, '1040::/120', '1020::2')
    lib.host_add_route(hs2, '1050::/120', '1020::2')
    lib.host_add_route(hs3, '10.0.10.0/24', '10.0.40.2')
    lib.host_add_route(hs3, '10.0.20.0/24', '10.0.40.2')
    lib.host_add_route(hs3, '10.0.30.0/24', '10.0.40.2')
    lib.host_add_route(hs3, '10.0.50.0/24', '10.0.40.2')
    lib.host_add_route(hs3, '1010::/120', '1040::2')
    lib.host_add_route(hs3, '1020::/120', '1040::2')
    lib.host_add_route(hs3, '1030::/120', '1040::2')
    lib.host_add_route(hs3, '1050::/120', '1040::2')
    sleep(15)

    # ----------Do ping tests before removing routes----------

    step('Do ping tests before removing routes')
    lib.host_ping_expect_success(10, hs1, hs3, '10.0.40.1')
    lib.host_ping_expect_success(10, hs1, hs3, '1040::1')
    lib.host_ping_expect_success(10, hs2, hs3, '10.0.40.1')
    lib.host_ping_expect_success(10, hs2, hs3, '1040::1')

    # ----------Remove Routes----------

    step('Remove Routes')
    lib.switch_remove_ipv4_route(ops1, '10.0.40.0/24', '10.0.30.2')
    lib.switch_remove_ipv4_route(ops1, '10.0.40.0/24', '10.0.50.2')
    lib.switch_remove_ipv6_route(ops1, '1040::/120', '1030::2')
    lib.switch_remove_ipv6_route(ops1, '1040::/120', '1050::2')
    lib.switch_remove_ipv4_route(ops2, '10.0.10.0/24', '10.0.30.1')
    lib.switch_remove_ipv4_route(ops2, '10.0.20.0/24', '10.0.30.1')
    lib.switch_remove_ipv4_route(ops2, '10.0.10.0/24', '10.0.50.1')
    lib.switch_remove_ipv4_route(ops2, '10.0.20.0/24', '10.0.50.1')
    lib.switch_remove_ipv6_route(ops2, '1010::/120', '1030::1')
    lib.switch_remove_ipv6_route(ops2, '1020::/120', '1030::1')
    lib.switch_remove_ipv6_route(ops2, '1010::/120', '1050::1')
    lib.switch_remove_ipv6_route(ops2, '1020::/120', '1050::1')
    sleep(15)

    # ----------Do ping tests after removing routes----------

    step('Do ping tests before after routes')
    lib.host_ping_expect_failure(10, hs1, hs3, '10.0.40.1')
    lib.host_ping_expect_failure(10, hs1, hs3, '1040::1')
    lib.host_ping_expect_failure(10, hs2, hs3, '10.0.40.1')
    lib.host_ping_expect_failure(10, hs2, hs3, '1040::1')
