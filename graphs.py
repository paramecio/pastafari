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

server_task=config_task.server_task

server_task=server_task+'/exec/'+config_task.api_key+'/'

url=make_url('pastafari/servers')

pastafari_folder='pastafari'

if hasattr(config, 'pastafari_folder'):
    pastafari_folder=config.pastafari_folder

load_lang(['paramecio', 'admin'], ['paramecio', 'common'])

env=env_theme(__file__)

env.directories.insert(1, config.paramecio_root+'/modules/admin/templates')

# Method for show the graphs
@route('/'+pastafari_folder+'/servergraphs/<server_id:int>')
def graphs(server_id):
    
    if check_login():
        
        s=get_session()
        
        #Load menu
        
        menu=get_menu(config_admin.modules_admin)

        lang_selected=get_language(s)
        
        t=PTemplate(env)
    
        conn=WebModel.connection()
        
        server=servers.Server(conn)
        
        arr_server=server.select_a_row(server_id)
    
        if arr_server:
        
            content_index=t.load_template('pastafari/admin/graphs.phtml', server=arr_server, api_key=config_task.api_key)
            
        else:
            
            content_index=''

        
        if t.show_basic_template==True:

            return t.load_template('admin/content.html', title='Servers', content_index=content_index, menu=menu, lang_selected=lang_selected, arr_i18n=I18n.dict_i18n)
        else:
            
            return content_index
        
    else:
        redirect(make_url(config.admin_folder))

# Method for get data for graphs
@route('/'+pastafari_folder+'/getdatagraphs/<server_id:int>')
def net_cpu_status(server_id):
    
    if check_login():
        
        s=get_session()
    
        conn=WebModel.connection()
    
        server=servers.Server(conn)
        
        arr_server=server.select_a_row(server_id)
        
        if arr_server:
        
            if 'ip' in arr_server:
            
                ip=arr_server['ip']
                
                now=datetime.obtain_timestamp(datetime.now(True))
                
                hours12=now-21600
                
                date_now=datetime.timestamp_to_datetime(now)
                
                date_hours12=datetime.timestamp_to_datetime(hours12)
                
                status_cpu=servers.StatusCpu(conn)
                
                status_cpu.set_conditions('where ip=%s and date>=%s and date<=%s', [ip, date_hours12, date_now])
                
                #arr_cpu=status_cpu.select_to_array(['idle', 'date'])
                cur=status_cpu.select(['idle', 'date'])
                
                x=0
                
                arr_cpu=[]
                
                cur.fetchone()
                
                for cpu_info in cur:
                    
                    arr_cpu.append(cpu_info['idle'])
                    
                cur.close()
                
                status_mem=servers.StatusMemory(conn)
                
                status_mem.set_conditions('where ip=%s and date>=%s and date<=%s', [ip, date_hours12, date_now]) 
                
                #status_mem.set_order(['id', 'ASC'])
                
                #arr_mem=status_mem.select_to_array(['used', 'free', 'date'])
                arr_mem=[]
                with status_mem.select(['used', 'free', 'cached', 'date'])  as cur:
                    #cur.fetchone()
                    
                    for mem_info in cur:
                        mem_info['used']=((mem_info['used']/1024)/1024)/1024
                        mem_info['free']=((mem_info['free']/1024)/1024)/1024
                        mem_info['cached']=((mem_info['cached']/1024)/1024)/1024
                        arr_mem.append(mem_info)
                
                if len(arr_mem)>2:
                    arr_mem.pop(0)
                
                #arr_cpu=status_cpu.select_to_array(['idle', 'date'])
                cur=status_cpu.select(['idle', 'date'])
                
                arr_net={}
                
                status_net=servers.StatusNet(conn)
                
                status_net.set_conditions('where ip=%s and date>=%s and date<=%s', [ip, date_hours12, date_now])
                
                arr_net=[]
                
                cur=status_net.select(['bytes_sent', 'bytes_recv', 'date'])
                
                substract_time=0 #datetime.obtain_timestamp(datetime.now())
                
                c_hours12=now
                
                c_elements=0
                
                c_count=cur.rowcount
                
                if c_count>0:
                
                    data_net=cur.fetchone()
                    
                    first_recv=data_net['bytes_recv']
                    first_sent=data_net['bytes_sent']
                    
                    if len(arr_cpu)<(c_count-1):
                        arr_cpu.append(arr_cpu[1:])
                    
                    for data_net in cur:
                        
                        timestamp=datetime.obtain_timestamp(data_net['date'], True)
                        
                        diff_time=timestamp-substract_time
                        
                        if substract_time!=0 and diff_time>300:
                            
                            count_time=timestamp
                            
                            while substract_time<=count_time:
                    
                                form_time=datetime.timestamp_to_datetime(substract_time)
                                
                                arr_net.append({'date': datetime.format_time(form_time)})
                                        
                                substract_time+=60
                        
                        bytes_sent=round((data_net['bytes_sent']-first_sent)/1024)
                        bytes_recv=round((data_net['bytes_recv']-first_recv)/1024)
                        cpu=arr_cpu[x]
                        
                        memory_used=arr_mem[x]['used']
                        memory_free=arr_mem[x]['free']
                        memory_cached=arr_mem[x]['cached']

                        arr_net.append({'bytes_sent': bytes_sent, 'bytes_recv': bytes_recv, 'date': datetime.format_time(data_net['date']), 'cpu': cpu, 'memory_used': memory_used, 'memory_free': memory_free, 'memory_cached': memory_cached})
                        
                        first_sent=data_net['bytes_sent']
                        first_recv=data_net['bytes_recv']
                        
                        c_hours12=timestamp
                        
                        substract_time=int(timestamp)
                        
                        c_elements+=1
                        
                        x+=1
                        
                    # If the last time is more little that now make a loop 
                    
                    while c_hours12<=now:
                    
                        form_time=datetime.timestamp_to_datetime(c_hours12)
                        
                        seconds=form_time[-2:]
                            
                        #print(form_time)
                        
                        if seconds=='00':
                            
                            arr_net.append({'date': datetime.format_time(form_time)})
                                
                            # if secons is 00 and z=1 put value
                            #arr_net.append({'date': datetime.format_time(form_time)})
                                
                            pass
                        
                        c_hours12+=1
                    
                    cur.close()
                    
                    if c_elements>2:
                        
                        return filter_ajax(arr_net)
                    else:
                        
                        return filter_ajax({})
                        
                    return filter_ajax({})
        
    return filter_ajax({})

# Method for get data for graphs
@route('/'+pastafari_folder+'/getdiskgraphs/<server_id:int>')
def disk_status(server_id):
    
    if check_login():
        
        s=get_session()
    
        conn=WebModel.connection()
    
        server=servers.Server(conn)
        
        arr_server=server.select_a_row(server_id)
        
        if arr_server:
        
            if 'ip' in arr_server:
            
                ip=arr_server['ip']
                
                status_disk=servers.StatusDisk(conn)
                
                status_disk.set_conditions('where ip=%s', [ip])
                
                arr_disk=status_disk.select_to_array(['disk', 'used', 'free', 'date'])
                
                return filter_ajax(arr_disk)
    return filter_ajax({})
