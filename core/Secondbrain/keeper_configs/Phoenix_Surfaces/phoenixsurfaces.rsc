# 2025-09-16 17:59:24 by RouterOS 7.18.2
# software id = 34MW-48MW
#
# model = RB4011iGS+
# serial number = HG109WDFXKS
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=LAN ranges=192.168.1.10-192.168.1.254
/ip dhcp-server
add address-pool=LAN interface=ether2 lease-time=1d name=LAN
/ip smb users
set [ find default=yes ] disabled=yes
/port
set 0 name=serial0
set 1 name=serial1
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface ovpn-server server
add mac-address=FE:42:79:22:62:01 name=ovpn-server1
/ip address
add address=142.190.24.250/30 interface=ether1 network=142.190.24.248
add address=192.168.1.1/24 interface=ether2 network=192.168.1.0
/ip dhcp-server network
add address=192.168.1.0/24 dns-server=8.8.8.8,8.8.4.4,9.9.9.9 gateway=\
    192.168.1.1 netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4,9.9.9.9
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,80,8080,2000 in-interface=\
    ether1 protocol=tcp
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
add disabled=no dst-address=0.0.0.0/0 gateway=142.190.24.249 routing-table=\
    main suppress-hw-offload=no
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
set name="Phoenix RB4011"
/system note
set show-at-login=no
/system routerboard settings
set enter-setup-on=delete-key
