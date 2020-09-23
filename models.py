# from django.db import models
from sqlalchemy import Sequence
from sqlalchemy.dialects import postgresql
from sqlalchemy import Column,Boolean, Integer, String, Date, ForeignKey, UniqueConstraint, Float, BLOB, ForeignKeyConstraint, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
#Create database
# from sqlalchemy import create_engine
# import getpass
# p=getpass.getpass()
# engine=create_engine("postgres://postgres:{0}@127.0.0.1:5432/machines".format(p))
# from models import *
# Base.metadata.create_all(engine)
Base = declarative_base()

class Machine(Base):
    __tablename__ = 'vms'
    __table_args__ = {'extend_existing': True}
    # machineId = Column(Integer, primary_key=True)
    vm = Column(String, primary_key=True) #vm.summary.vm or vm.__str__()
    name = Column(String) #vm.name
    powerState = Column(String) #vm.summary
    connectionState = Column(String) #vm.summary
    bootTime = Column(DateTime) #vm.summary
    guestFullName = Column(String) #vm.summary.guest
    hostName = Column(String) #vm.summary.guest
    ipAddress = Column(String) #vm.summary.guest
    annotation = Column(String) #vm.summary.config
    memorySizeMB = Column(Integer) #vm.summary.config
    numCpu = Column(Integer) #vm.summary.config
    numEthernetCards = Column(Integer) #vm.summary.config
    numVirtualDisks = Column(Integer) #vm.summary.config
    uuid = Column(String) #vm.summary.config
    guestId = Column(String) #vm.summary.config
    guestFullNameConf = Column(String) #vm.summary.config
    cards=relationship("EthCard", cascade="all,delete",backref="machine")
    
    def __repr__(self):
        return str(self.name)


class EthCard(Base):
    __tablename__ = 'ethernetcards'
    __table_args__ = {'extend_existing': True}
    cardId = Column(Integer,primary_key=True)
    macAddress = Column(String) #vm.guest.net => list .macAddress
    network = Column(String) #vm.guest.net => list .network
    connected = Column(Boolean) #vm.guest.net => list .connected
    ipAddress = Column(postgresql.ARRAY(String)) #vm.guest.net => list .ipAddress
    vm = Column(String, ForeignKey("vms.vm"))
    
    def __repr__(self):
	    return self.vm
    #    return str(self.cardId +": " + self.macAddress)