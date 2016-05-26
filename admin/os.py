#!/usr/bin/python3

from paramecio.citoplasma.generate_admin_class import GenerateAdminClass
from paramecio.citoplasma.lists import SimpleList
from paramecio.citoplasma.urls import make_url
from modules.pastafari.models import servers, tasks
from settings import config
from bottle import request, redirect

#t_admin=ptemplate('modules/pastafari')

def admin(**args):
    
    t=args['t']
    
    conn=args['connection']
    
    url=make_url(config.admin_folder+'/pastafari/os')
    
    os=servers.OsServer(conn)
    
    admin=GenerateAdminClass(os, url, t)
    
    return admin.show()
    

