#!/usr/bin/python3

import traceback, sys
from paramecio.citoplasma.mtemplates import env_theme, PTemplate
from paramecio.citoplasma.i18n import load_lang, I18n
from paramecio.citoplasma.urls import make_url, add_get_parameters
from paramecio.citoplasma.adminutils import get_menu, get_language, check_login
from paramecio.citoplasma.sessions import get_session
from bottle import route, get,post,response,request
from settings import config
from settings import config_admin
from paramecio.citoplasma.httputils import GetPostFiles
from paramecio.cromosoma.webmodel import WebModel
from bottle import redirect
from modules.pastafari.models import servers
from paramecio.citoplasma import datetime

#Dashboard of pastafari

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
    
    if check_login():
                
        #Load menu
        
        menu=get_menu(config_admin.modules_admin)
    
        lang_selected=get_language(s)
        
        content_index=t.load_template('pastafari/dashboard.phtml')

        return t.load_template('admin/content.html', title='Dashboard', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        
    else:
        redirect(config.admin_folder)

#THe info for the dashboard

@route('/'+pastafari_folder+'/getinfo')
def getinfo():
    
    connection=WebModel.connection()

    server=servers.Server(connection)
    
    status_disk=servers.StatusDisk(connection)
    
    status_net=servers.StatusNet(connection)
    
    status_cpu=servers.StatusCpu(connection)
    
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
    
    # Network use
    
    twelve_hours=int(timestamp_now)-43200
    
    twelve_hours_date=datetime.timestamp_to_datetime(twelve_hours)
    
    #status_net.set_conditions('WHERE date>%s', [twelve_hours_date])
    
    #SELECT(t2.sub1 - t1.sub1) AS sub1, (t2.sub2 - t1.sub2) AS sub2
    #FROM table t1 CROSS JOIN
    # table t2
    #WHERE t1.date = '2014-11-08' AND t2.id = '2014-11-07';
    
    # select (t1.bytes_sent+t2,bytes_sent) as bytes_sent from statusnet t1 CROSS JOIN statusnet t2
    
    arr_net={'total_bytes_recv': 0, 'total_bytes_sent': 0}
    
    #status_net.set_conditions('WHERE date>%s', [twelve_hours_date])
    
    #status_net.set_order('date', 'ASC')
    
    #select bytes_sent, bytes_recv, ip from statusnet WHERE date>'20160606093229' and last_updated=1 group by ip
    
    status_net.set_conditions('WHERE date>%s and last_updated=1 group by ip', [twelve_hours_date])
    
    with status_net.select(['bytes_recv', 'bytes_sent']) as cur:
        
        # I think that this loop can be optimized
        
        for net in cur:
            arr_net['total_bytes_recv']+=net['bytes_recv']
            arr_net['total_bytes_sent']+=net['bytes_sent']
        
    arr_cpu={'0-30': 0, '30-70': 0, '70-100': 0}
    
    status_cpu.set_conditions('WHERE date>%s and last_updated=1 group by ip', [twelve_hours_date])
    
    with status_cpu.select(['idle']) as cur:
        
        for cpu in cur:
            if cpu['idle']>70:
                arr_cpu['70-100']+=1
            elif cpu['idle']>30:
                arr_cpu['30-70']+=1
            else:
                arr_cpu['0-30']+=1
    #print(c_net)
    
    arr_json={'num_servers': c, 'num_servers_down': c_down, 'num_servers_updates': c_updates, 'disk_info': arr_disk, 'num_servers_bloated': c_bloated_disk, 'net_info': arr_net, 'cpu_info': arr_cpu}
    
    return arr_json


if config.default_module=="pastafari":

    home = route("/")(home)
