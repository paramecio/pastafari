#/usr/bin/env python3

from modules.pastafari.libraries.task import ArgsTask
from modules.pastafari.models.tasks import Task
from paramecio.cromosoma import coreforms
from paramecio.cromosoma.formsutils import show_form
from collections import OrderedDict

class MakeTask(ArgsTask):
    
    def __init__(self, conn):
        
        super().__init__(conn)
        
        self.name_task='MariaDB installation'
        
        self.description_task='Installation of a standalone mysql server'
        
        self.codename_task='standalone_mysql'
        
        self.files=[['modules/pastafari/scripts/servers/databases/mariadb/${os_server}/install_mariadb.py', 0o700]]
        
        # Format first array element is command with the interpreter, the task is agnostic, the files in os directory. The commands are setted with 750 permission.
        # First element is the file, next elements are the arguments
        
        #self.commands_to_execute=[['modules/pastafari/scripts/servers/databases/mysql/install_mariadb.py', '']];
        
        #THe files to delete
        
        self.delete_files=[]
        
        self.delete_directories=['modules/pastafari/scripts/servers/databases/mariadb']
        
        self.task=Task(conn)
        
        self.one_time=True
        
        self.version='1.0'
        
        self.arr_form=OrderedDict()
        
        self.arr_form['mysql_password']=coreforms.PasswordForm('mysql_password', '')
        
        self.arr_form['mysql_password'].required=True
        
        self.arr_form['mysql_password'].label='The MySQL password used by all servers'
        
        self.arr_form['repeat_mysql_password']=coreforms.PasswordForm('repeat_mysql_password', '')
        
        self.arr_form['repeat_mysql_password'].required=True
        
        self.arr_form['repeat_mysql_password'].label='Repeat MySQL password'
        
        self.yes_form=True
        
    
    def form(self, t, yes_error=False, pass_values=False, **args):
        
        #Here load the form for it task
        
        return '<h2>Mariadb/MySQL configuration</h2>'+show_form(args, self.arr_form, t, yes_error, pass_values)
        
    def check_form(self, **args):
        
        return True
    
    def update_task(self, post, task_id):
        
        self.task.create_forms()
        
        if 'mysql_password' in post and 'repeat_mysql_password' in post:
            
            if post['mysql_password'].strip()!='' and post['mysql_password']==post['repeat_mysql_password']:
                
                self.task.reset_require()
                
                self.commands_to_execute=[['modules/pastafari/scripts/servers/databases/mariadb/${os_server}/install_mariadb.py', '--password=%s' % post['mysql_password']]]
                
                #if self.task.insert({'name_task': 'Mariadb Install server', 'description_task': 'Install a mariadb/Mysql server in your selected hosts', 'codename_task': 'mariadb_simple_server', 'files': self.files, 'commands_to_execute': self.commands_to_execute, 'delete_files': self.delete_files, 'delete_directories': self.delete_directories, 'one_time': self.one_time, 'version': self.version}):
                if self.task.set_conditions('WHERE id=%s', [task_id]).update({'commands_to_execute': self.commands_to_execute}):
                    
                    return True
            else:
                self.arr_form['mysql_password'].txt_error='Passwords doesn\'t match'
                
        return False
            
        
        
