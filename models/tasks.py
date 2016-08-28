#!/usr/bin/env python3

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
        self.register(corefields.CharField('codename_task'))
        self.register(ArrayField('files', ArrayField('', corefields.CharField(''))))
        self.register(ArrayField('commands_to_execute', ArrayField('', corefields.CharField(''))))
        self.register(ArrayField('delete_files', corefields.CharField('')))
        self.register(ArrayField('delete_directories', corefields.CharField('')))
        self.register(corefields.BooleanField('error'))
        self.register(corefields.BooleanField('status'))
        self.register(corefields.CharField('url_return'))
        self.register(IpField('server'))
        self.register(corefields.TextField('where_sql_server'))
        self.fields['where_sql_server'].escape=True
        self.register(corefields.IntegerField('num_servers'))
        self.register(corefields.CharField('user'))
        self.register(corefields.CharField('password'))
        self.register(corefields.CharField('path'))
        self.register(corefields.BooleanField('one_time'))
        self.register(corefields.CharField('version'))
        self.register(corefields.CharField('post_func'))
        self.register(corefields.CharField('pre_func'))
        self.register(corefields.CharField('error_func'))
        self.register(DictField('extra_data', corefields.CharField('')))
    

class LogTask(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
        
        self.register(DateField('date'))
        self.register(corefields.ForeignKeyField('task_id', Task(connection)), True)
        self.register(IpField('server'))
        self.register(corefields.DoubleField('progress'))
        self.register(corefields.BooleanField('no_progress'))
        self.register(corefields.TextField('message'), True)
        self.register(corefields.BooleanField('error'))
        self.register(corefields.BooleanField('status'))
        self.register(DictField('data', corefields.CharField('data')))
