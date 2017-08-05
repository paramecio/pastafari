#!/usr/bin/env python3

import traceback, sys, time
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import make_url, add_get_parameters, redirect
from paramecio.citoplasma.adminutils import get_menu, get_language, check_login
from paramecio.citoplasma.sessions import get_session
from paramecio.citoplasma.lists import SimpleList
from bottle import route, get,post,response,request
from settings import config
from settings import config_admin
from paramecio.citoplasma.httputils import GetPostFiles, filter_ajax
from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models.tasks import Task, LogTask
from modules.pastafari.models.servers import Server
from modules.pastafari.libraries.configclass import config_task
from paramecio.wsgiapp import app
from bottle import request
import requests
import json

# Show the progress of a task in a server

num_tasks=10

if hasattr(config, 'num_tasks'):
    num_tasks=config.num_tasks

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

t=PTemplate(env)

# Server tasks list

@app.get('/'+pastafari_folder+'/tasklist/<server_id:int>')
def tasklist(server_id):
    
    content_index=''
    
    if check_login():

        conn=WebModel.connection()

        server=Server(conn)
        
        arr_server=server.select_a_row(server_id)
        
        if arr_server:

            s=get_session()

            menu=get_menu(config_admin.modules_admin)
        
            lang_selected=get_language(s)           

            task=Task(conn)
            
            arr_task_id=[]
            
            with task.query('select DISTINCT task_id from logtask where server=%s', [arr_server['ip']]) as cursor:
                for arr_task in cursor:
                    arr_task_id.append(arr_task['task_id'])
            
            task.set_conditions('WHERE id IN '+task.check_in_list_str('id', arr_task_id), [])
            
            task_list=SimpleList(task, make_url(pastafari_folder+'/tasklist/'+str(server_id), {}), t)
        
            task_list.fields_showed=['id', 'name_task', 'description_task', 'error', 'status']
        
            task_list.yes_search=False

            task_list.order_field='id'
            task_list.order=1
            
            request.environ['server_id']=arr_server['id']

            task_list.arr_extra_options=[server_task_options]
            
            return_url=make_url('pastafari/servers')
        
            content_index=t.load_template('pastafari/admin/showtasks.phtml', task_list=task_list, server=arr_server, return_url=return_url)
            
        else:
            cont_index=I18n.lang('pastafari', 'sorry_i_cannot_find_the_server', 'Sorry, i cannot find the server')
        
        conn.close()  
        
        return t.load_template('admin/content.html', title=I18n.lang('pastafari', 'task_list_of', 'Task list of')+ ' %s' % arr_server['hostname'], content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
    
    return ""


def server_task_options(url, id, arr_row):
    
    arr_options=[]
    
    arr_options.append('<a href="%s">%s</a>' % (make_url(pastafari_folder+'/serverslogs/'+str(request.environ['server_id'])+'/'+str(id)), 'Logs'))
    
    return arr_options


# A list of messages in tasks for a server

@app.get('/'+pastafari_folder+'/serverslogs/<server_id:int>/<task_id:int>')
def home(server_id, task_id):
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    s=get_session()
    
    if check_login():
                
        task=Task(connection)
        logtask=LogTask(connection)
        server=Server(connection)
        
        getpost=GetPostFiles() 
        
        getpost.obtain_get()
        
        #Load menu
            
        menu=get_menu(config_admin.modules_admin)
    
        lang_selected=get_language(s)           
        
        # server_id=getpost.get.get('id', 0)
        
        server_hostname=''
        
        arr_server=server.select_a_row(server_id)
        
        if arr_server:
            
            server_hostname=' - '+arr_server['hostname']
        
            ip=arr_server['ip']
            
            logtask.set_conditions('WHERE server=%s', [ip])
            
            logtask_list=SimpleList(logtask, make_url(pastafari_folder+'/serverslogs', {'id':str(server_id) }), t)
            
            logtask_list.limit_pages=100
            
            logtask_list.yes_search=False
            
            logtask_list.order_field='id'
            logtask_list.order=1
            
            logtask_list.fields_showed=['id', 'server', 'message', 'error', 'status']
            
            logtask_list.arr_extra_fields=[]
            logtask_list.arr_extra_options=[]
            
            return_url=make_url('pastafari/servers')
            
            content_index=t.load_template('pastafari/admin/logs_list.phtml', logtask_list=logtask_list, server=arr_server, return_url=return_url)
            #logtask_list.show()
            
            # Send request to server
                           
        else:
        
            content_index='Log no exists'
            
        connection.close()
        return t.load_template('admin/content.html', title='Servers log'+ server_hostname, content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        
    else:
        connection.close()
        redirect(make_url(config.admin_folder))

# Show progress of a task in a server

@app.get('/'+pastafari_folder+'/showprogress/<task_id:int>/<server>')
def showprogress(task_id, server):
    
    # Need check the server
    
    t=PTemplate(env)
    
    conn=WebModel.connection()
    
    s=get_session()
    
    if check_login():
            
        content_index=''
        
        conn=WebModel.connection()
        task=Task(conn)
        
        menu=get_menu(config_admin.modules_admin)
        
        lang_selected=get_language(s)           
        
        arr_task=task.select_a_row(task_id)
        
        if arr_task:
            
            server_model=Server(conn)
            
            server_model.set_conditions('where ip=%s', [server])
            
            arr_server=server_model.select_a_row_where()
            
            if arr_server:
            
                #arr_task=
                
                content_index=t.load_template('pastafari/progress.phtml', name_task=arr_task['name_task']+' - '+arr_server['hostname'], description_task=arr_task['description_task'], task_id=task_id, server=server, position=0)
        conn.close()
        return t.load_template('admin/content.html', title='Servers log', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)    
            
    else:
        conn.close()
        return ""


# Get json data of the servers executing same task

@app.get('/'+pastafari_folder+'/getservers/<task_id:int>/<position:int>')
def getservers(task_id, position):
    
    conn=WebModel.connection()
    
    s=get_session()

    if check_login():

        task=Task(conn)
        logtask=LogTask(conn)
        server=Server(conn)
        
        arr_task=task.select_a_row(task_id)
        
        server.set_conditions('WHERE ip IN (select DISTINCT server from logtask where task_id=%s)', [task_id])
        
        server.set_limit([position, num_tasks])
        
        arr_server=server.select_to_array(['hostname', 'ip'])
        
        response.set_header('Content-type', 'text/plain')
        
        if arr_server:
            conn.close()
            return filter_ajax({'servers': arr_server, 'error': 0})
            
        else:
            
            logtask.set_conditions('where task_id=%s and server=""', [task_id])
            
            logtask.set_order({'id': 1})
            
            arr_tasklog=logtask.select_a_row_where([], True)
            
            if arr_tasklog:
                
                if arr_tasklog['error']==1:
                    conn.close()        
                    return arr_tasklog
                else:
                    conn.close()
                    return filter_ajax({'error': 0, 'servers': []})
                    
            else:
                conn.close()
                return filter_ajax({'error': 0, 'servers': []})
                
            
            pass
        

    else:
        conn.close()
        return filter_ajax({})

# Get json format log of a server group executing a task

@app.post('/'+pastafari_folder+'/getprogress/<task_id:int>')
def getprogress(task_id):
    
    conn=WebModel.connection()
    
    s=get_session()

    if check_login():
        
        getpost=GetPostFiles() 
        
        getpost.obtain_post([], True)

        task=Task(conn)
        logtask=LogTask(conn)
        server=Server(conn)
        
        arr_task=task.select_a_row(task_id)
        
        try:
            
            servers=json.loads(getpost.post['servers'])
            
        except:
            
            servers={}
        
        #for ip in servers:
        
        if len(servers)>0:
        
            logtask.set_order({'id': 1})
            
            logtask.set_conditions('WHERE task_id=%s and status=1 and error=1 and server=""', [task_id])
            
            c_error=logtask.select_count()
            
            if c_error==0:
            
                logtask.set_order({'id': 1})
                
                checked_servers=logtask.check_in_list_str('server', servers)

                logtask.set_conditions('WHERE task_id=%s and status=1 and server IN '+checked_servers+' and server!=""', [task_id])
                
                arr_log=logtask.select_to_array(['status', 'error', 'server'])
                
                logtask.set_order({'id': 1})
                
                logtask.set_conditions('WHERE task_id=%s and status=0 and server NOT IN '+checked_servers+' and server!=""', [task_id])
                
                arr_log2=logtask.select_to_array(['status', 'error', 'server'])
                
                arr_log=arr_log2+arr_log
                
                #response.set_header('Content-type', 'text/plain')
                
                #return json.dumps(arr_log)
                
            else:
                
                arr_log=[]
                
                for server in servers:
                    
                    arr_log.append({'status':1, 'error':1, 'server': server})
                    
            response.set_header('Content-type', 'text/plain')
            
            conn.close()
            
            return filter_ajax(arr_log)
            
        response.set_header('Content-type', 'text/plain')    
        
        arr_log=[]
        
        conn.close()        
        
        return filter_ajax(arr_log)
                
                

    else:
        conn.close()
        return filter_ajax({})

# Get json data for a see progress in task in a server

@app.route('/'+pastafari_folder+'/showprogress/tasks')
@app.post('/'+pastafari_folder+'/showprogress/tasks')
def gettasks():
    
    if check_login():
        
        s=get_session()
        
        #Load menu
        
        menu=get_menu(config_admin.modules_admin)

        lang_selected=get_language(s)
        
        t=PTemplate(env)
    
        conn=WebModel.connection()

        getpostfiles=GetPostFiles()

        getpostfiles.obtain_get()
        
        getpostfiles.get['op']=getpostfiles.get.get('op', '')
        getpostfiles.get['task_id']=getpostfiles.get.get('task_id', '0')
        getpostfiles.get['position']=getpostfiles.get.get('position', '0')
        getpostfiles.get['server']=getpostfiles.get.get('server', '')
        
        try:
        
            task_id=int(getpostfiles.get['task_id'])
        except:
            task_id=0
            
        try:
            position=int(getpostfiles.get['position'])
        except:
            position=0
        
        task=Task(conn)
        logtask=LogTask(conn)
        
        arr_task=task.select_a_row(task_id)
        
        t.show_basic_template=False
        
        arr_rows={'wait': 1}
        
        if arr_task:
            
            logtask.set_limit([position, 20])
                
            logtask.set_order({'id': 0})
            
            logtask.conditions=['WHERE task_id=%s', [task_id]]
            
            if getpostfiles.get['server']!='':
                logtask.conditions=['WHERE task_id=%s and logtask.server=%s', [task_id, getpostfiles.get['server']]]
                
            #logtask.set_limit([position, 1])
            
            #arr_row=logtask.select_a_row_where([], 1, position)
            
            logtask.yes_reset_conditions=False
            
            c=logtask.select_count()
            
            if c>0:
                
                arr_rows=[]
                
                with logtask.select([], True) as cursor:            
                    for arr_row in cursor:
                        arr_rows.append(arr_row)
                
            else:
                arr_rows=[]
                
                with logtask.set_conditions('WHERE task_id=%s and logtask.error=1', [task_id]).select([], True) as cursor:            
                    for arr_row in cursor:
                        arr_rows.append(arr_row)

                if arr_rows==0:
                    
                    arr_rows={'wait': 1}
                else:

                    with logtask.set_conditions('WHERE task_id=%s and logtask.server=%s and logtask.error=1', [task_id, getpostfiles.get['server']]).select([], True) as cursor:            
                        for arr_row in cursor:
                            arr_rows.append(arr_row)
                    
            """
                
                arr_rows=[]
                
                with logtask.select() as cursor:            
                    for arr_row in cursor:
                        arr_rows.append(arr_row)
                
                if len(arr_rows)==0:
                    logtask.set_limit([1])
                
                    logtask.set_order({'id': 0})
                    
                    logtask.conditions=['WHERE task_id=%s and status=1 and error=1  and server=""', [task_id]]
                    
                    if logtask.select_count('id', True)==0:
                        
                        if arr_task['status']=='0' or arr_task['status']==0:
                            conn.close()
                            return filter_ajax({'wait': 1})
                        else:
                            conn.close()
                            return filter_ajax({})
                    else:
                        
                        logtask.set_limit([1])
                    
                        logtask.set_order({'id': 0})
                        
                        logtask.conditions=['WHERE task_id=%s and status=1 and error=1  and server=""', [task_id]]
                        
                        arr_rows=logtask.select_to_array([], True)
                
                #response.set_header('Content-type', 'text/plain')
                conn.close()
                return filter_ajax(arr_rows)
                
            else:
                conn.close()
                return filter_ajax({'wait': 1})
            """
                    
        else:
            
            arr_task={'task_id': task_id, 'progress': 100, 'message': 'Error: no exists task', 'error': 1, 'status': 1}
            
        conn.close()
        
        return filter_ajax(arr_rows)

        
        
    else:

        redirect(make_url(config.admin_folder))
