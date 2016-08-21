from gevent import monkey; monkey.patch_all()
from gevent.subprocess import Popen, PIPE
#from multiprocessing import Process
import argparse
import uuid
import gevent, traceback, sys, time
from bottle import route, run, default_app
from importlib import import_module
from os.path import isfile
from settings import config
from paramecio.citoplasma.i18n import I18n
from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models import servers, tasks
from modules.pastafari.libraries.task import Task
from modules.pastafari.libraries.configclass import config_task

# For deploy with uwsgi;  uwsgi --gevent 100 --http-socket :9090 --wsgi-file scheduler.py 

pastafari_scripts='./scripts'
pastafari_host='127.0.0.1'
pastafari_port=1337

#parser.add_argument('--port', help='The port where the task server is executed', required=True)

if hasattr(config, 'pastafari_scripts'):
    pastafari_scripts=config.pastafari_scripts

if hasattr(config, 'pastafari_port'):
    pastafari_port=config.pastafari_port
    
if hasattr(config, 'pastafari_host'):
    pastafari_host=config.pastafari_host

def execute_script(task_id):
    
    args=['python3 launcher.py --task_id='+str(task_id)]
    
    with Popen(args, bufsize=None, executable=None, stdin=None, stdout=PIPE, stderr=PIPE, preexec_fn=None, shell=True, cwd=None, env=None, universal_newlines=False, startupinfo=None, creationflags=0, threadpool=None) as proc:
        
        proc.wait()
        
        return_value=proc.returncode

        if return_value>0:
            connection=WebModel.connection()
            
            logtask=tasks.LogTask(connection)
            task=tasks.Task(connection)
            
            logtask.create_forms()
            task.create_forms()
            
            
            line=proc.stdout.read().decode('utf-8')
            line_error=proc.stderr.read().decode('utf-8')
            logtask.insert({'task_id': task_id, 'progress': 100, 'message': I18n.lang('pastafari', 'error_exec_launcher', 'Error executing launcher.py: ')+str(line)+"\n"+str(line_error), 'error': 1, 'status': 1})
            #Status die
            task.set_conditions('where id=%s', [task_id])
            task.reset_require()
            task.update({'status': 1, 'error': 1})
    

@route('/')
def home():
    
    response={'error': 1, 'code_error': 1, 'message': 'Nothing to see here...', 'progress' : 100}

    return response

@route('/exec/<api_key>/<task_id:int>')
def index(api_key, task_id):
    
    connection=WebModel.connection()
    
    # Get the task to execute.
    
    if api_key==config_task.api_key:
    
        task=tasks.Task(connection)
        logtask=tasks.LogTask(connection)
        logtask.create_forms()
        """
        task.set_conditions('where status=%s and id!=%s', [0, task_id])
        
        c=task.select_count()
        
        if c==0:
        """
        arr_task=task.select_a_row(task_id)
        
        if arr_task:
        
        # Add to queue

            greenlet = gevent.spawn( execute_script, task_id)
            """p = Process(target=execute_script, args=(task_id,))
            p.start()"""
            # Close the connection

            response={'error': 0, 'code_error': 0, 'message': 'Begin task with id '+str(task_id), 'progress' : 0}

            return response
        else:
            
            response={'error': 1, 'code_error': 1, 'message': 'Doesnt exists task with id '+str(task_id), 'progress' : 100, 'status': 1}
        
            return response
        """
        else:
            
            response={'error': 1, 'code_error': 1, 'message': 'Sorry, other task are in process', 'progress' : 100, 'status': 1}
            
            return response
        """
        
    else:
        
        response={'error': 1, 'code_error': 1, 'message': 'No permission for make tasks', 'progress' : 100, 'status': 1}
        
        return response
        #logtask.insert({})
"""
@route('/progress/<api_key>/<task_id:int>')
def progress(api_key, task_id):
    
    # Get response from logtask
    
    #response={'error': 0, 'code_error': 0, 'message': 'Task Successful!', 'progress' : 100}
    
    logtask=tasks.LogTask()
    
    logtask.conditions=['WHERE task_id=%s', [task_id]]
    
    response=logtask.select_a_row_where()

    return response

"""
#def control_process():
    
    

app = application  = default_app()

def run_app(app):
    run(app=app, host=pastafari_host, port=pastafari_port, debug=config.debug, server='gevent', reloader=config.reloader)
    
#app.add_hook('after_request', WebModel.close)

if __name__=='__main__':
    #pass
    #server='gevent', 
    run_app(app)

