#!/usr/bin/python3

import traceback, sys, time
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import make_url, add_get_parameters
from paramecio.citoplasma.adminutils import get_menu, get_language
from paramecio.citoplasma.sessions import get_session
from paramecio.citoplasma.lists import SimpleList
from bottle import route, get,post,response,request
from settings import config
from settings import config_admin
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.webmodel import WebModel
from bottle import redirect
from modules.pastafari.models.tasks import Task, LogTask
from modules.pastafari.models.servers import Server
from modules.pastafari.libraries.configclass import config_task
import requests
import json

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

env.directories.insert(1, 'paramecio/modules/admin/templates')

@get('/'+pastafari_folder+'/serverslogs')
def home():
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
            
            task=Task(connection)
            logtask=LogTask(connection)
            server=Server(connection)
            
            getpost=GetPostFiles() 
            
            getpost.obtain_get()
            
            #Load menu
                
            menu=get_menu(config_admin.modules_admin)
        
            lang_selected=get_language(s)           
            
            server_id=getpost.get.get('id', 0)
            
            server_hostname=''
            
            arr_server=server.select_a_row(server_id)
            
            if arr_server:
                
                server_hostname=' - '+arr_server['hostname']
            
                ip=arr_server['ip']
                
                logtask.set_conditions('WHERE server=%s', [ip])
                
                logtask_list=SimpleList(logtask, '', t)
                
                logtask_list.limit_pages=100
                
                logtask_list.yes_search=False
                
                logtask_list.s['order']=1
                
                logtask_list.fields_showed=['server', 'message', 'error', 'status']
                
                logtask_list.arr_extra_fields=[]
                logtask_list.arr_extra_options=[]
                
                return_url=make_url('%s/%s' % (config.admin_folder, 'pastafari/servers'))
                
                content_index=t.load_template('pastafari/admin/logs_list.phtml', logtask_list=logtask_list, server=arr_server, return_url=return_url)
                #logtask_list.show()
                
                # Send request to server
                               
            else:
            
                content_index='Log no exists'
                
            return t.load_template('admin/content.html', title='Servers log'+ server_hostname, content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
            
        else:
            redirect(config.admin_folder)
    
    else:
    
        redirect(config.admin_folder)
        
@get('/'+pastafari_folder+'/showprogress/<task_id:int>/<server>')
def showprogress(task_id, server):
    
    t=PTemplate(env)
    
    conn=WebModel.connection()
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
            
            conn=WebModel.connection()
            task=Task(conn)
            
            arr_task=task.select_a_row(task_id)
            
            if arr_task:
            
                menu=get_menu(config_admin.modules_admin)
            
                lang_selected=get_language(s)           
                
                #arr_task=
                
                content_index=t.load_template('pastafari/progress.phtml', description_task=I18n.lang('pastafari', 'add_monit', 'Adding monitoritation to the server...'), task_id=task_id, server=server, position=0)
        
        return t.load_template('admin/content.html', title='Servers log', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)    
            
    
    return ""


@get('/'+pastafari_folder+'/getservers/<task_id:int>')
def getservers(task_id):
    
    conn=WebModel.connection()
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
    
            task=Task(conn)
            logtask=LogTask(conn)
            server=Server(conn)
            
            arr_task=task.select_a_row(task_id)
            
            server.set_conditions('WHERE ip IN (select DISTINCT server from logtask where task_id=%s)', [task_id])
            
            arr_server=server.select_to_array(['hostname', 'ip'])
            
            response.set_header('Content-type', 'text/plain')
            
            return json.dumps(arr_server)

    else:
        return {}

@post('/'+pastafari_folder+'/getprogress/<task_id:int>')
def getprogress(task_id):
    
    conn=WebModel.connection()
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
            
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
            
            logtask.set_order(['id'], ['DESC'])
            
            logtask.set_conditions('WHERE task_id=%s and status=1 and server IN (\''+'\',\''.join(servers)+'\') and server!=""', [task_id])
            
            arr_log=logtask.select_to_array(['status', 'error', 'server'])
            
            logtask.set_order(['id'], ['DESC'])
            
            logtask.set_conditions('WHERE task_id=%s and status=0 and server NOT IN (\''+'\',\''.join(servers)+'\') and server!=""', [task_id])
            
            arr_log2=logtask.select_to_array(['status', 'error', 'server'])
            
            arr_log=arr_log2+arr_log
            
            response.set_header('Content-type', 'text/plain')
            
            return json.dumps(arr_log)

    else:
        return {}
