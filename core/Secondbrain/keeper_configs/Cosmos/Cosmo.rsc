# 2025-09-16 13:46:47 by RouterOS 7.19.1
# software id = B6JJ-9Y87
#
# model = RB4011iGS+
# serial number = HGF09QPPDAQ
/interface ethernet
set [ find default-name=ether2 ] disabled=yes name=LAN
/interface vlan
add interface=ether3 name=GUEST vlan-id=20
add interface=ether3 name="Maggies " vlan-id=50
/ip pool
add name=LAN ranges=192.168.1.10-192.168.1.254
add name=GUEST ranges=10.10.20.10-10.10.20.254
add name=MAGGIES ranges=192.168.100.10-192.168.100.254
/ip dhcp-server
add address-pool=LAN interface=ether3 lease-time=1d name=COSMOS
add address-pool=GUEST interface=GUEST name=GUEST
add address-pool=MAGGIES interface="Maggies " lease-time=1d name=Maggies
/port
set 0 name=serial0
set 1 name=serial1
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface ovpn-server server
add mac-address=FE:BF:EF:8E:F6:D5 name=ovpn-server1
/ip address
add address=192.168.1.1/24 interface=ether3 network=192.168.1.0
add address=142.190.106.74/30 interface=ether1 network=142.190.106.72
add address=10.20.20.1/24 interface=GUEST network=10.20.20.0
add address=192.168.100.1/24 interface="Maggies " network=192.168.100.0
/ip dhcp-server network
add address=10.20.20.0/24 dns-server=8.8.4.4,8.8.8.8 gateway=10.20.20.1 \
    netmask=24
add address=192.168.1.0/24 dns-server=8.8.4.4,8.8.8.8 gateway=192.168.1.1 \
    netmask=24
add address=192.168.100.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.100.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4
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
/ip ipsec profile
set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip route
add disabled=no distance=1 dst-address=0.0.0.0/0 gateway=142.190.106.73 \
    routing-table=main scope=30 suppress-hw-offload=no target-scope=10
/ip service
set ftp disabled=yes
set ssh disabled=yes
set telnet disabled=yes
set www disabled=yes
set api disabled=yes
set api-ssl disabled=yes
set winbox port=8899
/system clock
set time-zone-name=America/Chicago
/system identity
set name=COSMOS
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
