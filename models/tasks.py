#!/usr/bin/env python3

from modules.pastafari.models import servers
from paramecio.cromosoma.webmodel import WebModel
from paramecio.cromosoma import corefields
from paramecio.cromosoma.extrafields.dictfield import DictField
from paramecio.cromosoma.extrafields.arrayfield import ArrayField
from paramecio.cromosoma.extrafields.datefield import DateField
from paramecio.cromosoma.extrafields.urlfield import UrlField
from paramecio.cromosoma.extrafields.ipfield import IpField
import requests
from settings import config
from modules.pastafari.libraries.configclass import config_task
from paramecio.citoplasma.urls import redirect, make_url

server_task=config_task.server_task

server_task=server_task+'/exec/'+config_task.api_key+'/'

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

class Task(WebModel):
    
    def __init__(self, connection):
        
        super().__init__(connection)
    
        self.connection=connection
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
        
        self.error=False
        self.txt_error=''
    
    def run_task(self, url, name_task, codename_task, description_task, files, commands_to_execute, delete_files, delete_directories, server, pre_func, post_func, error_func, extra_data):
        
        logtask=LogTask(self.connection)
        
        self.create_forms()
        logtask.create_forms()
        
        if self.insert({'name_task': name_task,'description_task': description_task, 'url_return': url, 'files':  files, 'commands_to_execute': commands_to_execute, 'delete_files': delete_files, 'delete_directories': delete_directories, 'server': server, 'where_sql_server':'', 'pre_func': pre_func, 'post_func': post_func, 'error_func': error_func, 'extra_data': extra_data }):
            
            task_id=self.insert_id()
                                            
            #try:
            
            r=requests.get(server_task+str(task_id))
            
            arr_data=r.json()
            
            arr_data['task_id']=task_id
            
            if not logtask.insert(arr_data):
                
                self.error=True
                self.txt_error="Error:Wrong format of json data..."
            else:
                
                redirect(make_url(pastafari_folder+'/showprogress/'+str(task_id)+'/'+server))
        else:
            
            self.error=True
            self.txt_error="Cannot insert the task"

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
