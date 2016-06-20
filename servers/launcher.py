#!/usr/bin/python3

import argparse
import json
from settings import config
from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models import servers, tasks
from modules.pastafari.libraries.task import Task
from modules.pastafari.libraries.configclass import config_task
from multiprocessing.pool import Pool

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
        
        task=Task(arr_task['server'], task_id)
        
        task.files=task_model.fields['files'].loads(arr_task['files'])
        
        if task.files==False:
            task.files=[]
        
        task.commands_to_execute=task_model.fields['files'].loads(arr_task['commands_to_execute'])
        
        if task.commands_to_execute==False:
            task.commands_to_execute=[]
        
        task.delete_files=task_model.fields['files'].loads(arr_task['delete_files'])
        
        if task.delete_files==False:
            task.delete_files=[]
        
        task.delete_directories=task_model.fields['files'].loads(arr_task['delete_directories'])
        
        task.one_time=False
        
        if arr_task['one_time']==1:
            task.one_time=True
            
        task.version=arr_task['version']
        
        task.codename=arr_task['codename_task']
        
        if task.delete_directories==False:
            task.delete_directories=[]
        
        if arr_task['where_sql_server']=='':
            
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

                    arr_task=[]
                    
                    for server in arr_servers:
                        arr_task.append([task, server['ip'], server['os_codename']])
                    
                    pool.map(execute_multitask, arr_task)
                    
                    #for x in range(num_pools)
                        #pool.
                    pass
                
                z+=num_tasks
            
            pass
        
        if not task.commands_to_execute:
            print('Error: no task files')
            exit(1)

    exit(0)

def execute_multitask(arr_task=[]):
    
    
    task=arr_task[0]
    server=arr_task[1]
    os_server=arr_task[2]
    
    task.server=server
    task.os_server=os_server
    
    task.exec()

if __name__=='__main__':
    start()
