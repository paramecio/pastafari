#!/usr/bin/python3

from paramecio.cromosoma.webmodel import WebModel
from paramecio.cromosoma import corefields
from paramecio.cromosoma.extrafields.dictfield import DictField
from paramecio.cromosoma.extrafields.datefield import DateField
from paramecio.cromosoma.extrafields.ipfield import IpField
from paramecio.cromosoma.extrafields.parentfield import ParentField
from paramecio.citoplasma.urls import make_media_url_module
from paramecio.citoplasma import datetime

class LonelyIpField(IpField):
    
    def __init__(self, name, size=25):
        
        super().__init__(name, size)
        
        self.duplicated_ip=False
        
    def check(self, value):
        
        value=super().check(value)
        
        if self.duplicated_ip==True:
            self.txt_error='Error: you have a server with this ip in the database'
            self.error=True
            return value
        
        return value

class LastUpdatedField(DateField):        
    
    def __init__(self, name):
        
        super().__init__(name)
        
        self.escape=False
    
    def show_formatted(self, value):
        
        now=datetime.now(True)
        
        timestamp_now=datetime.obtain_timestamp(now)
        
        timestamp_value=datetime.obtain_timestamp(value)

        five_minutes=int(timestamp_now)-300
        
        if timestamp_value<five_minutes:
            
            return '<img src="'+make_media_url_module('images/status_red.png', 'pastafari')+'" />'
        else:
            return '<img src="'+make_media_url_module('images/status_green.png', 'pastafari')+'" />'


class OsServer(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(corefields.CharField('name'), True)
        self.register(corefields.CharField('codename'), True)            

class Server(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(corefields.CharField('hostname'), True)
        self.register(LonelyIpField('ip'), True)
        self.fields['ip'].unique=True
        self.fields['ip'].indexed=True
        self.register(corefields.BooleanField('status'))
        self.register(corefields.BooleanField('monitoring'))
        self.register(corefields.CharField('os_codename'), True)
        self.register(corefields.IntegerField('num_updates'))
        self.register(corefields.DoubleField('actual_idle'))
        self.register(LastUpdatedField('date'))
        
class ServerGroup(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        # name, related_table, size=11, required=False, identifier_field='id', named_field="id", select_fields=[]):
        self.register(corefields.CharField('name'), True)
        self.register(ParentField('parent_id', 11, False, 'name'))

class ServerGroupItem(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)

        self.register(corefields.ForeignKeyField('group_id', ServerGroup(connection)), True)
        self.register(corefields.ForeignKeyField('server_id', Server(connection)), True)

class StatusNet(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(IpField('ip'), True)
        self.fields['ip'].indexed=True
        self.register(corefields.DoubleField('bytes_sent'))
        self.register(corefields.DoubleField('bytes_recv'))
        self.register(corefields.IntegerField('errin'))
        self.register(corefields.IntegerField('errout'))
        self.register(corefields.IntegerField('dropin'))
        self.register(corefields.IntegerField('dropout'))
        self.register(corefields.BooleanField('last_updated'))
        self.register(DateField('date'))

class StatusCpu(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        self.register(IpField('ip'), True)
        self.fields['ip'].indexed=True
        self.register(corefields.DoubleField('idle'))
        self.register(corefields.BooleanField('last_updated'))
        self.register(DateField('date'))
        
class StatusDisk(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        self.register(corefields.CharField('disk'), True)
        self.register(IpField('ip'), True)
        self.fields['ip'].indexed=True
        self.register(corefields.DoubleField('size'))
        self.register(corefields.DoubleField('used'))
        self.register(corefields.DoubleField('free'))
        self.register(corefields.DoubleField('percent'))
        self.register(DateField('date'))

class StatusMemory(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(IpField('ip'), True)
        self.fields['ip'].indexed=True
        
        #svmem(total=518418432, available=413130752, percent=20.3, used=208052224, free=310366208, active=137457664, inactive=40919040, buffers=20692992, cached=82071552, shared=4820992)
        
        self.register(corefields.BigIntegerField('total'), True)
        self.register(corefields.BigIntegerField('available'), True)
        self.register(corefields.DoubleField('percent'), True)
        self.register(corefields.BigIntegerField('used'), True)
        self.register(corefields.BigIntegerField('free'), True)
        self.register(corefields.BigIntegerField('active'), True)
        self.register(corefields.BigIntegerField('inactive'), True)
        self.register(corefields.BigIntegerField('buffers'), True)
        self.register(corefields.BigIntegerField('cached'), True)
        self.register(corefields.BigIntegerField('shared'), True)
        
        self.register(corefields.BooleanField('last_updated'))
        self.register(DateField('date'))
