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
from paramecio.citoplasma.base_admin import base_admin
import requests
import json
import re
from paramecio.wsgiapp import app

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

@app.post('/'+pastafari_folder+'/maketask')
def home():
    
    return base_admin(admin_task, env, 'Make task')
    
def admin_task(connection, t, s, **args):
    
    task=Task(connection)
    
    getpost=GetPostFiles()            
    
    getpost.obtain_get()
    
    if request_type()=='POST':
        getpost.obtain_post()

    #Load task worker
    
    task_first, task_path=checktask(getpost.post, connection)
    
    if task_first is not None:
        
        post={'name_task': task_first.name_task, 'description_task': task_first.description_task, 'codename_task': task_first.codename_task, 'files': task_first.files, 'commands_to_execute': task_first.commands_to_execute, 'delete_files': task_first.delete_files, 'delete_directories': task_first.delete_directories, 'url_return': task_first.url_return, 'one_time': task_first.one_time, 'version': task_first.one_time}
            
        #post_task={'task': getpost.post['task']}
        
        where_sql_server='WHERE 1=1'
        
        post_task=[]
        
        try:
            group_id=int(getpost.get.get('group_id', '0'))
            
        except:
            group_id=0
            
        if group_id>0:
            
            where_sql_server+=' AND id IN (select server_id from servergroupitem where group_id='+str(group_id)+')'
        
        pattern=re.compile('^server_.*$')
            
        for k, server_id in getpost.post.items():
            
            if pattern.match(k):
                
                try:
                    server_id=int(server_id)
                    
                    if server_id>0:
                        
                        post_task.append(str(server_id))
                except:
                    pass
        
        #Create where
        if len(post_task)>0:
            where_sql_server+=' AND id IN ('+','.join(post_task)+')'
            
        post['where_sql_server']=where_sql_server
        
        #Create pàth
        
        post['path']=task_path
        
        #Insert task
        
        task.create_forms()
        
        if task.insert(post):
        
            task_id=task.insert_id()
        
            if task_first.yes_form:
                
                redirect(make_url('pastafari/formtask/'+str(task_id)))
                
            else:
                redirect(make_url('pastafari/executetask/'+str(task_id)))
        else:
            print(task.show_errors())
            return "Error: cannot insert the task"
            #redirect to showprogress
        
        #return where_sql_server

@app.get('/'+pastafari_folder+'/formtask/<task_id:int>')
def formtask(task_id):
    
    args={}
    
    args['task_id']=task_id
    
    return base_admin(form_task, env, 'Options for the task', **args)

def form_task(connection, t, s, **args):
    
    task=Task(connection)
    
    arr_task=task.select_a_row(args['task_id'])
    
    if arr_task:
        
        task_execute=import_module(arr_task['path'])
                
        if config.reloader:
                reload(task_execute)
        
        task_first=task_execute.MakeTask(connection)
        
        if task_first.yes_form:
        
            return t.load_template('pastafari/maketask.phtml', form=task_first.form(t), task_id=args['task_id'])
        else:
            redirect(make_url('pastafari/executetask/'+str(task_id)))
    
    else:
    
        return 'Task no exists'

@app.post('/'+pastafari_folder+'/executetask/<task_id:int>')
@app.get('/'+pastafari_folder+'/executetask/<task_id:int>')
def executetask(task_id):
    
    args={}
    
    args['task_id']=task_id
    
    return base_admin(send_task, env, 'Options for the task', **args)
    
def send_task(connection, t, s, **args):
    
    task=Task(connection)
    logtask=LogTask(connection)
    
    arr_task=task.select_a_row(args['task_id'])
    
    getpost=GetPostFiles()
    
    getpost.obtain_post()
    
    if arr_task:
        
        task_execute=import_module(arr_task['path'])
                
        if config.reloader:
            reload(task_execute)
        
        task_first=task_execute.MakeTask(connection)
        
        yes_redirect=False
        
        if task_first.yes_form:
        
            if task_first.update_task(getpost.post, arr_task['id']):
                
                yes_redirect=True
                
            else:
                
                return t.load_template('pastafari/maketask.phtml', form=task_first.form(t, yes_error=True, pass_values=True, **getpost.post), task_id=args['task_id'])
                
            
        else:
            
            yes_redirect=True
            
        if yes_redirect:
            #try:
                
            r=requests.get(server_task+str(arr_task['id']))
            
            arr_data=r.json()
            
            arr_data['task_id']=arr_task['id']
            
            logtask.create_forms()
            
            if not logtask.insert(arr_data):
                
                return "Error:Wrong format of json data..."

            else:
                
                # Redirect to show multiples tasks.
                
                redirect(make_url('pastafari/showmultiprogress/'+str(arr_task['id'])))
                    #return make_url('pastafari/showmultiprogress/'+str(arr_task['id']))
                    
                    #content_index=t.load_template('pastafari/updates.phtml', task_id=task_id, title_task=name_task, description_task=description_task, num_servers=num_servers)
            """
            except:
                
                task_first.task.update({'status': 1, 'error': 1})
                
                return "Error:cannot connect to task server, check the url for it..."+traceback.format_exc()
            """
    
    else:
    
        return 'Task no exists'

@app.get('/'+pastafari_folder+'/showmultiprogress/<task_id:int>')
def showmultiprogress(task_id):
    
    args={}
    
    args['task_id']=task_id
    
    return base_admin(show_progress, env, 'Show progress in servers', **args)
    
def show_progress(connection, t, s, **args):
    
    server=Server(connection)
    task=Task(connection)
    
    arr_task=task.select_a_row(args['task_id'])
    
    if arr_task:
                            
        num_servers=server.set_conditions(arr_task['where_sql_server'], []).select_count()
    
        return t.load_template('pastafari/updates.phtml', task_id=arr_task['id'], title_task=arr_task['name_task'], description_task=arr_task['description_task'], num_servers=num_servers)
    else:
        return "No multitasks found"

"""
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
                
            return t.load_template('admin/content.html', title=I18n.lang('pastafari', 'making_task', 'Making task in server')+': '+task_first.name_task, content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        
    else:
    
        redirect(make_url(config.admin_folder))
"""
                

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
            
            try:
            
                task_execute=import_module(task_file)   
                
                if config.reloader:
                        reload(task_execute)
                
                task_first=task_execute.MakeTask(conn)
            
                return (task_first, task_file)
                
            except:
                
                return (False, False)
        else:
            
            return (False, False)
    else:
        
        return (False, False)
