#/usr/bin/env python3

from paramecio.citoplasma.generate_admin_class import GenerateAdminClass
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.citoplasma.urls import make_url
from modules.pastafari.models import servers, tasks
#from paramecio.citoplasma.mtemplates import ptemplate
from paramecio.cromosoma import formsutils
from settings import config
from bottle import request, redirect, response
import requests
import json

#t_admin=ptemplate('modules/pastafari')

server_task='http://127.0.0.1:1337'

if hasattr(config, 'server_task'):
    server_task=config.server_task
    

server_task=server_task+'/progress/'

def admin(**args):

    conn=args['connection']

    t=args['t']

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
    
    task=tasks.Task(conn)
    tasklog=tasks.LogTask(conn)
    
    arr_task=task.select_a_row(task_id)
    
    t.show_basic_template=False
    
    if arr_task:
        
        tasklog.set_limit([position, 20])
            
        tasklog.set_order(['id'], ['ASC'])
        
        tasklog.conditions=['WHERE task_id=%s', [task_id]]
        
        if getpostfiles.get['server']!='':
            tasklog.conditions=['WHERE task_id=%s and logtask.server=%s', [task_id, getpostfiles.get['server']]]
            
        #tasklog.set_limit([position, 1])
        
        #arr_row=tasklog.select_a_row_where([], 1, position)
        
        tasklog.yes_reset_conditions=False
        
        c=tasklog.select_count()
        
        if c>0:
            
            arr_rows=[]
            
            cursor=tasklog.select()
            
            for arr_row in cursor:
                arr_rows.append(arr_row)
            
            if len(arr_rows)==0:
                tasklog.set_limit([1])
            
                tasklog.set_order(['id'], ['ASC'])
                
                tasklog.conditions=['WHERE task_id=%s and status=1 and error=1  and server=""', [task_id]]
                
                if tasklog.select_count('id', True)==0:
                    
                    if arr_task['status']=='0' or arr_task['status']==0:
                        return {'wait': 1}
                    else:
                        return {}
                else:
                    
                    tasklog.set_limit([1])
                
                    tasklog.set_order(['id'], ['ASC'])
                    
                    tasklog.conditions=['WHERE task_id=%s and status=1 and error=1  and server=""', [task_id]]
                    
                    arr_rows=tasklog.select_to_array([], True)
            
            response.set_header('Content-type', 'text/plain')
            
            return json.dumps(arr_rows)
            
        else:
            return {'wait': 1}
                
                
    else:
        return {}
