# 2025-09-16 15:19:40 by RouterOS 7.15.2
# software id = GWD5-3VYK
#
# model = RB4011iGS+
# serial number = HFG097JY2F1
/interface ethernet
set [ find default-name=ether1 ] name="ether1 - WAN-Uniti"
set [ find default-name=ether2 ] name="ether2 - LAN"
set [ find default-name=ether3 ] name="ether3 LTE BackUp"
/interface vlan
add interface="ether2 - LAN" name=GUEST vlan-id=300
/ip pool
add name=LAN ranges=192.168.100.20-192.168.100.254
add name=GUEST ranges=10.10.20.10-10.10.20.254
/ip dhcp-server
add address-pool=GUEST interface=GUEST lease-time=1d name=GUEST
add address-pool=LAN interface="ether2 - LAN" lease-time=1d name=LAN
/ip smb users
set [ find default=yes ] disabled=yes
/port
set 0 name=serial0
set 1 name=serial1
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=10.10.20.1/24 interface=GUEST network=10.10.20.0
add address=192.168.100.1/24 interface="ether2 - LAN" network=192.168.100.0
add address=142.190.161.62/30 interface="ether1 - WAN-Uniti" network=\
    142.190.161.60
/ip dhcp-client
add interface="ether3 LTE BackUp"
/ip dhcp-server network
add address=10.10.20.0/24 dns-server=10.10.20.1 gateway=10.10.20.1 netmask=24
add address=192.168.100.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.100.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=\
    9.9.9.9,8.8.8.8,1.1.1.1,9.9.9.9,75.76.160.3,75.76.160.4
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,2000,53,80,8080,443 \
    in-interface="ether1 - WAN-Uniti" protocol=tcp
add action=drop chain=input dst-port=53,161,123 in-interface=\
    "ether1 - WAN-Uniti" protocol=udp src-address-list=""
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1 - WAN-Uniti"
add action=masquerade chain=srcnat out-interface="ether3 LTE BackUp"
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=142.190.161.61 routing-table=\
    main suppress-hw-offload=no
add disabled=no distance=50 dst-address=0.0.0.0/0 gateway=192.168.10.254 \
    routing-table=main scope=30 suppress-hw-offload=no target-scope=10
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh disabled=yes
set api disabled=yes
set winbox port=8899
set api-ssl disabled=yes
/ip smb shares
set [ find default=yes ] directory=/pub
/system clock
set time-zone-name=America/New_York
/system identity
set name="Dunlap Shipman PC RB4011"
/system note
set note="This is Dunlap & Shipman"
/system routerboard settings
set enter-setup-on=delete-key
