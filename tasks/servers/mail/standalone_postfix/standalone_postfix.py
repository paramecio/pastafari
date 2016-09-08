#/usr/bin/env python3

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
        self.files.append(['modules/mail/utilities/${os_server}/remove_domain.py', 0o750])
        self.files.append(['modules/mail/utilities/${os_server}/add_user.py', 0o750])
        self.files.append(['modules/mail/utilities/${os_server}/remove_user.py', 0o750])
        self.files.append(['modules/mail/utilities/${os_server}/add_redirection.py', 0o750])
        self.files.append(['modules/mail/utilities/${os_server}/remove_redirection.py', 0o750])
        self.files.append(['modules/mail/utilities/${os_server}/add_alias.py', 0o750])
        self.files.append(['modules/mail/utilities/${os_server}/remove_alias.py', 0o750])
        #dd_alias.py        add_user.py      remove_domain.py add_domain.py       autoreply.py     remove_redirection.py add_redirection.py  remove_alias.py  remove_user.py

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
        
        self.name_task='Postfix server'
        
        self.description_task='Install a mail server in your selected hosts with postfix, dovecot, sqlgrey based in unix accounts'
        
        self.codename_task='standalone_postfix'
        
        self.one_time=True
        
        self.version='1.0'
        
        self.arr_form=OrderedDict()
        """
        self.arr_form['domain']=coreforms.TextForm('domain', '')
        
        self.arr_form['domain'].required=True
        
        self.arr_form['domain'].label='The Base domain'
        """       
    
    def form(self, t, yes_error=False, pass_values=False, **args):
        
        return "" 
        
    def check_form(self, **args):
        
        return True
    
    def insert_task(self, post):
        
        self.task.create_forms()
        
        if self.task.insert({'name_task': self.name_task, 'description_task': self.description_task, 'codename_task': self.codename_task, 'files': self.files, 'commands_to_execute': self.commands_to_execute, 'delete_files': self.delete_files, 'delete_directories': self.delete_directories, 'one_time': self.one_time, 'version': self.version, 'simultaneous': self.simultaneous}):
                    
            return (self.task.insert_id(), 'Postfix Install server', 'Install a mail server with postfix/dovecot in your selected hosts, based in unix accounts')
        else:
            return (False, 'Postfix Install server', 'Install a mail server with postfix/dovecot in your selected hosts, based in unix accounts')
        
