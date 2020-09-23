from pyVim import connect
import getpass
# from IPython import embed
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime, os
from csv import reader
from models import Machine,EthCard
#check https://host/mob - auth same as to vcenter
class VC():
    def __init__(self,host,user):
        pwd=getpass.getpass("Password: ")
        try:
            self.vc=connect.SmartConnectSSL(host=host,user=user,pwd=pwd)
        except:
            self.vc=connect.SmartConnectNoSSL(host=host,user=user,pwd=pwd)
    def get_vms(self):
        self.machines={}
        for datacenter in self.vc.content.rootFolder.childEntity:
            for machine in datacenter.vmFolder.childEntity:
                if "Folder" in machine.__str__():
                    for j in machine.childEntity:
                        self.machines[j.name]={}
                        self.machines[j.name]["vm"]=j
                        self.get_config(j)
                else:
                    self.machines[machine.name]={}
                    self.machines[machine.name]["vm"]=machine
                    self.get_config(machine)
    def create_model(self,vm,sess):
        machine=Machine(
            name=vm.name,
            vm=vm.__str__(),
            powerState=vm.summary.runtime.powerState,
            connectionState=vm.summary.runtime.connectionState,
            bootTime=vm.summary.runtime.bootTime,
            guestFullName=vm.summary.guest.guestFullName,
            hostName=vm.summary.guest.hostName,
            ipAddress=vm.summary.guest.ipAddress,
            annotation=vm.summary.config.annotation,
            memorySizeMB=vm.summary.config.memorySizeMB,
            numCpu=vm.summary.config.numCpu,
            numEthernetCards=vm.summary.config.numEthernetCards,
            numVirtualDisks=vm.summary.config.numVirtualDisks,
            uuid=vm.summary.config.uuid,
            guestId=vm.summary.config.guestId,
            guestFullNameConf=vm.summary.config.guestFullName
            )
        karty=[]
        for x in vm.guest.net:
            karty.append(EthCard(macAddress=x.macAddress,network=x.network,connected=x.connected,ipAddress=x.ipAddress,vm=machine.vm))
        return machine,karty
        
    def push_to_db(self,sess):
        self.get_vms()
        for k,vm in self.machines.items():
           x,y=self.create_model(vm,sess)
           sess.add(x)
           sess.commit()
           sess.add_all(y)
           sess.commit()
    #vmware info
    def get_vmware_version(self):
        return self.vc.RetrieveContent().about.version
    def get_vmware_fullName(self):
        return self.vc.RetrieveContent().about.fullName
    
    #guest machine info
    def get_power_state(self,machine):
        return True if machine.summary.__dict__["runtime"].__dict__["powerState"]=="poweredOn" else False
    def get_config(self,machine):
        self.machines[machine.name]["config"]={}
        self.machines[machine.name]["config"]["cpus"]=machine.summary.config.numCpu
        self.machines[machine.name]["config"]["ram"]=machine.summary.config.memorySizeMB
        self.machines[machine.name]["config"]["ip"]="dynamic" if machine.summary.guest.ipAddress=="0.0.0.0" else machine.summary.guest.ipAddress
        self.machines[machine.name]["config"]["hostname"]=machine.summary.guest.hostName
        self.machines[machine.name]["config"]["os"]=machine.summary.guest.guestFullName
        self.machines[machine.name]["config"]["state"]=machine.summary.runtime.powerState
        self.machines[machine.name]["config"]["disk_memory"]=self.convert_size(machine.summary.storage.committed)
    def convert_size(self,size_bytes):
        import math
        if size_bytes == 0:
            return "0B"
        size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
        i = int(math.floor(math.log(size_bytes, 1024)))
        p = math.pow(1024, i)
        s = round(size_bytes / p, 2)
        return "%s %s" % (s, size_name[i])        
print("#"*60)
print("Ansible hosts file creator, create your hosts file from your VMWare Infrastructure")
host=input("VMWare Host: ")
user=input("Login: ")
vmware=VC(host,user)
# embed() #za pomoca obiektu VC mozemy kontrolowac naszego VMware'a dir(VC) wyswietla komendy
def get_pass(passwd):
    import crypt
    hashed_passwd=crypt.crypt(passwd, crypt.mksalt(crypt.METHOD_SHA512))
    return hashed_passwd
