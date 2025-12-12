# 2025-09-16 17:55:06 by RouterOS 7.15.2
# software id = DDEC-HYR0
#
# model = RB4011iGS+
# serial number = HFG090S5PC1
/interface vlan
add interface=ether2 name=VLAN100 vlan-id=100
add interface=ether2 name=VLAN200 vlan-id=200
add interface=ether2 name=VLAN300 vlan-id=300
add interface=ether2 name=VLAN400 vlan-id=400
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=LEGACY ranges=192.168.1.10-192.168.1.254
add name=VLAN100 ranges=10.10.100.10-10.10.100.254
add name=VLAN300 ranges=10.10.30.10-10.10.30.254
add name=VLAN200 ranges=10.10.200.10-10.10.200.254
add name=VLAN400 ranges=10.10.40.10-10.10.40.254
/ip dhcp-server
add address-pool=LEGACY interface=ether2 name=LEGACY
add address-pool=VLAN200 interface=VLAN200 lease-time=1d name=VLAN200
add address-pool=VLAN300 interface=VLAN300 lease-time=1d name=VLAN300
add address-pool=VLAN400 interface=VLAN400 lease-time=1d name=VLAN400
add address-pool=VLAN100 interface=VLAN100 lease-time=1d name=VLAN100
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
add address=192.168.1.1/24 interface=ether2 network=192.168.1.0
add address=69.85.239.58/30 interface=ether1 network=69.85.239.56
add address=10.10.30.1/24 interface=VLAN300 network=10.10.30.0
add address=10.10.200.1/24 interface=VLAN200 network=10.10.200.0
add address=10.10.40.1/24 interface=VLAN400 network=10.10.40.0
add address=10.10.100.1/24 interface=VLAN100 network=10.10.100.0
/ip dhcp-server network
add address=10.10.30.0/24 dns-server=8.8.8.8,4.2.2.2 gateway=10.10.30.1 \
    netmask=24
add address=10.10.40.0/24 dns-server=8.8.8.8,4.2.2.2 gateway=10.10.40.1 \
    netmask=24
add address=10.10.100.0/24 dns-server=8.8.8.8,4.2.2.2 gateway=10.10.100.1 \
    netmask=24
add address=10.10.200.0/24 dns-server=8.8.8.8,4.2.2.2 gateway=10.10.200.1 \
    netmask=24
add address=192.168.1.0/24 dns-server=8.8.8.8,4.2.2.2 gateway=192.168.1.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4,1.1.1.1,142.190.111.111
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,2000 in-interface=ether1 \
    protocol=tcp
add action=drop chain=input dst-port=161 in-interface=ether1 protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface=ether1
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip route
add disabled=no distance=1 dst-address=0.0.0.0/0 gateway=69.85.239.57 \
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
set name="MOBAMA Unit D RB4011"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
