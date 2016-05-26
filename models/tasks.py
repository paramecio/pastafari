#!/usr/bin/python3

from modules.pastafari.models import servers
from paramecio.cromosoma.webmodel import WebModel
from paramecio.cromosoma import corefields
from paramecio.cromosoma.extrafields.dictfield import DictField
from paramecio.cromosoma.extrafields.arrayfield import ArrayField
from paramecio.cromosoma.extrafields.datefield import DateField
from paramecio.cromosoma.extrafields.urlfield import UrlField
from paramecio.cromosoma.extrafields.ipfield import IpField

class Task(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
    
        self.register(corefields.CharField('name_task'), True)
        self.register(corefields.CharField('description_task'), True)
        self.register(ArrayField('files', ArrayField('', corefields.CharField(''))))
        self.register(ArrayField('commands_to_execute', ArrayField('', corefields.CharField(''))))
        self.register(ArrayField('delete_files', corefields.CharField('')))
        self.register(ArrayField('delete_directories', corefields.CharField('')))
        self.register(corefields.BooleanField('error'))
        self.register(corefields.BooleanField('status'))
        self.register(corefields.CharField('url_return'))
        self.register(IpField('server'), True)
        self.register(corefields.CharField('user'))
        self.register(corefields.CharField('password'))
        self.register(corefields.CharField('path'))

class LogTask(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(DateField('date'))
        self.register(corefields.ForeignKeyField('task_id', Task(connection)), True)
        self.register(corefields.DoubleField('progress'))
        self.register(corefields.BooleanField('no_progress'))
        self.register(corefields.TextField('message'), True)
        self.register(corefields.BooleanField('error'))
        self.register(corefields.BooleanField('status'))
        self.register(DictField('data', corefields.CharField('data')))
