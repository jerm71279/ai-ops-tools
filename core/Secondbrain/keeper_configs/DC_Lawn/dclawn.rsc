# 1970-08-17 11:58:44 by RouterOS 7.11.3
# software id = LNH8-TTY9
#
# model = RB4011iGS+
# serial number = HG109N7J15D
/interface bridge
add name=bridge1
/interface vlan
add interface=bridge1 name="Guest Wifi" vlan-id=20
add interface=bridge1 name=VoIP vlan-id=3
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name=Bridge ranges=192.168.1.20-192.168.1.250
add name="Guest Wifi" ranges=10.0.0.10-10.0.0.250
/ip dhcp-server
add address-pool=Bridge interface=bridge1 lease-time=1d name=Bridge
add address-pool="Guest Wifi" interface="Guest Wifi" lease-time=1d name=\
    "Guest Wifi"
/port
set 0 name=serial0
set 1 name=serial1
/interface bridge port
add bridge=bridge1 interface=ether2
add bridge=bridge1 interface=ether3
add bridge=bridge1 interface=ether4
add bridge=bridge1 interface=ether5
add bridge=bridge1 interface=ether6
add bridge=bridge1 interface=ether7
add bridge=bridge1 interface=ether8
add bridge=bridge1 interface=ether9
add bridge=bridge1 interface=ether10
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/ip address
add address=208.114.200.186/30 interface=ether1 network=208.114.200.184
add address=192.168.1.1/24 interface=bridge1 network=192.168.1.0
add address=10.0.0.1/24 interface="Guest Wifi" network=10.0.0.0
/ip dhcp-server network
add address=10.0.0.0/24 dns-server=10.0.0.1,8.8.8.8,8.8.4.4 gateway=10.0.0.1 \
    netmask=24
add address=192.168.1.0/24 dns-server=192.168.1.1,8.8.8.8,8.8.4.4 gateway=\
    192.168.1.1 netmask=24
/ip dns
set servers=142.190.111.111,142.190.222.222
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,80,443,8080,2000 \
    in-interface=ether1 protocol=tcp
add action=drop chain=input dst-port=53,123,161 in-interface=ether1 protocol=\
    udp
/ip firewall nat
add action=masquerade chain=srcnat
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=208.114.200.185 routing-table=\
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
set name="DC Lawn"
/system note
set note="DC Lawn Router" show-at-login=no
/system ntp client
set enabled=yes
/system ntp client servers
add address=0.us.pool.ntp.org
add address=1.us.pool.ntp.org
add address=2.us.pool.ntp.org
add address=3.us.pool.ntp.org
/system routerboard settings
set enter-setup-on=delete-key
