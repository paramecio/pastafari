#/usr/bin/python3

from modules.pastafari.libraries.task import ArgsTask
from modules.pastafari.models.tasks import Task
from paramecio.cromosoma import coreforms
from paramecio.cromosoma.formsutils import show_form
from collections import OrderedDict

class MakeTask(ArgsTask):
    
    def __init__(self, conn):
        
        super().__init__(conn)
        
        self.files=[['modules/pastafari/scripts/servers/mail/postfix/${os_server}/install_postfix.sh', 0o700]]
        self.files.append(['modules/pastafari/scripts/servers/mail/postfix/${os_server}/files/main.cf', 0o644])
        self.files.append(['modules/pastafari/scripts/servers/mail/postfix/${os_server}/files/master.cf', 0o644])
        self.files.append(['modules/mail/utilities/${os_server}/add_domain.py', 0o700])
        self.files.append(['modules/mail/utilities/${os_server}/autoreply.py', 0o755])
        #self.files.append(['modules/pastafari/scripts/servers/mail/postfix/${os_server}/files/utilities/add_account.py', 0o700])
        #self.files.append(['modules/pastafari/scripts/servers/mail/postfix/${os_server}/files/utilities/remove_domain.py', 0o700])
        #self.files.append(['modules/pastafari/scripts/servers/mail/postfix/${os_server}/files/utilities/remove_account.py', 0o700])
        
        self.files.append(['modules/pastafari/scripts/servers/mail/dovecot/${os_server}/install_dovecot.sh', 0o700])
        
        self.files.append(['modules/pastafari/scripts/servers/mail/dovecot/${os_server}/files/10-auth.conf', 0o644])
        self.files.append(['modules/pastafari/scripts/servers/mail/dovecot/${os_server}/files/10-mail.conf', 0o644])
        self.files.append(['modules/pastafari/scripts/servers/mail/dovecot/${os_server}/files/10-master.conf', 0o644])
        self.files.append(['modules/pastafari/scripts/servers/mail/dovecot/${os_server}/files/10-ssl.conf', 0o644])
        
        self.files.append(['modules/pastafari/scripts/servers/databases/sqlite/${os_server}/install_sqlite.sh', 0o700])
        
        self.files.append(['modules/pastafari/scripts/servers/mail/sqlgrey/${os_server}/install_sqlgrey.sh', 0o700])
        self.files.append(['modules/pastafari/scripts/servers/mail/sqlgrey/${os_server}/files/sqlgrey.conf', 0o644])
        
        self.files.append(['modules/pastafari/scripts/servers/mail/opendkim/${os_server}/install_opendkim.sh', 0o700])
        self.files.append(['modules/pastafari/scripts/servers/mail/opendkim/${os_server}/files/opendkim.conf', 0o644])
        self.files.append(['modules/pastafari/scripts/servers/mail/opendkim/${os_server}/files/opendkim', 0o644])
        
        self.files.append(['modules/pastafari/scripts/servers/system/quota/${os_server}/install_quota_home.py', 0o700])
        
        # Format first array element is command with the interpreter, the task is agnostic, the files in os directory. The commands are setted with 750 permission.
        # First element is the file, next elements are the arguments
        
        self.commands_to_execute=[['modules/pastafari/scripts/servers/mail/postfix/${os_server}/install_postfix.sh', '']];
        
        self.commands_to_execute.append(['modules/pastafari/scripts/servers/mail/dovecot/${os_server}/install_dovecot.sh', ''])
        
        self.commands_to_execute.append(['modules/pastafari/scripts/servers/databases/sqlite/${os_server}/install_sqlite.sh', ''])
        
        self.commands_to_execute.append(['modules/pastafari/scripts/servers/mail/sqlgrey/${os_server}/install_sqlgrey.sh', ''])
        
        self.commands_to_execute.append(['modules/pastafari/scripts/servers/mail/opendkim/${os_server}/install_opendkim.sh', ''])
        
        self.commands_to_execute.append(['modules/pastafari/scripts/servers/system/quota/${os_server}/install_quota_home.py', '', ''])
        
        #THe files to delete
        
        self.delete_files=[]
        
        self.delete_directories=['modules/pastafari/scripts/servers/mail', 'modules/pastafari/scripts/servers/system']
        
        self.task=Task(conn)
        
        self.one_time=True
        
        self.version='1.0'
        
        self.arr_form=OrderedDict()
        """
        self.arr_form['domain']=coreforms.TextForm('domain', '')
        
        self.arr_form['domain'].required=True
        
        self.arr_form['domain'].label='The Base domain'
        """       
    
    def form(self, t, yes_error=False, pass_values=False, **args):
        
        #Here load the form for it task
        
        
        
        #return "The MySQL password used by all servers: <input type=\"password\" name=\"mysql_password\"/>"
        
        #return t.load_template('forms/modelform.phtml', forms=self.arr_form)
        # def show_form(post, arr_form, t, yes_error=True, pass_values=True, modelform_tpl='forms/modelform.phtml'):
        
        return show_form(args, self.arr_form, t, yes_error, pass_values)
        
    def check_form(self, **args):
        
        return True
    
    def insert_task(self, post):
        
        self.task.create_forms()
        
        """
        if 'mysql_password' in post and 'repeat_mysql_password' in post:
            
            if post['mysql_password'].strip()!='' and post['mysql_password']==post['repeat_mysql_password']:
                
                self.commands_to_execute=[['modules/pastafari/scripts/servers/databases/mariadb/${os_server}/install_mariadb.py', '--password=%s' % post['mysql_password']]]
                
                if self.task.insert({'name_task': 'Postfix Install server', 'description_task': 'Install a mariadb/Mysql server in your selected hosts', 'codename_task': 'mariadb_simple_server', 'files': self.files, 'commands_to_execute': self.commands_to_execute, 'delete_files': self.delete_files, 'delete_directories': self.delete_directories, 'one_time': self.one_time, 'version': self.version}):
                    
                    return (self.task.insert_id(), 'Postfix Install server', 'Install a mariadb/Mysql server in your selected hosts')
            else:
                self.arr_form['mysql_password'].txt_error='Passwords doesn\'t match'
                
        return (False, 'Mariadb Install server', 'Install a mariadb/Mysql server in your selected hosts')
        """
        if self.task.insert({'name_task': 'Postfix server', 'description_task': 'Install a mail server in your selected hosts with postfix, dovecot, sqlgrey based in unix accounts', 'codename_task': 'standalone_postfix', 'files': self.files, 'commands_to_execute': self.commands_to_execute, 'delete_files': self.delete_files, 'delete_directories': self.delete_directories, 'one_time': self.one_time, 'version': self.version}):
                    
            return (self.task.insert_id(), 'Postfix Install server', 'Install a mail server with postfix/dovecot in your selected hosts, based in unix accounts')
        else:
            return (False, 'Postfix Install server', 'Install a mail server with postfix/dovecot in your selected hosts, based in unix accounts')
        
