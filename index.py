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
from modules.pastafari.models import servers
from paramecio.citoplasma import datetime

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

@route('/'+pastafari_folder+'/getinfo')
def getinfo():
    
    connection=WebModel.connection()

    server=servers.Server(connection)
    
    status_disk=servers.StatusDisk(connection)
    
    c=server.select_count()
    
    now=datetime.now(True)
        
    timestamp_now=datetime.obtain_timestamp(now)

    five_minutes=int(timestamp_now)-300
    
    five_minutes_date=datetime.timestamp_to_datetime(five_minutes)
    
    server.set_conditions('WHERE date<%s', [five_minutes_date])
    
    c_down=server.select_count()
    
    server.set_conditions('WHERE num_updates>%s', [0])
    
    c_updates=server.select_count()
    
    with status_disk.query('select sum(used) as total_used, sum(free) as total_free from statusdisk') as cur:
        arr_disk=cur.fetchone()
        
    status_disk.set_conditions('WHERE percent>%s', [85])
    
    c_bloated_disk=status_disk.select_count()
    
    arr_json={'num_servers': c, 'num_servers_down': c_down, 'num_servers_updates': c_updates, 'disk_info': arr_disk, 'num_servers_bloated': c_bloated_disk}
    
    return arr_json


if config.default_module=="pastafari":

    home = route("/")(home)
