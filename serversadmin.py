#/usr/bin/env python3

from paramecio.citoplasma.generate_admin_class import GenerateAdminClass
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.httputils import GetPostFiles, filter_ajax
from paramecio.cromosoma.formsutils import csrf_token
from paramecio.citoplasma.urls import make_url, redirect
from paramecio.citoplasma.mtemplates import set_flash_message
from paramecio.citoplasma import datetime
from modules.pastafari.models import servers, tasks
from modules.pastafari.libraries.configclass import config_task
from modules.pastafari.libraries.task import Task
#from paramecio.citoplasma.mtemplates import ptemplate
from paramecio.citoplasma.i18n import I18n, load_lang
from paramecio.cromosoma import formsutils, webmodel
from paramecio.cromosoma.coreforms import SelectForm
from paramecio.cromosoma.coreforms import PasswordForm
from paramecio.cromosoma.coreforms import SelectModelForm
from itsdangerous import JSONWebSignatureSerializer
from collections import OrderedDict
import requests
import re
import os
import copy
import json
import configparser
from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models import servers, tasks
from bottle import request, route, post
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.adminutils import check_login, get_menu, get_language
from settings import config
from settings import config_admin
from paramecio.citoplasma.sessions import get_session
from paramecio.wsgiapp import app

#t_admin=ptemplate('modules/pastafari')

server_task=config_task.server_task

server_task=server_task+'/exec/'+config_task.api_key+'/'

url=make_url('pastafari/servers')

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

env.directories.insert(1, config.paramecio_root+'/modules/admin/templates')

