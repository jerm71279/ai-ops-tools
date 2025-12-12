# 2025-09-16 16:08:01 by RouterOS 7.16.2
# software id = JLZS-VX14
#
# model = RB4011iGS+
# serial number = HFG099TX1PY
/interface ethernet
set [ find default-name=ether1 ] name="ether1 - WAN "
set [ find default-name=ether2 ] name="ether2 - LAN"
set [ find default-name=ether3 ] name="ether3 "
/interface vlan
add interface="ether2 - LAN" name=CourtHouseCoffee vlan-id=100
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=LAN ranges=192.168.1.10-192.168.1.254
add name=CourtHouseCoffee ranges=10.10.10.10-10.10.10.254
/ip dhcp-server
add address-pool=LAN interface="ether2 - LAN" lease-time=1d name=LAN
add address-pool=CourtHouseCoffee interface=CourtHouseCoffee name=\
    CourtHouseCoffee
/port
set 0 name=serial0
set 1 name=serial1
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=96.90.17.93/30 interface="ether1 - WAN " network=96.90.17.92
add address=192.168.1.1/24 interface="ether2 - LAN" network=192.168.1.0
add address=10.10.10.1/24 interface=CourtHouseCoffee network=10.10.10.0
/ip dhcp-server network
add address=10.10.10.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=10.10.10.1 \
    netmask=24
add address=192.168.1.0/24 dns-server=192.168.1.1 gateway=192.168.1.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4,9.9.9.9
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,2000,8080,443 in-interface=\
    "ether1 - WAN " protocol=tcp
add action=drop chain=input dst-port=53,123,161 in-interface="ether1 - WAN " \
    protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1 - WAN "
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip ipsec profile
set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=96.90.17.94 routing-table=main \
    suppress-hw-offload=no
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh disabled=yes
set api disabled=yes
set winbox port=8899
set api-ssl disabled=yes
/system clock
set time-zone-name=America/New_York
/system identity
set name="Hinson Law RB4011"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
