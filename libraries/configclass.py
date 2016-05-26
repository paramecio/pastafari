#!/usr/bin/python3

import os

class ConfigClass:
	
    def __init__(self):
    
        #Local paths

        self.base_path=os.path.dirname(os.path.dirname(__file__))

        self.tasks_path=['tasks', 'parameciossh.tasks']

        self.scripts_path=['scripts', 'modules/pastafari/scripts']

        self.logs_path='logs'

        #Remote paths

        self.remote_path='/home/spanel'

        #Relative to remote_path

        self.tmp_sftp_path='tmp'

        self.remote_user='spanel'
        
        self.remote_password=None

        #Local home

        self.home=''

        #SSH configuration

        self.user_key=''

        self.public_key=''

        self.private_key=''

        self.password_key=None

        self.port=22

        self.deny_missing_host_key=True

        #Internal tasks

        self.num_of_forks=10

        self.stop_if_error=False

        self.num_errors=0

        self.num_success=0

        self.num_total=0

        self.num_servers=0

        self.file_resume=None
        
        self.server_task='http://127.0.0.1:1337'
        
        self.url_monit=''
        
        self.api_key=''

# Class for global configuration

config_task=ConfigClass()
