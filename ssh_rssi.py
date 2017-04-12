import paramiko
import re

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

ssh.connect('192.168.1.161', username='admin', 
    password='saarinen')
stdin, stdout, stderr = ssh.exec_command(
    "./wl status")
stdin.flush()
data = stdout.readlines()
#for line in data:
    #if line.split(':')[0] == 'AirPort':
#    print line
#print data[1]
m=re.search('.*RSSI: (-\d+).*',data[1])
RSSI=m.group(1)
print RSSI
