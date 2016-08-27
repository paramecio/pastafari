#!/usr/bin/env python3

import traceback, sys
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import make_url, add_get_parameters, redirect
from paramecio.citoplasma.adminutils import get_menu, get_language, check_login
from paramecio.citoplasma.sessions import get_session
from bottle import route, get,post,response,request
from settings import config
from settings import config_admin
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.formsutils import request_type
from paramecio.cromosoma.webmodel import WebModel
from paramecio.citoplasma.i18n import I18n
from modules.pastafari.models.tasks import Task, LogTask
from modules.pastafari.models.servers import Server
from modules.pastafari.libraries.configclass import config_task
from itsdangerous import JSONWebSignatureSerializer
from importlib import import_module, reload
import requests
import json
import re

#Script  for make and show the  progress of the tasks.

server_task=config_task.server_task

server_task=server_task+'/exec/'+config_task.api_key+'/'

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

num_updated_servers=2

if hasattr(config, 'num_updated_servers'):
    num_updated_servers=config.num_updated_servers

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

env.directories.insert(1, config.paramecio_root+'/modules/admin/templates')

@post('/'+pastafari_folder+'/maketask')
def home():
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    getpost=GetPostFiles()            
    
    getpost.obtain_get()
    
    try:
        group_id=int(getpost.get.get('group_id', '0'))
    except:
        group_id=0

    if request_type()=='POST':
        getpost.obtain_post()
    
    s=get_session()

    if check_login():
        #task=Task(connection)
        logtask=LogTask(connection)
        server=Server(connection)
        
        #Load menu
        
        menu=get_menu(config_admin.modules_admin)
    
        lang_selected=get_language(s)
        
        content_index=''
        
        #Load task
        
        task_first=checktask(getpost.post, connection)
        
        if task_first is not None:
            
            post_task={'task': getpost.post['task']}
            
            pattern=re.compile('^server_.*$')
                
            for k, server_id in getpost.post.items():
                
                if pattern.match(k):
                    
                    try:
                        server_id=int(server_id)
                        
                        if server_id>0:
                            
                            post_task[k]=str(server_id)
                    except:
                        pass
                    
            
            content_index=t.load_template('pastafari/maketask.phtml', form=task_first.form(t), post=post_task, group_id=group_id)
        else:
            content_index="Doesn't exists the task file"
        
        #Get form of task
        
        return t.load_template('admin/content.html', title=I18n.lang('pastafari', 'making_task', 'Making task in server...'), content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        
    else:
        redirect(make_url(config.admin_folder))


@post('/'+pastafari_folder+'/executetask')
def executetask():
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    getpost=GetPostFiles()            
    
    getpost.obtain_get()
    
    try:
        group_id=int(getpost.get.get('group_id', '0'))
    except:
        group_id=0

    #if request_type()=='POST':
    getpost.obtain_post()
    
    s=get_session()
    
    if check_login():
            
        task=Task(connection)
        logtask=LogTask(connection)
        server=Server(connection)
        
        #Load menu
        
        menu=get_menu(config_admin.modules_admin)
    
        lang_selected=get_language(s)
        
        content_index=''
        
        #Load task
        
        task_first=checktask(getpost.post, connection)
        
        if task_first is not None:
            
            # Process the task
            
            arr_servers=[]
            
            post_task={'task': getpost.post['task']}
                
            pattern=re.compile('^server_.*$')
            
            for k, server_id in getpost.post.items():
                
                if pattern.match(k):
                    
                    try:
                        server_id=int(server_id)
                        
                        if server_id>0:
                            arr_servers.append(str(server_id))
                            post_task[k]=str(server_id)
                    except:
                        pass
            
            (task_id, name_task, description_task)=task_first.insert_task(getpost.post)
            
            if task_id:

                #arr_servers=[]
                
                where_sql='WHERE 1=1'
                
                if group_id>0:
                    where_sql+=' AND id IN (select server_id from servergroupitem where group_id='+str(group_id)+')'
                
                if len(arr_servers)>0:
                    where_sql='WHERE id IN (%s)' % ",".join(arr_servers)
                
                task_first.task.reset_require()
                
                task_first.task.set_conditions('WHERE id=%s', [task_id])
                
                if task_first.task.update({'where_sql_server': where_sql}):
                    
                    try:
                    
                        r=requests.get(server_task+str(task_id))
                        
                        arr_data=r.json()
                        
                        arr_data['task_id']=task_id
                        
                        logtask.create_forms()
                        
                        if not logtask.insert(arr_data):
                            
                            content_index="Error:Wrong format of json data..."

                        else:
                            
                            # Redirect to show multiples tasks.
                            
                            server.set_conditions(where_sql, [])
                            
                            num_servers=server.select_count()
                            
                            content_index=t.load_template('pastafari/updates.phtml', task_id=task_id, title_task=name_task, description_task=description_task, num_servers=num_servers)
                    
                    except:
                        
                        task_first.task.update({'status': 1, 'error': 1})
                        
                        content_index="Error:cannot connect to task server, check the url for it..."+traceback.format_exc()
                    
                    pass
                    
                else:
                    content_index="Error: cannot insert the task: "+task_first.task.show_errors()
                
            else:
                
                content_index=t.load_template('pastafari/maketask.phtml', form=task_first.form(t, yes_error=True, pass_values=True, **getpost.post), post=post_task, group_id=group_id)
                
            return t.load_template('admin/content.html', title=I18n.lang('pastafari', 'making_task', 'Making task in server...'), content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        
    else:
    
        redirect(make_url(config.admin_folder))
                
                
                

def checktask(post, conn):
    
    task_first=None
    
    if 'task' in post:
                
        s=JSONWebSignatureSerializer(config.key_encrypt)
        
        arr_file=s.loads(post['task'])
        
        if 'file' in arr_file:
            task_file=arr_file['file']
            # Import module
            
            task_file=task_file.replace('/', '.')
            
            task_file=task_file.replace('.py', '')
            
            task_execute=import_module(task_file)   
            
            if config.reloader:
                    reload(task_execute)
            
            task_first=task_execute.MakeTask(conn)
        
    return task_first
