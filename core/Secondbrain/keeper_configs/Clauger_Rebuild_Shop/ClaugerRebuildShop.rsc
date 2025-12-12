# 2025-09-15 21:25:51 by RouterOS 7.11.3
# software id = UV7U-DGX6
#
# model = RB4011iGS+
# serial number = HFG09EF6541
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=LAN ranges=192.168.0.20-192.168.0.254
/ip dhcp-server
add address-pool=LAN interface=ether2 lease-time=1d name=server1
/port
set 0 name=serial0
set 1 name=serial1
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=170.249.171.134/30 interface=ether1 network=170.249.171.132
add address=192.168.0.1/24 interface=ether2 network=192.168.0.0
/ip dhcp-server network
add address=192.168.0.0/24 dns-server=192.168.0.1 gateway=192.168.0.1 \
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
add disabled=no dst-address=0.0.0.0/0 gateway=170.249.171.133 routing-table=\
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
set name=Clauger-Rebuild-Shop
/system note
set note="This is Clauger-Rebuild Shop's Router"
/system ntp client
set enabled=yes
/system ntp client servers
add address=0.us.pool.ntp.org
add address=1.us.pool.ntp.org
add address=2.us.pool.ntp.org
add address=3.us.pool.ntp.org
/system routerboard settings
set enter-setup-on=delete-key
