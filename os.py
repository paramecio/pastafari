#!/usr/bin/python3

from paramecio.citoplasma.generate_admin_class import GenerateAdminClass
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.urls import make_url
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models import servers, tasks
from bottle import request, redirect, route, post
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.adminutils import check_login, get_menu, get_language
from settings import config
from settings import config_admin
from paramecio.citoplasma.sessions import get_session

#t_admin=ptemplate('modules/pastafari')

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

env.directories.insert(1, config.paramecio_root+'/modules/admin/templates')

@route('/'+pastafari_folder+'/os')
@post('/'+pastafari_folder+'/os')
def home():
    
    if check_login():
        
        s=get_session()
        
        #Load menu
        
        menu=get_menu(config_admin.modules_admin)

        lang_selected=get_language(s)
        
        t=PTemplate(env)
    
        conn=WebModel.connection()
        
        url=make_url(pastafari_folder+'/os')
        
        os=servers.OsServer(conn)
        
        admin=GenerateAdminClass(os, url, t)
        
        content_index=admin.show()

        return t.load_template('admin/content.html', title='Os Servers', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        
    else:
        redirect(make_url(config.admin_folder))
    

