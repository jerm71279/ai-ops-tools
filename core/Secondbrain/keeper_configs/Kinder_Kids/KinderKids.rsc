# 1970-08-20 14:44:50 by RouterOS 7.17
# software id = NGWA-NB07
#
# model = RB4011iGS+
# serial number = HG409NJJ5N9
/interface bridge
add name=bridge1 port-cost-mode=short
/interface vlan
add interface=bridge1 name=Office vlan-id=10
add interface=bridge1 name="VLAN50 CC Reader" vlan-id=50
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=Office ranges=192.168.1.25-192.168.1.254
add name=Bridge ranges=10.3.3.2-10.3.3.254
add name=CC ranges=192.168.50.10-192.168.50.200
/ip dhcp-server
add address-pool=Bridge interface=bridge1 lease-time=1d name=Bridge
add address-pool=Office interface=Office lease-time=1d name=Office
add address-pool=CC interface="VLAN50 CC Reader" lease-time=1d name="CC Read"
/port
set 0 name=serial0
set 1 name=serial1
/interface bridge port
add bridge=bridge1 interface=ether2 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether3 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether4 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether5 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether6 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether7 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether8 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether9 internal-path-cost=10 path-cost=10
add bridge=bridge1 interface=ether10 internal-path-cost=10 path-cost=10
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface ovpn-server server
add mac-address=FE:B2:54:12:14:10 name=ovpn-server1
/ip address
add address=192.168.1.1/24 interface=Office network=192.168.1.0
add address=10.3.3.1/24 interface=bridge1 network=10.3.3.0
add address=69.85.196.126/30 interface=ether1 network=69.85.196.124
add address=192.168.50.1/24 interface="VLAN50 CC Reader" network=192.168.50.0
/ip dhcp-server network
add address=10.3.3.0/24 dns-server=8.8.8.8,8.8.1.1 gateway=10.3.3.1 netmask=\
    24
add address=192.168.1.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.1.1 \
    netmask=24
add address=192.168.50.0/24 dns-server=8.8.8.8,9.9.9.9 gateway=192.168.50.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4,9.9.9.9
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,80,443,8080,2000 \
    in-interface=ether1 protocol=tcp
add action=drop chain=input dst-port=53,123,161 in-interface=ether1 protocol=\
    udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface=ether1
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip hotspot profile
set [ find default=yes ] html-directory=hotspot
/ip ipsec profile
set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip route
add disabled=no distance=1 dst-address=0.0.0.0/0 gateway=69.85.196.125 \
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
/system clock
set time-zone-name=America/Chicago
/system identity
set name="Kinder KIds (Friendship Rd)"
/system note
set show-at-login=no
/system ntp client
set enabled=yes
/system ntp client servers
add address=0.us.pool.ntp.org
add address=1.us.pool.ntp.org
add address=2.us.pool.ntp.org
add address=3.us.pool.ntp.org
/system routerboard settings
set enter-setup-on=delete-key