def admin(**args):
    
    t=args['t']
    
    conn=args['connection']
    
    server=servers.Server(conn)
    
    os_model=servers.OsServer(conn)
    
    task=tasks.Task(conn)
    
    logtask=tasks.LogTask(conn)
    
    group_server=servers.ServerGroup(conn)
    
    group_server_item=servers.ServerGroupItem(conn)
    
    getpostfiles=GetPostFiles()
    
    getpostfiles.obtain_get()
    
    getpostfiles.get['op']=getpostfiles.get.get('op', '')
    
    getpostfiles.get['group_id']=getpostfiles.get.get('group_id', '0')

    request_type=formsutils.request_type()
    
    server.fields['os_codename'].name_form=SelectForm

    server.create_forms(['hostname', 'ip', 'os_codename'])
    
    arr_os={}
    
    with os_model.select() as cur:
        arr_os = { v['codename'] : v['name'] for v in cur }
    
    server.fields['date'].label=I18n.lang('pastafari', 'server_status', 'Server status')
    
    server.forms['os_codename'].arr_select=arr_os
    
    server.forms['password']=PasswordForm('password', '')
    
    server.forms['password'].required=True
    
    server.forms['password'].label=I18n.lang('pastafari', 'password', 'Password')
    
    server.forms['delete_root_password']=SelectForm('delete_root_password', '1', {'0': 'No', '1': 'Yes'})
    
    server.forms['delete_root_password'].label=I18n.lang('pastafari', 'delete_root_password', 'Disable root password')
    
    server.forms['clean_gcc']=SelectForm('clean_gcc', '1', {'0': 'No', '1': 'Yes'})
    
    server.forms['clean_gcc'].label=I18n.lang('pastafari', 'clean_gcc', 'Clean build dependencies for soft monitoring install?,if you want gcc in your server, answer NO')
    
    server.forms['group_id']=SelectModelForm('group_id', getpostfiles.get['group_id'], group_server, 'name', 'id', 'parent_id')
    
    server.forms['group_id'].field=group_server_item.fields['server_id']
    
    server.forms['group_id'].required=True
    
    server.forms['group_id'].label=label=I18n.lang('pastafari', 'principal_group', 'Principal group')

    if getpostfiles.get['op']=='1':
        
        if request_type!="POST":
            
            forms=formsutils.show_form({}, server.forms, t, False, False)
            
            return t.load_template('pastafari/admin/add_servers.phtml', group_id=getpostfiles.get['group_id'], form_server=forms, url=url+'?op=1&group_id='+getpostfiles.get['group_id'])
        else:
            
            #if insert then send task to servertask
            
            getpostfiles.obtain_post()
            
            post={}
            
            post['password']=getpostfiles.post.get('password', '')
            post['delete_root_password']=getpostfiles.post.get('delete_root_password', '0')
            post['ip']=getpostfiles.post.get('ip', '')
            post['clean_gcc']=getpostfiles.post.get('clean_gcc', '1')
            
            try:
            
                post['group_id']=getpostfiles.post.get('group_id', '0')
                
            except:
                
                post['group_id']='0'
            
            check_form=formsutils.CheckForm()
            
            (post, pass_form)=check_form.check(post, {'password': server.forms['password'], 'delete_root_password': server.forms['delete_root_password'], 'ip': server.forms['ip'], 'group_id': server.forms['group_id']})
            
            server.set_conditions('WHERE ip=%s', [post['ip']])
            
            c_ip=server.select_count()
            
            if c_ip==0:
            
                if check_form.error==0:
                    
                    #try connect to the server
                    
                    task_ssh=Task(post['ip'])
                    
                    testing_task=copy.copy(config_task)
                    
                    testing_task.remote_user='root'
                    testing_task.remote_password=post['password']
                    
                    task_ssh.config=testing_task
                    
                    if task_ssh.prepare_connection():
                    
                        task_ssh.ssh.close()
                
                        if not server.insert(getpostfiles.post):
                            
                            forms=formsutils.show_form(getpostfiles.post, server.forms, t, True)
                            
                            return t.load_template('pastafari/admin/add_servers.phtml', group_id=getpostfiles.get['group_id'], form_server=forms, url=url+'?op=1')
                
                        else:
                            
                            server_id=server.insert_id()
                            
                            # Insert in server group
                            
                            group_server_item.valid_fields=['group_id', 'server_id']
                            
                            if group_server_item.insert({'group_id': post['group_id'], 'server_id': server_id}):
                            
                                task.create_forms()
                                
                                os_server=getpostfiles.post['os_codename'].replace('/', '').replace('.', '')
                                
                                ip=server.fields['ip'].check(getpostfiles.post['ip'])
                                
                                files=[]
                                
                                files.append(['modules/pastafari/scripts/standard/'+os_server+'/install_python.sh', 0o750])
                                files.append(['modules/pastafari/scripts/standard/'+os_server+'/install_curl.sh', 0o750])
                                files.append(['modules/pastafari/scripts/standard/'+os_server+'/install_psutil.sh', 0o750])
                                files.append(['modules/pastafari/scripts/standard/'+os_server+'/upgrade.sh', 0o750])
                                files.append(['modules/pastafari/scripts/standard/'+os_server+'/clean_gcc.sh', 0o750])
                                
                                files.append(['modules/pastafari/scripts/monit/'+os_server+'/alive.py', 0o750])
                                #files.append(['monit/'+os_server+'/files/alive.sh', 0o750];
                                files.append(['modules/pastafari/scripts/monit/'+os_server+'/files/get_info.py', 0o750])
                                files.append(['modules/pastafari/scripts/monit/'+os_server+'/files/get_updates.py', 0o750])
                                files.append(['modules/pastafari/scripts/monit/'+os_server+'/files/crontab/alive', 0o640])
                                files.append(['modules/pastafari/scripts/monit/'+os_server+'/files/sudoers.d/spanel', 0o640])
                                files.append([config_task.public_key, 0o600])

                                commands_to_execute=[]
                                
                                commands_to_execute.append(['modules/pastafari/scripts/standard/'+os_server+'/install_curl.sh', ''])
                                commands_to_execute.append(['modules/pastafari/scripts/standard/'+os_server+'/install_python.sh', ''])
                                commands_to_execute.append(['modules/pastafari/scripts/standard/'+os_server+'/install_psutil.sh', ''])
                                commands_to_execute.append(['modules/pastafari/scripts/monit/'+os_server+'/alive.py', '--url='+config_task.url_monit+'/'+ip+'/'+config_task.api_key+' --user='+config_task.remote_user+' --pub_key='+config_task.public_key])
                                
                                delete_files=[]
                                
                                delete_files.append('modules/pastafari/scripts/standard/'+os_server+'/install_python.sh')
                                delete_files.append('modules/pastafari/scripts/standard/'+os_server+'/install_curl.sh')
                                delete_files.append('modules/pastafari/scripts/standard/'+os_server+'/install_psutil.sh')
                                delete_files.append(config_task.public_key)
                                
                                delete_directories=['modules/pastafari']
                                delete_directories=[os.path.dirname(config_task.public_key)]
                                
                                if post['delete_root_password']=='1':
                                    #delete_root_passwd.sh
                                    files.append(['modules/pastafari/scripts/standard/'+os_server+'/delete_root_passwd.sh', 0o750])
                                    commands_to_execute.append(['modules/pastafari/scripts/standard/'+os_server+'/delete_root_passwd.sh', ''])
                                    
                                if post['clean_gcc']=='1':
                                    #delete_root_passwd.sh
                                    files.append(['modules/pastafari/scripts/standard/'+os_server+'/clean_gcc.sh', 0o750])
                                    commands_to_execute.append(['modules/pastafari/scripts/standard/'+os_server+'/clean_gcc.sh', ''])
                                    
                                #'modules.pastafari.tasks.system.install.task_functions'
                                if task.insert({'name_task': 'monit_server','description_task': I18n.lang('pastafari', 'add_monit', 'Adding monitoritation to the server...'), 'url_return': url, 'files': files, 'commands_to_execute': commands_to_execute, 'delete_files': delete_files, 'delete_directories': delete_directories, 'server': ip, 'user': 'root', 'password': post['password'], 'path': '/root', 'error_func': '', 'extra_data': {'server_id': server_id}}):
                                                    
                                    task_id=task.insert_id()
                                                    
                                    try:
                                    
                                        r=requests.get(server_task+str(task_id))
                                        
                                        arr_data=r.json()
                                        
                                        arr_data['task_id']=task_id
                                        
                                        logtask.create_forms()
                                        
                                        if not logtask.insert(arr_data):
                                            
                                            return "Error:Wrong format of json data..."
                                            
                                            #return t_admin.load_template('pastafari/ajax_progress.phtml', title='Adding monitoritation to the server...') #"Load template with ajax..."
                                    
                                    except:
                                        
                                        logtask.conditions=['WHERE id=%s', [task_id]]
                                        
                                        task.update({'status': 1, 'error': 1})
                                        
                                        server.conditions=['WHERE id=%s', [server_id]]
                                        
                                        group_server_item.conditions=['WHERE server_id=%s', [server_id]]
                                    
                                        group_server_item.delete()
                                    
                                        server.delete()
                                        
                                        return "Error:cannot connect to task server, check the url for it..."
                                    
                                    #return t.load_template('pastafari/progress.phtml', name_task=I18n.lang('pastafari', 'add_monit', 'Adding monitoritation to the server...'), description_task=I18n.lang('pastafari', 'add_monit_explain', 'Installing the basic scripts for send info from server to monit module'), task_id=task_id, server=ip, position=0)
                                    #return "Server is building..."
                                    #redirect('servers?op=2&task_id='+str(task_id))
                                    #@get('/'+pastafari_folder+'/showprogress/<task_id:int>/<server>')
                                    redirect(make_url(pastafari_folder+'/showprogress/'+str(task_id)+'/'+ip))
                    
                                else:
                                    
                                    server.conditions=['WHERE id=%s', [server_id]]
                                    
                                    server.delete()
                                    
                                    group_server_item.conditions=['WHERE server_id=%s', [server_id]]
                                    
                                    group_server_item.delete()
                                    
                                    return "Error: cannot create the new task"
                            else:
                                
                                server.conditions=['WHERE id=%s', [server_id]]
                                    
                                server.delete()
                                
                                return "Error: you need a initial group for your server"
                                
                    else:
                        task_ssh.ssh.close()
                        return "Cannot connect to the new server "+task_ssh.txt_error
                    
                else:
                    
                    forms=formsutils.show_form(getpostfiles.post, server.forms, t, True)
                        
                    return t.load_template('pastafari/admin/add_servers.phtml', group_id=getpostfiles.get['group_id'], form_server=forms, url=url+'?op=1&group_id='+getpostfiles.get['group_id'])
                    
            else:
                
                server.fields['ip'].duplicated_ip=True
                
                forms=formsutils.show_form(getpostfiles.post, server.forms, t, True)
                        
                return t.load_template('pastafari/admin/add_servers.phtml', group_id=getpostfiles.get['group_id'], form_server=forms, url=url+'?op=1&group_id='+getpostfiles.get['group_id'])
                
    #elif getpostfiles.get['op']=='2':
        
        #return ""
    
    elif getpostfiles.get['op']=='2':
        
        getpostfiles=GetPostFiles()
        
        getpostfiles.obtain_get()
        
        server_id=int(getpostfiles.get.get('id', '0'))
        
        arr_server=server.select_a_row(server_id)
        
        if arr_server:
        
            return t.load_template('pastafari/admin/graphs.phtml', server=arr_server, api_key=config_task.api_key)
            
        else:
            
            return ""
            
    
    elif getpostfiles.get['op']=='5':
        
        getpostfiles.get['id']=getpostfiles.get.get('id', '0')
        
        getpostfiles.get['delete']=getpostfiles.get.get('delete', '0')
        
        try:
            getpostfiles.get['id']=int(getpostfiles.get['id'])
        except:
            getpostfiles.get['id']=0
            
        if getpostfiles.get['delete']!='0':
            
            group_server_item.set_conditions('WHERE server_id=%s', [ getpostfiles.get['id']])
            
            group_server_item.delete()
            
            server.set_conditions('WHERE id=%s', [ getpostfiles.get['id']])
            
            server.delete()
            
            set_flash_message('Deleted the server sucessfully')
            
            redirect(make_url(pastafari_folder+'/servers'))
            
            pass
        else:
            
            return "It deleted the server in database <strong>only</strong><p>You need delete the server with the tool of your election: <input type=\"button\" value=\"Do you are sure?\" onclick=\"javascript:location.href='"+make_url(pastafari_folder+'/servers', {'op': '5', 'id': str(getpostfiles.get['id']), 'delete': '1'})+"';\"></p>"
        
        
        pass
    
    else:
        
        getpost=GetPostFiles()
        
        getpost.obtain_get()
        
        try: 
        
            group_id=int(getpost.get.get('group_id', '0'))
            
        except:
            
            group_id=0
        
        select_form_group=SelectModelForm('group_id', group_id, servers.ServerGroup(conn), 'name', 'id', 'parent_id')
        
        select_form_group.name_field_id='change_group_id_form'
                
        servers_list=SimpleList(server, url, t)
        
        yes_form=0
        
        type_op=''
        
        #servers_list.arr_extra_fields=[I18n.lang('common', 'options', 'Options')]
        
        servers_list.arr_extra_options=[server_options]
        
        servers_list.yes_search=False
        
        select_task=None
        
        if 'type' in getpost.get:
            
            if getpost.get['type']=='down':
                
                actual_timestamp=datetime.obtain_timestamp(datetime.now())
            
                past_timestamp=actual_timestamp-300
                
                actual_time=datetime.timestamp_to_datetime(actual_timestamp)
            
                past_time=datetime.timestamp_to_datetime(past_timestamp)
                
                servers_list.model.set_conditions('WHERE date<%s', [past_time])
                
            elif getpost.get['type']=='heavy':
                servers_list.model.set_conditions("where actual_idle>%s", [80])
            
            elif getpost.get['type']=='disks':
                servers_list.model.set_conditions("where ip IN (select ip from statusdisk where percent>90)", [])
                
            elif getpost.get['type']=='update_servers':
                
                servers_list.model.set_conditions("where num_updates>0", [])
                
                servers_list.arr_extra_fields=[I18n.lang('common', 'update_server', 'Update server')]
        
                servers_list.arr_extra_options=[server_update_options]
                
                servers_list.yes_search=False
                
                yes_form=1
                
            elif getpost.get['type']=='task_servers': 
                
                servers_list.arr_extra_fields=[I18n.lang('pastafari', 'choose_server', 'Choose server')]
        
                servers_list.arr_extra_options=[server_update_options]
                
                servers_list.yes_search=False
                
                yes_form=2
                
                # Get tasks and put in select_task
                
                # Folders are tasks/ and modules/pastafari/tasks
                
                base_path='modules/pastafari/tasks'
                
                config_parser = configparser.ConfigParser()
                
                select_task=scandir(base_path, config_parser, OrderedDict(),  'tasks')
                
                #OrderedDict([('tasks', {'servers': [['Servers', 'tasks', 0]]}), ('servers', {'databases': [['Database servers', 'servers', 0]], 'mail': [['Mail', 'servers', 0], ['Standalone postfix server,  Install on your servers a simple and secure postfix mail server', 'mail', 'modules/pastafari/tasks/servers/mail/postfix/standalone_postfix.py', 1]]})])

                
            type_op=getpost.get['type']
        
        if group_id>0:
            servers_list.model.conditions[0]+=' AND id IN (select server_id from servergroupitem where group_id=%s)'
            servers_list.model.conditions[1].append(group_id)
        
        servers_list.fields_showed=['hostname', 'ip', 'num_updates', 'date']
        
        servers_list.limit_pages=100
        
        servers_list.s['order']='0'
        servers_list.s['order_field']='hostname'

        show_servers=servers_list.show()
        
        return t.load_template('pastafari/admin/servers.phtml', show_servers=show_servers, type_op=type_op, yes_form=yes_form, csrf_token=csrf_token(), select_form_group=select_form_group, group_id=group_id, select_task=select_task)
    
    
    return ""

