# 2025-09-16 17:06:44 by RouterOS 7.11.3
# software id = CEBN-VC4S
#
# model = RB4011iGS+
# serial number = HFG09FSATKJ
/interface vlan
add interface=ether2 name=GUEST vlan-id=20
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=MGMT ranges=192.168.1.20-192.168.1.254
add name=GUEST ranges=10.10.20.10-10.10.20.254
/ip dhcp-server
add address-pool=MGMT interface=ether2 lease-time=1d name=MGMT
add address-pool=GUEST interface=GUEST lease-time=1d name=GUEST
/port
set 0 name=serial0
set 1 name=serial1
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=192.168.1.1/24 interface=ether2 network=192.168.1.0
add address=10.10.20.1/24 interface=GUEST network=10.10.20.0
add address=142.190.109.246/30 interface=ether1 network=142.190.109.244
/ip dhcp-server network
add address=10.10.20.0/24 dns-server=10.10.20.1 gateway=10.10.20.1 netmask=24
add address=192.168.1.0/24 dns-server=192.168.1.1 gateway=192.168.1.1 \
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
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=142.190.109.245 routing-table=\
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
set name="Platinum Vacations RB4011"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
