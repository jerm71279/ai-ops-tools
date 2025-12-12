# 2025-09-11 16:58:33 by RouterOS 7.18.1
# software id = DHA4-2MYH
#
# model = RB4011iGS+
# serial number = HG109PY9F34
/interface vlan
add interface=ether2 name=GUEST vlan-id=20
add interface=ether2 name=LAN vlan-id=10
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=LAN ranges=192.168.0.20-192.168.0.254
add name=GUEST ranges=10.10.20.10-10.10.20.254
/ip dhcp-server
add address-pool=LAN interface=ether2 lease-time=1d name=LAN
add address-pool=GUEST interface=GUEST name=GUEST
/port
set 0 name=serial0
set 1 name=serial1
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=192.168.0.1/24 interface=ether2 network=192.168.0.0
add address=10.10.20.1/24 interface=GUEST network=10.10.20.0
add address=208.114.201.50/30 interface=ether1 network=208.114.201.48
/ip dhcp-server network
add address=10.10.20.0/24 dns-server=10.10.20.1 gateway=10.10.20.1 netmask=24
add address=192.168.0.0/24 dns-server=192.168.0.1 gateway=192.168.0.1 \
    netmask=24
add address=192.168.2.0/24 dns-server=192.168.2.1 gateway=192.168.2.1 \
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
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=208.114.201.49 routing-table=\
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
set name="Jubilee Pool"
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
