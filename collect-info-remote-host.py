### Pyscript to collect he Python version and uname on remote hosts

import paramiko
import os, sys
import subprocess, platform
#from pathlib import Path
#from getpass import getpass

hosts = open("hostslist.txt",'r')
fileout = open('py_cmdout.txt', 'w')
fileouterr = open('py_cmderr.txt', 'w')

username = "root"
passw = "password"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
#python_version=platform.python_version()
#osdist=platform.linux_distribution()

## CAlling as function  
def puname():
   try:
      for host in hosts:
         host=host.strip()
         print ("connecting.... ", host)
         client.connect(host, username=username, password=passw)
         stdin, stdout, strerr = client.exec_command('python -c 'import platform; print(platform.linux_distribution())'')
         osdist = stdout.read().decode()
         stdin, stdout, stderr = client.exec_command("python -c 'import platform; print(platform.python_version())'")
         python_version = stdout.read().decode()
         fileout.write( host + "\t pyver: " +  python_version + "\t OS-Distro: %s %s %s "  % osdist + "\n" )
   except:
         print("Authentication Error", host)
         fileouterr.write(host + "\t "  + "unable to connect - sshException" + "\n")
         return puname()
puname()

hosts.close()
client.close()
fileout.close()



