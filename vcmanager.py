from pyVim import connect
import pyVmomi
import getpass
from IPython import embed
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import datetime
from csv import reader
from models import Machine,EthCard
#check https://host/mob - auth same as to vcenter
class VC():
    def __init__(self,host,user):
        pwd=getpass.getpass("Password: ")
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
    def guest_creds(self, user,gpaswd):
        creds = pyVmomi.vim.vm.guest.NamePasswordAuthentication(username=user, password=gpaswd)
        return creds
    def push_command(self,command,arguments,machine,user=0,gpasswd=0):
        
        version=self.get_vmware_version()
        if int(version.split(".")[0])<5:
            print("Wersja VMWare ({0}) jest za niska do wykonania operacji na gosciu potrzebna jest przynajmniej wersja 5.0".format(version))
        else:
            if user==0:
                user=input("Uzytkownik do polaczenia sie z gosciem: ")
            if gpasswd==0:
                gpasswd=getpass.getpass("Password: ")
            creds=self.guest_creds(user,gpasswd)
            cmdspec = pyVmomi.vim.vm.guest.ProcessManager.ProgramSpec(arguments=arguments, programPath=command)
            cmdoutput = self.vc.content.guestOperationsManager.processManager.StartProgramInGuest(vm=self.machines[machine]["vm"], auth=creds, spec=cmdspec)
            self.machines[machine]["operacje"]={"pid":cmdoutput,"sciezka_programu":command,"argumenty":arguments}
# host=input("Host: ")
# user=input("Login: ")
# pap=VC(host,user)
# embed()
