# 2025-09-15 22:20:22 by RouterOS 7.17.1
# software id = HJPX-WF9F
#
# model = RB4011iGS+
# serial number = HG109MF4V7A
/interface ethernet
set [ find default-name=ether2 ] name="ether2 "
/interface wireguard
add listen-port=13231 mtu=1420 name=wg0
/interface vlan
add interface="ether2 " name=Chatworth vlan-id=500
add interface="ether2 " name="FH Clothier" vlan-id=400
add interface="ether2 " name="Fairhope Single Tax" vlan-id=200
add interface="ether2 " name="Fairhope Single Tax Guest" vlan-id=250
add interface="ether2 " name="Pearl Guest" vlan-id=350
add interface="ether2 " name="Pearl Restuarant" vlan-id=300
add interface="ether2 " name=Sway vlan-id=100
/interface wireless security-profiles
set [ find default=yes ] supplicant-identity=MikroTik
/ip pool
add name="Fairhop Single Tax" ranges=192.168.0.10-192.168.0.254
add name="Pearl Restaurant" ranges=192.168.30.20-192.168.30.250
add name=Sway ranges=192.168.10.20-192.168.10.250
add name="FH Clothier" ranges=192.168.40.20-192.168.40.250
add name=Ether2 ranges=192.168.1.20-192.168.1.254
add name=Chatworth ranges=192.168.50.20-192.168.50.254
add name="Fairhope Single Tax Guest" ranges=10.10.1.20-10.10.1.250
add name="Pearl Guest" ranges=10.10.2.20-10.10.2.250
/ip dhcp-server
add address-pool=Ether2 interface="ether2 " lease-time=1d name=ether2
add address-pool=Sway interface=Sway lease-time=1d name=Sway
add address-pool="Fairhop Single Tax" interface="Fairhope Single Tax" \
    lease-time=1d name="Fairhope Single Tax"
add address-pool="Pearl Restaurant" interface="Pearl Restuarant" lease-time=\
    1d name="Pearl Restaurant"
add address-pool="FH Clothier" interface="FH Clothier" lease-time=1d name=\
    "FH Clothier"
add address-pool=Chatworth interface=Chatworth lease-time=1d name=Chatworth
add address-pool="Fairhope Single Tax Guest" interface=\
    "Fairhope Single Tax Guest" lease-time=1d name=\
    "Fairhope Single Tax Guest"
add address-pool="Pearl Guest" interface="Pearl Guest" lease-time=1d30m name=\
    "Pearl Guest"
/port
set 0 name=serial0
set 1 name=serial1
/ppp profile
set *0 change-tcp-mss=default use-ipv6=default
/ip firewall connection tracking
set udp-timeout=10s
/ip neighbor discovery-settings
set discover-interface-list=!dynamic
/interface detect-internet
set detect-interface-list=all internet-interface-list=all lan-interface-list=\
    all
/interface wireguard peers
add allowed-address=10.8.0.20/32,192.168.1.0/24 client-address=10.8.0.20/32 \
    client-dns=1.1.1.1 client-listen-port=51820 interface=wg0 name=\
    Ob3raConn3ct persistent-keepalive=30m private-key=\
    "ALNtTHfu3FUpmMRFYcKEqOuYIEVW8WShV3ODDLm6N2A=" public-key=\
    "tMvNBycu0ujoaWN1OEQCSgTm1FHonCsT9kYuKXgH0hE="
/ip address
add address=208.114.200.214/30 interface=ether1 network=208.114.200.212
add address=192.168.1.1/24 interface="ether2 " network=192.168.1.0
add address=192.168.10.1/24 interface=Sway network=192.168.10.0
add address=192.168.0.1/24 interface="Fairhope Single Tax" network=\
    192.168.0.0
add address=192.168.30.1/24 interface="Pearl Restuarant" network=192.168.30.0
add address=192.168.40.1/24 interface="FH Clothier" network=192.168.40.0
add address=192.168.50.1/24 interface=Chatworth network=192.168.50.0
add address=10.10.1.1/24 interface="Fairhope Single Tax Guest" network=\
    10.10.1.0
add address=10.10.2.1/24 interface="Pearl Guest" network=10.10.2.0
add address=10.8.0.1/24 interface=wg0 network=10.8.0.0
/ip dhcp-server network
add address=10.10.1.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=10.10.1.1 \
    netmask=24
add address=10.10.2.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=10.10.2.1 \
    netmask=24
add address=192.168.0.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.0.1 \
    netmask=24
add address=192.168.1.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.1.1 \
    netmask=24
add address=192.168.10.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.10.1 \
    netmask=24
add address=192.168.30.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.30.1 \
    netmask=24
add address=192.168.40.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.40.1 \
    netmask=24
add address=192.168.50.0/24 dns-server=8.8.8.8,8.8.4.4 gateway=192.168.50.1 \
    netmask=24
/ip dns
set allow-remote-requests=yes servers=8.8.8.8,8.8.4.4,1.1.1.1
/ip firewall filter
add action=drop chain=input dst-port=21,22,23,53,80,443,8080,2000 \
    in-interface=ether1 protocol=tcp
add action=drop chain=input dst-port=53,123,161 in-interface=ether1 protocol=\
    udp
/ip firewall nat
add action=masquerade chain=srcnat out-interface=ether1
add action=dst-nat chain=dstnat dst-port=1194 in-interface=ether1 protocol=\
    tcp to-addresses=192.168.1.1 to-ports=80
/ip firewall service-port
set ftp disabled=yes
set tftp disabled=yes
set h323 disabled=yes
set sip disabled=yes
set pptp disabled=yes
/ip hotspot profile
set [ find default=yes ] html-directory=hotspot
/ip ipsec profile
set [ find default=yes ] dpd-interval=2m dpd-maximum-failures=5
/ip route
add disabled=no dst-address=0.0.0.0/0 gateway=208.114.200.213 routing-table=\
    main suppress-hw-offload=no
/ip service
set telnet disabled=yes
set ftp disabled=yes
set ssh port=30303
set api disabled=yes
set winbox port=8899
set api-ssl disabled=yes
/ip ssh
set always-allow-password-login=yes forwarding-enabled=local
/ppp aaa
set accounting=no
/system clock
set time-zone-name=America/Chicago
/system identity
set name="Fairhope Strip Mall"
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
