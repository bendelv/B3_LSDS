import netifaces as ni

i = ni.interfaces()
print(ni.gateways())
print(ip)  # should print "192.168.100.37"
