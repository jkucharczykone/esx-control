# esx-control
Python script to create ansible hosts file from VMWare

## How to run?

### Windows

Compiled on Windows 10 x64 

In directory dist you can find esx-control.exe or you can click <a href="https://github.com/jkucharczykone/esx-control/raw/master/dist/esx-control.exe"> here to download Windows distribution.</a> Compiled on Windows 10 x64 

```

.\dist\esx_control.exe

```

### Linux

```
#If you want to run in your own env
pip install -r requirements.txt

#If you want to try with uploaded env
source esx-control/bin/activate

#Main run
python main.py

```

## Runtime

```
############################################################
Ansible hosts file creator, create your hosts file from your VMWare Infrastructure
VMWare Host: <vmware ipaddress>
Login: <vmware admin username>
Password:
############################################################
Found <number of machines> machines
Your hosts file:
<path_to_application>\hosts
Press any key to quit.
```

## Hosts file improvement

```
#Add groups to use later in ansible
[windows:children]
windows_7
windows_2003
windows_2008_r2
windows_2008
windows_2012
windows_xp
[linux:children]
other_32
other_linux_64_kernel_26
rhel_5_32
rhel_6_32
centos_45_32
centos_45_64
centos_456_32
centos_4567_64
centos_7 
debian

```
