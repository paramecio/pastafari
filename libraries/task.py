#!/usr/bin/env python3

import paramiko, json
import os, sys,traceback
from stat import S_ISDIR
from modules.pastafari.models import tasks
from modules.pastafari.models.servers import ServerGroupTask
from modules.pastafari.libraries.configclass import config_task
from paramecio.citoplasma.i18n import I18n
from paramecio.cromosoma.webmodel import WebModel

class ArgsTask:
    
    def __init__(self, conn):
        
        self.files=[]
        
        # Format first array element is command with the interpreter, the task is agnostic, the files in os directory. The commands are setted with 750 permission.
        # First element is the file, next elements are the arguments
        
        self.commands_to_execute=[];
        
        #THe files to delete
        
        self.delete_files=[];
        
        self.delete_directories=[]
        
        self.one_time=False
        
        self.version='1.0'
        
        self.simultaneous=False

    def form(self):
        
        return ""
        
    def insert_task(self, post):
        
        # Insert task
        
        pass

class Task:

    def __init__(self, server, task_id=0):
        
        self.config=config_task
        
        self.server=server
        
        self.name=''
        
        self.codename=''
        
        self.description=''

        self.txt_error=''
        
        self.os_server=''
        
        self.files=[]
        
        # Format first array element is command with the interpreter, the task is agnostic, the files in os directory. The commands are setted with 750 permission.
        # First element is the file, next elements are the arguments
        
        self.commands_to_execute=[];
        
        #THe files to delete
        
        self.delete_files=[];
        
        self.delete_directories=[];
        
        #The id of the task in db
        
        self.id=task_id
        
        self.user=''
        self.password=''
        
        connection=WebModel.connection()
        
        self.logtask=tasks.LogTask(connection)
        self.task=tasks.Task(connection)
        self.taskdone=ServerGroupTask(connection)
        
        self.ssh=paramiko.SSHClient()
        
        self.logtask.reset_require()
        self.task.reset_require()
        
        self.one_time=False
        
        self.version='1.0'
        
        self.simultaneous=False
        
        pass

    def prepare_connection(self):
        
        self.ssh.load_system_host_keys()
        
        #Check if the unknown host keys are rejected or not
        
        #if self.config.deny_missing_host_key == False:
            
            #self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Check if in known_hosts
        check_ssh_host= paramiko.hostkeys.HostKeys()
        
        check_ssh_host.load(self.config.ssh_directory+'/known_hosts')
        
        host_key=self.ssh.get_host_keys()
        
        add_host=False
        
        if check_ssh_host.lookup(self.server)==None:
            
            # Be tolerant for the first connect with hostkey policy
            
            self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            add_host=True
            
            #self.ssh.save_host_keys(config_task.ssh_directory)
            
            #Add host to known_hosts file
            
            #hashed_host=check_ssh_host.hash_host(self.server)
            
            #print(hashed_host)
        #Prepare ssh keys
        
        #rsa=prepare_ssh_keys(self.config.password_key)
        """
        rsa=None
        
        if self.config.remote_password is None:
        
            try:
            
                rsa=paramiko.RSAKey.from_private_key_file(self.config.private_key, self.config.password_key)
            
            except (paramiko.ssh_exception.PasswordRequiredException, paramiko.ssh_exception.SSHException):
                rsa=None
                self.txt_error='Error: you need a valid password for rsa key'
            
            if rsa==None:
                return False
        """
        
        rsa=paramiko.RSAKey.from_private_key_file(self.config.private_key, self.config.password_key)
        
        try:
            
            self.ssh.connect(self.server, port=self.config.port, username=self.config.remote_user, password=self.config.remote_password, pkey=rsa, key_filename=None, timeout=None, allow_agent=True, look_for_keys=True, compress=False, sock=None, gss_auth=False, gss_kex=False, gss_deleg_creds=True, gss_host=None, banner_timeout=None)           
            
            if add_host:
                host_key.save(self.config.ssh_directory+'/known_hosts')
            
        except paramiko.SSHException as e:
            self.txt_error="Error: cannot connect to the server SSHException\n"+str(e)
            return False
        
        except paramiko.AuthenticationException as e:
            self.txt_error="Error: cannot connect to the server AuthenticationException \n"+str(e)
            return False
            
        except paramiko.BadHostKeyException as e:
            self.txt_error="Error: cannot connect to the server BadHostKeyException\n"+str(e)
            return False
            
        except OSError as e:
            self.txt_error="Error: cannot connect to the server OsError \n"+str(e)
            return False
            
        except:    
            self.txt_error="Error: cannot connect to the server Generic\n"+traceback.format_exc()
            return False
        
        #finally:
        #   self.ssh.close()
        
        return True
        

    def upload_files(self):
        
        try:
    
            sftp=self.ssh.open_sftp()
        
        except:

            self.txt_error='Sorry, error connecting to sftp: '+traceback.format_exc()
            return False
        
        c=len(self.files)
        
        if c>0:
        
            percent=100/c
            
            progress=0
            
            for f in self.files:
                
                source_file=f[0]
                
                source_file=source_file.replace('${os_server}', self.os_server)
                
                permissions=f[1]
                dest_file=self.config.remote_path+'/'+source_file
                
                try:
                    
                    if not os.path.isfile(source_file):
                        self.txt_error="Sorry, you don't have source file to upload "+source_file
                        return False
                    
                    dir_file=os.path.dirname(source_file)
                    
                    parts_dir_file=dir_file.split('/')
                        
                    # Create remote directory
                    
                    try:
                        
                        f_stat=sftp.stat(dir_file)

                    except IOError:

                        try:
                            
                            final_path=''
                            
                            for d in parts_dir_file:
                                
                                final_path+=d+'/'
                                
                                #print(self.config.remote_path+'/'+final_path)
                                
                                try:
                                    
                                    f_stat=sftp.stat(final_path)
                                
                                except IOError:
                                
                                    sftp.mkdir(final_path)
                            
                        except:
                            
                            self.txt_error='Sorry, error creating the directories for the files: '+traceback.format_exc()
                            return False
                    
                    # Upload file
                    
                    try:
                    
                        sftp.put(source_file, dest_file, callback=None, confirm=True)
                        
                        sftp.chmod(dest_file, permissions)
                        
                        progress+=percent
                        
                        self.logtask.insert({'task_id': self.id, 'progress': progress, 'message': I18n.lang('pastafari', 'uploading_files', 'Uploading file: ')+source_file, 'error': 0, 'server': self.server})
                        
                    except:
                        
                        self.txt_error='Sorry, cannot upload file '+source_file+': '+traceback.format_exc()
                        return False
                    
                    # Create directory recursively if not exists
                
                except:
                    self.txt_error='Error: '+traceback.format_exc()
                    return False
         
            self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': I18n.lang('pastafari', 'upload_successful', 'Files uploaded successfully...'), 'error': 0, 'server': self.server})
        
        return True

    def delete_files_and_dirs(self):
        
        sftp=self.ssh.open_sftp()
        
        c=len(self.delete_files)
        
        if c>0:
        
            percent=100/c
            
            progress=0
            
            for filepath in self.delete_files:
                
                filepath=filepath.replace('${os_server}', self.os_server)
                
                try:
                    sftp.remove(self.config.remote_path+'/'+filepath)
                    
                    progress+=percent
                    
                    self.logtask.insert({'task_id': self.id, 'progress': progress, 'message': I18n.lang('pastafari', 'cleaning_files', 'Cleaning file: ')+filepath, 'error': 0, 'server': self.server})
                    
                except IOError:
                    
                    self.txt_error="Sorry, cannot remove file "+filepath+" from server."
                    
                    return False


        c=len(self.delete_directories)
        
        if c>0:
        
            percent=100/c
            
            progress=0

            for path in self.delete_directories:

                path=path.replace('${os_server}', self.os_server)

                if self.delete_dir(path, sftp):
                
                    progress+=percent
                    
                    self.logtask.insert({'task_id': self.id, 'progress': progress, 'message': I18n.lang('pastafari', 'cleaning_directories', 'Cleaning directory: ')+path, 'error': 0, 'server': self.server})

                else:
                    self.txt_error+="Sorry, cannot remove directory "+path+" from server."
                    
                    return False

        return True

    
    def isdir(self, path, sftp):
        try:
            return S_ISDIR(sftp.stat(path).st_mode)
        except IOError:
            return False

    def delete_dir(self, path, sftp):
        
        #path=self.config.remote_path+'/'+path
        
        if path is not "/":
        
            files = sftp.listdir(path)
            
            for f in files:
                filepath = os.path.join(path, f)
                try:
                    if self.isdir(filepath, sftp):
                        self.delete_dir(filepath, sftp)
                    else:
                        sftp.remove(filepath)
                except IOError:
                    self.txt_error="Sorry, cannot remove "+filepath+" from server."
                    return False

            sftp.rmdir(path)
            
        return True

    def exec(self):
        
        # Get task
        
        #self.id=task_id
        
        self.task.reset_require()
        
        self.task.valid_fields=['name_task', 'description_task', 'error', 'status', 'server']
        
        self.logtask.valid_fields=self.logtask.fields.keys()
        
        if self.id==0:
            
            # Insert the task
            
            self.task.reset_require()
            
            self.task.insert({'name_task': self.name, 'description_task': self.description, 'server': self.server})
            
            self.id=self.task.insert_id()
        
        if not self.prepare_connection():
            self.task.conditions=['WHERE id=%s', [self.id]]
            self.task.update({'error': 1, 'status': 1})
            
            self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': self.txt_error, 'error': 1, 'status': 1, 'server': self.server})
            
            return False
        
        #Check if script was executed
        
        if self.codename!='':
        
            if self.one_time==True:
            
                with self.ssh.open_sftp() as sftp:
                    
                    try:
                    
                        with sftp.file(self.config.remote_path+'/tasks/'+self.codename) as f:
                            version=f.read()
                            version=version.decode('utf-8').strip()
                            
                            if version==self.version:
                                #self.task.conditions=['WHERE id=%s', [self.id]]
                                #self.task.update({'error': 0, 'status': 1})
                                
                                self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': 'This script was executed correctly in this server', 'error': 0, 'status': 1, 'server': self.server})
                                
                                return True
                                
                    except IOError:
                        # It was not executed
                        pass
        
        if not self.upload_files():
            self.task.conditions=['WHERE id=%s', [self.id]]
            self.task.update({'error': 1, 'status': 1})
            
            self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': self.txt_error, 'error': 1, 'status': 1, 'server': self.server})
            
            return False

        self.logtask.insert({'task_id': self.id, 'progress': 0, 'message': 'Executing commands...', 'error': 0, 'status': 0, 'server': self.server})

        # Execute commands
        
        for c in self.commands_to_execute:
        
            try:
                command=c[0]
                
                command=command.replace('${os_server}', self.os_server)
                
                arguments=c[1]
                
                sudo_str=''
                
                if len(c)==3:
                    sudo_str='sudo '
                
                #, get_pty=True
                stdin, stdout, stderr = self.ssh.exec_command(sudo_str+self.config.remote_path+'/'+command+' '+arguments)
                
                for line in stdout:
                    
                    if line==None:
                        
                        line="[]"
                    
                    line=line.strip()

                    try:
                        json_code=json.loads(line)
                        
                        if not 'progress' in json_code or not 'message' in json_code or not 'error' in json_code:
                            self.task.conditions=['WHERE id=%s', [self.id]]
                            self.task.update({'error': 1, 'status': 1})
                            
                            self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': 'Malformed json code: '+str(line), 'error': 1, 'server': self.server})
                            
                            return False
                            
                        else:
                            
                            json_code['task_id']=self.id
                    
                            self.logtask.insert(json_code)
                                                
                    
                    
                    except:
                        
                        #self.task.conditions=['WHERE id=%s', [self.id]]
                        #self.task.update({'error': 0, 'status':0})
                        
                        self.logtask.insert({'task_id': self.id, 'progress': 0, 'no_progress': 1, 'message': str(line), 'error': 0, 'status': 0, 'server': self.server})
                        
                        #return False
                
                last_log_id=self.logtask.insert_id()
                
                if stdout.channel.recv_exit_status()>0:
                    #line=stdout.readlines()
                    #logging.warning(action.codename+" WARNING: "+line)
                    final_text='Error executing the command: %s' % command
                    
                    self.task.conditions=['WHERE id=%s', [self.id]]
                    self.task.update({'error': 1, 'status': 1})
                    
                    for line in stdout:
                        final_text+=' '+line
                    
                    for line in stderr:
                        final_text+=' '+line
                    
                    self.logtask.set_conditions('where id=%s', [last_log_id])
                    
                    self.logtask.update({'progress': 100, 'error': 1, 'message': final_text, 'status': 1, 'server': self.server})
                    
                    return False
                
            except:
                
                self.task.conditions=['WHERE id=%s', [self.id]]
                self.task.update({'error': 1, 'status': 1})
                
                self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': traceback.format_exc(), 'error': 1, 'status': 1, 'server': self.server})

                return False
        
        # Clean files
        
        if not self.delete_files_and_dirs():
            
            self.task.conditions=['WHERE id=%s', [self.id]]
            self.task.update({'error': 1, 'status': 1})
                
            self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': self.txt_error, 'error': 1, 'status': 1, 'server': self.server})
            
            return False
        
        #Upload files

        #self.ssh.close()

        # FInish task
        
        #Put this version how executed
        
        if self.codename!='':
        
            if self.one_time==True:
                
                with self.ssh.open_sftp() as sftp:
                
                    try:
                        path_check=self.config.remote_path+'/tasks/'
                                            
                        f_stat=sftp.stat(path_check)
                    
                    except IOError:
                    
                        sftp.mkdir(path_check)
                
                    with sftp.file(path_check+self.codename, 'w') as f:
                        f.write(self.version)
                    
            
        self.logtask.insert({'task_id': self.id, 'progress': 100, 'message': I18n.lang('pastafari', 'finished_successfully', 'All tasks done successfully...'), 'error': 0, 'status': 1, 'server': self.server})
        
        # Add 
        self.taskdone.create_forms()
        
        self.taskdone.insert({'name_task': self.codename, 'ip': self.server})
        
        self.task.conditions=['WHERE id=%s', [self.id]]
        self.task.update({'error': 0, 'status': 1})
        
        #connection.close()
        return True
        
    def __del__(self):
        
        if self.ssh!=None:
            self.ssh.close()
