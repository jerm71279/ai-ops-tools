# 2025-09-16 10:12:09 by RouterOS 7.19.3
# software id = BMXA-MN9I
#
# model = RB4011iGS+
# serial number = HGF09PD6BAV
/ip pool
add name=LAN ranges=192.168.1.20-192.168.1.254
/ip dhcp-server
add address-lists=192.168.1.0/24 address-pool=LAN interface=ether2 \
    lease-time=1d name=LAN server-address=192.168.1.1
/port
set 0 name=serial0
set 1 name=serial1
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface ovpn-server server
add mac-address=FE:25:1F:34:83:2C name=ovpn-server1
/ip address
add address=142.190.106.2/30 interface=ether1 network=142.190.106.0
add address=192.168.1.1/24 interface=ether2 network=192.168.1.0
/ip dhcp-server network
add address=192.168.1.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.1.1 \
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
/ip ipsec profile
set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=142.190.106.1 routing-table=\
    main suppress-hw-offload=no
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
set name="Luna's"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
