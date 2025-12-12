# 2025-09-16 18:29:12 by RouterOS 7.12.1
# software id = ISXB-825S
#
# model = RB4011iGS+
# serial number = HFG098CDNAH
/interface ethernet
set [ find default-name=ether1 ] name="ether1- WAN Uniti"
set [ find default-name=ether2 ] name=ether2-LAN
/interface vlan
add interface=ether2-LAN name=Ver vlan-id=10
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=LAN ranges=192.168.1.10-192.168.1.254
add name=VER ranges=192.168.10.10-192.168.10.254
/ip dhcp-server
add address-pool=LAN interface=ether2-LAN lease-time=1d name=LAN
add address-pool=VER interface=Ver lease-time=1d10m name=VER
/port
set 0 name=serial0
set 1 name=serial1
/interface bridge port
add bridge=*F interface=ether2-LAN
add bridge=*F interface=ether3
add bridge=*F interface=*E
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=69.85.239.26/30 interface="ether1- WAN Uniti" network=\
    69.85.239.24
add address=192.168.1.1/24 interface=ether2-LAN network=192.168.1.0
add address=192.168.10.1/24 interface=Ver network=192.168.10.0
/ip dhcp-server network
add address=192.168.1.0/24 dns-server=192.168.1.1 gateway=192.168.1.1 \
    netmask=24
add address=192.168.10.0/24 dns-server=192.168.10.1 gateway=192.168.10.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,443,8080,2000,53 in-interface=\
    "ether1- WAN Uniti" protocol=tcp src-port=""
add action=drop chain=input dst-port=53,123,161 in-interface=\
    "ether1- WAN Uniti" protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1- WAN Uniti"
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=69.85.239.25 routing-table=main \
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
set name="Sexton Gym/Viratos RB4011"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
