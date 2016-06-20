#/usr/bin/python3

from modules.pastafari.libraries.task import ArgsTask
from modules.pastafari.models.tasks import Task

class MakeTask(ArgsTask):
    
    def __init__(self, conn):
        
        super().__init__(conn)
        
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
    
    def form(self, t):
        
        #Here load the form for it task
        
        return "The MySQL password used by all servers: <input type=\"text\" name=\"mysql_password\"/>"
    
    def insert_task(self, post):
        
        self.task.create_forms()
        
        if 'mysql_password' in post:
        
            self.commands_to_execute=[['modules/pastafari/scripts/servers/databases/mariadb/${os_server}/install_mariadb.py', '--password=%s' % post['mysql_password']]]
            
            if self.task.insert({'name_task': 'Mariadb Install server', 'description_task': 'Install a mariadb/Mysql server in your selected hosts', 'codename_task': 'mariadb_simple_server', 'files': self.files, 'commands_to_execute': self.commands_to_execute, 'delete_files': self.delete_files, 'delete_directories': self.delete_directories, 'one_time': self.one_time, 'version': self.version}):
                
                return (self.task.insert_id(), 'Mariadb Install server', 'Install a mariadb/Mysql server in your selected hosts')
                
        return False
            
        
        
