# sep/16/2025 14:59:02 by RouterOS 6.49.13
# software id = HA2B-3TMG
#
# model = RouterBOARD 3011UiAS
# serial number = 783E08397D26
/interface ethernet
set [ find default-name=ether1 ] name="ether1 - WAN-Uniti"
set [ find default-name=ether2 ] name="ether2 - LAN"
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=LAN ranges=192.168.88.20-192.168.88.254
/ip dhcp-server
add address-pool=LAN disabled=no interface="ether2 - LAN" lease-time=1d name=\
    LAN
/user group
set full policy="local,telnet,ssh,ftp,reboot,read,write,policy,test,winbox,pas\
    sword,web,sniff,sensitive,api,romon,dude,tikapp"
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=192.168.88.1/24 interface="ether2 - LAN" network=192.168.88.0
add address=69.85.251.18/30 interface="ether1 - WAN-Uniti" network=\
    69.85.251.16
/ip dhcp-server network
add address=192.168.88.0/24 dns-server=192.168.88.1 gateway=192.168.88.1
/ip dns
set allow-remote-requests=yes servers=9.9.9.9,8.8.4.4,8.8.8.8,142.190.111.111
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,80,2000 in-interface=\
    "ether1 - WAN-Uniti" protocol=tcp
add action=drop chain=input dst-port=53,123,161 in-interface=\
    "ether1 - WAN-Uniti" protocol=udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface="ether1 - WAN-Uniti"
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set irc disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
set udplite disabled=yes
set dccp disabled=yes
set sctp disabled=yes
/ip route
add distance=1 gateway=69.85.251.17
/ip service
set telnet disabled=yes
set ftp disabled=yes
set www disabled=yes
set ssh disabled=yes
set api disabled=yes
set winbox port=8899
set api-ssl disabled=yes
/ip ssh
set allow-none-crypto=yes forwarding-enabled=remote
/lcd
set time-interval=hour
/snmp
set enabled=yes
/system clock
set time-zone-name=America/Chicago
/system identity
set name=GooRoos
/system note
set note="This is Gooroo's"
