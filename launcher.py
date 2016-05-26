#!/usr/bin/python3

import argparse
import json
from settings import config
from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models import servers, tasks
from modules.pastafari.libraries.task import Task
from modules.pastafari.libraries.configclass import config_task

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
    
    task.commands_to_execute=task_model.fields['files'].loads(arr_task['commands_to_execute'])
    
    task.delete_files=task_model.fields['files'].loads(arr_task['delete_files'])
    
    task.delete_directories=task_model.fields['files'].loads(arr_task['delete_directories'])
    
    task.exec()
    
    if not task.files:
        print('Error: no task files')
        exit(1)

exit(0)
