# 2025-09-16 12:16:42 by RouterOS 7.15.3
# software id = BJ3R-MLBX
#
# model = RB4011iGS+
# serial number = HFG09AHBEJB
/interface ethernet
set [ find default-name=ether1 ] name="ether1 WAN Uniti"
set [ find default-name=ether2 ] name="ether2 Clauger LAN"
set [ find default-name=ether4 ] name="ether4 Heal & Thrive LAN"
/interface vlan
add interface="ether2 Clauger LAN" name=Guest vlan-id=100
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name="Clauger Pool" ranges=192.168.0.10-192.168.0.254
add name="Heal and Thrive Pool" ranges=192.168.100.10-192.168.100.200
/port
set 0 name=serial0
set 1 name=serial1
/queue simple
add max-limit=27M/27M name="Heal and Thrive 25M" target=\
    "ether4 Heal & Thrive LAN"
add max-limit=27M/27M name=Clauger target="ether2 Clauger LAN"
/ip dhcp-server
add address-pool="Clauger Pool" allow-dual-stack-queue=no \
    insert-queue-before="Heal and Thrive 25M" interface="ether2 Clauger LAN" \
    lease-time=1d name="LAN DHCP"
add address-pool="Heal and Thrive Pool" allow-dual-stack-queue=no \
    insert-queue-before=Clauger interface="ether4 Heal & Thrive LAN" \
    lease-time=1d name="Heal & Thrive"
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=170.249.181.170/30 interface="ether1 WAN Uniti" network=\
    170.249.181.168
add address=192.168.0.1/24 interface="ether2 Clauger LAN" network=192.168.0.0
add address=192.168.100.1/24 interface="ether4 Heal & Thrive LAN" network=\
    192.168.100.0
/ip dhcp-client
add interface="ether1 WAN Uniti"
/ip dhcp-server network
add address=192.168.0.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.0.1
add address=192.168.100.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.100.1 \
    netmask=24
/ip dns
set servers=142.190.111.111,142.190.222.222
/ip firewall filter
add action=drop chain=input dst-port=21,22,2000,80,8080,443 in-interface=\
    "ether1 WAN Uniti" protocol=tcp
add action=drop chain=input dst-port=161,53,123 in-interface=\
    "ether1 WAN Uniti" protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1 WAN Uniti"
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=170.249.181.169 routing-table=\
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
set name="Clauger Office RB4011"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
