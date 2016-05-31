#!/usr/bin/python3

import traceback, sys
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import make_url, add_get_parameters
from paramecio.citoplasma.adminutils import get_menu, get_language
from paramecio.citoplasma.sessions import get_session
from bottle import route, get,post,response,request
from settings import config
from settings import config_admin
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.webmodel import WebModel
from bottle import redirect
from modules.pastafari.models.tasks import Task, LogTask
from modules.pastafari.libraries.configclass import config_task
import requests

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

@post('/'+pastafari_folder+'/updateservers')
@get('/'+pastafari_folder+'/updateservers')
def home():
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
            
            task=Task(connection)
            logtask=LogTask(connection)
            
            getpost=GetPostFiles()            
            
            #Load menu
            
            menu=get_menu(config_admin.modules_admin)
        
            lang_selected=get_language(s)
            
            content_index=''
            
            # Send request to server
            
            commands_to_execute=[['bin/upgrade.sh', '']]
            
            task.create_forms()
            
            if task.insert({'name_task': 'update_server','description_task': I18n.lang('pastafari', 'update_servers', 'Updating servers...'), 'url_return': '', 'commands_to_execute': commands_to_execute, 'server': '', 'where_sql_server': 'WHERE num_updates>0'}):
                                                
                task_id=task.insert_id()
                                
                try:
                
                    r=requests.get(server_task+str(task_id))
                    
                    arr_data=r.json()
                    
                    arr_data['task_id']=task_id
                    
                    logtask.create_forms()
                    
                    if not logtask.insert(arr_data):
                        
                        content_index="Error:Wrong format of json data..."
                        
                        #return t_admin.load_template('pastafari/ajax_progress.phtml', title='Adding monitoritation to the server...') #"Load template with ajax..."
                
                except:
                    
                    #logtask.conditions=['WHERE id=%s', [task_id]]
                    
                    task.update({'status': 1, 'error': 1})
                    
                    content_index="Error:cannot connect to task server, check the url for it..."
                    
            else:
                content_index="Error: cannot insert the task: "+task.show_errors()

            return t.load_template('admin/content.html', title='Updating servers', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
            
        else:
            redirect(config.admin_folder)
    
    else:
    
        redirect(config.admin_folder)


if config.default_module=="pastafari":

    home = route("/")(home)
