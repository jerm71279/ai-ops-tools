# 2025-09-19 16:47:46 by RouterOS 7.17
# software id = 1CVT-QRCB
#
# model = RB4011iGS+
# serial number = HG109WVPFY9
/interface bridge
add admin-mac=D4:01:C3:0A:0B:56 auto-mac=no comment=defconf name=bridge \
    port-cost-mode=short
/interface list
add comment=defconf name=WAN
add comment=defconf name=LAN
/ip pool
add name=LAN ranges=192.168.1.20-192.168.1.254
/ip dhcp-server
add address-pool=LAN interface=bridge lease-time=1d name=Bridge
/port
set 0 name=serial0
set 1 name=serial1
/interface bridge port
add bridge=bridge comment=defconf interface=ether2 internal-path-cost=10 \
    path-cost=10
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
add comment=defconf interface=ether1 list=WAN
/interface ovpn-server server
add mac-address=FE:83:64:B3:2A:49 name=ovpn-server1
/ip address
add address=192.168.1.1/24 interface=bridge network=192.168.1.0
add address=208.114.200.94/30 interface=ether1 network=208.114.200.92
/ip arp
add address=192.168.1.71 interface=bridge mac-address=9C:05:D6:E0:A2:E0
/ip dhcp-server network
add address=192.168.1.0/24 dns-server=9.9.9.9,8.8.8.8 gateway=192.168.1.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4
/ip dns static
add address=192.168.88.1 comment=defconf name=router.lan type=A
/ip firewall filter
add action=drop chain=input dst-port=21,22,80,443,2000,8080,53 in-interface=\
    ether1 protocol=tcp
add action=drop chain=input dst-port=123,23,53,161 in-interface=ether1 \
    protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat comment="defconf: masquerade" \
    ipsec-policy=out,none out-interface=ether1
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip ipsec profile
set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip route
add disabled=no distance=1 dst-address=0.0.0.0/0 gateway=208.114.200.93 \
    pref-src="" routing-table=main scope=30 suppress-hw-offload=no \
    target-scope=10
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
set name="Celebration - MikroTik"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
/tool mac-server
set allowed-interface-list=LAN
/tool mac-server mac-winbox
set allowed-interface-list=LAN
