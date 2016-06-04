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

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

env.directories.insert(1, 'paramecio/modules/admin/templates')

@route('/'+pastafari_folder)
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
            
            content_index=t.load_template('pastafari/dashboard.phtml')

            return t.load_template('admin/content.html', title='Dashboard', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
            
        else:
            redirect(config.admin_folder)
    
    else:
    
        redirect(config.admin_folder)


if config.default_module=="pastafari":

    home = route("/")(home)
