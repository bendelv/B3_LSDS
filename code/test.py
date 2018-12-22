import netifaces as ni

interfaces = ni.interfaces()
if 'wlo1' in interfaces:
    ip = ni.ifaddresses('wlo1')[ni.AF_INET][0]['addr']
elif 'wlp2s0' in interfaces:
    ip = ni.ifaddresses('wlp2s0')[ni.AF_INET][0]['addr']

print(ip)
