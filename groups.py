#!/usr/bin/python3

import traceback, sys
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import make_url, add_get_parameters
from paramecio.citoplasma.adminutils import get_menu, get_language
from paramecio.citoplasma.sessions import get_session
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.generate_admin_class import GenerateAdminClass
from bottle import route, get,post,response,request
from settings import config
from settings import config_admin
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.webmodel import WebModel
from bottle import redirect
from modules.pastafari.models import servers
from paramecio.citoplasma import datetime
from paramecio.citoplasma.hierarchy_links import HierarchyModelLinks

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

env.directories.insert(1, config.paramecio_root+'/modules/admin/templates')

@get('/'+pastafari_folder+'/groups')
@post('/'+pastafari_folder+'/groups')
def home():
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
            
            getpostfiles=GetPostFiles()
            
            getpostfiles.obtain_get()
            
            parent_id=getpostfiles.get.get('parent_id', '0')
            
            parent_id=int(parent_id)
            
            #Load menu
            
            menu=get_menu(config_admin.modules_admin)
        
            lang_selected=get_language(s)
            
            groups=servers.ServerGroup(connection)
            
            groups.create_forms()
            
            groups.forms['parent_id'].default_value=parent_id
            
            hierarchy=HierarchyModelLinks(groups, 'All groups', 'name', 'parent_id', make_url('pastafari/groups'))
            
            hierarchy.prepare()
            
            group_list=GenerateAdminClass(groups, make_url(pastafari_folder+'/groups', {'parent_id': str(parent_id)}), t)
            
            groups.set_conditions('WHERE parent_id=%s', [parent_id])
            
            group_list.list.fields_showed=['name']
            
            group_list.list.arr_extra_options=[task_options]
            
            content_index=t.load_template('pastafari/groups.phtml', group_list=group_list, hierarchy_links=hierarchy, son_id=parent_id)
            #group_list.show()

            return t.load_template('admin/content.html', title=I18n.lang('pastafari', 'servers_groups', 'Server\'s Group'), content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
            
        else:
            redirect(make_url(config.admin_folder))
    
    else:
    
        redirect(make_url(config.admin_folder))

@route('/'+pastafari_folder+'/editservers/<parent_id:int>')
def edit_servers(parent_id):
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
                
            #Load menu
            
            group=servers.ServerGroup(connection)
            
            arr_group=group.select_a_row(parent_id)
            
            menu=get_menu(config_admin.modules_admin)
        
            lang_selected=get_language(s)
            
            content_index=t.load_template('pastafari/add_servers_group.phtml', group=arr_group)

            return t.load_template('admin/content.html', title=I18n.lang('pastafari', 'servers_groups_config', 'Server\'s Group servers'), content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
            
        else:
            redirect(make_url(config.admin_folder))
    
    else:
    
        redirect(make_url(config.admin_folder))

@post('/'+pastafari_folder+'/editservers/<parent_id:int>')
def add_servers(parent_id):
    pass

@route('/'+pastafari_folder+'/configure/<parent_id:int>')
def execute_task(parent_id):
    
    # Get python file with the code
    
    return ""


def task_options(url, id, arr_row):
    
    arr_list=SimpleList.standard_options(url, id, arr_row)
    
    arr_list.append('<a href="%s">Subgroups</a>' % (make_url(pastafari_folder+'/groups', {'parent_id': str(id)})) )
    
    arr_list.append('<a href="%s">Edit servers</a>' % (make_url(config.admin_folder+'/'+pastafari_folder+'/servers', {'group_id': str(id)})))
    
    return arr_list
