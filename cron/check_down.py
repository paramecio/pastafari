import os
import sys

sys.path.insert(0, os.path.realpath(os.path.dirname(__file__))+'/../../../')

from paramecio.cromosoma.webmodel import WebModel
from modules.pastafari.models import servers
from paramecio.citoplasma.sendmail import SendMail
from paramecio.citoplasma import datetime
from paramecio.citoplasma.i18n import I18n
from paramecio.citoplasma.urls import make_url
from settings import config

email_address='localhost'

if hasattr(config, 'email_address'):
    email_address=config.email_address

if not hasattr(config, 'email_notification'):
    print('You need an email address configured for notifications')
    exit(1)


conn=WebModel.connection()

server=servers.Server(conn)

now=datetime.now(True)
        
timestamp_now=datetime.obtain_timestamp(now)

five_minutes=int(timestamp_now)-300

five_minutes_date=datetime.timestamp_to_datetime(five_minutes)

server.set_conditions('WHERE date<%s', [five_minutes_date])

arr_server=[]

with server.select(['hostname']) as cur:
    for s in cur:
        arr_server.append(s['hostname'])

if len(arr_server)>0:
    
    send_mail=SendMail()
                
    content_mail="THE NEXT SERVERS ARE DOWN: "+", ".join(arr_server)+"\n\n"
    
    content_mail='Please, click in this link for view the servers down; '+config.domain_url+make_url(config.admin_folder+'/pastafari/servers', {'type': 'down'})
    
    if not send_mail.send(email_address, [config.email_notification], I18n.lang('pastafari', 'servers_down', 'WARNING:  SERVERS ARE DOWN!'), content_mail):
        print('Sended email with notification')