import pyVmomi
def guest_creds(user,gpaswd):
    creds = pyVmomi.vim.vm.guest.NamePasswordAuthentication(username=user, password=gpaswd)
    return creds
def write_hosts(vm_container):
    hosts_file={}
    for k in vm_container.machines:
        if vm_container.machines[k]["config"]["state"]=="poweredOn":
            if vm_container.machines[k]["config"]["os"]:
                if vm_container.machines[k]["config"]["os"] not in hosts_file.keys():
                    hosts_file[vm_container.machines[k]["config"]["os"]]=[(k,vm_container.machines[k]["config"]["ip"],vm_container.machines[k]["config"]["cpus"],vm_container.machines[k]["config"]["ram"],vm_container.machines[k]["config"]["disk_memory"],vm_container.machines[k]["config"]["hostname"])]
                else:
                    hosts_file[vm_container.machines[k]["config"]["os"]].append((k,vm_container.machines[k]["config"]["ip"],vm_container.machines[k]["config"]["cpus"],vm_container.machines[k]["config"]["ram"],vm_container.machines[k]["config"]["disk_memory"],vm_container.machines[k]["config"]["hostname"]))
    return hosts_file
# def change_password(vm,new_pass,rootcreds):
vmware.get_vms()
dicter=write_hosts(vmware)
#gdybysmy chcieli polaczyc wyniki z roznych vwmareow
#vmware2=VC(host,user)
#dicter2=write_hosts(vmware2)
#vmware2.get_vms()
#keys=set(list(dicter.keys())+list(dicter2.keys()))
keys=set(list(dicter.keys()))
klucze={}
for key in keys:
    if "Windows 7" in key:
        klucze[key]="windows_7"
    if "Server 2003" in key:
        klucze[key]="windows_2003"
    if "Server 2008 R2" in key:
        klucze[key]="windows_2008_r2"
    if "Server 2008 (64-bit)" in key:
        klucze[key]="windows_2008"
    if "Server 2012 (64-bit)" in key:
        klucze[key]="windows_2012"
    if "Windows XP" in key:
        klucze[key]="windows_xp"
    if "Other (32-bit)" in key:
        klucze[key]="other_32"
    if "Other 2.6.x Linux (64-bit)" in key:
        klucze[key]="other_linux_64_kernel_26"
    if "Red Hat Enterprise Linux 5 (32-bit)" in key:
        klucze[key]="rhel_5_32"
    if "Red Hat Enterprise Linux 6 (32-bit)" in key:
        klucze[key]="rhel_6_32"
    if "CentOS 4/5 (32-bit)" in key:
        klucze[key]="centos_45_32"
    if "CentOS 4/5 (64-bit)" in key:
        klucze[key]="centos_45_64"
    if "CentOS 4/5/6 (32-bit)" in key:
        klucze[key]="centos_456_32"
    if "CentOS 4/5/6/7 (64-bit)" in key:
        klucze[key]="centos_4567_64"
    if "x86_64 CentOS Linux release" in key:
        klucze[key]="centos_7"  
    if "Debian" in key:
        klucze[key]="debian"

full={} 
for y,v in klucze.items():
    temp=[]
    if v in full.keys():
        temp+=full[v]
        if y in dicter.keys(): 
            temp+=dicter[y] 
        #if y in dicter2.keys(): 
        #    temp+=dicter2[y]
    else:
        full[v]=[] 
        if y in dicter.keys(): 
            temp+=dicter[y] 
        #if y in dicter2.keys(): 
        #    temp+=dicter2[y] 
    full[v]=temp 
machine_counter=0
with open("hosts","w") as f: 
    for k in full: 
        f.write("[{0}]\n".format(k)) 
        for machine in full[k]: 
            machine_counter+=1
            f.write("{0} ansible_host={1} cpus={2} ram={3} disk_memory='{4}'\n".format(machine[0],machine[1],machine[2],machine[3],machine[4])) 
print("#"*60)
print("Found {0} machines".format(machine_counter))
print("Your hosts file:\n{0}\hosts".format(os.path.abspath(os.path.dirname(__file__))))
end=input("Press any key to quit.")