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

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

env.directories.insert(1, 'paramecio/modules/admin/templates')

@get('/'+pastafari_folder+'/groups')
@post('/'+pastafari_folder+'/groups')
def home():
    
    connection=WebModel.connection()
    #Fix, make local variable
    
    t=PTemplate(env)
    
    s=get_session()
    
    if 'login' in s:
        
        if s['privileges']==2:
                
            #Load menu
            
            menu=get_menu(config_admin.modules_admin)
        
            lang_selected=get_language(s)
            
            groups=servers.ServerGroup(connection)
            
            group_list=GenerateAdminClass(groups, make_url(pastafari_folder+'/groups'), t)
            
            group_list.list.fields_showed=['name']
            
            group_list.list.arr_extra_options=[task_options]
            
            content_index=group_list.show()

            return t.load_template('admin/content.html', title=I18n.lang('pastafari', 'servers_groups', 'Server\'s Group'), content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
            
        else:
            redirect(config.admin_folder)
    
    else:
    
        redirect(config.admin_folder)


@route('/'+pastafari_folder+'/runtaskgroup/<group_id:int>')
def execute_task(group_id):
    
    return ""


def task_options(url, id, arr_row):
    
    arr_list=SimpleList.standard_options(url, id, arr_row)
    
    arr_list.append('<a href="%s">Execute task</a>' % (make_url(pastafari_folder+'/runtaskgroup/%i') % id))
    
    return arr_list
