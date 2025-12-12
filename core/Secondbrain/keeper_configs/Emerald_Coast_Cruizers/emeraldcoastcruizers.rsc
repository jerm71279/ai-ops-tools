# 2025-09-16 14:15:37 by RouterOS 7.15.2
# software id = H0WD-880A
#
# model = RB4011iGS+
# serial number = HFG0962SGF5
/interface ethernet
set [ find default-name=ether1 ] name="ether1 - WAN Uniti"
set [ find default-name=ether2 ] name="ether2 - LAN"
/ip pool
add name=MGMT ranges=192.168.1.20-192.168.1.254
/ip dhcp-server
add address-pool=MGMT interface="ether2 - LAN" lease-time=1d name=MGMT
/port
set 0 name=serial0
set 1 name=serial1
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=192.168.1.1/24 interface="ether2 - LAN" network=192.168.1.0
add address=142.190.50.46/30 interface="ether1 - WAN Uniti" network=\
    142.190.50.44
/ip dhcp-server network
add address=192.168.1.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.1.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,80,8080,2000 in-interface=\
    "ether1 - WAN Uniti" protocol=tcp
add action=drop chain=input dst-port=161,123,53 in-interface=\
    "ether1 - WAN Uniti" protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1 - WAN Uniti"
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=142.190.50.45 routing-table=\
    main suppress-hw-offload=no
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
set name="Emerald Coast Cruisers"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
