# 2025-09-16 17:24:11 by RouterOS 7.16.2
# software id = FJUS-84KJ
#
# model = RB4011iGS+
# serial number = HG109K607T1
/interface bridge
add admin-mac=D4:01:C3:0A:13:9C auto-mac=no comment=defconf name=bridge \
    port-cost-mode=short
/interface ethernet
set [ find default-name=ether1 ] name="ether1 - WAN Uniti"
set [ find default-name=ether2 ] name="ether2 - LAN"
set [ find default-name=ether10 ] poe-out=off poe-priority=1 \
    power-cycle-interval=1w
/interface vlan
add interface=bridge name=Guest vlan-id=200
/interface list
add comment=defconf name=WAN
add comment=defconf name=LAN
/ip pool
add name=LAN ranges=192.168.1.20-192.168.1.254
add name=Guest ranges=192.168.0.10-192.168.0.110
/ip dhcp-server
add address-pool=LAN interface=bridge lease-time=1d name=LAN
add address-pool=Guest interface=Guest lease-time=1h name=Guest
/port
set 0 name=serial0
set 1 name=serial1
/interface bridge port
add bridge=bridge comment=defconf interface="ether2 - LAN" \
    internal-path-cost=10 path-cost=10
add bridge=bridge comment=defconf interface=ether3 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=ether4 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=ether5 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=ether6 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=ether7 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=ether8 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=ether9 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=ether10 internal-path-cost=10 \
    path-cost=10
add bridge=bridge comment=defconf interface=sfp-sfpplus1 internal-path-cost=\
    10 path-cost=10
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface list member
add comment=defconf interface=bridge list=LAN
add comment=defconf interface="ether1 - WAN Uniti" list=WAN
/ip address
add address=208.114.200.134/30 interface="ether1 - WAN Uniti" network=\
    208.114.200.132
add address=192.168.1.1/24 interface=bridge network=192.168.1.0
add address=192.168.0.1/24 interface=Guest network=192.168.0.0
/ip dhcp-server network
add address=192.168.0.0/24 dns-server=192.168.0.1 gateway=192.168.0.1 \
    netmask=24
add address=192.168.1.0/24 dns-server=192.168.1.1 gateway=192.168.1.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4,9.9.9.9
/ip dns static
add address=192.168.88.1 comment=defconf name=router.lan type=A
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,80,443,8080,2000 \
    in-interface="ether1 - WAN Uniti" protocol=tcp
add action=drop chain=input dst-port=53,123,161 in-interface=\
    "ether1 - WAN Uniti" protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1 - WAN Uniti"
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip ipsec profile
set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=208.114.200.133 routing-table=\
    main suppress-hw-offload=no
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh disabled=yes
set api disabled=yes
set winbox port=8899
set api-ssl disabled=yes
/ipv6 firewall address-list
add address=::/128 comment="defconf: unspecified address" list=bad_ipv6
add address=::1/128 comment="defconf: lo" list=bad_ipv6
add address=fec0::/10 comment="defconf: site-local" list=bad_ipv6
add address=::ffff:0.0.0.0/96 comment="defconf: ipv4-mapped" list=bad_ipv6
add address=::/96 comment="defconf: ipv4 compat" list=bad_ipv6
add address=100::/64 comment="defconf: discard only " list=bad_ipv6
add address=2001:db8::/32 comment="defconf: documentation" list=bad_ipv6
add address=2001:10::/28 comment="defconf: ORCHID" list=bad_ipv6
add address=3ffe::/16 comment="defconf: 6bone" list=bad_ipv6
/ipv6 firewall filter
add action=accept chain=input comment=\
    "defconf: accept established,related,untracked" connection-state=\
    established,related,untracked
add action=drop chain=input comment="defconf: drop invalid" connection-state=\
    invalid
add action=accept chain=input comment="defconf: accept ICMPv6" protocol=\
    icmpv6
add action=accept chain=input comment="defconf: accept UDP traceroute" port=\
    33434-33534 protocol=udp
add action=accept chain=input comment=\
    "defconf: accept DHCPv6-Client prefix delegation." dst-port=546 protocol=\
    udp src-address=fe80::/10
add action=accept chain=input comment="defconf: accept IKE" dst-port=500,4500 \
    protocol=udp
add action=accept chain=input comment="defconf: accept ipsec AH" protocol=\
    ipsec-ah
add action=accept chain=input comment="defconf: accept ipsec ESP" protocol=\
    ipsec-esp
add action=accept chain=input comment=\
    "defconf: accept all that matches ipsec policy" ipsec-policy=in,ipsec
add action=drop chain=input comment=\
    "defconf: drop everything else not coming from LAN" in-interface-list=\
    !LAN
add action=accept chain=forward comment=\
    "defconf: accept established,related,untracked" connection-state=\
    established,related,untracked
add action=drop chain=forward comment="defconf: drop invalid" \
    connection-state=invalid
add action=drop chain=forward comment=\
    "defconf: drop packets with bad src ipv6" src-address-list=bad_ipv6
add action=drop chain=forward comment=\
    "defconf: drop packets with bad dst ipv6" dst-address-list=bad_ipv6
add action=drop chain=forward comment="defconf: rfc4890 drop hop-limit=1" \
    hop-limit=equal:1 protocol=icmpv6
add action=accept chain=forward comment="defconf: accept ICMPv6" protocol=\
    icmpv6
add action=accept chain=forward comment="defconf: accept HIP" protocol=139
add action=accept chain=forward comment="defconf: accept IKE" dst-port=\
    500,4500 protocol=udp
add action=accept chain=forward comment="defconf: accept ipsec AH" protocol=\
    ipsec-ah
add action=accept chain=forward comment="defconf: accept ipsec ESP" protocol=\
    ipsec-esp
add action=accept chain=forward comment=\
    "defconf: accept all that matches ipsec policy" ipsec-policy=in,ipsec
add action=drop chain=forward comment=\
    "defconf: drop everything else not coming from LAN" in-interface-list=\
    !LAN
/system clock
set time-zone-name=America/Chicago
/system identity
set name="Ravenite RB4011"
/system note
set note="Ravenite Mikrotik"
/system routerboard settings
set enter-setup-on=delete-key
/tool mac-server
set allowed-interface-list=LAN
/tool mac-server mac-winbox
set allowed-interface-list=LAN