@app.route('/'+pastafari_folder+'/servers')
@app.post('/'+pastafari_folder+'/servers')
def home():
    
    if check_login():
        
        s=get_session()
        
        #Load menu
        
        menu=get_menu(config_admin.modules_admin)

        lang_selected=get_language(s)
        
        t=PTemplate(env)
    
        conn=WebModel.connection()
        
        content_index=admin(t=t, connection=conn)
        
        if t.show_basic_template==True:

            return t.load_template('admin/content.html', title='Servers', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        else:
            
            return content_index
        
    else:
        redirect(make_url(config.admin_folder))
        
def server_options(url, id, arr_row):
    
    arr_options=[]
    
    arr_options.append('<a href="%s">%s</a>' % (make_url(pastafari_folder+'/servergraphs/'+str(id)), 'Server graphs'))
    arr_options.append('<a href="%s">%s</a>' % (make_url(pastafari_folder+'/tasklist/'+str(id)), 'Server logs'))
    arr_options.append('<a href="%s">%s</a>' % (make_url(pastafari_folder+'/servers', {'op': '5', 'id': str(id)}), 'Delete server from db'))
    
    return arr_options
    

def server_update_options(url, id, arr_row):
    
    arr_options=[]
    
    arr_options.append('<input type="checkbox" name="server_'+str(id)+'" id="server_'+str(id)+'" class="server_checkbox" value="'+str(id)+'" />')
    
    return arr_options

def scandir(mydir, config_parser, arr_dir=OrderedDict(), father='', s=JSONWebSignatureSerializer(config.key_encrypt)):
    
    search_dir=os.listdir(mydir)
    
    for one_path in search_dir:
       
        if os.path.isfile(mydir+'/'+one_path):
            if one_path=='info.cfg':
                # Read the info file and put radio form in python files signed in file
                config_parser.clear()
                config_parser.read(mydir+'/'+one_path)
                
                if 'info' in config_parser:                   
                    if 'name' in config_parser['info']:
                        
                        if not father in arr_dir:
                            arr_dir[father]={}
                        
                        arr_dir[father][os.path.basename(mydir)]=[]
                        
                        arr_dir[father][os.path.basename(mydir)].append([config_parser['info']['name'], father, 0])
                        
                        if 'modules' in config_parser:
                            for k, v in config_parser['modules'].items():
                                arr_dir[father][os.path.basename(mydir)].append([config_parser['modules'][k], s.dumps({'file': mydir+'/'+k+'.py'}), 1])
                
        
        elif os.path.isdir(mydir+'/'+one_path):
            
            arr_dir=scandir(mydir+'/'+one_path, config_parser, arr_dir, os.path.basename(mydir))
    
    return arr_dir
