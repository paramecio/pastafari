#!/usr/bin/env python3

import argparse
import json
from settings import config
from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models import servers, tasks
from modules.pastafari.libraries.task import Task
from modules.pastafari.libraries.configclass import config_task
from multiprocessing.pool import Pool
import importlib

num_tasks=10

if hasattr(config, 'num_tasks'):
    num_tasks=config.num_tasks

def start():
    
    parser = argparse.ArgumentParser(description='A daemon used for make a task in a server.The results are saved in a sql database using task class')
    parser.add_argument('--task_id', help='The task to execute', required=True)

    args = parser.parse_args()

    task_id=int(args.task_id)

    conn=WebModel.connection()

    task_model=tasks.Task(conn)

    logtask=tasks.LogTask(conn)

    arr_task=task_model.select_a_row(task_id)
    
    if arr_task:
        
        if arr_task['user']!='' and arr_task['password']!='' and arr_task['path']!='':
            
            config_task.remote_user=arr_task['user']
            config_task.remote_password=arr_task['password']
            config_task.remote_path=arr_task['path']
            
            task_model.create_forms()
            task_model.reset_require()
            
            task_model.set_conditions('WHERE id=%s', [task_id])
            
            task_model.update({'password': ''})
        
        commands_to_execute=json.loads(arr_task['commands_to_execute'])
        
        if not commands_to_execute:
            print('Error: no task files')
            exit(1)
        
        if arr_task['where_sql_server']=='':
            
            task=generate_task(arr_task, task_id)
            
            task.exec()
                
        else:
            
            # Select the servers and make all tasks asynchronous
            
            server_model=servers.Server(conn)
            
            server_model.set_conditions(arr_task['where_sql_server'], [])
            
            server_model.yes_reset_conditions=False
            
            c=server_model.select_count()
            
            #Update task with number of servers
            
            task_model.set_conditions('WHERE id=%s', [task_id])
            
            task_model.reset_require()
            
            task_model.valid_fields=['num_servers']
            
            task_model.update({'num_servers': c})
            
            z=0
            
            while z<c:
                
                # Set the num of pools
                
                server_model.set_limit([z, num_tasks])
                
                arr_servers=server_model.select_to_array()
                
                num_pools=len(arr_servers)
                
                with Pool(processes=num_pools) as pool:

                    arr_task_exec=[]
                    
                    for server in arr_servers:
                        arr_task_exec.append([arr_task, task_id, server['ip'], server['os_codename']])
                    
                    pool.map(execute_multitask, arr_task_exec)
                    
                    #for x in range(num_pools)
                        #pool.
                    pass
                
                z+=num_tasks
            
            pass
            
        # Task done
        
        task_model.set_conditions('WHERE id=%s', [task_id])
            
        task_model.reset_require()
        
        task_model.valid_fields=['status']
        
        task_model.update({'num_servers': 1})

    conn.close()

    exit(0)

def execute_multitask(arr_task_exec=[]):
    
    
    arr_task=arr_task_exec[0]
    task_id=arr_task_exec[1]
    server=arr_task_exec[2]
    os_server=arr_task_exec[3]
    
    task=generate_task(arr_task, task_id)
    
    task.server=server
    task.os_server=os_server
    
    task.exec()
    
    del task

def generate_task(arr_task, task_id):
    
    task=Task(arr_task['server'], task_id)
        
    task.files=json.loads(arr_task['files'])
    
    if task.files==False:
        task.files=[]
    
    task.commands_to_execute=json.loads(arr_task['commands_to_execute'])
    
    if task.commands_to_execute==False:
        task.commands_to_execute=[]
    
    task.delete_files=json.loads(arr_task['delete_files'])
    
    if task.delete_files==False:
        task.delete_files=[]
    
    task.delete_directories=json.loads(arr_task['delete_directories'])
    
    task.one_time=False
    
    if arr_task['one_time']==1:
        task.one_time=True
        
    task.version=arr_task['version']
    
    task.codename=arr_task['codename_task']
    
    if task.delete_directories==False:
        task.delete_directories=[]
    
    # Functions for pre, post and error task
    
    if arr_task['post_func']!='':
        #try:
        task_functions_post=importlib.import_module(arr_task['post_func'])
        task.post_task=task_functions_post.post_task
        #except:
        #pass
    
    if arr_task['pre_func']!='':
        #try:
        task_functions_pre=importlib.import_module(arr_task['pre_func'])
        task.pre_task=task_functions_pre.pre_task
        #except:
        #pass
            
    if arr_task['error_func']!='':
        #try:
        task_functions_error=importlib.import_module(arr_task['error_func'])
        task.error_task=task_functions_error.error_task
            
        #except:
        #pass
    
    
    if arr_task['extra_data']!='':
        
        task.extra_data=json.loads(arr_task['extra_data'])
        
    return task
    

if __name__=='__main__':
    start()
